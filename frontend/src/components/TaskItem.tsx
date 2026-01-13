import { useState } from 'react';
import { Task } from '@/lib/types';

interface TaskItemProps {
  task: Task;
  onToggle: (taskId: string, isCompleted: boolean) => void;
  onDelete: (taskId: string) => void;
}

export default function TaskItem({ task, onToggle, onDelete }: TaskItemProps) {
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async () => {
    setIsDeleting(true);
    await onDelete(task.id);
    setIsDeleting(false);
  };

  return (
    <div className="flex items-center justify-between p-4 bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-all duration-200">
      <div className="flex items-center gap-4 overflow-hidden">
        <input
          type="checkbox"
          checked={task.is_completed}
          onChange={(e) => onToggle(task.id, e.target.checked)}
          className="w-5 h-5 text-blue-600 rounded border-gray-300 focus:ring-blue-500 cursor-pointer"
        />

        <div className={`flex flex-col ${task.is_completed ? 'opacity-50' : ''}`}>
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
        disabled={isDeleting}
        className="ml-4 px-3 py-1.5 text-sm font-medium text-red-600 bg-red-50 hover:bg-red-100 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isDeleting ? '...' : 'Delete'}
      </button>
    </div>
  );
}