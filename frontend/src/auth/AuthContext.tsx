/**
 * Authentication context and provider.
 *
 * Stores access token in memory (React state) — never localStorage.
 * Refresh token is managed via httpOnly cookie by the browser.
 * Provides login, logout, refresh, and RBAC helpers.
 */

import {
  createContext,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from 'react';

import { post, setTokenGetter, setUnauthorizedHandler } from '@/api/client';
import type { LoginCredentials, TokenResponse, User, UserRole } from '@/types';

export interface AuthContextValue {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => Promise<void>;
  hasRole: (role: UserRole) => boolean;
  hasPermission: (permission: string) => boolean;
}

const ROLE_PERMISSIONS: Record<UserRole, string[]> = {
  administrador: [
    'configs:read',
    'configs:write',
    'dashboard:read',
    'dashboard:export',
    'tasks:execute',
    'tasks:read',
    'users:manage',
  ],
  operador: [
    'configs:read',
    'dashboard:read',
    'dashboard:export',
    'tasks:read',
  ],
};

export const AuthContext = createContext<AuthContextValue | null>(null);

/** Decode JWT payload without verification (client-side only). */
function decodeToken(token: string): User | null {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return {
      id: payload.sub ?? payload.user_id,
      username: payload.username ?? '',
      role: payload.role ?? 'operador',
    };
  } catch {
    return null;
  }
}

const SESSION_TIMEOUT_MS = 30 * 60 * 1000; // 30 minutes

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const lastActivityRef = useRef(Date.now());
  const sessionTimerRef = useRef<ReturnType<typeof setInterval>>();

  // Track user activity for session timeout
  useEffect(() => {
    const updateActivity = () => {
      lastActivityRef.current = Date.now();
    };
    window.addEventListener('mousemove', updateActivity);
    window.addEventListener('keydown', updateActivity);
    return () => {
      window.removeEventListener('mousemove', updateActivity);
      window.removeEventListener('keydown', updateActivity);
    };
  }, []);

  const clearSession = useCallback(() => {
    setToken(null);
    setUser(null);
    if (sessionTimerRef.current) {
      clearInterval(sessionTimerRef.current);
    }
  }, []);

  // Session inactivity check
  useEffect(() => {
    if (!token) return;
    sessionTimerRef.current = setInterval(() => {
      if (Date.now() - lastActivityRef.current > SESSION_TIMEOUT_MS) {
        clearSession();
      }
    }, 60_000);
    return () => {
      if (sessionTimerRef.current) clearInterval(sessionTimerRef.current);
    };
  }, [token, clearSession]);

  const refreshToken = useCallback(async (): Promise<string | null> => {
    try {
      const res = await fetch('/api/v1/auth/refresh', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
      });
      if (!res.ok) return null;
      const data: TokenResponse = await res.json();
      setToken(data.access_token);
      setUser(decodeToken(data.access_token));
      return data.access_token;
    } catch {
      clearSession();
      return null;
    }
  }, [clearSession]);

  // Wire up API client token getter and 401 handler
  useEffect(() => {
    setTokenGetter(() => token);
    setUnauthorizedHandler(refreshToken);
  }, [token, refreshToken]);

  // Attempt token refresh on mount (session restore)
  useEffect(() => {
    refreshToken().finally(() => setIsLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const login = useCallback(async (credentials: LoginCredentials) => {
    const data = await post<TokenResponse>('/auth/login', credentials);
    setToken(data.access_token);
    setUser(decodeToken(data.access_token));
    lastActivityRef.current = Date.now();
  }, []);

  const logout = useCallback(async () => {
    try {
      await post('/auth/logout');
    } finally {
      clearSession();
    }
  }, [clearSession]);

  const hasRole = useCallback(
    (role: UserRole) => user?.role === role,
    [user],
  );

  const hasPermission = useCallback(
    (permission: string) => {
      if (!user) return false;
      return ROLE_PERMISSIONS[user.role]?.includes(permission) ?? false;
    },
    [user],
  );

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      token,
      isAuthenticated: !!token && !!user,
      isLoading,
      login,
      logout,
      hasRole,
      hasPermission,
    }),
    [user, token, isLoading, login, logout, hasRole, hasPermission],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
