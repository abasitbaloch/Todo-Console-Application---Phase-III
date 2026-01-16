/**
 * Task API client - Fixes the Checkbox Toggle
 */
const BASE_URL = "https://janabkakarot-todo-console-application-phase-iii.hf.space";

export async function toggleTaskStatus(taskId: string, isCompleted: boolean) {
  const token = localStorage.getItem("auth_token");
  
  // Notice the trailing slash after ${taskId}/ - critical for PUT requests!
  const response = await fetch(`${BASE_URL}/tasks/${taskId}/`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify({ is_completed: isCompleted })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Could not update task.");
  }

  return await response.json();
}