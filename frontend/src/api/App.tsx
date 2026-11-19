import { useCallback, useEffect, useState } from "react";
import type { Session } from "@supabase/supabase-js";
import { createTask, fetchTasks, updateTaskStatus } from "../../frontend/src/api/tasks";
import { LoginForm } from "./components/LoginForm";
import { TaskForm } from "./components/TaskForm";
import { TaskList } from "./components/TaskList";
import { supabase } from "./lib/supabase";
import { TASK_STATUSES, isTaskStatus, type CreateTaskInput, type Task, type TaskStatus, type UserProfile } from "./types/task";
import { calculateCompletionPercentage, filterTasksByStatus } from "./utils/taskUtils";

export default function App() {
  const [session, setSession] = useState<Session | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [people, setPeople] = useState<UserProfile[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [filter, setFilter] = useState<TaskStatus | "all">("all");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => setSession(data.session));
    const { data } = supabase.auth.onAuthStateChange((_event, s) => setSession(s));
    return () => data.subscription.unsubscribe();
  }, []);

  const loadData = useCallback(async () => {
    if (!session) return;
    setLoading(true);
    setError(null);
    try {
      const { data: users, error: usersError } = await supabase.from("users").select("*");
      if (usersError) throw new Error(usersError.message);
      const all = users as UserProfile[];
      setPeople(all);
      setProfile(all.find((u) => u.id === session.user.id) ?? null);
      setTasks(await fetchTasks(session.access_token));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected error");
    } finally {
      setLoading(false);
    }
  }, [session]);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  async function handleCreate(input: CreateTaskInput) {
    if (!session) return;
    try {
      const created = await createTask(session.access_token, input);
      setTasks((prev) => [created, ...prev]);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create task");
    }
  }

  async function handleStatusChange(id: string, status: TaskStatus) {
    if (!session) return;
    try {
      const updated = await updateTaskStatus(session.access_token, id, status);
      setTasks((prev) => prev.map((t) => (t.id === id ? updated : t)));
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not update task");
    }
  }

  if (!session) return <LoginForm />;

  const visible = filter === "all" ? tasks : filterTasksByStatus(tasks, filter);
  const employees = people.filter((p) => p.role === "employee");

  return (
    <main>
      <header>
        <h1>Tasks</h1>
        <p>{profile ? `${profile.full_name} (${profile.role})` : session.user.email}</p>
        <button onClick={() => supabase.auth.signOut()}>Sign out</button>
      </header>

      <p>Completion: {calculateCompletionPercentage(tasks)}%</p>

      {error && <p role="alert">{error}</p>}
      {profile?.role === "manager" && <TaskForm employees={employees} onCreate={handleCreate} />}

      <select value={filter} onChange={(e) => setFilter(isTaskStatus(e.target.value) ? e.target.value : "all")}>
        <option value="all">All</option>
        {TASK_STATUSES.map((s) => (
          <option key={s} value={s}>{s.replace("_", " ")}</option>
        ))}
      </select>

      {loading ? <p>Loading...</p> : <TaskList tasks={visible} people={people} onStatusChange={handleStatusChange} />}
    </main>
  );
}