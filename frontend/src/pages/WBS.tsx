import { useCallback, useEffect, useState } from "react";
import api from "../services/api";
import { useProject } from "../context/ProjectContext";

type WBSItem = {
  id: number;
  project_id: number;
  parent_id?: number | null;
  code?: string;
  name?: string;
  description?: string;
};

export default function WBS() {
  /*
   * The selected project comes from the global project context
   * (single source of truth, shared with Dashboard / Schedule /
   * Documents / Cost through the top-bar selector).
   */
  const {
    selectedProjectId: projectId,
    selectedProject,
  } = useProject();

  const [items, setItems] = useState<WBSItem[]>([]);
  const [loadingWbs, setLoadingWbs] = useState(false);
  const [error, setError] = useState("");

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

      {selectedProject && (
        <div className="mb-4 text-sm text-gray-600">
          Selected Project:{" "}
          <strong>
            {selectedProject.project_code
              ? `${selectedProject.project_code} - `
              : ""}
            {selectedProject.name ?? selectedProject.id}
          </strong>
        </div>
      )}

      {!selectedProject && (
        <div className="mb-4 text-sm text-gray-500">
          No projects available. Select a project from the top bar.
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
