import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import api from "../services/api";

export interface Project {
  id: number;
  project_code?: string;
  name?: string;
  client?: string | null;
  status?: string | null;
}

interface ProjectContextValue {
  projects: Project[];
  loading: boolean;
  error: string;
  selectedProjectId: number | "";
  selectedProject: Project | null;
  selectProject: (id: number | "") => void;
  reloadProjects: () => Promise<void>;
}

const STORAGE_KEY = "pip.selectedProjectId";

const ProjectContext = createContext<ProjectContextValue | undefined>(
  undefined
);

export function ProjectProvider({
  children,
}: {
  children: ReactNode;
}) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedProjectId, setSelectedProjectId] = useState<number | "">(
    ""
  );

  const loadProjects = useCallback(async () => {
    try {
      setLoading(true);
      setError("");

      const response = await api.get("/projects/");
      const data: Project[] = Array.isArray(response.data)
        ? response.data
        : [];

      setProjects(data);

      /*
       * Single source of truth for the whole application:
       * 1. keep the current selection when it is still valid
       * 2. restore the persisted selection (localStorage)
       * 3. fall back to the first project
       */
      setSelectedProjectId((current) => {
        if (
          current !== "" &&
          data.some((project: Project) => Number(project.id) === Number(current))
        ) {
          return current;
        }

        const stored = Number(localStorage.getItem(STORAGE_KEY));

        if (
          stored &&
          data.some((project: Project) => Number(project.id) === stored)
        ) {
          return stored;
        }

        return data.length > 0 ? Number(data[0].id) : "";
      });
    } catch (err) {
      console.error("Failed to load projects:", err);
      setError("Failed to load projects.");
      setProjects([]);
      setSelectedProjectId("");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadProjects();
  }, [loadProjects]);

  const selectProject = useCallback((id: number | "") => {
    setSelectedProjectId(id);

    if (id === "") {
      localStorage.removeItem(STORAGE_KEY);
    } else {
      localStorage.setItem(STORAGE_KEY, String(id));
    }
  }, []);

  const selectedProject = useMemo(
    () =>
      projects.find(
        (project) => Number(project.id) === Number(selectedProjectId)
      ) ?? null,
    [projects, selectedProjectId]
  );

  const value = useMemo<ProjectContextValue>(
    () => ({
      projects,
      loading,
      error,
      selectedProjectId,
      selectedProject,
      selectProject,
      reloadProjects: loadProjects,
    }),
    [projects, loading, error, selectedProjectId, selectedProject, selectProject, loadProjects]
  );

  return (
    <ProjectContext.Provider value={value}>
      {children}
    </ProjectContext.Provider>
  );
}

export function useProject(): ProjectContextValue {
  const context = useContext(ProjectContext);

  if (!context) {
    throw new Error("useProject must be used within a <ProjectProvider>");
  }

  return context;
}
