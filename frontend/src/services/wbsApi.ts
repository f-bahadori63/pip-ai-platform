import api from "./api";

export interface WBSItem {
  id: number;
  project_id: number;
  parent_id: number | null;
  code: string;
  name: string;
  level: number;
}

export const getProjectWBS = async (projectId: number) => {
  const response = await api.get<WBSItem[]>(`/wbs/project/${projectId}`);
  return response.data;
};

export const createWBSItem = async (item: Omit<WBSItem, "id">) => {
  const response = await api.post("/wbs/", item);
  return response.data;
};