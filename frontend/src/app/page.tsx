import AuthForm from '@/components/AuthForm';

export default function HomePage() {
  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h1 className="text-center text-4xl font-extrabold text-gray-900 mb-2">
            Todo App
          </h1>
          <p className="text-center text-gray-600">
            Manage your tasks efficiently
          </p>
        </div>
        <AuthForm mode="login" />
      </div>
    </div>
  );
}
