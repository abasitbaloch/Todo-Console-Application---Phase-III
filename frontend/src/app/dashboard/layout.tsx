"use client";

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();

  useEffect(() => {
    // Directly check for the authentication token in localStorage
    // This bypasses the "isAuthenticated" type error
    const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
    
    if (!token) {
      router.push('/');
    }
  }, [router]);

  return <>{children}</>;
}