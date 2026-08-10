import { Card, CardContent, Typography, Box } from "@mui/material";
import type { ReactNode } from "react";

interface KPICardProps {
  title: string;
  value: string | number;
  icon: ReactNode;
  color?: string;
}

export default function KPICard({
  title,
  value,
  icon,
  color = "primary.main",
}: KPICardProps) {
  return (
    <Card
      sx={{
        height: "100%",
        background:
          "linear-gradient(135deg, #1e293b 0%, #0f172a 100%)",
        border: "1px solid rgba(255,255,255,0.08)",
      }}
    >
      <CardContent>
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <Box>
            <Typography
              variant="subtitle2"
              sx={{ color: "rgba(255,255,255,0.7)" }}
            >
              {title}
            </Typography>

            <Typography
              variant="h4"
              sx={{
                mt: 1,
                fontWeight: "bold",
                color: "white",
              }}
            >
              {value}
            </Typography>
          </Box>

          <Box
            sx={{
              width: 56,
              height: 56,
              borderRadius: 3,
              bgcolor: color,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "white",
              flexShrink: 0,
            }}
          >
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}
