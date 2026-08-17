import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
  timeout: 120000,
});

export async function uploadDocument(
  projectId: number,
  file: File
) {
  const formData = new FormData();

  formData.append("file", file);

  return api.post(
    `/documents/upload?project_id=${projectId}`,
    formData
  );
}

export default api;

