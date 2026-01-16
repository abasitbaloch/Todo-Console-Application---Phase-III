"use client";

import { User, UserLogin, UserCreate, AuthResponse } from './types';

// 1. Correct the fallback to your Phase 3 URL
const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://janabkakarot-todo-console-application-phase-iii.hf.space';

const getUrl = (path: string) => {
    const cleanBase = BASE_URL.replace(/\/$/, ''); // Remove trailing slash from base
    const cleanPath = path.startsWith('/') ? path : `/${path}`; // Ensure path starts with /
    return `${cleanBase}${cleanPath}`;
};

class AuthService {
    // 2. Changed to auth_token to match your chat-api.ts
    private tokenKey = 'auth_token';

    getToken(): string | null {
        if (typeof window === 'undefined') return null;
        return localStorage.getItem(this.tokenKey);
    }

    setToken(token: string) {
        if (typeof window === 'undefined') return;
        localStorage.setItem(this.tokenKey, token);
    }

    // 3. Added missing isAuthenticated for your Layout
    isAuthenticated(): boolean {
        return !!this.getToken();
    }

    // 4. Added missing getCurrentUser for your Dashboard
    async getCurrentUser(): Promise<User | null> {
        const token = this.getToken();
        if (!token) return null;

        try {
            const response = await fetch(getUrl('/api/users/me'), {
                headers: { 'Authorization': `Bearer ${token}` },
            });
            if (!response.ok) throw new Error();
            return await response.json();
        } catch {
            this.logout();
            return null;
        }
    }

 logout() {
    if (typeof window === 'undefined') return;
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem('user');
    
    // CHANGE THIS from '/login' to '/'
    window.location.href = '/'; 
}

    async login(data: UserLogin): Promise<AuthResponse> {
        const response = await fetch(getUrl('/api/auth/login'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Login failed');
        }
        
        const result = await response.json();
        this.setToken(result.access_token);
        // Save user info for the dashboard to use
        localStorage.setItem('user', JSON.stringify(result.user));
        return result;
    }

    async register(data: UserCreate): Promise<AuthResponse> {
        const response = await fetch(getUrl('/api/auth/register'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Registration failed');
        }

        const result = await response.json();
        this.setToken(result.access_token);
        localStorage.setItem('user', JSON.stringify(result.user));
        return result;
    }
}

export const authService = new AuthService();