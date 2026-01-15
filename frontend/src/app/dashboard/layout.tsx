"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const [isAuthorized, setIsAuthorized] = useState(false);

  useEffect(() => {
    // 1. Check if we are in the browser
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('auth_token');
      
      // 2. If no token, send them away
      if (!token) {
        console.log("No token found, redirecting...");
        router.push('/'); 
      } else {
        // 3. Token exists, allow the dashboard to show
        setIsAuthorized(true);
      }
    }
  }, [router]);

  // While checking, show a clean loading state to prevent "flashing" or 404s
  if (!isAuthorized) {
    return (
      <div className="flex justify-center items-center min-h-screen bg-gray-50">
        <div className="flex flex-col items-center gap-2">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          <p className="text-gray-500 text-sm animate-pulse">Verifying Session...</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}