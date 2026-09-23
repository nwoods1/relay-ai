const API_BASE_URL =
  "http://127.0.0.1:8000/api";


export function getAccessToken() {
  return localStorage.getItem(
    "relay_access_token"
  );
}


export function setAccessToken(
  token: string
) {
  localStorage.setItem(
    "relay_access_token",
    token
  );
}


export function clearAccessToken() {
  localStorage.removeItem(
    "relay_access_token"
  );
}


export async function apiRequest<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getAccessToken();

  const headers = new Headers(
    options.headers
  );

  headers.set(
    "Content-Type",
    "application/json"
  );

  if (token) {
    headers.set(
      "Authorization",
      `Bearer ${token}`
    );
  }

  const response = await fetch(
    `${API_BASE_URL}${path}`,
    {
      ...options,
      headers,
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw {
      status: response.status,
      data,
    };
  }

  return data;
}