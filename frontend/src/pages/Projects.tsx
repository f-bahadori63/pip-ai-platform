import { useEffect, useState } from "react";
import { Typography, Box } from "@mui/material";

import api from "../services/api";
import ProjectTable from "../components/projects/ProjectTable";

interface Project {
id: number;
project_code: string;
name: string;
client: string;
contract_value: number;
currency: string;
status: string;
}

export default function Projects() {
const [projects, setProjects] = useState<Project[]>([]);

useEffect(() => {
api
.get("/projects/")
.then((res) => setProjects(res.data))
.catch(console.error);
}, []);

return ( <Box> <Typography
     variant="h4"
     sx={{ fontWeight: "bold" }}
     gutterBottom
   >
Projects </Typography>


  <Typography
    variant="body1"
    color="text.secondary"
    sx={{ mb: 3 }}
  >
    Enterprise Project Portfolio Management
  </Typography>

  <ProjectTable projects={projects} />
</Box>


);
}


