import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  LinearProgress,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import RefreshIcon from "@mui/icons-material/Refresh";
import api, { uploadScheduleExcel } from "../services/api";
import { useProject } from "../context/ProjectContext";

interface ScheduleActivity {
  id: number;
  project_id: number;
  wbs_id: number | null;
  activity_code: string;
  activity_name: string;
  duration_days: number;
  progress_percent: number;
  status: string;
  start_date: string;
  finish_date: string;
  responsible_party: string;
  created_at?: string;
}

interface ManagementAnalysis {
  project_id: number;
  project: {
    code: string;
    name: string;
  };
  wbs: {
    created: number;
    linked_activities: number;
    total_items: number;
    items: Array<{ id: number; code: string; name: string; activity_count: number }>;
  };
  evm: {
    status?: string;
    message?: string;
    planned_progress?: number | null;
    actual_progress?: number | null;
    spi?: number | null;
    cpi?: number | null;
    eac?: number | null;
    tcpi?: number | null;
  };
  schedule: {
    health: string;
    total_activities: number;
    variance?: number | null;
    critical_activities: number;
  };
  alerts: Array<{ level: string; title: string; message: string }>;
  recovery: { required: boolean; priority?: string | null; recommendation?: string | null };
}

function formatDate(value: string) {
  if (!value) {
    return "-";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function statusColor(
  status: string
): "success" | "warning" | "error" | "default" | "info" {
  const normalized = status.toLowerCase();

  if (normalized === "completed") {
    return "success";
  }

  if (normalized === "in progress") {
    return "info";
  }

  if (normalized.includes("delay") || normalized.includes("late")) {
    return "error";
  }

  if (normalized.includes("hold")) {
    return "warning";
  }

  return "default";
}

export default function Schedule() {
  /*
   * Project selection comes from the global project context
   * (top-bar selector) — no hardcoded project ID. All schedule
   * views follow the selected project.
   */
  const {
    selectedProjectId: projectId,
    selectedProject,
  } = useProject();

  const [activities, setActivities] = useState<ScheduleActivity[]>([]);
  const [loadingSchedule, setLoadingSchedule] = useState(false);
  const [uploadingExcel, setUploadingExcel] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");
  const [error, setError] = useState("");

  const [analysis, setAnalysis] = useState<ManagementAnalysis | null>(null);
  const [analyzing, setAnalyzing] = useState(false);

  const runAnalysis = useCallback(async (selectedProjectId: number) => {
    try {
      setAnalyzing(true);
      setError("");

      const response = await api.post<ManagementAnalysis>(
        `/analysis/project/${selectedProjectId}/run`
      );

      setAnalysis(response.data);
    } catch (err) {
      console.error("Management analysis failed:", err);
    } finally {
      setAnalyzing(false);
    }
  }, []);

  const loadSchedule = useCallback(async (selectedProjectId: number) => {
    try {
      setLoadingSchedule(true);
      setError("");

      const response = await api.get<ScheduleActivity[]>(
        `/schedule/project/${selectedProjectId}`
      );

      const data = Array.isArray(response.data)
        ? response.data
        : [];

      setActivities(
        [...data].sort((a, b) => {
          const dateA = new Date(a.start_date).getTime();
          const dateB = new Date(b.start_date).getTime();

          return dateA - dateB;
        })
      );
    } catch (err) {
      console.error("Failed to load schedule:", err);
      setActivities([]);
      setError("Failed to load project schedule.");
    } finally {
      setLoadingSchedule(false);
    }
  }, []);

  useEffect(() => {
    if (projectId !== "") {
      loadSchedule(projectId);
    }
  }, [projectId, loadSchedule]);

  const handleExcelUpload = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];

    event.target.value = "";

    if (!file) {
      return;
    }

    if (projectId === "") {
      setError("Please select a project before uploading an Excel schedule.");
      return;
    }

    const lowerName = file.name.toLowerCase();

    if (!lowerName.endsWith(".xlsx") && !lowerName.endsWith(".xls")) {
      setError("Only Excel files (.xlsx, .xls) are allowed.");
      return;
    }

    try {
      setUploadingExcel(true);
      setUploadMessage("");
      setError("");

      const response = await uploadScheduleExcel(
        projectId,
        file
      );

      const imported =
        response?.data?.import ??
        response?.data ??
        {};

      const inserted =
        Number(imported.inserted ?? 0);

      const updated =
        Number(imported.updated ?? 0);

      const total =
        Number(
          imported.total ??
          imported.total_activities ??
          inserted + updated
        );

      setUploadMessage(
        `Excel uploaded successfully. ${total || inserted + updated} activities processed.`
      );

      await loadSchedule(projectId);

      // Analyze the freshly imported schedule: derive WBS, compute EVM
      // and generate the management intelligence report.
      await runAnalysis(projectId);

    } catch (err: any) {
      console.error(
        "Excel schedule upload failed:",
        err
      );

      const detail =
        err?.response?.data?.detail;

      setError(
        typeof detail === "string"
          ? detail
          : "Excel schedule upload failed."
      );

    } finally {
      setUploadingExcel(false);
    }
  };

  const statistics = useMemo(() => {
    const total = activities.length;

    const completed = activities.filter(
      (activity) =>
        activity.status.toLowerCase() === "completed"
    ).length;

    const inProgress = activities.filter(
      (activity) =>
        activity.status.toLowerCase() === "in progress"
    ).length;

    const notStarted = activities.filter(
      (activity) =>
        activity.status.toLowerCase() === "not started"
    ).length;

    const averageProgress =
      total > 0
        ? activities.reduce(
            (sum, activity) =>
              sum + Number(activity.progress_percent || 0),
            0
          ) / total
        : 0;

    return {
      total,
      completed,
      inProgress,
      notStarted,
      averageProgress,
    };
  }, [activities]);

  return (
    <Box sx={{ p: 3 }}>
      <Stack
        direction={{ xs: "column", md: "row" }}
        spacing={2}
        sx={{
          mb: 3,
          justifyContent: "space-between",
          alignItems: { xs: "flex-start", md: "center" },
        }}
      >
        <Box>
          <Typography
            variant="h4"
            sx={{ fontWeight: 700 }}
          >
            Schedule Intelligence
          </Typography>

          <Typography
            color="text.secondary"
            sx={{ mt: 0.5 }}
          >
            Project schedule, progress and activity control
          </Typography>
        </Box>

        <Stack
          direction="row"
          spacing={1}
          sx={{ alignItems: "center" }}
        >
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            disabled={
              projectId === "" ||
              loadingSchedule
            }
            onClick={() => {
              if (projectId !== "") {
                loadSchedule(projectId);
              }
            }}
          >
            Refresh
          </Button>
        </Stack>
      </Stack>

      {selectedProject && (
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{ mb: 2 }}
        >
          Selected Project:{" "}
          <strong>{selectedProject.name}</strong>{" "}
          (ID: {selectedProject.id})
        </Typography>
      )}

      {error && (
        <Alert
          severity="error"
          sx={{ mb: 3 }}
        >
          {error}
        </Alert>
      )}
      {uploadMessage && (
        <Alert
          severity="success"
          sx={{ mb: 3 }}
          onClose={() => setUploadMessage("")}
        >
          {uploadMessage}
        </Alert>
      )}

      {analyzing && (
        <Alert severity="info" sx={{ mb: 3 }}>
          Analyzing project schedule — deriving WBS, computing EVM and
          generating management intelligence...
        </Alert>
      )}

      {analysis && (
        <Card sx={{ mb: 3, borderRadius: 3 }}>
          <CardContent>
            <Stack
              direction={{ xs: "column", sm: "row" }}
              spacing={2}
              sx={{ justifyContent: "space-between", alignItems: { xs: "flex-start", sm: "center" }, mb: 2 }}
            >
              <Box>
                <Typography variant="h6" sx={{ fontWeight: 700 }}>
                  Management Intelligence — {analysis.project.code} / {analysis.project.name}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Generated automatically after schedule import
                </Typography>
              </Box>

              <Button
                size="small"
                variant="outlined"
                disabled={analyzing || projectId === ""}
                onClick={() => {
                  if (projectId !== "") {
                    runAnalysis(projectId);
                  }
                }}
              >
                {analyzing ? "Analyzing..." : "Re-run Analysis"}
              </Button>
            </Stack>

            <Stack direction="row" spacing={1} sx={{ flexWrap: "wrap", mb: 2 }}>
              <Chip
                label={`Schedule: ${analysis.schedule.health}`}
                color={
                  analysis.schedule.health.toUpperCase() === "RED"
                    ? "error"
                    : analysis.schedule.health.toUpperCase() === "YELLOW"
                      ? "warning"
                      : "success"
                }
                size="small"
              />
              <Chip
                label={`Activities: ${analysis.schedule.total_activities}`}
                size="small"
              />
              <Chip
                label={`Variance: ${analysis.schedule.variance != null ? Number(analysis.schedule.variance).toFixed(1) : "N/A"}%`}
                size="small"
              />
              <Chip
                label={`Critical: ${analysis.schedule.critical_activities}`}
                color="warning"
                size="small"
              />
              <Chip
                label={`WBS: ${analysis.wbs.total_items} items (${analysis.wbs.created} auto-created)`}
                size="small"
              />
            </Stack>

            {analysis.evm?.status && (
              <Alert severity="info" sx={{ mb: 2 }}>
                <strong>EVM:</strong> Planned {analysis.evm.planned_progress != null ? `${Number(analysis.evm.planned_progress).toFixed(1)}%` : "N/A"} · Actual{" "}
                {analysis.evm.actual_progress != null ? `${Number(analysis.evm.actual_progress).toFixed(1)}%` : "N/A"} · SPI{" "}
                {analysis.evm.spi != null ? Number(analysis.evm.spi).toFixed(3) : "N/A"} · CPI{" "}
                {analysis.evm.cpi != null ? Number(analysis.evm.cpi).toFixed(3) : "N/A"} · EAC{" "}
                {analysis.evm.eac != null ? Math.round(analysis.evm.eac).toLocaleString("en-US") : "N/A"}
              </Alert>
            )}

            {analysis.alerts.length > 0 && (
              <Box sx={{ mb: 2 }}>
                {analysis.alerts.map((alert, index) => (
                  <Alert
                    key={index}
                    severity={alert.level.toUpperCase() === "WARNING" ? "warning" : "error"}
                    sx={{ mb: 1 }}
                  >
                    <strong>{alert.title}:</strong> {alert.message}
                  </Alert>
                ))}
              </Box>
            )}

            {analysis.recovery.required && (
              <Alert severity="error">
                <strong>Recovery ({analysis.recovery.priority ?? "HIGH"}):</strong>{" "}
                {analysis.recovery.recommendation ?? "Recovery plan not generated."}
              </Alert>
            )}
          </CardContent>
        </Card>
      )}

      <Box
        sx={{
          mb: 3,
          p: 2,
          border: "1px dashed",
          borderColor: "divider",
          borderRadius: 2,
          display: "flex",
          alignItems: { xs: "stretch", sm: "center" },
          justifyContent: "space-between",
          gap: 2,
          flexDirection: { xs: "column", sm: "row" },
        }}
      >
        <Box>
          <Typography
            variant="subtitle1"
            sx={{ fontWeight: 700 }}
          >
            Import Project Schedule
          </Typography>

          <Typography
            variant="body2"
            color="text.secondary"
            sx={{ mt: 0.5 }}
          >
            Upload an Excel schedule (.xlsx or .xls) for the selected project.
          </Typography>
        </Box>

        <Button
          component="label"
          variant="contained"
          disabled={
            projectId === "" ||
            uploadingExcel
          }
        >
          {uploadingExcel
            ? "Uploading..."
            : "Upload Excel Schedule"}

          <input
            type="file"
            hidden
            accept=".xlsx,.xls"
            onChange={handleExcelUpload}
          />
        </Button>
      </Box>


      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: {
            xs: "1fr",
            sm: "repeat(2, 1fr)",
            lg: "repeat(5, 1fr)",
          },
          gap: 2,
          mb: 3,
        }}
      >
        <Card>
          <CardContent>
            <Typography
              color="text.secondary"
              variant="body2"
            >
              Total Activities
            </Typography>

            <Typography
              variant="h4"
              sx={{ fontWeight: 700, mt: 1 }}
            >
              {statistics.total}
            </Typography>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography
              color="text.secondary"
              variant="body2"
            >
              Completed
            </Typography>

            <Typography
              variant="h4"
              sx={{
                fontWeight: 700,
                mt: 1,
                color: "success.main",
              }}
            >
              {statistics.completed}
            </Typography>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography
              color="text.secondary"
              variant="body2"
            >
              In Progress
            </Typography>

            <Typography
              variant="h4"
              sx={{
                fontWeight: 700,
                mt: 1,
                color: "info.main",
              }}
            >
              {statistics.inProgress}
            </Typography>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography
              color="text.secondary"
              variant="body2"
            >
              Not Started
            </Typography>

            <Typography
              variant="h4"
              sx={{
                fontWeight: 700,
                mt: 1,
              }}
            >
              {statistics.notStarted}
            </Typography>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography
              color="text.secondary"
              variant="body2"
            >
              Average Progress
            </Typography>

            <Typography
              variant="h4"
              sx={{
                fontWeight: 700,
                mt: 1,
              }}
            >
              {statistics.averageProgress.toFixed(1)}%
            </Typography>

            <LinearProgress
              variant="determinate"
              value={Math.min(
                100,
                Math.max(
                  0,
                  statistics.averageProgress
                )
              )}
              sx={{ mt: 1.5 }}
            />
          </CardContent>
        </Card>
      </Box>

      <Card>
        <CardContent sx={{ p: 0 }}>
          <Box sx={{ p: 2 }}>
            <Typography
              variant="h6"
              sx={{ fontWeight: 700 }}
            >
              Schedule Activities
            </Typography>

            <Typography
              variant="body2"
              color="text.secondary"
              sx={{ mt: 0.5 }}
            >
              {statistics.total} activities loaded from
              the project schedule API.
            </Typography>
          </Box>

          {loadingSchedule ? (
            <Box
              sx={{
                minHeight: 220,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <Stack
                spacing={1}
                sx={{ alignItems: "center" }}
              >
                <CircularProgress />
                <Typography color="text.secondary">
                  Loading schedule...
                </Typography>
              </Stack>
            </Box>
          ) : activities.length === 0 ? (
            <Box sx={{ p: 3 }}>
              <Alert severity="info">
                No schedule activities found for
                this project.
              </Alert>
            </Box>
          ) : (
            <TableContainer>
              <Table
                stickyHeader
                size="small"
              >
                <TableHead>
                  <TableRow>
                    <TableCell>
                      <strong>Code</strong>
                    </TableCell>

                    <TableCell>
                      <strong>Activity</strong>
                    </TableCell>

                    <TableCell>
                      <strong>Duration</strong>
                    </TableCell>

                    <TableCell>
                      <strong>Progress</strong>
                    </TableCell>

                    <TableCell>
                      <strong>Status</strong>
                    </TableCell>

                    <TableCell>
                      <strong>Start</strong>
                    </TableCell>

                    <TableCell>
                      <strong>Finish</strong>
                    </TableCell>

                    <TableCell>
                      <strong>Responsible Party</strong>
                    </TableCell>
                  </TableRow>
                </TableHead>

                <TableBody>
                  {activities.map((activity) => (
                    <TableRow
                      key={activity.id}
                      hover
                    >
                      <TableCell>
                        <Typography
                          variant="body2"
                          sx={{ fontWeight: 700 }}
                        >
                          {activity.activity_code}
                        </Typography>
                      </TableCell>

                      <TableCell>
                        {activity.activity_name}
                      </TableCell>

                      <TableCell>
                        {activity.duration_days} days
                      </TableCell>

                      <TableCell
                        sx={{ minWidth: 150 }}
                      >
                        <Stack spacing={0.5}>
                          <Stack
                            direction="row"
                            sx={{ justifyContent: "space-between" }}
                          >
                            <Typography
                              variant="body2"
                            >
                              {Number(
                                activity.progress_percent || 0
                              ).toFixed(0)}
                              %
                            </Typography>
                          </Stack>

                          <LinearProgress
                            variant="determinate"
                            value={Math.min(
                              100,
                              Math.max(
                                0,
                                Number(
                                  activity.progress_percent || 0
                                )
                              )
                            )}
                          />
                        </Stack>
                      </TableCell>

                      <TableCell>
                        <Chip
                          label={activity.status}
                          color={statusColor(
                            activity.status
                          )}
                          size="small"
                        />
                      </TableCell>

                      <TableCell>
                        {formatDate(
                          activity.start_date
                        )}
                      </TableCell>

                      <TableCell>
                        {formatDate(
                          activity.finish_date
                        )}
                      </TableCell>

                      <TableCell>
                        {activity.responsible_party || "-"}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>
    </Box>
  );
}



