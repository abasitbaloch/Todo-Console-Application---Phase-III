"use client";

import { User, UserLogin, UserCreate, AuthResponse } from './types';

const BASE_URL = 'https://janabkakarot-todo-console-application-phase-iii.hf.space';

/**
 * Helper to ensure URLs match FastAPI expectations (ALWAYS trailing slashes)
 */
const getUrl = (path: string) => {
    const cleanBase = BASE_URL.replace(/\/$/, '');
    const cleanPath = path.startsWith('/') ? path : `/${path}`;
    
    // Enforce trailing slash to match the new backend auth.py decorators
    // This turns /api/auth/login into /api/auth/login/
    const baseWithSlash = cleanPath.endsWith('/') ? cleanPath : `${cleanPath}/`;
    
    return `${cleanBase}${baseWithSlash}`;
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
            // Hits: /api/auth/me/
            const response = await fetch(getUrl('/api/auth/me'), {
                headers: { 'Authorization': `Bearer ${token}` },
            });

            if (response.status === 401) {
                console.warn("Session expired, logging out...");
                this.logout();
                return null;
            }

            if (!response.ok) {
                console.error(`Auth check failed with status: ${response.status}`);
                return null;
            }

            return await response.json();
        } catch (error) {
            console.error('Network error checking user:', error);
            return null;
        }
    }

    logout() {
        if (typeof window === 'undefined') return;
        localStorage.removeItem(this.tokenKey);
        localStorage.removeItem('user');
        window.location.href = '/';
    }

    async login(data: UserLogin): Promise<AuthResponse> {
        // Hits: /api/auth/login/
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
        // Hits: /api/auth/register/
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