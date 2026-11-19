import type { Task, TaskStatus } from "../types/task";

export function filterTasksByStatus(tasks: readonly Task[], status: TaskStatus): Task[] {
  return tasks.filter((task) => task.status === status);
}

export function calculateCompletionPercentage(tasks: readonly Task[]): number {
  if (tasks.length === 0) return 0;
  const completed = filterTasksByStatus(tasks, "completed").length;
  return Math.round((completed / tasks.length) * 100);
}