import { describe, expect, it } from "vitest";
import type { Task, TaskStatus } from "../types/task";
import { calculateCompletionPercentage, filterTasksByStatus } from "./taskUtils";

const make = (id: string, status: TaskStatus): Task => ({
  id, company_id: "c", title: id, description: null, status,
  assigned_to: "u", created_by: "m", created_at: "", updated_at: "",
});

describe("taskUtils", () => {
  const tasks = [make("1", "completed"), make("2", "pending"), make("3", "completed"), make("4", "in_progress")];

  it("filters by status", () => {
    expect(filterTasksByStatus(tasks, "completed").map((t) => t.id)).toEqual(["1", "3"]);
  });
  it("calculates completion percentage", () => {
    expect(calculateCompletionPercentage(tasks)).toBe(50);
  });
  it("returns 0 for an empty list", () => {
    expect(calculateCompletionPercentage([])).toBe(0);
  });
});