import { describe, it, expect } from "vitest";
import { ApiError } from "./api";

describe("ApiError", () => {
  it("creates error with status and detail", () => {
    const err = new ApiError(400, { detail: "Bad request" });
    expect(err.status).toBe(400);
    expect(err.detail).toEqual({ detail: "Bad request" });
  });

  it("creates error with string detail", () => {
    const err = new ApiError(404, "Not found");
    expect(err.status).toBe(404);
    expect(err.message).toBe("Not found");
  });
});
