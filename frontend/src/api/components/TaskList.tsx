import { TASK_STATUSES, isTaskStatus, type Task, type TaskStatus, type UserProfile } from "../types/task";

interface Props {
  tasks: Task[];
  people: UserProfile[];
  onStatusChange: (id: string, status: TaskStatus) => Promise<void>;
}

export function TaskList({ tasks, people, onStatusChange }: Props) {
  if (tasks.length === 0) return <p>No tasks found.</p>;
  const nameOf = (id: string) => people.find((p) => p.id === id)?.full_name ?? "Unknown";

  return (
    <ul>
      {tasks.map((task) => (
        <li key={task.id}>
          <strong>{task.title}</strong> — {nameOf(task.assigned_to)}
          {task.description && <p>{task.description}</p>}
          <select
            value={task.status}
            onChange={(e) => isTaskStatus(e.target.value) && onStatusChange(task.id, e.target.value)}
          >
            {TASK_STATUSES.map((s) => (
              <option key={s} value={s}>{s.replace("_", " ")}</option>
            ))}
          </select>
        </li>
      ))}
    </ul>
  );
}