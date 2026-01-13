"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { authService } from '../../lib/client-auth';
import { api } from '../../lib/api';
import { User, Task } from '@/lib/types';
import TaskList from '@/components/TaskList';
import TaskForm from '@/components/TaskForm';

export default function Dashboard() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initDashboard = async () => {
      try {
        const currentUser = await authService.getCurrentUser();
        if (!currentUser) {
          router.push('/');
          return;
        }

        const fetchedTasks = await api.getTasks();
        setUser(currentUser);
        setTasks(fetchedTasks);
      } catch (error) {
        console.error('Dashboard init failed:', error);
        router.push('/');
      } finally {
        setLoading(false);
      }
    };

    initDashboard();
  }, [router]);

  const handleCreateTask = async (title: string, description: string) => {
    try {
      const newTask = await api.createTask(title, description);
      setTasks([...tasks, newTask]);
    } catch (error) {
      console.error('Failed to create task:', error);
      alert('Failed to create task');
    }
  };

  // UPDATED: Expects string ID and is_completed
  const handleUpdateTask = async (taskId: string, is_completed: boolean) => {
    try {
      const updatedTask = await api.updateTask(taskId, { is_completed });
      setTasks(tasks.map(t => (t.id === taskId ? updatedTask : t)));
    } catch (error) {
      console.error('Failed to update task:', error);
    }
  };

  // UPDATED: Expects string ID
  const handleDeleteTask = async (taskId: string) => {
    if (!confirm('Are you sure?')) return;
    try {
      await api.deleteTask(taskId);
      setTasks(tasks.filter(t => t.id !== taskId));
    } catch (error) {
      console.error('Failed to delete task:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-xl text-gray-600">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow-sm p-4">
        <div className="max-w-4xl mx-auto flex justify-between items-center">
          <h1 className="text-xl font-bold text-gray-800">Todo App</h1>
          <div className="flex items-center gap-4">
            <span className="text-gray-600">Welcome, {user?.email}</span>
            <button
              onClick={() => {
                authService.logout();
                router.push('/');
              }}
              className="text-red-500 hover:text-red-700 font-medium"
            >
              Logout
            </button>
          </div>
        </div>
      </nav>

      <main className="max-w-4xl mx-auto p-6">
        <div className="grid gap-8 md:grid-cols-[350px_1fr]">
          <div>
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-lg font-bold mb-4">New Task</h2>
              <TaskForm onSubmit={handleCreateTask} />
            </div>
          </div>

          <div>
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-lg font-bold mb-4">Your Tasks</h2>
              <TaskList
                tasks={tasks}
                onToggle={handleUpdateTask}
                onDelete={handleDeleteTask}
              />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}