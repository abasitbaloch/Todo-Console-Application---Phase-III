import { authService } from './client-auth';

// The live backend URL on Hugging Face
const BASE_URL = 'https://janabkakarot-todo-console-application.hf.space';

/**
 * Helper to build the correct API URL.
 * FastAPI with the updated tasks.py now expects a trailing slash (e.g., /tasks/)
 */
const getUrl = (path: string) => {
  const cleanBase = BASE_URL.replace(/\/$/, ""); // Remove base trailing slash
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
   * Update task status (completed/pending)
   * FastAPI expects the task_id in the URL
   */
  async toggleTask(taskId: string, completed: boolean) {
    const token = authService.getToken();
    const response = await fetch(getUrl(`/tasks/${taskId}`), {
      method: 'PUT', // Matches @router.put("/{task_id}") in your tasks.py
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ is_completed: completed }),
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
    // DELETE usually returns 204 No Content, no JSON to return
    return true;
  }
};