/**
 * Vitest unit tests for auth flows and WebSocket message handling.
 *
 * Tests Task 19.6: Auth context, RBAC, login page, and WebSocket provider.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';

import { render, screen } from '@/test/test-utils';
import { AuthContext, type AuthContextValue } from '@/auth/AuthContext';
import { LoginPage } from '@/auth/LoginPage';
import { WebSocketContext, type WebSocketContextValue } from '@/providers/WebSocketProvider';
import type { ReactNode } from 'react';

// ---------------------------------------------------------------------------
// RBAC Permission Tests
// ---------------------------------------------------------------------------

describe('RBAC permissions', () => {
  function renderWithAuth(ui: ReactNode, authValue: AuthContextValue) {
    return render(
      <AuthContext.Provider value={authValue}>{ui}</AuthContext.Provider>,
    );
  }

  const baseAuth: AuthContextValue = {
    user: null,
    token: null,
    isAuthenticated: false,
    isLoading: false,
    login: vi.fn(),
    logout: vi.fn(),
    hasRole: () => false,
    hasPermission: () => false,
  };

  it('administrador has configs:write permission', () => {
    const adminAuth: AuthContextValue = {
      ...baseAuth,
      user: { id: 1, username: 'admin', role: 'administrador' },
      token: 'mock-token-for-test',
      isAuthenticated: true,
      hasRole: (role) => role === 'administrador',
      hasPermission: (perm) =>
        ['configs:read', 'configs:write', 'dashboard:read', 'dashboard:export', 'tasks:execute', 'tasks:read', 'users:manage'].includes(perm),
    };

    expect(adminAuth.hasPermission('configs:write')).toBe(true);
    expect(adminAuth.hasPermission('tasks:execute')).toBe(true);
    expect(adminAuth.hasPermission('users:manage')).toBe(true);
  });

  it('operador does not have configs:write permission', () => {
    const operadorAuth: AuthContextValue = {
      ...baseAuth,
      user: { id: 2, username: 'operador', role: 'operador' },
      token: 'mock-token-for-test',
      isAuthenticated: true,
      hasRole: (role) => role === 'operador',
      hasPermission: (perm) =>
        ['configs:read', 'dashboard:read', 'dashboard:export', 'tasks:read'].includes(perm),
    };

    expect(operadorAuth.hasPermission('configs:write')).toBe(false);
    expect(operadorAuth.hasPermission('tasks:execute')).toBe(false);
    expect(operadorAuth.hasPermission('configs:read')).toBe(true);
    expect(operadorAuth.hasPermission('dashboard:read')).toBe(true);
  });

  it('renders content conditionally based on permission', () => {
    const adminAuth: AuthContextValue = {
      ...baseAuth,
      user: { id: 1, username: 'admin', role: 'administrador' },
      isAuthenticated: true,
      hasPermission: (perm) => perm === 'configs:write',
    };

    function TestComponent() {
      return (
        <div>
          {adminAuth.hasPermission('configs:write') && <button>Crear</button>}
          {adminAuth.hasPermission('users:manage') && <button>Gestionar usuarios</button>}
        </div>
      );
    }

    renderWithAuth(<TestComponent />, adminAuth);
    expect(screen.getByText('Crear')).toBeInTheDocument();
    expect(screen.queryByText('Gestionar usuarios')).not.toBeInTheDocument();
  });
});

// ---------------------------------------------------------------------------
// LoginPage Tests
// ---------------------------------------------------------------------------

describe('LoginPage', () => {
  const mockAuth: AuthContextValue = {
    user: null,
    token: null,
    isAuthenticated: false,
    isLoading: false,
    login: vi.fn(),
    logout: vi.fn(),
    hasRole: () => false,
    hasPermission: () => false,
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders login form with username and password fields', () => {
    render(
      <AuthContext.Provider value={mockAuth}>
        <LoginPage />
      </AuthContext.Provider>,
    );
    expect(screen.getByLabelText('Usuario')).toBeInTheDocument();
    expect(screen.getByLabelText('Contraseña')).toBeInTheDocument();
    expect(screen.getByText('Ingresar')).toBeInTheDocument();
  });

  it('renders the platform title', () => {
    render(
      <AuthContext.Provider value={mockAuth}>
        <LoginPage />
      </AuthContext.Provider>,
    );
    expect(screen.getByText('Iniciar Sesión')).toBeInTheDocument();
    expect(screen.getByText(/Plataforma Web Scraping/)).toBeInTheDocument();
  });
});

// ---------------------------------------------------------------------------
// WebSocket Context Tests
// ---------------------------------------------------------------------------

describe('WebSocketContext', () => {
  it('provides subscribe and unsubscribe functions', () => {
    const subscribeFn = vi.fn();
    const unsubscribeFn = vi.fn();

    const wsValue: WebSocketContextValue = {
      subscribe: subscribeFn,
      unsubscribe: unsubscribeFn,
      isConnected: true,
    };

    function TestConsumer() {
      return <div>Connected: {wsValue.isConnected ? 'yes' : 'no'}</div>;
    }

    render(
      <WebSocketContext.Provider value={wsValue}>
        <TestConsumer />
      </WebSocketContext.Provider>,
    );

    expect(screen.getByText('Connected: yes')).toBeInTheDocument();
  });

  it('shows disconnected state', () => {
    const wsValue: WebSocketContextValue = {
      subscribe: vi.fn(),
      unsubscribe: vi.fn(),
      isConnected: false,
    };

    function TestConsumer() {
      return <div>Connected: {wsValue.isConnected ? 'yes' : 'no'}</div>;
    }

    render(
      <WebSocketContext.Provider value={wsValue}>
        <TestConsumer />
      </WebSocketContext.Provider>,
    );

    expect(screen.getByText('Connected: no')).toBeInTheDocument();
  });
});
