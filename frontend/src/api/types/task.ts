export const TASK_STATUSES = ["pending", "in_progress", "completed"] as const;
export type TaskStatus = (typeof TASK_STATUSES)[number];
export type UserRole = "manager" | "employee";

export interface Task {
  id: string;
  company_id: string;
  title: string;
  description: string | null;
  status: TaskStatus;
  assigned_to: string;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface CreateTaskInput {
  title: string;
  description?: string;
  assigned_to: string;
}

export interface UserProfile {
  id: string;
  company_id: string;
  full_name: string;
  email: string;
  role: UserRole;
}

export function isTaskStatus(value: unknown): value is TaskStatus {
  return typeof value === "string" && (TASK_STATUSES as readonly string[]).includes(value);
}

export function isTask(value: unknown): value is Task {
  if (typeof value !== "object" || value === null) return false;
  const t = value as Record<string, unknown>;
  return (
    typeof t.id === "string" &&
    typeof t.company_id === "string" &&
    typeof t.title === "string" &&
    isTaskStatus(t.status) &&
    typeof t.assigned_to === "string"
  );
}