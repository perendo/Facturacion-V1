import { describe, it, expect, beforeEach } from "vitest";
import { getUser, setUser, clearUser, isAuthenticated } from "./auth";

describe("auth utilities", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("getUser returns null when no user is stored", () => {
    expect(getUser()).toBeNull();
  });

  it("setUser and getUser round-trip", () => {
    const user = { id: 1, email: "test@example.com", full_name: "Test" };
    setUser(user);
    expect(getUser()).toEqual(user);
    expect(isAuthenticated()).toBe(true);
  });

  it("clearUser removes stored user", () => {
    setUser({ id: 1 });
    clearUser();
    expect(getUser()).toBeNull();
    expect(isAuthenticated()).toBe(false);
  });
});
