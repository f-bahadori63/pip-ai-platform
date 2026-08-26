import { useEffect, useState } from "react";
import {
  Alert,
  Box,
  Chip,
  CircularProgress,
  Divider,
  Grid,
  LinearProgress,
  Paper,
  Stack,
  Typography,
} from "@mui/material";

import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import ScheduleIcon from "@mui/icons-material/Schedule";
import AccountBalanceWalletIcon from "@mui/icons-material/AccountBalanceWallet";
import TrendingDownIcon from "@mui/icons-material/TrendingDown";
import CrisisAlertIcon from "@mui/icons-material/CrisisAlert";
import AutoAwesomeIcon from "@mui/icons-material/AutoAwesome";

import api from "../services/api";
import AIChat from "../components/ai/AIChat";
import CriticalActivities from "../components/dashboard/CriticalActivities";

type DashboardData = {
  project_id: number;
  project_status: string;
  progress: {
    planned_progress: number;
    actual_progress: number;
    variance: number;
  };
  schedule: {
    health: string;
    delay_index: number;
    critical_activities: number;
  };
  cost: {
    planned_cost: number;
    actual_cost: number;
    earned_value: number;
    remaining_cost: number;
    cost_variance: number;
    cost_health: string;
  };
  alerts: Array<{
    level: string;
    title: string;
    message: string;
    action: string;
  }>;
  recovery: {
    required: boolean;
    priority: string;
    recommendation: string;
  };
};

function statusColor(status: string) {
  const value = status.toUpperCase();

  if (value === "RED" || value === "CRITICAL") {
    return "error";
  }

  if (value === "YELLOW" || value === "WARNING" || value === "HIGH") {
    return "warning";
  }

  return "success";
}

function formatNumber(value: number) {
  return new Intl.NumberFormat("en-US", {
    maximumFractionDigits: 0,
  }).format(value);
}

function KPI({
  title,
  value,
  subtitle,
  icon,
  color,
}: {
  title: string;
  value: string;
  subtitle?: string;
  icon: React.ReactNode;
  color: "primary" | "success" | "warning" | "error";
}) {
  return (
    <Paper
      sx={{
        height: "100%",
        p: 2.5,
        background:
          "linear-gradient(145deg, rgba(30,41,59,0.98), rgba(15,23,42,0.98))",
        border: "1px solid rgba(255,255,255,0.08)",
      }}
    >
      <Stack
        direction="row"
        spacing={2}
        sx={{
          justifyContent: "space-between",
          alignItems: "flex-start"
        }}>
        <Box>
          <Typography
            variant="body2"
            sx={{ color: "rgba(255,255,255,0.65)" }}
          >
            {title}
          </Typography>

          <Typography
            variant="h4"
            sx={{
              mt: 1,
              fontWeight: 800,
              color: "white",
            }}
          >
            {value}
          </Typography>

          {subtitle && (
            <Typography
              variant="caption"
              sx={{
                display: "block",
                mt: 0.75,
                color: "rgba(255,255,255,0.5)",
              }}
            >
              {subtitle}
            </Typography>
          )}
        </Box>

        <Box
          sx={{
            width: 48,
            height: 48,
            borderRadius: 2,
            bgcolor: `${color}.main`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "white",
          }}
        >
          {icon}
        </Box>
      </Stack>
    </Paper>
  );
}

export default function Dashboard() {
  const [projects, setProjects] = useState<any[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<number | "">("");

  useEffect(() => {
    let cancelled = false;

    const loadProjects = async () => {
      try {
        const response = await api.get("/projects/");
        const data = Array.isArray(response.data) ? response.data : [];

        if (!cancelled) {
          setProjects(data);

          if (data.length > 0) {
            setSelectedProjectId(Number(data[0].id));
          }
        }
      } catch (error) {
        console.error("Failed to load projects:", error);

        if (!cancelled) {
          setProjects([]);
          setSelectedProjectId("");
        }
      }
    };

    loadProjects();

    return () => {
      cancelled = true;
    };
  }, []);

  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (selectedProjectId === "") {
      return;
    }

    let active = true;

    api
      .get<DashboardData>(`/dashboard/project/${selectedProjectId}`)
      .then((response) => {
        if (active) {
          console.log("Investor Dashboard Data:", response.data);
          setDashboard(response.data);
        }
      })
      .catch((err) => {
        console.error("Dashboard API Error:", err);

        if (active) {
          setError(
            err?.response?.data?.detail ||
              err?.message ||
              "Unable to load project dashboard."
          );
        }
      });

    return () => {
      active = false;
    };
  }, [selectedProjectId]);

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        API ERROR: {error}
      </Alert>
    );
  }

  if (!dashboard) {
    return (
      <Box
        sx={{
          minHeight: "60vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <Stack spacing={2} sx={{
          alignItems: "center"
        }}>
          <CircularProgress />
          <Typography sx={{
            color: "text.secondary"
          }}>
            Loading Project Intelligence...
          </Typography>
        </Stack>
      </Box>
    );
  }

  const progress = Math.max(
    0,
    Math.min(100, dashboard.progress.actual_progress)
  );

  return (
    <Box sx={{ pb: 5 }}>
      {/* PROJECT SELECTOR */}
      <Box sx={{ mb: 3, display: "flex", alignItems: "center", gap: "12px" }}>
        <label htmlFor="dashboard-project-selector" style={{ color: "rgba(255,255,255,0.7)", fontSize: "14px" }}>
          Project
        </label>
        <select
          id="dashboard-project-selector"
          value={selectedProjectId === "" ? "" : String(selectedProjectId)}
          onChange={(event) => {
            const value = event.target.value;
            setSelectedProjectId(value === "" ? "" : Number(value));
          }}
          style={{
            background: "#1e293b",
            color: "white",
            border: "1px solid rgba(255,255,255,0.15)",
            borderRadius: "8px",
            padding: "6px 10px",
            fontSize: "14px",
          }}
        >
          <option value="">Select project</option>
          {projects.map((project) => (
            <option key={project.id} value={String(project.id)}>
              {project.project_code ?? project.code ?? project.name ?? project.id}
            </option>
          ))}
        </select>
      </Box>

      {/* HEADER */}
      <Stack
        direction={{ xs: "column", md: "row" }}
        spacing={2}
        sx={{
          justifyContent: "space-between",
          alignItems: { xs: "flex-start", md: "center" },
          mb: 4
        }}>
        <Box>
          <Typography
            variant="h4"
            sx={{
              color: "white",
              fontWeight: 800,
              letterSpacing: "-0.5px",
            }}
          >
            Project Intelligence Center
          </Typography>

          <Typography
            sx={{
              mt: 0.75,
              color: "rgba(255,255,255,0.55)",
            }}
          >
            Operational project control and management intelligence
          </Typography>
        </Box>

        <Stack direction="row" spacing={1} sx={{
          alignItems: "center"
        }}>
          <Typography
            variant="body2"
            sx={{ color: "rgba(255,255,255,0.55)" }}
          >
            Project {dashboard.project_id}
          </Typography>

          <Chip
            label={dashboard.project_status}
            color={statusColor(dashboard.project_status)}
            icon={<CrisisAlertIcon />}
          />
        </Stack>
      </Stack>

      {/* EXECUTIVE KPI ROW */}
      <Grid container spacing={2.5}>
        <Grid size={{ xs: 12, sm: 6, lg: 3 }}>
          <KPI
            title="Project Status"
            value={dashboard.project_status}
            subtitle="Overall health"
            icon={<CrisisAlertIcon />}
            color={statusColor(dashboard.project_status)}
          />
        </Grid>

        <Grid size={{ xs: 12, sm: 6, lg: 3 }}>
          <KPI
            title="Actual Progress"
            value={`${dashboard.progress.actual_progress}%`}
            subtitle={`Planned ${dashboard.progress.planned_progress}%`}
            icon={<TrendingDownIcon />}
            color={
              dashboard.progress.variance < 0 ? "warning" : "success"
            }
          />
        </Grid>

        <Grid size={{ xs: 12, sm: 6, lg: 3 }}>
          <KPI
            title="Schedule Health"
            value={dashboard.schedule.health}
            subtitle={`Variance ${dashboard.progress.variance}%`}
            icon={<ScheduleIcon />}
            color={statusColor(dashboard.schedule.health)}
          />
        </Grid>

        <Grid size={{ xs: 12, sm: 6, lg: 3 }}>
          <KPI
            title="Cost Health"
            value={dashboard.cost.cost_health}
            subtitle={`CV ${formatNumber(dashboard.cost.cost_variance)}`}
            icon={<AccountBalanceWalletIcon />}
            color={statusColor(dashboard.cost.cost_health)}
          />
        </Grid>
      </Grid>

      {/* PROGRESS + EVM */}
      <Grid container spacing={2.5} sx={{ mt: 0.25 }}>
        <Grid size={{ xs: 12, lg: 6 }}>
          <Paper
            sx={{
              p: 3,
              height: "100%",
              background: "rgba(23,35,58,0.96)",
              border: "1px solid rgba(255,255,255,0.07)",
            }}
          >
            <Stack
              direction="row"
              sx={{
                justifyContent: "space-between",
                alignItems: "center"
              }}>
              <Typography variant="h6" sx={{
                fontWeight: 700
              }}>
                Schedule Intelligence
              </Typography>

              <Chip
                label={`${dashboard.progress.variance}% variance`}
                color={dashboard.progress.variance < 0 ? "warning" : "success"}
                size="small"
              />
            </Stack>

            <Box sx={{ mt: 3 }}>
              <Stack
                direction="row"
                sx={{
                  justifyContent: "space-between",
                  mb: 1
                }}>
                <Typography variant="body2" sx={{
                  color: "text.secondary"
                }}>
                  Actual Progress
                </Typography>

                <Typography sx={{
                  fontWeight: 700
                }}>
                  {dashboard.progress.actual_progress}%
                </Typography>
              </Stack>

              <LinearProgress
                variant="determinate"
                value={progress}
                sx={{
                  height: 10,
                  borderRadius: 5,
                  bgcolor: "rgba(255,255,255,0.08)",
                }}
              />
            </Box>

            <Grid container spacing={2} sx={{ mt: 2 }}>
              <Grid size={{ xs: 6 }}>
                <Typography variant="caption" sx={{
                  color: "text.secondary"
                }}>
                  Planned
                </Typography>
                <Typography variant="h6">
                  {dashboard.progress.planned_progress}%
                </Typography>
              </Grid>

              <Grid size={{ xs: 6 }}>
                <Typography variant="caption" sx={{
                  color: "text.secondary"
                }}>
                  Critical Activities
                </Typography>
                <Typography variant="h6">
                  {dashboard.schedule.critical_activities}
                </Typography>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        <Grid size={{ xs: 12, lg: 6 }}>
          <Paper
            sx={{
              p: 3,
              height: "100%",
              background: "rgba(23,35,58,0.96)",
              border: "1px solid rgba(255,255,255,0.07)",
            }}
          >
            <Typography variant="h6" sx={{
              fontWeight: 700
            }}>
              EVM / Cost Intelligence
            </Typography>

            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid size={{ xs: 6, sm: 3 }}>
                <Typography variant="caption" sx={{
                  color: "text.secondary"
                }}>
                  Planned Cost
                </Typography>
                <Typography sx={{
                  fontWeight: 700
                }}>
                  {formatNumber(dashboard.cost.planned_cost)}
                </Typography>
              </Grid>

              <Grid size={{ xs: 6, sm: 3 }}>
                <Typography variant="caption" sx={{
                  color: "text.secondary"
                }}>
                  Actual Cost
                </Typography>
                <Typography sx={{
                  fontWeight: 700
                }}>
                  {formatNumber(dashboard.cost.actual_cost)}
                </Typography>
              </Grid>

              <Grid size={{ xs: 6, sm: 3 }}>
                <Typography variant="caption" sx={{
                  color: "text.secondary"
                }}>
                  Earned Value
                </Typography>
                <Typography sx={{
                  fontWeight: 700
                }}>
                  {formatNumber(dashboard.cost.earned_value)}
                </Typography>
              </Grid>

              <Grid size={{ xs: 6, sm: 3 }}>
                <Typography variant="caption" sx={{
                  color: "text.secondary"
                }}>
                  Remaining
                </Typography>
                <Typography sx={{
                  fontWeight: 700
                }}>
                  {formatNumber(dashboard.cost.remaining_cost)}
                </Typography>
              </Grid>
            </Grid>

            <Divider sx={{ my: 2 }} />

            <Stack direction="row" sx={{
              justifyContent: "space-between"
            }}>
              <Typography sx={{
                color: "text.secondary"
              }}>
                Cost Variance
              </Typography>

              <Typography
                color={
                  dashboard.cost.cost_variance < 0
                    ? "error.main"
                    : "success.main"
                }
                sx={{
                  fontWeight: 800
                }}
              >
                {formatNumber(dashboard.cost.cost_variance)}
              </Typography>
            </Stack>
          </Paper>
        </Grid>
      </Grid>

      {/* CRITICAL ACTIVITIES + RECOVERY */}
      <Grid container spacing={2.5} sx={{ mt: 0.25 }}>
        <Grid size={{ xs: 12, lg: 7 }}>
          <Paper
            sx={{
              p: 3,
              background: "rgba(23,35,58,0.96)",
              border: "1px solid rgba(255,255,255,0.07)",
            }}
          >
            <Stack
              direction="row"
              sx={{
                justifyContent: "space-between",
                alignItems: "center",
                mb: 2
              }}>
              <Stack direction="row" spacing={1} sx={{
                alignItems: "center"
              }}>
                <WarningAmberIcon color="warning" />
                <Typography variant="h6" sx={{
                  fontWeight: 700
                }}>
                  Critical Activities
                </Typography>
              </Stack>

              <Chip
                label={`${dashboard.schedule.critical_activities} critical`}
                color="warning"
                size="small"
              />
            </Stack>

            <CriticalActivities />
          </Paper>
        </Grid>

        <Grid size={{ xs: 12, lg: 5 }}>
          <Paper
            sx={{
              p: 3,
              height: "100%",
              background:
                "linear-gradient(145deg, rgba(59,42,20,0.75), rgba(23,35,58,0.98))",
              border: "1px solid rgba(255,152,0,0.2)",
            }}
          >
            <Stack direction="row" spacing={1} sx={{
              alignItems: "center"
            }}>
              <AutoAwesomeIcon color="warning" />

              <Typography variant="h6" sx={{
                fontWeight: 700
              }}>
                AI Recovery
              </Typography>
            </Stack>

            <Stack direction="row" spacing={1} sx={{ mt: 2 }}>
              <Chip
                label={
                  dashboard.recovery.required
                    ? "RECOVERY REQUIRED"
                    : "NO RECOVERY REQUIRED"
                }
                color={dashboard.recovery.required ? "error" : "success"}
                size="small"
              />

              <Chip
                label={`Priority: ${dashboard.recovery.priority}`}
                color="warning"
                size="small"
              />
            </Stack>

            <Typography
              sx={{
                mt: 2,
                color: "rgba(255,255,255,0.78)",
                whiteSpace: "pre-line",
                lineHeight: 1.8,
              }}
            >
              {dashboard.recovery.recommendation}
            </Typography>
          </Paper>
        </Grid>
      </Grid>

      {/* MANAGEMENT ALERTS */}
      <Paper
        sx={{
          mt: 2.5,
          p: 3,
          background: "rgba(23,35,58,0.96)",
          border: "1px solid rgba(255,255,255,0.07)",
        }}
      >
        <Stack
          direction="row"
          spacing={1}
          sx={{
            alignItems: "center",
            mb: 2
          }}>
          <WarningAmberIcon color="warning" />

          <Typography variant="h6" sx={{
            fontWeight: 700
          }}>
            Management Alerts
          </Typography>
        </Stack>

        <Stack spacing={1.5}>
          {dashboard.alerts.map((alert, index) => (
            <Alert
              key={`${alert.title}-${index}`}
              severity={
                alert.level === "CRITICAL"
                  ? "error"
                  : alert.level === "ACTION_REQUIRED"
                    ? "warning"
                    : "info"
              }
              variant="outlined"
            >
              <Typography sx={{
                fontWeight: 700
              }}>
                {alert.title}
              </Typography>

              <Typography variant="body2">
                {alert.message}
              </Typography>

              <Typography
                variant="caption"
                sx={{ display: "block", mt: 0.5 }}
              >
                Action: {alert.action}
              </Typography>
            </Alert>
          ))}
        </Stack>
      </Paper>

      {/* AI CHAT */}
      <Box sx={{ mt: 2.5 }}>
        <AIChat projectId={Number(selectedProjectId)} />
      </Box>
    </Box>
  );
}

