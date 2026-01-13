# Todo Frontend

Next.js frontend for the Phase II Full-Stack Todo Application.

## Tech Stack

- **Next.js 15.1.3** - React framework with App Router
- **React 19** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first CSS framework
- **lucide-react** - Icon library

## Prerequisites

- Node.js 18+
- Backend API running on http://localhost:8000

## Installation

```bash
# Install dependencies
npm install
```

## Environment Variables

Create a `.env.local` file in the `frontend/` directory:

```env
# Better Auth Secret (MUST match backend JWT_SECRET)
AUTH_SECRET=your-random-256-bit-secret-here

# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth Configuration
BETTER_AUTH_URL=http://localhost:3000
```

**⚠️ IMPORTANT**: `AUTH_SECRET` must match the backend's `JWT_SECRET`

## Running the Application

### Development Mode

```bash
npm run dev
```

The application will be available at http://localhost:3000

### Production Build

```bash
# Build for production
npm run build

# Start production server
npm start
```

### Linting

```bash
npm run lint
```

## Project Structure

```
frontend/
├── src/
│   ├── app/                  # Next.js App Router pages
│   │   ├── dashboard/        # Protected dashboard
│   │   │   ├── layout.tsx    # Dashboard layout with auth check
│   │   │   └── page.tsx      # Dashboard page with tasks
│   │   ├── register/         # Registration page
│   │   │   └── page.tsx      # Registration form
│   │   ├── globals.css       # Global styles with Tailwind
│   │   ├── layout.tsx        # Root layout
│   │   └── page.tsx          # Landing/login page
│   ├── components/           # React components
│   │   ├── AuthForm.tsx      # Login/register form
│   │   ├── TaskList.tsx      # Task list container
│   │   ├── TaskForm.tsx      # Create task form
│   │   └── TaskItem.tsx      # Individual task item
│   └── lib/                  # Utilities
│       ├── api.ts            # API client
│       ├── auth.ts           # Authentication service
│       └── types.ts          # TypeScript types
├── public/                   # Static assets
├── tailwind.config.ts        # Tailwind configuration
├── tsconfig.json             # TypeScript configuration
├── next.config.js            # Next.js configuration
├── postcss.config.js         # PostCSS configuration
└── package.json              # Node dependencies
```

## Features

### Authentication
- User registration with email/password validation
- Login with JWT token authentication
- Protected routes with automatic redirect
- Logout functionality

### Task Management
- Create tasks with title and optional description
- View all tasks ordered by creation date (newest first)
- Inline editing of task title and description
- Mark tasks as complete/incomplete
- Delete tasks with confirmation
- Visual distinction for completed tasks (strikethrough)

### UI/UX
- Responsive design (mobile-first)
- Loading states for async operations
- Error handling with user-friendly messages
- Success feedback for operations
- Smooth animations and transitions
- Touch-friendly tap targets (min 44px)
- Accessibility features (focus indicators, ARIA labels)

## Pages

### `/` - Landing/Login Page
- Login form with email and password
- Link to registration page
- Redirects to dashboard if already authenticated

### `/register` - Registration Page
- Registration form with email and password
- Password strength validation
- Link to login page
- Redirects to dashboard after successful registration

### `/dashboard` - Dashboard (Protected)
- Requires authentication
- Task creation form
- Task list with all user's tasks
- Inline editing, completion toggle, and deletion
- Logout button

## Components

### `AuthForm`
Reusable authentication form component for login and registration.

**Props:**
- `mode: 'login' | 'register'` - Form mode

### `TaskList`
Container component for task management.

**Props:**
- `initialTasks: Task[]` - Initial tasks from server

**Features:**
- Create new tasks
- Update existing tasks
- Toggle task completion
- Delete tasks
- Error and success message display

### `TaskForm`
Form component for creating new tasks.

**Props:**
- `onSubmit: (title: string, description: string) => Promise<void>` - Submit handler

### `TaskItem`
Individual task item component with inline editing.

**Props:**
- `task: Task` - Task data
- `onToggle: (taskId: string, isCompleted: boolean) => void` - Toggle handler
- `onUpdate: (taskId: string, title: string, description: string | null) => Promise<void>` - Update handler
- `onDelete: (taskId: string) => void` - Delete handler

**Features:**
- View mode with title, description, and metadata
- Edit mode with inline form
- Completion checkbox
- Delete button with confirmation

## API Integration

The frontend communicates with the backend API using the `api.ts` client:

```typescript
import { tasksApi, authApi } from '@/lib/api';

// Get all tasks
const tasks = await tasksApi.getAll();

// Create task
const newTask = await tasksApi.create({ title, description });

// Update task
const updatedTask = await tasksApi.update(taskId, { title, description, is_completed });

// Delete task
await tasksApi.delete(taskId);

// Get current user
const user = await authApi.getMe();
```

## Styling

### Tailwind CSS

The application uses Tailwind CSS with custom configuration:

- Custom color palette (primary, success, error)
- Responsive breakpoints (xs, sm, md, lg, xl, 2xl)
- Custom animations (fade-in, slide-up, scale-in)
- Touch-friendly sizing utilities
- Accessibility utilities

### Global Styles

Custom CSS in `globals.css`:

- CSS variables for consistent theming
- Animation keyframes
- Custom scrollbar styling
- Loading spinner
- Utility classes for common patterns

## Troubleshooting

### Frontend won't start

```bash
# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Authentication fails

- Verify `AUTH_SECRET` matches backend `JWT_SECRET`
- Check backend is running on port 8000
- Check `NEXT_PUBLIC_API_URL` is correct

### Build errors

```bash
# Clear Next.js cache
rm -rf .next

# Rebuild
npm run build
```

### Type errors

```bash
# Regenerate TypeScript types
npm run build
```

## Development Tips

### Hot Reload

Next.js automatically reloads when you save files. If hot reload stops working:

```bash
# Restart dev server
npm run dev
```

### Debugging

Use React DevTools and browser console for debugging. Add `console.log` statements in components for troubleshooting.

### Environment Variables

- Variables prefixed with `NEXT_PUBLIC_` are exposed to the browser
- Other variables are only available server-side
- Restart dev server after changing `.env.local`

## License

This project is part of the Phase II Full-Stack Web Application specification.
