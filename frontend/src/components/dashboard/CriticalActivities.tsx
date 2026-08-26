import { useEffect, useState } from "react";
import {
  Chip,
  CircularProgress,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";

import api from "../../services/api";

type Activity = {
  activity_id?: number;
  activity_code?: string;
  activity_name: string;
  planned_progress: number;
  actual_progress: number;
  schedule_variance: number;
  delay_index: number;
  risk_level: string;
};

export default function CriticalActivities() {
  const [activities, setActivities] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get("/dashboard/critical-activities/1")
      .then((response) => {
        console.log("CRITICAL ACTIVITIES:", response.data);
        setActivities(response.data.activities || []);
      })
      .catch((error) => {
        console.error("Critical Activities Error:", error);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <CircularProgress size={24} />;
  }

  if (activities.length === 0) {
    return (
      <Typography sx={{
        color: "text.secondary"
      }}>No critical activities detected.
              </Typography>
    );
  }

  return (
    <TableContainer
      component={Paper}
      elevation={0}
      sx={{
        background: "rgba(15,23,42,0.55)",
        border: "1px solid rgba(255,255,255,0.06)",
      }}
    >
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>Activity</TableCell>
            <TableCell align="right">Planned</TableCell>
            <TableCell align="right">Actual</TableCell>
            <TableCell align="right">Variance</TableCell>
            <TableCell align="right">Risk</TableCell>
          </TableRow>
        </TableHead>

        <TableBody>
          {activities.map((item, index) => (
            <TableRow key={item.activity_id ?? `${item.activity_name}-${index}`}>
              <TableCell>
                <Typography sx={{
                  fontWeight: 600
                }}>
                  {item.activity_name}
                </Typography>

                {item.activity_code && (
                  <Typography variant="caption" sx={{
                    color: "text.secondary"
                  }}>
                    {item.activity_code}
                  </Typography>
                )}
              </TableCell>

              <TableCell align="right">
                {item.planned_progress}%
              </TableCell>

              <TableCell align="right">
                {item.actual_progress}%
              </TableCell>

              <TableCell
                align="right"
                sx={{
                  color:
                    item.schedule_variance < 0
                      ? "error.main"
                      : "success.main",
                  fontWeight: 700,
                }}
              >
                {item.schedule_variance}%
              </TableCell>

              <TableCell align="right">
                <Chip
                  label={item.risk_level}
                  size="small"
                  color={
                    item.risk_level === "HIGH" ||
                    item.risk_level === "CRITICAL"
                      ? "error"
                      : "warning"
                  }
                />
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
