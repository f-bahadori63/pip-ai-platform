import { useCallback, useEffect, useState } from "react";
import api from "../services/api";

type Project = {
  id: number;
  name?: string;
  code?: string;
  description?: string;
};

type WBSItem = {
  id: number;
  project_id: number;
  parent_id?: number | null;
  code?: string;
  name?: string;
  description?: string;
};

export default function WBS() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [projectId, setProjectId] = useState<number | "">("");
  const [items, setItems] = useState<WBSItem[]>([]);
  const [loadingProjects, setLoadingProjects] = useState(true);
  const [loadingWbs, setLoadingWbs] = useState(false);
  const [error, setError] = useState("");

  /*
   * Load available projects.
   *
   * Project selection is the only source of project scope.
   * No project ID is hardcoded.
   */
  useEffect(() => {
    let cancelled = false;

    const loadProjects = async () => {
      try {
        setLoadingProjects(true);
        setError("");

        const response = await api.get("/projects/");
        const data = Array.isArray(response.data)
          ? response.data
          : [];

        if (cancelled) {
          return;
        }

        setProjects(data);

        if (data.length > 0) {
          setProjectId((current) => {
            if (
              current !== "" &&
              data.some((project: Project) => project.id === current)
            ) {
              return current;
            }

            return data[0].id;
          });
        } else {
          setProjectId("");
          setItems([]);
        }
      } catch (err) {
        if (!cancelled) {
          console.error("Failed to load projects:", err);
          setError("Failed to load projects.");
          setProjects([]);
          setProjectId("");
          setItems([]);
        }
      } finally {
        if (!cancelled) {
          setLoadingProjects(false);
        }
      }
    };

    loadProjects();

    return () => {
      cancelled = true;
    };
  }, []);

  /*
   * Load WBS strictly for the selected project.
   *
   * Backend endpoint:
   * GET /wbs/project/{project_id}
   */
  const loadWbs = useCallback(async (selectedProjectId: number) => {
    try {
      setLoadingWbs(true);
      setError("");

      const response = await api.get(
        `/wbs/project/${selectedProjectId}`
      );

      const data = Array.isArray(response.data)
        ? response.data
        : [];

      /*
       * Defensive frontend filtering:
       * even if backend accidentally returns records from
       * another project, they must never be rendered here.
       */
      const scopedItems = data.filter(
        (item: WBSItem) =>
          Number(item.project_id) === Number(selectedProjectId)
      );

      setItems(scopedItems);
    } catch (err) {
      console.error("Failed to load WBS:", err);
      setItems([]);
      setError("Failed to load WBS for the selected project.");
    } finally {
      setLoadingWbs(false);
    }
  }, []);

  /*
   * Project selection controls WBS loading.
   */
  useEffect(() => {
    if (projectId === "") {
      setItems([]);
      return;
    }

    loadWbs(projectId);
  }, [projectId, loadWbs]);

  const selectedProject = projects.find(
    (project) => project.id === projectId
  );

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold">
          WBS Management
        </h1>

        <p className="mt-1 text-sm text-gray-500">
          Project-scoped Work Breakdown Structure
        </p>
      </div>

      <div className="mb-6 rounded-lg border p-4">
        <label
          htmlFor="wbs-project-selector"
          className="mb-2 block text-sm font-medium"
        >
          Project
        </label>

        <select
          id="wbs-project-selector"
          value={projectId === "" ? "" : String(projectId)}
          onChange={(event) => {
            const value = event.target.value;

            setProjectId(
              value === "" ? "" : Number(value)
            );
          }}
          disabled={loadingProjects}
          className="w-full rounded-md border px-3 py-2"
        >
          {loadingProjects && (
            <option value="">
              Loading projects...
            </option>
          )}

          {!loadingProjects && projects.length === 0 && (
            <option value="">
              No projects found
            </option>
          )}

          {projects.map((project) => (
            <option
              key={project.id}
              value={project.id}
            >
              {project.code
                ? `${project.code} - ${project.name ?? "Project"}`
                : project.name ?? `Project ${project.id}`}
            </option>
          ))}
        </select>
      </div>

      {selectedProject && (
        <div className="mb-4 text-sm text-gray-600">
          Selected Project:{" "}
          <strong>
            {selectedProject.code
              ? `${selectedProject.code} - `
              : ""}
            {selectedProject.name ?? selectedProject.id}
          </strong>
        </div>
      )}

      {error && (
        <div className="mb-4 rounded-lg border border-red-300 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      {loadingWbs && (
        <div className="rounded-lg border p-6 text-sm text-gray-500">
          Loading WBS...
        </div>
      )}

      {!loadingWbs && projectId !== "" && items.length === 0 && (
        <div className="rounded-lg border p-6 text-sm text-gray-500">
          No WBS items found for this project.
        </div>
      )}

      {!loadingWbs && items.length > 0 && (
        <div className="overflow-hidden rounded-lg border">
          <table className="w-full text-left">
            <thead className="border-b bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-sm font-medium">
                  ID
                </th>
                <th className="px-4 py-3 text-sm font-medium">
                  WBS Code
                </th>
                <th className="px-4 py-3 text-sm font-medium">
                  Name
                </th>
                <th className="px-4 py-3 text-sm font-medium">
                  Parent ID
                </th>
              </tr>
            </thead>

            <tbody>
              {items.map((item) => (
                <tr
                  key={item.id}
                  className="border-b last:border-b-0"
                >
                  <td className="px-4 py-3 text-sm">
                    {item.id}
                  </td>

                  <td className="px-4 py-3 text-sm font-medium">
                    {item.code ?? "-"}
                  </td>

                  <td className="px-4 py-3 text-sm">
                    {item.name ?? "-"}
                  </td>

                  <td className="px-4 py-3 text-sm">
                    {item.parent_id ?? "-"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
