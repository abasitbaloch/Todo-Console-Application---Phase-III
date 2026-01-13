// backend/src/lib/client-auth.ts
import { User, UserLogin, UserCreate, AuthResponse } from './types';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://janabkakarot-todo-console-application.hf.space';

// frontend/src/lib/client-auth.ts

// Change your getUrl function to this:
const getUrl = (path: string) => {
    const cleanBase = BASE_URL.replace('http://', 'https://').replace(/\/$/, '');
    const cleanPath = path.startsWith('/') ? path : `/${path}`;
    const finalPath = cleanPath.endsWith('/') ? cleanPath : `${cleanPath}/`;
    return `${cleanBase}${finalPath}`;
};

class AuthService {
    private tokenKey = 'access_token';

    getToken(): string | null {
        if (typeof window === 'undefined') return null;
        return localStorage.getItem(this.tokenKey);
    }

    setToken(token: string) {
        if (typeof window === 'undefined') return;
        localStorage.setItem(this.tokenKey, token);
    }

    logout() {
        if (typeof window === 'undefined') return;
        localStorage.removeItem(this.tokenKey);
        window.location.href = '/login';
    }

    async login(data: UserLogin): Promise<AuthResponse> {
        const response = await fetch(getUrl('/auth/login'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });

        if (!response.ok) throw new Error('Login failed');
        const result = await response.json();
        this.setToken(result.access_token);
        return result;
    }

    async register(data: UserCreate): Promise<AuthResponse> {
        const response = await fetch(getUrl('/auth/register'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });

        if (!response.ok) throw new Error('Registration failed');
        const result = await response.json();
        this.setToken(result.access_token);
        return result;
    }
}

export const authService = new AuthService();