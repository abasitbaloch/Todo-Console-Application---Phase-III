"use client";

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { authService } from '../../lib/client-auth';
import { api } from '../../lib/api';
import { User, Task } from '@/lib/types';
import TaskList from '@/components/TaskList';
import TaskForm from '@/components/TaskForm';
import ChatInterface from '@/components/chat/ChatInterface'; 

export default function Dashboard() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);

  // 1. Function to fetch tasks (extracted so it can be reused)
  const refreshTasks = useCallback(async () => {
    try {
      const fetchedTasks = await api.getTasks();
      setTasks(fetchedTasks || []);
    } catch (error) {
      console.error('Failed to fetch tasks:', error);
    }
  }, []);

  useEffect(() => {
    const initDashboard = async () => {
      try {
        const token = authService.getToken();
        if (!token) {
          router.push('/');
          return;
        }

        let currentUser = await authService.getCurrentUser();
        if (!currentUser) {
          const savedUser = localStorage.getItem('user');
          if (savedUser) currentUser = JSON.parse(savedUser);
        }

        if (!currentUser) {
          router.push('/');
          return;
        }

        setUser(currentUser);
        await refreshTasks(); // Initial load
        
      } catch (error) {
        console.error('Dashboard init failed:', error);
      } finally {
        setLoading(false);
      }
    };

    initDashboard();
  }, [router, refreshTasks]);

  // Task Handlers
  const handleCreateTask = async (title: string, description: string) => {
    try {
      const newTask = await api.createTask(title, description);
      setTasks(prev => [newTask, ...prev]);
    } catch (error) {
      alert('Failed to create task.');
    }
  };

  const handleUpdateTask = async (taskId: string, is_completed: boolean) => {
    try {
      // Use the checkbox fix: ensure URL has trailing slash in api.ts
      const updatedTask = await api.updateTask(taskId, { is_completed });
      setTasks(prev => prev.map(t => (t.id === taskId ? updatedTask : t)));
    } catch (error) {
      console.error('Update failed:', error);
    }
  };

  const handleDeleteTask = async (taskId: string) => {
    if (!confirm('Delete this task?')) return;
    try {
      await api.deleteTask(taskId);
      setTasks(prev => prev.filter(t => t.id !== taskId));
    } catch (error) {
      console.error('Delete failed:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col justify-center items-center min-h-screen bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mb-4"></div>
        <div className="text-xl text-gray-600">Loading Phase III Dashboard...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col h-screen overflow-hidden">
      {/* Navigation Bar */}
      <nav className="bg-white shadow-sm p-4 border-b border-gray-200 shrink-0">
        <div className="max-w-[1600px] mx-auto flex justify-between items-center">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🤖</span>
            <h1 className="text-xl font-bold text-gray-800">AI Task Manager</h1>
          </div>
          <div className="flex items-center gap-4">
            <span className="hidden md:block text-sm text-gray-600 font-medium">{user?.email}</span>
            <button
              onClick={() => { authService.logout(); router.push('/'); }}
              className="px-4 py-2 bg-white text-gray-700 rounded-lg border border-gray-300 hover:bg-gray-50 transition-all text-sm font-semibold"
            >
              Logout
            </button>
          </div>
        </div>
      </nav>

      {/* Main Responsive Grid */}
      <main className="flex-1 max-w-[1600px] mx-auto w-full p-4 md:p-6 grid grid-cols-1 lg:grid-cols-12 gap-6 overflow-hidden">
        
        {/* Left Column: Task Creator */}
        <div className="lg:col-span-3 space-y-6 overflow-y-auto">
          <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-200">
            <h2 className="text-md font-bold mb-4 text-gray-700 uppercase tracking-wider">New Task</h2>
            <TaskForm onSubmit={handleCreateTask} />
          </div>
        </div>

        {/* Center Column: Task List */}
        <div className="lg:col-span-4 flex flex-col overflow-hidden">
          <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-200 flex-1 flex flex-col overflow-hidden">
            <h2 className="text-md font-bold mb-4 text-gray-700 uppercase tracking-wider shrink-0">
               Your Tasks ({tasks.length})
            </h2>
            <div className="flex-1 overflow-y-auto pr-2">
              {tasks.length === 0 ? (
                <div className="text-center py-10 text-gray-400">No tasks yet.</div>
              ) : (
                <TaskList tasks={tasks} onToggle={handleUpdateTask} onDelete={handleDeleteTask} />
              )}
            </div>
          </div>
        </div>

        {/* Right Column: AI Chatbot */}
        <div className="lg:col-span-5 flex flex-col overflow-hidden h-full">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 flex-1 overflow-hidden flex flex-col">
              {/* 2. PASS REFRESH FUNCTION TO CHAT */}
              <ChatInterface onTaskCreated={refreshTasks} /> 
            </div>
        </div>
        
      </main>
    </div>
  );
}