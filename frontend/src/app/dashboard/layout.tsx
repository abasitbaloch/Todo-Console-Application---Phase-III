"use client";

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { authService } from '../../lib/client-auth';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();

  useEffect(() => {
    // Check if user is authenticated
    if (!authService.isAuthenticated()) {
      router.push('/');
    }
  }, [router]);

  return <>{children}</>;
}
