import { Box, MenuItem, Select, Typography } from "@mui/material";

import { useProject } from "../../context/ProjectContext";

/*
 * Global project selector.
 *
 * This is the single source of truth for the project that the whole
 * application operates on. Every page (Dashboard, WBS, Schedule,
 * Documents, Cost, ...) reads its project from this selection, so the
 * displayed data is always consistent.
 */
export default function ProjectSelector() {
  const {
    projects,
    loading,
    selectedProjectId,
    selectProject,
  } = useProject();

  return (
    <Box
      sx={{
        display: "flex",
        alignItems: "center",
        gap: 1,
        bgcolor: "rgba(255,255,255,0.06)",
        borderRadius: 2,
        px: 1.5,
        py: 0.5,
      }}
    >
      <Typography
        variant="body2"
        sx={{ color: "rgba(255,255,255,0.75)", whiteSpace: "nowrap" }}
      >
        Project
      </Typography>

      <Select
        size="small"
        value={selectedProjectId === "" ? "" : String(selectedProjectId)}
        displayEmpty
        disabled={loading}
        onChange={(event) => {
          const value = event.target.value;
          selectProject(value === "" ? "" : Number(value));
        }}
        sx={{
          minWidth: 190,
          color: "white",
          "& .MuiOutlinedInput-notchedOutline": {
            borderColor: "rgba(255,255,255,0.25)",
          },
          "& .MuiSvgIcon-root": {
            color: "rgba(255,255,255,0.8)",
          },
        }}
      >
        <MenuItem value="">
          <em>Select project</em>
        </MenuItem>

        {projects.map((project) => (
          <MenuItem
            key={project.id}
            value={String(project.id)}
          >
            {project.project_code
              ? `${project.project_code} — ${project.name ?? "Project"}`
              : project.name ?? `Project ${project.id}`}
          </MenuItem>
        ))}
      </Select>
    </Box>
  );
}
