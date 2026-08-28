import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000",
  timeout: 120000,
});

export async function uploadDocument(file: File) {
  const formData = new FormData();

  formData.append("file", file);

  return api.post("/documents/upload", formData);
}


export async function uploadScheduleExcel(file: File) {
  const formData = new FormData();

  formData.append("file", file);

  return api.post("/import/schedule", formData);
}
export default api;
export interface AIChatResponse {
  model: string;
  response: string;
  done: boolean;
  project_id: number | null;
}

export async function aiChat(
  prompt: string,
  projectId?: number | null
): Promise<AIChatResponse> {
  const params = new URLSearchParams();

  params.set("prompt", prompt);

  if (projectId !== undefined && projectId !== null) {
    params.set("project_id", String(projectId));
  }

  const response = await api.post<AIChatResponse>(
    `/ai/chat?${params.toString()}`
  );

  return response.data;
}

