import { useState, type FormEvent } from "react";
import type { CreateTaskInput, UserProfile } from "../types/task";

interface Props {
  employees: UserProfile[];
  onCreate: (input: CreateTaskInput) => Promise<void>;
}

export function TaskForm({ employees, onCreate }: Props) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [assignedTo, setAssignedTo] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    try {
      await onCreate({ title, description: description || undefined, assigned_to: assignedTo });
      setTitle("");
      setDescription("");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <h3>Assign a task</h3>
      <input placeholder="Title" value={title} onChange={(e) => setTitle(e.target.value)} maxLength={200} required />
      <input placeholder="Description" value={description} onChange={(e) => setDescription(e.target.value)} />
      <select value={assignedTo} onChange={(e) => setAssignedTo(e.target.value)} required>
        <option value="">Select employee</option>
        {employees.map((emp) => (
          <option key={emp.id} value={emp.id}>{emp.full_name}</option>
        ))}
      </select>
      <button type="submit" disabled={submitting}>{submitting ? "Creating..." : "Create"}</button>
    </form>
  );
}