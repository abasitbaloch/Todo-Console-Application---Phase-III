import { useState } from 'react';
import { Task } from '@/lib/types';

interface TaskItemProps {
  task: Task;
  onToggle: (taskId: string, isCompleted: boolean) => Promise<void>;
  onDelete: (taskId: string) => Promise<void>;
}

export default function TaskItem({ task, onToggle, onDelete }: TaskItemProps) {
  const [isDeleting, setIsDeleting] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);

  // Optimistic Toggle Handler
  const handleToggle = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.checked;
    setIsUpdating(true);
    try {
      await onToggle(task.id, newValue);
    } catch (error) {
      console.error("Failed to update task visually:", error);
      // Optional: You could add a toast notification here
    } finally {
      setIsUpdating(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm("Are you sure?")) return;
    setIsDeleting(true);
    try {
      await onDelete(task.id);
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className={`flex items-center justify-between p-4 bg-white border rounded-lg shadow-sm transition-all duration-200 
      ${isUpdating ? 'border-blue-200 bg-blue-50/30' : 'border-gray-200'}`}>
      
      <div className="flex items-center gap-4 overflow-hidden">
        <input
          type="checkbox"
          checked={task.is_completed}
          onChange={handleToggle}
          disabled={isUpdating}
          className="w-5 h-5 text-blue-600 rounded border-gray-300 focus:ring-blue-500 cursor-pointer disabled:opacity-50"
        />

        <div className={`flex flex-col transition-opacity ${task.is_completed ? 'opacity-50' : 'opacity-100'}`}>
          <h3 className={`font-medium text-gray-900 truncate ${task.is_completed ? 'line-through text-gray-500' : ''}`}>
            {task.title}
          </h3>
          {task.description && (
            <p className="text-sm text-gray-500 truncate max-w-xs">
              {task.description}
            </p>
          )}
        </div>
      </div>

      <button
        onClick={handleDelete}
        disabled={isDeleting || isUpdating}
        className="ml-4 px-3 py-1.5 text-sm font-medium text-red-600 bg-red-50 hover:bg-red-100 rounded-md transition-colors disabled:opacity-30"
      >
        {isDeleting ? '...' : 'Delete'}
      </button>
    </div>
  );
}