const USER_KEY = "user";

export function getToken(): string | null {
  // Tokens are stored in an HttpOnly cookie by the backend and are not
  // accessible from JavaScript (mitigates XSS token theft).
  return null;
}

export function setToken(_token: string): void {
  // No-op: authentication cookie is issued by the backend.
  void _token;
}

export function clearToken(): void {
  // No-op: cookie is cleared by the backend /auth/logout endpoint.
}

export function getUser<T = unknown>(): T | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as T;
  } catch {
    return null;
  }
}

export function setUser(user: unknown): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function clearUser(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem(USER_KEY);
}

export function clearAuth(): void {
  clearUser();
  if (typeof window !== "undefined") {
    fetch((process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000") + "/api/v1/auth/logout", {
      method: "POST",
      credentials: "include",
    }).catch(() => undefined);
  }
}

export function isAuthenticated(): boolean {
  return !!getUser();
}
