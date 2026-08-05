import { useEffect, useState } from "react";
import { Box, Paper, Typography, CircularProgress } from "@mui/material";

import { getProjectWBS, type WBSItem } from "../services/wbsApi";

export default function WBS() {
  const [items, setItems] = useState<WBSItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getProjectWBS(1)
      .then(setItems)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <Box>
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        WBS Management
      </Typography>

      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Work Breakdown Structure - Primavera Style
      </Typography>

      <Paper sx={{ p: 3, borderRadius: 3 }}>
        {loading ? (
          <CircularProgress />
        ) : items.length === 0 ? (
          <Typography color="text.secondary">
            No WBS items found for this project.
          </Typography>
        ) : (
          items.map((item) => (
            <Box
              key={item.id}
              sx={{
                pl: (item.level - 1) * 4,
                py: 1.5,
                borderBottom: "1px solid rgba(255,255,255,0.06)",
              }}
            >
              <Typography
                variant="body1"
                sx={{ fontWeight: item.level === 1 ? 700 : 400 }}
              >
                {item.code} - {item.name}
              </Typography>
            </Box>
          ))
        )}
      </Paper>
    </Box>
  );
}