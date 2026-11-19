import { isTask, type CreateTaskInput, type Task, type TaskStatus } from "../../../backend/src/types/task";
import { api, ApiError } from "./client";

function assertTask(data: unknown): Task {
  if (!isTask(data)) throw new ApiError(502, "Unexpected response from server");
  return data;
}

export async function fetchTasks(token: string, status?: TaskStatus): Promise<Task[]> {
  const query = status ? `?status=${encodeURIComponent(status)}` : "";
  const data = await api<unknown>(`/tasks${query}`, {}, token);
  if (!Array.isArray(data) || !data.every(isTask)) {
    throw new ApiError(502, "Unexpected response from server");
  }
  return data;
}

export async function createTask(token: string, input: CreateTaskInput): Promise<Task> {
  const data = await api<unknown>("/tasks", { method: "POST", body: JSON.stringify(input) }, token);
  return assertTask(data);
}

export async function updateTaskStatus(token: string, id: string, status: TaskStatus): Promise<Task> {
  const data = await api<unknown>(`/tasks/${id}`, { method: "PATCH", body: JSON.stringify({ status }) }, token);
  return assertTask(data);
}