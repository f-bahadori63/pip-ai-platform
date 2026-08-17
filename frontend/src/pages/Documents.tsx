import { useEffect, useState } from "react";
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  MenuItem,
  Select,
  Typography,
} from "@mui/material";
import api from "../services/api";

interface Project {
  id: number;
  project_code: string;
  name: string;
  client?: string;
  status?: string;
}

interface UploadResult {
  [key: string]: unknown;
}

export default function Documents() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [projectId, setProjectId] = useState<number | "">("");
  const [loadingProjects, setLoadingProjects] = useState(true);
  const [file, setFile] = useState<File | null>(null);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<UploadResult | null>(null);

  useEffect(() => {
    let active = true;

    const loadProjects = async () => {
      try {
        setLoadingProjects(true);
        setError("");

        const response = await api.get("/projects/");

        const data = Array.isArray(response.data)
          ? response.data
          : Array.isArray(response.data?.projects)
            ? response.data.projects
            : [];

        if (active) {
          setProjects(data);
        }
      } catch (err) {
        console.error("Failed to load projects:", err);

        if (active) {
          setProjects([]);
          setError("Failed to load projects.");
        }
      } finally {
        if (active) {
          setLoadingProjects(false);
        }
      }
    };

    loadProjects();

    return () => {
      active = false;
    };
  }, []);

  const handleProcess = async () => {
    if (projectId === "") {
      setError("Please select a project.");
      return;
    }

    if (!file) {
      setError("Please select an Excel or PDF file.");
      return;
    }

    try {
      setProcessing(true);
      setError("");
      setResult(null);

      const formData = new FormData();
      formData.append("file", file);

      const response = await api.post(
        `/documents/upload?project_id=${projectId}`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
          timeout: 120000,
        }
      );

      setResult(response.data);
    } catch (err: any) {
      console.error("Document processing failed:", err);

      setError(
        String(
          err?.response?.data?.detail ||
          err?.response?.data?.message ||
          "Document processing failed."
        )
      );
    } finally {
      setProcessing(false);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
        Documents Intelligence
      </Typography>

      <Typography color="text.secondary" sx={{ mb: 3 }}>
        Upload project documents and generate Management Intelligence.
      </Typography>

      <Box
        sx={{
          maxWidth: 900,
          p: 3,
          borderRadius: 3,
          boxShadow: 2,
          backgroundColor: "background.paper",
        }}
      >
        <Typography sx={{ fontWeight: 600, mb: 1 }}>
          Project
        </Typography>

        {loadingProjects ? (
          <Box sx={{ display: "flex", alignItems: "center", mb: 3 }}>
            <CircularProgress size={20} sx={{ mr: 1 }} />
            <Typography>Loading projects...</Typography>
          </Box>
        ) : (
          <Box sx={{ mb: 3 }}>
            <Select
              fullWidth
              value={projectId === "" ? "" : String(projectId)}
              displayEmpty
              disabled={processing}
              onChange={(event) => {
                const value = event.target.value;
                setProjectId(value === "" ? "" : Number(value));
                setFile(null);
                setResult(null);
                setError("");
              }}
            >
              <MenuItem value="">
                <em>Select a project</em>
              </MenuItem>

              {projects.map((project) => (
                <MenuItem
                  key={project.id}
                  value={String(project.id)}
                >
                  {project.project_code} — {project.name}
                </MenuItem>
              ))}
            </Select>

            {projectId !== "" && (
              <Typography
                variant="body2"
                sx={{ mt: 1 }}
              >
                Selected Project ID: {projectId}
              </Typography>
            )}

            {projects.length === 0 && (
              <Alert severity="warning" sx={{ mt: 2 }}>
                No projects found.
              </Alert>
            )}
          </Box>
        )}

        <Button
          variant="outlined"
          component="label"
          disabled={projectId === "" || processing}
        >
          {file ? "Change File" : "Select Excel / PDF"}

          <input
            hidden
            type="file"
            accept=".xlsx,.xls,.pdf"
            onChange={(event) => {
              setFile(event.target.files?.[0] ?? null);
              setResult(null);
              setError("");
            }}
          />
        </Button>

        {file && (
          <Typography sx={{ mt: 1, mb: 2 }}>
            Selected file: <strong>{file.name}</strong>
          </Typography>
        )}

        {error && (
          <Alert severity="error" sx={{ mt: 2, mb: 2 }}>
            {error}
          </Alert>
        )}

        <Box sx={{ mt: 3 }}>
          <Button
            variant="contained"
            size="large"
            disabled={
              projectId === "" ||
              file === null ||
              processing ||
              loadingProjects
            }
            onClick={handleProcess}
          >
            {processing ? "Processing..." : "Process Document"}
          </Button>
        </Box>

        {result && (
          <Box sx={{ mt: 4 }}>
            <Typography
              variant="h6"
              sx={{ fontWeight: 700, mb: 2 }}
            >
              Management Intelligence
            </Typography>

            <Alert severity="success" sx={{ mb: 2 }}>
              Document processed successfully.
            </Alert>

            <Box
              sx={{
                p: 2,
                borderRadius: 2,
                backgroundColor: "grey.100",
                whiteSpace: "pre-wrap",
                overflowX: "auto",
              }}
            >
              {String(
                result.management_intelligence ||
                result.ai_response ||
                result.message ||
                JSON.stringify(result, null, 2)
              )}
            </Box>
          </Box>
        )}
      </Box>
    </Box>
  );
}

