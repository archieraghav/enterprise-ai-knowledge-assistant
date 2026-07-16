import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1";

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export function setAuthToken(token: string | null) {
  if (token) {
    api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common["Authorization"];
  }
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface RegisterResponse {
  id: string;
  email: string;
  full_name: string;
  is_superuser: boolean;
}

export async function login(email: string, password: string): Promise<LoginResponse> {
  const response = await api.post<LoginResponse>("/auth/login", { email, password });
  return response.data;
}

export async function register(
  email: string,
  password: string,
  fullName: string,
  organizationName: string
): Promise<RegisterResponse> {
  const response = await api.post<RegisterResponse>("/auth/register", {
    email,
    password,
    full_name: fullName,
    organization_name: organizationName,
  });
  return response.data;
}

export interface CurrentUser {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
}

export async function getCurrentUser(): Promise<CurrentUser> {
  const response = await api.get<CurrentUser>("/users/me");
  return response.data;
}
export interface DocumentItem {
  id: string;
  title: string;
  file_type: string;
  status: string;
  created_at: string;
}

export interface DocumentListResponse {
  items: DocumentItem[];
  total: number;
  page: number;
  page_size: number;
}

export async function listDocuments(page = 1, pageSize = 20): Promise<DocumentListResponse> {
  const response = await api.get<DocumentListResponse>("/documents", {
    params: { page, page_size: pageSize },
  });
  return response.data;
}

export async function uploadDocument(file: File): Promise<DocumentItem> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await api.post<DocumentItem>("/documents/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
}

export async function deleteDocument(documentId: string): Promise<void> {
  await api.delete(`/documents/${documentId}`);
}

export interface StreamEvent {
  type: "token" | "done";
  content?: string;
  citations?: Array<{ document_id: string; document_title: string; excerpt: string }>;
}

export async function* streamAnswer(question: string, token: string): AsyncGenerator<StreamEvent> {
  const response = await fetch(`${API_BASE_URL}/qa/ask/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ question }),
  });

  if (!response.body) throw new Error("No response body from stream");

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        const jsonStr = line.slice(6);
        try {
          const event: StreamEvent = JSON.parse(jsonStr);
          yield event;
        } catch {
          // Skip malformed chunks rather than crashing the stream.
        }
      }
    }
  }
}