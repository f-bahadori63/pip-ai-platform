import { useEffect, useState } from "react";
import {
  Box,
  Grid,
  Paper,
  Typography,
  Chip,
} from "@mui/material";

import api from "../services/api";


export default function Dashboard() {

  const [dashboard, setDashboard] = useState<any>(null);
  const [error, setError] = useState("");


  useEffect(() => {

    console.log("Loading dashboard");

    api.get("/dashboard/project/1")
      .then((res) => {
        console.log("Dashboard Data:", res.data);
        setDashboard(res.data);
      })
      .catch((err) => {
        console.error(err);
        setError(err.message);
      });

  }, []);


  if (error) {
    return (
      <Typography color="error">
        API ERROR: {error}
      </Typography>
    );
  }


  if (!dashboard) {
    return (
      <Typography color="white">
        Loading dashboard...
      </Typography>
    );
  }


  const cards = [
    {
      title: "Project Status",
      value: dashboard.project_status,
    },
    {
      title: "Progress Variance",
      value: `${dashboard.progress.variance}%`,
    },
    {
      title: "Schedule Health",
      value: dashboard.schedule.health,
    },
    {
      title: "Cost Health",
      value: dashboard.cost.cost_health,
    },
  ];


  return (

    <Box>

      <Typography
        variant="h4"
        sx={{
          mb: 4,
          color: "white",
          fontWeight: "bold",
        }}
      >
        Project Intelligence Dashboard
      </Typography>


      <Grid container spacing={3}>

        {cards.map((card) => (

          <Grid
            key={card.title}
            size={{ xs: 12, md: 3 }}
          >

            <Paper
              sx={{
                p: 3,
                bgcolor: "#17233a",
                color: "white",
              }}
            >

              <Typography variant="subtitle2">
                {card.title}
              </Typography>

              <Typography
                variant="h5"
                sx={{
                  mt: 2,
                  fontWeight: "bold",
                }}
              >
                {card.value}
              </Typography>

            </Paper>

          </Grid>

        ))}


        <Grid size={{ xs: 12, md: 6 }}>

          <Paper
            sx={{
              p: 3,
              bgcolor: "#17233a",
              color: "white",
            }}
          >

            <Typography variant="h6">
              AI Alerts
            </Typography>


            {dashboard.alerts.map(
              (alert:any, index:number)=>(

              <Box key={index} sx={{ mt:2 }}>

                <Chip
                  label={alert.level}
                  color="warning"
                  sx={{ mr:1 }}
                />

                <Typography component="span">
                  {alert.title}
                </Typography>

              </Box>

            ))}

          </Paper>

        </Grid>


        <Grid size={{ xs:12, md:6 }}>

          <Paper
            sx={{
              p:3,
              bgcolor:"#17233a",
              color:"white",
            }}
          >

            <Typography variant="h6">
              AI Recovery Recommendation
            </Typography>


            <Typography sx={{mt:2}}>
              {dashboard.recovery.recommendation}
            </Typography>

          </Paper>

        </Grid>


      </Grid>

    </Box>

  );
}
