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
    // 1. Give the browser a split second to ensure localStorage is ready
    const checkAuth = () => {
      if (typeof window !== 'undefined') {
        const token = localStorage.getItem('auth_token');
        
        if (!token) {
          console.log("No token found, redirecting to login...");
          router.push('/'); 
        } else {
          setIsAuthorized(true);
        }
      }
    };

    checkAuth();
  }, [router]);

  // While checking, show a loading screen
  if (!isAuthorized) {
    return (
      <div className="flex justify-center items-center min-h-screen bg-white">
        <div className="flex flex-col items-center gap-3">
          <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-600"></div>
          <p className="text-gray-500 font-medium">Entering Dashboard...</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}