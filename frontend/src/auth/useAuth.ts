/**
 * Hook for accessing auth context.
 *
 * Returns user, token, login/logout functions, and RBAC helpers.
 * Must be used within an AuthProvider.
 */

import { useContext } from 'react';

import { AuthContext, type AuthContextValue } from '@/auth/AuthContext';

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
