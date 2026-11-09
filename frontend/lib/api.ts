import { getToken, clearAuth } from "./auth";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const BASE_URL = `${API_BASE}/api/v1`;

export class ApiError extends Error {
  status: number;
  detail: unknown;
  constructor(status: number, detail: unknown) {
    super(typeof detail === "string" ? detail : "Request failed");
    this.status = status;
    this.detail = detail;
  }
}

type RequestOptions = Omit<RequestInit, "body"> & {
  params?: Record<string, string | number | boolean | null | undefined>;
  body?: unknown;
};

function buildUrl(path: string, params?: RequestOptions["params"]): string {
  const url = new URL(`${BASE_URL}${path}`);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== "") {
        url.searchParams.set(key, String(value));
      }
    });
  }
  return url.toString();
}

export async function api<T = unknown>(path: string, options: RequestOptions = {}): Promise<T> {
  const { params, headers, body, ...rest } = options;
  const token = getToken();
  const finalHeaders: Record<string, string> = {
    ...(headers as Record<string, string>),
  };
  if (body !== undefined && !(body instanceof FormData)) {
    finalHeaders["Content-Type"] = finalHeaders["Content-Type"] || "application/json";
  }
  if (token) {
    finalHeaders["Authorization"] = `Bearer ${token}`;
  }

  const computedBody =
    body instanceof FormData
      ? body
      : body !== undefined
      ? typeof body === "string"
        ? body
        : JSON.stringify(body)
      : undefined;
  const res = await fetch(buildUrl(path, params), {
    ...rest,
    headers: finalHeaders,
    body: computedBody as BodyInit | undefined,
    credentials: "include",
  });

  if (res.status === 401) {
    clearAuth();
    if (typeof window !== "undefined") {
      window.location.href = "/login";
    }
    throw new ApiError(401, "Unauthorized");
  }

  if (res.status === 204) {
    return undefined as T;
  }

  const text = await res.text();
  let data: unknown = null;
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = text;
    }
  }

  if (!res.ok) {
    const detail =
      data && typeof data === "object" && "detail" in (data as Record<string, unknown>)
        ? (data as Record<string, unknown>).detail
        : data;
    const err = new ApiError(res.status, detail);
    if (Array.isArray(detail)) {
      err.message = detail.map((d) => (d && typeof d === "object" && "msg" in d ? String((d as { msg: unknown }).msg) : JSON.stringify(d))).join("; ");
    } else if (detail && typeof detail === "object") {
      err.message = JSON.stringify(detail);
    }
    throw err;
  }

  return data as T;
}

export const apiGet = <T = unknown>(path: string, params?: RequestOptions["params"]) =>
  api<T>(path, { method: "GET", params });

export const apiPost = <T = unknown>(path: string, body?: unknown) =>
  api<T>(path, { method: "POST", body });

export const apiPut = <T = unknown>(path: string, body?: unknown) =>
  api<T>(path, { method: "PUT", body });

export const apiPatch = <T = unknown>(path: string, body?: unknown) =>
  api<T>(path, { method: "PATCH", body });

export const apiDelete = <T = unknown>(path: string) =>
  api<T>(path, { method: "DELETE" });