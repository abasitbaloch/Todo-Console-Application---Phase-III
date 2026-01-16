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
        // 1. Check if we have a token first
        const token = authService.getToken();
        if (!token) {
          console.log("No token found, redirecting to login...");
          router.push('/login'); // Change to /login to avoid 404 on home
          return;
        }

        // 2. Get user info (from state/localStorage or API)
        let currentUser = await authService.getCurrentUser();
        
        if (!currentUser) {
          // Fallback: Try to get from localStorage if API fails
          const savedUser = localStorage.getItem('user');
          if (savedUser) {
            currentUser = JSON.parse(savedUser);
          }
        }

        if (!currentUser) {
          router.push('/login');
          return;
        }

        setUser(currentUser);

        // 3. Fetch Tasks
        const fetchedTasks = await api.getTasks();
        setTasks(fetchedTasks || []);
        
      } catch (error) {
        console.error('Dashboard init failed:', error);
        // If we get an error, only redirect if it's an auth error
        // router.push('/login'); 
      } finally {
        setLoading(false);
      }
    };

    initDashboard();
  }, [router]);

  const handleCreateTask = async (title: string, description: string) => {
    try {
      const newTask = await api.createTask(title, description);
      setTasks(prev => [...prev, newTask]);
    } catch (error) {
      console.error('Failed to create task:', error);
      alert('Failed to create task. Please check your connection.');
    }
  };

  const handleUpdateTask = async (taskId: string, is_completed: boolean) => {
    try {
      const updatedTask = await api.updateTask(taskId, { is_completed });
      setTasks(tasks.map(t => (t.id === taskId ? updatedTask : t)));
    } catch (error) {
      console.error('Failed to update task:', error);
    }
  };

  const handleDeleteTask = async (taskId: string) => {
    if (!confirm('Are you sure you want to delete this task?')) return;
    try {
      await api.deleteTask(taskId);
      setTasks(tasks.filter(t => t.id !== taskId));
    } catch (error) {
      console.error('Failed to delete task:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col justify-center items-center min-h-screen bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mb-4"></div>
        <div className="text-xl text-gray-600 font-medium">Loading your tasks...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Navigation Bar */}
      <nav className="bg-white shadow-md p-4 sticky top-0 z-10">
        <div className="max-w-5xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-2">
            <span className="text-2xl">📋</span>
            <h1 className="text-xl font-bold text-gray-800">AI Todo Dashboard</h1>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right hidden sm:block">
              <p className="text-sm font-semibold text-gray-900">{user?.email}</p>
              <p className="text-xs text-gray-500">Authenticated</p>
            </div>
            <button
              onClick={() => {
                authService.logout();
                router.push('/login');
              }}
              className="px-4 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors font-medium border border-red-200"
            >
              Logout
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content Area */}
      <main className="max-w-5xl mx-auto p-6">
        <div className="grid gap-8 lg:grid-cols-[380px_1fr]">
          {/* Left Column: Task Creation */}
          <aside>
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 sticky top-24">
              <h2 className="text-lg font-bold mb-4 text-gray-800 flex items-center gap-2">
                <span>➕</span> Create New Task
              </h2>
              <TaskForm onSubmit={handleCreateTask} />
              
              <div className="mt-8 p-4 bg-blue-50 rounded-lg border border-blue-100">
                <p className="text-xs text-blue-700 font-medium uppercase tracking-wider mb-1">AI Tip</p>
                <p className="text-sm text-blue-800">
                  You can also manage tasks using the AI Chatbot!
                </p>
              </div>
            </div>
          </aside>

          {/* Right Column: Task List */}
          <section>
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 min-h-[500px]">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-lg font-bold text-gray-800">Your Tasks ({tasks.length})</h2>
                <div className="text-sm text-gray-500 italic">Phase III AI Connected</div>
              </div>
              
              {tasks.length === 0 ? (
                <div className="text-center py-20 bg-gray-50 rounded-lg border-2 border-dashed border-gray-200">
                  <p className="text-gray-400 text-lg">No tasks yet. Create one to get started!</p>
                </div>
              ) : (
                <TaskList
                  tasks={tasks}
                  onToggle={handleUpdateTask}
                  onDelete={handleDeleteTask}
                />
              )}
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}

// version 1.0