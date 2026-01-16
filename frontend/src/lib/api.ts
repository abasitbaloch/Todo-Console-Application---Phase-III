import { authService } from './client-auth';

// UPDATED: Added '-phase-iii' to match your actual backend URL
const BASE_URL = 'https://janabkakarot-todo-console-application-phase-iii.hf.space';

/**
 * Helper to build the correct API URL.
 * FastAPI with the updated tasks.py now expects a trailing slash (e.g., /tasks/)
 */
const getUrl = (path: string) => {
  const cleanBase = BASE_URL.replace(/\/$/, ""); 
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  // Ensure the final URL ends with a slash to avoid 307 redirects or 404s
  const finalPath = cleanPath.endsWith('/') ? cleanPath : `${cleanPath}/`;
  return `${cleanBase}${finalPath}`;
};

export const api = {
  /**
   * Get all tasks for the logged-in user
   */
  async getTasks() {
    const token = authService.getToken();
    const response = await fetch(getUrl('/tasks'), {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      // If unauthorized, logout - this now redirects to '/' correctly
      if (response.status === 401) authService.logout();
      throw new Error('Failed to fetch tasks');
    }
    return response.json();
  },

  /**
   * Create a new task
   */
  async createTask(title: string, description?: string) {
    const token = authService.getToken();
    const response = await fetch(getUrl('/tasks'), {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ title, description }),
    });

    if (!response.ok) throw new Error('Failed to create task');
    return response.json();
  },

  /**
   * Update task status
   */
  async updateTask(taskId: string, data: { is_completed: boolean }) {
    const token = authService.getToken();
    const response = await fetch(getUrl(`/tasks/${taskId}`), {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) throw new Error('Failed to update task');
    return response.json();
  },

  /**
   * Delete a task
   */
  async deleteTask(taskId: string) {
    const token = authService.getToken();
    const response = await fetch(getUrl(`/tasks/${taskId}`), {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) throw new Error('Failed to delete task');
    return true;
  }
};