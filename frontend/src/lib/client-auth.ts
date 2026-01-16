"use client";

import { User, UserLogin, UserCreate, AuthResponse } from './types';

const BASE_URL = 'https://janabkakarot-todo-console-application-phase-iii.hf.space';

/**
 * Helper to ensure URLs match FastAPI expectations (trailing slashes)
 */
const getUrl = (path: string) => {
    const cleanBase = BASE_URL.replace(/\/$/, '');
    const cleanPath = path.startsWith('/') ? path : `/${path}`;
    
    // Logic: FastAPI often expects a trailing slash before query params or at end
    // This turns /api/auth/me into /api/auth/me/
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
            // FIX: Changed /api/users/me to /api/auth/me/ to match backend logs
            const response = await fetch(getUrl('/api/auth/me'), {
                headers: { 'Authorization': `Bearer ${token}` },
            });

            // Only log out if the server explicitly says the token is invalid (401)
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
        // Redirect to root '/' where AuthForm is
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