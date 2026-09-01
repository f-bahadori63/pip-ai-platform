import { useCallback, useEffect, useState } from "react";
import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Grid,
  Paper,
  Stack,
  TextField,
  Typography,
} from "@mui/material";

import AccountBalanceWalletIcon from "@mui/icons-material/AccountBalanceWallet";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import TrendingDownIcon from "@mui/icons-material/TrendingDown";
import SavingsIcon from "@mui/icons-material/Savings";
import PaidIcon from "@mui/icons-material/Paid";
import AutoAwesomeIcon from "@mui/icons-material/AutoAwesome";

function EVMField({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <Box
      sx={{
        p: 1.5,
        minWidth: 0,
        height: "100%",
        boxSizing: "border-box",
        overflow: "hidden",
        borderRadius: 2,
        bgcolor: "rgba(255,255,255,0.06)",
        border: "1px solid rgba(255,255,255,0.08)",
      }}
    >
      <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.6)" }}>
        {label}
      </Typography>

      <Typography
        variant="h6"
        sx={{
          mt: 0.25,
          minWidth: 0,
          fontWeight: 700,
          fontSize: "clamp(1rem, 1.5vw, 1.25rem)",
          lineHeight: 1.2,
          color: "white",
          overflowWrap: "anywhere",
          fontVariantNumeric: "tabular-nums",
        }}
      >
        {value}
      </Typography>
    </Box>
  );
}

import api from "../services/api";
import { useProject } from "../context/ProjectContext";

interface EvmData {
  status?: string;
  message?: string;
  planned_progress?: number | null;
  actual_progress?: number | null;
  budget_source?: string;
  bac?: number | null;
  pv?: number | null;
  ev?: number | null;
  ac?: number | null;
  sv?: number | null;
  spi?: number | null;
  cv?: number | null;
  cpi?: number | null;
  eac?: number | null;
  etc?: number | null;
  vac?: number | null;
  tcpi?: number | null;
}

interface AnalysisReport {
  project_id: number;
  generated_at: string;
  project: {
    code: string;
    name: string;
    client?: string | null;
    currency?: string | null;
  };
  wbs: {
    created: number;
    linked_activities: number;
    total_items: number;
    items: Array<{
      id: number;
      code: string;
      name: string;
      activity_count: number;
    }>;
  };
  evm: EvmData;
  schedule: {
    health: string;
    total_activities: number;
    planned_progress?: number | null;
    actual_progress?: number | null;
    variance?: number | null;
    delay_index?: number | null;
    critical_activities: number;
  };
  alerts: Array<{ level: string; title: string; message: string }>;
  recovery: { required: boolean; priority?: string | null; recommendation?: string | null };
}

interface CostData {
  planned_cost: number;
  actual_cost: number;
  earned_value: number;
  remaining_cost: number;
  cost_variance: number;
  cost_health: string;
  cost_source?: "schedule_import" | "manual" | null;
  evm?: EvmData;
  message?: string;
}

function healthColor(health: string) {
  const value = String(health || "").toUpperCase();

  if (value === "RED" || value === "CRITICAL") {
    return "error";
  }

  if (value === "YELLOW" || value === "WARNING") {
    return "warning";
  }

  return "success";
}

function formatNumber(value: number) {
  return new Intl.NumberFormat("en-US", {
    maximumFractionDigits: 0,
  }).format(value ?? 0);
}

function CostCard({
  title,
  value,
  color,
  icon,
  subtitle,
}: {
  title: string;
  value: string;
  color: "primary" | "success" | "warning" | "error";
  icon: React.ReactNode;
  subtitle?: string;
}) {
  return (
    <Paper
      sx={{
        position: "relative",
        height: "100%",
        minHeight: 155,
        minWidth: 0,
        p: 2.5,
        boxSizing: "border-box",
        overflow: "hidden",
        borderRadius: 3,
        background:
          "linear-gradient(145deg, rgba(30,41,59,0.98), rgba(15,23,42,0.98))",
        border: "1px solid rgba(255,255,255,0.08)",
      }}
    >
      <Box sx={{ minWidth: 0, width: "100%" }}>
        <Typography
          variant="body2"
          sx={{
            minHeight: "2.5em",
            pr: 6.5,
            lineHeight: 1.25,
            color: "rgba(255,255,255,0.65)",
          }}
        >
          {title}
        </Typography>

        <Typography
          variant="h4"
          sx={{
            mt: 1,
            maxWidth: "100%",
            fontWeight: 800,
            fontSize: "clamp(1.55rem, 2.2vw, 2.15rem)",
            lineHeight: 1.12,
            color: "white",
            overflowWrap: "anywhere",
            fontVariantNumeric: "tabular-nums",
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
              lineHeight: 1.3,
              color: "rgba(255,255,255,0.5)",
            }}
          >
            {subtitle}
          </Typography>
        )}
      </Box>

      <Box
        sx={{
          position: "absolute",
          top: 16,
          right: 16,
          width: 42,
          height: 42,
          flexShrink: 0,
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
    </Paper>
  );
}

export default function Cost() {
  const {
    selectedProjectId,
    selectedProject,
    loading: loadingProjects,
  } = useProject();

  const [cost, setCost] = useState<CostData | null>(null);
  const [loadingCost, setLoadingCost] = useState(false);
  const [error, setError] = useState("");

  const [plannedCost, setPlannedCost] = useState("");
  const [actualCost, setActualCost] = useState("");
  const [earnedValue, setEarnedValue] = useState("");
  const [saving, setSaving] = useState(false);

  const [analysis, setAnalysis] = useState<AnalysisReport | null>(null);
  const [analyzing, setAnalyzing] = useState(false);

  const loadCost = useCallback(async (projectId: number) => {
    try {
      setLoadingCost(true);
      setError("");

      const response = await api.get<CostData>(
        `/cost/project/${projectId}`
      );

      setCost(response.data);
    } catch (err: any) {
      console.error("Failed to load cost data:", err);
      setCost(null);
      setError(
        String(
          err?.response?.data?.detail ||
            err?.message ||
            "Failed to load cost data."
        )
      );
    } finally {
      setLoadingCost(false);
    }
  }, []);

  const runAnalysis = useCallback(async (projectId: number) => {
    try {
      setAnalyzing(true);
      setError("");

      const response = await api.post<AnalysisReport>(
        `/analysis/project/${projectId}/run`
      );

      setAnalysis(response.data);
      await loadCost(projectId); // refresh EVM after analysis
    } catch (err: any) {
      console.error("Management analysis failed:", err);
      setError(
        String(
          err?.response?.data?.detail ||
            err?.message ||
            "Management analysis failed."
        )
      );
    } finally {
      setAnalyzing(false);
    }
  }, [loadCost]);

  useEffect(() => {
    if (selectedProjectId === "") {
      setCost(null);
      return;
    }

    loadCost(selectedProjectId);
  }, [selectedProjectId, loadCost]);

  const handleSave = async () => {
    if (selectedProjectId === "") {
      setError("Please select a project.");
      return;
    }

    try {
      setSaving(true);
      setError("");

      const params = new URLSearchParams();

      params.set("planned_cost", plannedCost || "0");
      params.set("actual_cost", actualCost || "0");
      params.set("earned_value", earnedValue || "0");

      await api.post(
        `/cost/project/${selectedProjectId}?${params.toString()}`
      );

      setPlannedCost("");
      setActualCost("");
      setEarnedValue("");

      await loadCost(selectedProjectId);
    } catch (err: any) {
      console.error("Failed to save cost data:", err);
      setError(
        String(
          err?.response?.data?.detail ||
            err?.message ||
            "Failed to save cost data."
        )
      );
    } finally {
      setSaving(false);
    }
  };

  const noData = Boolean(cost?.message);

  return (
    <Box
      sx={{
        width: "100%",
        maxWidth: "none",
        minWidth: 0,
        p: { xs: 1, md: 2 },
        pb: 5,
        boxSizing: "border-box",
      }}
    >
      <Stack
        direction={{ xs: "column", md: "row" }}
        spacing={2}
        sx={{ mb: 3, justifyContent: "space-between", alignItems: { xs: "flex-start", md: "center" } }}
      >
        <Box>
          <Stack direction="row" spacing={1.5} alignItems="center">
            <Typography variant="h4" sx={{ fontWeight: 700 }}>
              Cost Intelligence
            </Typography>
 
            {cost?.cost_source === "schedule_import" && (
              <Chip
                size="small"
                color="success"
                label="Auto-detected from schedule upload"
              />
            )}
            {cost?.cost_source === "manual" && (
              <Chip
                size="small"
                color="default"
                label="Manual entry"
              />
            )}
          </Stack>
 
          <Typography color="text.secondary" sx={{ mt: 0.5 }}>
            Earned Value Management for the selected project
          </Typography>
        </Box>

        {selectedProject && (
          <Paper
            sx={{
              px: 2,
              py: 1,
              borderRadius: 2,
              bgcolor: "#1e293b",
              color: "white",
            }}
          >
            <Typography variant="body2">
              {selectedProject.project_code
                ? `${selectedProject.project_code} — `
                : ""}
              {selectedProject.name ?? `Project ${selectedProject.id}`}
              {" "}(ID: {selectedProject.id})
            </Typography>
          </Paper>
        )}
      </Stack>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {loadingProjects && (
        <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2 }}>
          <CircularProgress size={20} />
          <Typography>Loading projects...</Typography>
        </Box>
      )}

      {!loadingProjects && selectedProjectId === "" && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          Please select a project to view cost intelligence.
        </Alert>
      )}

      {selectedProjectId !== "" && (
        <>
          {loadingCost ? (
            <Box
              sx={{
                minHeight: "40vh",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <Stack spacing={2} sx={{ alignItems: "center" }}>
                <CircularProgress />
                <Typography color="text.secondary">
                  Loading cost data...
                </Typography>
              </Stack>
            </Box>
          ) : noData ? (
            <Alert severity="info" sx={{ mb: 3 }}>
              {cost?.message ?? "No cost data available for this project."}
            </Alert>
          ) : cost ? (
            <Grid container spacing={2.5}>
              <Grid size={{ xs: 12, sm: 6, lg: 4, xl: 3 }}>
                <CostCard
                  title="Planned Cost (PV)"
                  value={formatNumber(cost.planned_cost)}
                  subtitle="Budgeted value of planned work"
                  icon={<AccountBalanceWalletIcon />}
                  color="primary"
                />
              </Grid>

              <Grid size={{ xs: 12, sm: 6, lg: 4, xl: 3 }}>
                <CostCard
                  title="Actual Cost (AC)"
                  value={formatNumber(cost.actual_cost)}
                  subtitle="Money spent so far"
                  icon={<PaidIcon />}
                  color="warning"
                />
              </Grid>

              <Grid size={{ xs: 12, sm: 6, lg: 4, xl: 3 }}>
                <CostCard
                  title="Earned Value (EV)"
                  value={formatNumber(cost.earned_value)}
                  subtitle="Value of work performed"
                  icon={<TrendingUpIcon />}
                  color="success"
                />
              </Grid>

              <Grid size={{ xs: 12, sm: 6, lg: 4, xl: 3 }}>
                <CostCard
                  title="Cost Variance (CV)"
                  value={formatNumber(cost.cost_variance)}
                  subtitle={
                    cost.cost_variance < 0
                      ? "Over budget"
                      : "Under budget"
                  }
                  icon={
                    cost.cost_variance < 0 ? (
                      <TrendingDownIcon />
                    ) : (
                      <SavingsIcon />
                    )
                  }
                  color={cost.cost_variance < 0 ? "error" : "success"}
                />
              </Grid>

              <Grid size={{ xs: 12, sm: 6, lg: 4, xl: 3 }}>
                <CostCard
                  title="Remaining Cost"
                  value={formatNumber(cost.remaining_cost)}
                  subtitle="Planned minus actual"
                  icon={<SavingsIcon />}
                  color="primary"
                />
              </Grid>

              <Grid size={{ xs: 12, sm: 6, lg: 4, xl: 3 }}>
                <CostCard
                  title="Cost Health"
                  value={cost.cost_health}
                  subtitle="EVM health indicator"
                  icon={<AccountBalanceWalletIcon />}
                  color={healthColor(cost.cost_health)}
                />
              </Grid>
            </Grid>
          ) : null}

          <Paper
            sx={{
              mt: 4,
              p: 3,
              borderRadius: 3,
              boxShadow: 2,
            }}
          >
            <Typography variant="h6" sx={{ fontWeight: 700, mb: 1 }}>
              Record Cost Snapshot
            </Typography>

            <Typography color="text.secondary" sx={{ mb: 2 }}>
              Add a cost record for the selected project. The KPI cards are
              recalculated automatically.
            </Typography>

            <Grid container spacing={2}>
              <Grid size={{ xs: 12, sm: 4 }}>
                <TextField
                  fullWidth
                  label="Planned Cost"
                  type="number"
                  value={plannedCost}
                  onChange={(event) => setPlannedCost(event.target.value)}
                />
              </Grid>

              <Grid size={{ xs: 12, sm: 4 }}>
                <TextField
                  fullWidth
                  label="Actual Cost"
                  type="number"
                  value={actualCost}
                  onChange={(event) => setActualCost(event.target.value)}
                />
              </Grid>

              <Grid size={{ xs: 12, sm: 4 }}>
                <TextField
                  fullWidth
                  label="Earned Value"
                  type="number"
                  value={earnedValue}
                  onChange={(event) => setEarnedValue(event.target.value)}
                />
              </Grid>
            </Grid>

            <Box sx={{ mt: 2, display: "flex", justifyContent: "flex-end" }}>
              <Button
                variant="contained"
                disabled={saving || !selectedProjectId}
                onClick={handleSave}
              >
                {saving ? "Saving..." : "Save Cost Snapshot"}
              </Button>
            </Box>
          </Paper>

          {cost?.evm && (
            <Paper
              sx={{
                mt: 4,
                p: 3,
                borderRadius: 3,
                boxShadow: 2,
                background:
                  "linear-gradient(145deg, rgba(30,41,59,0.98), rgba(15,23,42,0.98))",
                border: "1px solid rgba(255,255,255,0.08)",
              }}
            >
              <Stack
                direction={{ xs: "column", sm: "row" }}
                spacing={2}
                sx={{ justifyContent: "space-between", alignItems: "center", mb: 2 }}
              >
                <Box>
                  <Typography variant="h6" sx={{ fontWeight: 700, color: "white" }}>
                    EVM — Earned Value Management
                  </Typography>
                  <Typography variant="body2" sx={{ color: "rgba(255,255,255,0.6)" }}>
                    Computed automatically from schedule progress {cost.evm.budget_source === "contract_value" ? "and project contract value" : "and cost data"}
                  </Typography>
                </Box>

                <Chip
                  label={cost.evm.status ?? "N/A"}
                  color={healthColor(cost.evm.status ?? "UNKNOWN")}
                />
              </Stack>

              {cost.evm.message && (
                <Alert severity="info" sx={{ mb: 2 }}>
                  {cost.evm.message}
                </Alert>
              )}

              <Grid container spacing={2}>
                <Grid size={{ xs: 12, sm: 6, lg: 3 }}>
                  <EVMField label="Planned Progress" value={cost.evm.planned_progress != null ? `${Number(cost.evm.planned_progress).toFixed(1)}%` : "N/A"} />
                </Grid>
                <Grid size={{ xs: 12, sm: 6, lg: 3 }}>
                  <EVMField label="Actual Progress" value={cost.evm.actual_progress != null ? `${Number(cost.evm.actual_progress).toFixed(1)}%` : "N/A"} />
                </Grid>
                <Grid size={{ xs: 12, sm: 6, lg: 3 }}>
                  <EVMField label="PV (Planned Value)" value={formatNumber(cost.evm.pv ?? 0)} />
                </Grid>
                <Grid size={{ xs: 12, sm: 6, lg: 3 }}>
                  <EVMField label="EV (Earned Value)" value={formatNumber(cost.evm.ev ?? 0)} />
                </Grid>
                <Grid size={{ xs: 12, sm: 6, lg: 3 }}>
                  <EVMField label="AC (Actual Cost)" value={formatNumber(cost.evm.ac ?? 0)} />
                </Grid>
                <Grid size={{ xs: 12, sm: 6, lg: 3 }}>
                  <EVMField label="SV (Schedule Variance)" value={formatNumber(cost.evm.sv ?? 0)} />
                </Grid>
                <Grid size={{ xs: 12, sm: 6, lg: 3 }}>
                  <EVMField label="SPI" value={cost.evm.spi != null ? Number(cost.evm.spi).toFixed(3) : "N/A"} />
                </Grid>
                <Grid size={{ xs: 12, sm: 6, lg: 3 }}>
                  <EVMField label="CV (Cost Variance)" value={formatNumber(cost.evm.cv ?? 0)} />
                </Grid>
                <Grid size={{ xs: 12, sm: 6, lg: 3 }}>
                  <EVMField label="CPI" value={cost.evm.cpi != null ? Number(cost.evm.cpi).toFixed(3) : "N/A"} />
                </Grid>
                <Grid size={{ xs: 12, sm: 6, lg: 3 }}>
                  <EVMField label="EAC" value={formatNumber(cost.evm.eac ?? 0)} />
                </Grid>
                <Grid size={{ xs: 12, sm: 6, lg: 3 }}>
                  <EVMField label="ETC" value={formatNumber(cost.evm.etc ?? 0)} />
                </Grid>
                <Grid size={{ xs: 12, sm: 6, lg: 3 }}>
                  <EVMField label="VAC" value={formatNumber(cost.evm.vac ?? 0)} />
                </Grid>
                <Grid size={{ xs: 12, sm: 6, lg: 3 }}>
                  <EVMField label="TCPI" value={cost.evm.tcpi != null ? Number(cost.evm.tcpi).toFixed(3) : "N/A"} />
                </Grid>
                <Grid size={{ xs: 12, sm: 6, lg: 3 }}>
                  <EVMField label="BAC" value={formatNumber(cost.evm.bac ?? 0)} />
                </Grid>
              </Grid>
            </Paper>
          )}

          <Box sx={{ mt: 4, display: "flex", justifyContent: "flex-end" }}>
            <Button
              variant="outlined"
              startIcon={<AutoAwesomeIcon />}
              disabled={analyzing || !selectedProjectId}
              onClick={() => runAnalysis(selectedProjectId)}
            >
              {analyzing ? "Analyzing..." : "Run Management Analysis"}
            </Button>
          </Box>

          {analysis && (
            <Paper sx={{ mt: 3, p: 3, borderRadius: 3, boxShadow: 2 }}>
              <Typography variant="h6" sx={{ fontWeight: 700, mb: 1 }}>
                Management Intelligence — {analysis.project.code} / {analysis.project.name}
              </Typography>

              <Stack direction="row" spacing={1} sx={{ flexWrap: "wrap", mb: 2 }}>
                <Chip
                  label={`Schedule: ${analysis.schedule.health}`}
                  color={healthColor(analysis.schedule.health)}
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
                  label={`WBS items: ${analysis.wbs.total_items} (${analysis.wbs.created} auto-created)`}
                  size="small"
                />
              </Stack>

              {analysis.evm?.status && (
                <Alert severity={healthColor(analysis.evm.status) === "success" ? "success" : "warning"} sx={{ mb: 2 }}>
                  EVM: SPI {analysis.evm.spi != null ? Number(analysis.evm.spi).toFixed(3) : "N/A"} ·
                  CPI {analysis.evm.cpi != null ? Number(analysis.evm.cpi).toFixed(3) : "N/A"} ·
                  EAC {formatNumber(analysis.evm.eac ?? 0)}
                </Alert>
              )}

              {analysis.alerts.length > 0 && (
                <Box sx={{ mb: 2 }}>
                  {analysis.alerts.map((alert, index) => (
                    <Alert key={index} severity={healthColor(alert.level) === "error" ? "error" : "warning"} sx={{ mb: 1 }}>
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
            </Paper>
          )}
        </>
      )}
    </Box>
  );
}
