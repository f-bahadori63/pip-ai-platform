import { useEffect, useState } from "react";
import {
Typography,
Paper,
Grid,
Box,
Chip,
Divider,
} from "@mui/material";

import FolderIcon from "@mui/icons-material/Folder";
import PlayCircleIcon from "@mui/icons-material/PlayCircle";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import AttachMoneyIcon from "@mui/icons-material/AttachMoney";

import api from "../services/api";
import KPICard from "../components/dashboard/KPICard";

interface Project {
id: number;
project_code: string;
name: string;
client: string;
contract_value: number;
currency: string;
status: string;
}

export default function Dashboard() {
const [projects, setProjects] = useState<Project[]>([]);

useEffect(() => {
  console.log("Dashboard mounted");

  api
    .get("/projects/")
    .then((res) => {
      console.log("SUCCESS:", res.data);
      setProjects(res.data);
    })
    .catch((err) => {
      console.error("ERROR:", err);
    });
}, []);

const activeProjects = projects.filter(
(p) => p.status === "Active" || p.status === "Planning"
).length;

const delayedProjects = projects.filter(
(p) => p.status === "Delayed"
).length;

const totalContractValue = projects.reduce(
(sum, p) => sum + p.contract_value,
0
);

return ( <Box> <Typography
     variant="h4"
     fontWeight="bold"
     gutterBottom
   >
Dashboard </Typography>

```
  <Typography
    variant="body1"
    color="text.secondary"
    sx={{ mb: 4 }}
  >
    EPC Project Management Platform
  </Typography>

  <Grid container spacing={3} sx={{ mb: 4 }}>
    <Grid item xs={12} sm={6} md={3}>
      <KPICard
        title="Projects"
        value={projects.length}
        icon={<FolderIcon />}
      />
    </Grid>

    <Grid item xs={12} sm={6} md={3}>
      <KPICard
        title="Active"
        value={activeProjects}
        icon={<PlayCircleIcon />}
        color="success.main"
      />
    </Grid>

    <Grid item xs={12} sm={6} md={3}>
      <KPICard
        title="Delayed"
        value={delayedProjects}
        icon={<WarningAmberIcon />}
        color="warning.main"
      />
    </Grid>

    <Grid item xs={12} sm={6} md={3}>
      <KPICard
        title="Contract Value"
        value={`${(totalContractValue / 1_000_000_000).toFixed(0)} B`}
        icon={<AttachMoneyIcon />}
        color="secondary.main"
      />
    </Grid>
  </Grid>

  <Paper
    sx={{
      p: 3,
      borderRadius: 3,
    }}
  >
    <Box
      sx={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        mb: 3,
      }}
    >
      <Typography variant="h6" fontWeight="bold">
        Projects
      </Typography>

      <Chip
        label={`${projects.length} Total`}
        color="primary"
        size="small"
      />
    </Box>

    {projects.length === 0 ? (
      <Typography color="text.secondary">
        No projects found.
      </Typography>
    ) : (
      projects.map((project) => (
        <Box key={project.id}>
          <Box
            sx={{
              py: 2,
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              flexWrap: "wrap",
              gap: 2,
            }}
          >
            <Box>
              <Typography
                variant="subtitle1"
                fontWeight="bold"
              >
                {project.project_code}
              </Typography>

              <Typography variant="body1">
                {project.name}
              </Typography>

              <Typography
                variant="body2"
                color="text.secondary"
              >
                Client: {project.client}
              </Typography>
            </Box>

            <Box
              sx={{
                textAlign: "right",
              }}
            >
              <Chip
                label={project.status}
                color={
                  project.status === "Delayed"
                    ? "error"
                    : "success"
                }
                size="small"
                sx={{ mb: 1 }}
              />

              <Typography
                variant="body2"
                fontWeight="medium"
              >
                {(project.contract_value / 1_000_000_000).toFixed(0)} B {project.currency}
              </Typography>
            </Box>
          </Box>

          <Divider />
        </Box>
      ))
    )}
  </Paper>
</Box>
);
}