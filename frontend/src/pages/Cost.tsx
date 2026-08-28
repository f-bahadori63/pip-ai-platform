import { useCallback, useEffect, useState } from "react";
import {
  Alert,
  Box,
  Button,
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

import api from "../services/api";
import { useProject } from "../context/ProjectContext";

interface CostData {
  planned_cost: number;
  actual_cost: number;
  earned_value: number;
  remaining_cost: number;
  cost_variance: number;
  cost_health: string;
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
        height: "100%",
        p: 2.5,
        borderRadius: 3,
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
          alignItems: "flex-start",
        }}
      >
        <Box>
          <Typography
            variant="body2"
            sx={{ color: "rgba(255,255,255,0.65)" }}
          >
            {title}
          </Typography>

          <Typography
            variant="h4"
            sx={{ mt: 1, fontWeight: 800, color: "white" }}
          >
            {value}
          </Typography>

          {subtitle && (
            <Typography
              variant="caption"
              sx={{ display: "block", mt: 0.75, color: "rgba(255,255,255,0.5)" }}
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
    <Box sx={{ p: 3, pb: 5 }}>
      <Stack
        direction={{ xs: "column", md: "row" }}
        spacing={2}
        sx={{ mb: 3, justifyContent: "space-between", alignItems: { xs: "flex-start", md: "center" } }}
      >
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700 }}>
            Cost Intelligence
          </Typography>

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
              <Grid size={{ xs: 12, sm: 6, lg: 3 }}>
                <CostCard
                  title="Planned Cost (PV)"
                  value={formatNumber(cost.planned_cost)}
                  subtitle="Budgeted value of planned work"
                  icon={<AccountBalanceWalletIcon />}
                  color="primary"
                />
              </Grid>

              <Grid size={{ xs: 12, sm: 6, lg: 3 }}>
                <CostCard
                  title="Actual Cost (AC)"
                  value={formatNumber(cost.actual_cost)}
                  subtitle="Money spent so far"
                  icon={<PaidIcon />}
                  color="warning"
                />
              </Grid>

              <Grid size={{ xs: 12, sm: 6, lg: 3 }}>
                <CostCard
                  title="Earned Value (EV)"
                  value={formatNumber(cost.earned_value)}
                  subtitle="Value of work performed"
                  icon={<TrendingUpIcon />}
                  color="success"
                />
              </Grid>

              <Grid size={{ xs: 12, sm: 6, lg: 3 }}>
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

              <Grid size={{ xs: 12, sm: 6, lg: 3 }}>
                <CostCard
                  title="Remaining Cost"
                  value={formatNumber(cost.remaining_cost)}
                  subtitle="Planned minus actual"
                  icon={<SavingsIcon />}
                  color="primary"
                />
              </Grid>

              <Grid size={{ xs: 12, sm: 6, lg: 3 }}>
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
        </>
      )}
    </Box>
  );
}
