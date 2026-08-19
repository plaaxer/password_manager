const BASE_URL = "http://localhost:8000/api/v2";
export const UNAUTHORIZED_EVENT = "argus:unauthorized";

function getToken(): string | null { return localStorage.getItem("token"); }

function authHeaders(masterPassword?: string): HeadersInit {
  const token = getToken();
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(masterPassword ? { "X-Master-Password": masterPassword } : {}),
  };
}

function getErrorMessage(detail: unknown): string {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) return detail.map((item) => item?.msg ?? "Invalid request").join("; ");
  return "Request failed";
}

async function handleResponse<T>(response: Response, protectedRequest = false): Promise<T> {
  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: "Unknown error" }));
    if (protectedRequest && response.status === 401) {
      logout();
      window.dispatchEvent(new Event(UNAUTHORIZED_EVENT));
    }
    throw new Error(getErrorMessage(body.detail));
  }
  return response.json();
}

export async function register(username: string, password: string): Promise<void> {
  const response = await fetch(`${BASE_URL}/register`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ username, password }) });
  await handleResponse<unknown>(response);
}

export async function login(username: string, password: string): Promise<string> {
  const body = new URLSearchParams({ username, password });
  const response = await fetch(`${BASE_URL}/login`, { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded" }, body });
  const data = await handleResponse<{ access_token: string }>(response);
  localStorage.setItem("token", data.access_token);
  return data.access_token;
}

export function logout() { localStorage.removeItem("token"); }

export interface PasswordMeta { service_name: string; username: string; updated_at: string; group_name?: string; }
export interface PasswordData { service_name: string; password: string; username?: string; notes?: string; group_name?: string; }

export async function listPasswords(masterPassword: string): Promise<PasswordMeta[]> {
  const response = await fetch(`${BASE_URL}/passwords`, { headers: authHeaders(masterPassword) });
  return handleResponse<PasswordMeta[]>(response, true);
}

export async function getPassword(serviceName: string, masterPassword: string): Promise<PasswordData> {
  const response = await fetch(`${BASE_URL}/passwords/${encodeURIComponent(serviceName)}`, { headers: authHeaders(masterPassword) });
  return handleResponse<PasswordData>(response, true);
}

export async function storePassword(data: PasswordData, masterPassword: string): Promise<void> {
  const response = await fetch(`${BASE_URL}/passwords`, { method: "POST", headers: authHeaders(masterPassword), body: JSON.stringify(data) });
  await handleResponse<unknown>(response, true);
}

export async function updatePassword(serviceName: string, data: PasswordData, masterPassword: string): Promise<void> {
  const response = await fetch(`${BASE_URL}/passwords/${encodeURIComponent(serviceName)}`, { method: "PUT", headers: authHeaders(masterPassword), body: JSON.stringify(data) });
  await handleResponse<unknown>(response, true);
}

export async function deletePassword(serviceName: string, masterPassword: string): Promise<void> {
  const response = await fetch(`${BASE_URL}/passwords/${encodeURIComponent(serviceName)}`, { method: "DELETE", headers: authHeaders(masterPassword) });
  await handleResponse<unknown>(response, true);
}
