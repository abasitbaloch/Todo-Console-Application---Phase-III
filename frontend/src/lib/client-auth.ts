"use client";

import { User, UserLogin, UserCreate, AuthResponse } from './types';

const BASE_URL = 'https://janabkakarot-todo-console-application-phase-iii.hf.space';

const getUrl = (path: string) => {
    const cleanBase = BASE_URL.replace(/\/$/, '');
    const cleanPath = path.startsWith('/') ? path : `/${path}`;
    return `${cleanBase}${cleanPath}`;
};

class AuthService {
    private tokenKey = 'auth_token';

    getToken(): string | null {
        if (typeof window === 'undefined') return null;
        return localStorage.getItem(this.tokenKey);
    }

    setToken(token: string) {
        if (typeof window === 'undefined') return;
        localStorage.setItem(this.tokenKey, token);
    }

    isAuthenticated(): boolean {
        return !!this.getToken();
    }

    async getCurrentUser(): Promise<User | null> {
    const token = this.getToken();
    if (!token) return null;

    try {
        const response = await fetch(getUrl('/api/users/me'), {
            headers: { 'Authorization': `Bearer ${token}` },
        });

        // Only log out if the server explicitly says the token is invalid (401)
        if (response.status === 401) {
            console.warn("Session expired, logging out...");
            this.logout();
            return null;
        }

        if (!response.ok) {
            console.error("Server error during auth check, but keeping session alive.");
            return null;
        }

        return await response.json();
    } catch (error) {
        // If the network fails (Hugging Face sleeping), DO NOT log out.
        // Just return null so the page can try again or show a local user.
        console.error('Network error checking user:', error);
        return null;
    }
}

    logout() {
        if (typeof window === 'undefined') return;
        localStorage.removeItem(this.tokenKey);
        localStorage.removeItem('user');
        // FIX: Redirect to root '/' where your AuthForm is
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