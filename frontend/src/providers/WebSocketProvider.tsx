/**
 * WebSocket context provider.
 *
 * Manages connection lifecycle to /api/v1/ws/tasks?token={accessToken}.
 * Distributes parsed WsMessage events to subscribed components.
 * Reconnects automatically on disconnect with exponential backoff.
 */

import {
  createContext,
  useCallback,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from 'react';

import { useAuth } from '@/auth/useAuth';
import type { WsMessage } from '@/types';

type Subscriber = (message: WsMessage) => void;

export interface WebSocketContextValue {
  subscribe: (handler: Subscriber) => void;
  unsubscribe: (handler: Subscriber) => void;
  isConnected: boolean;
}

export const WebSocketContext = createContext<WebSocketContextValue | null>(null);

const MAX_RECONNECT_DELAY = 30_000;

export function WebSocketProvider({ children }: { children: ReactNode }) {
  const { token, isAuthenticated } = useAuth();
  const [isConnected, setIsConnected] = useState(false);
  const subscribersRef = useRef<Set<Subscriber>>(new Set());
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectDelayRef = useRef(1000);

  const subscribe = useCallback((handler: Subscriber) => {
    subscribersRef.current.add(handler);
  }, []);

  const unsubscribe = useCallback((handler: Subscriber) => {
    subscribersRef.current.delete(handler);
  }, []);

  useEffect(() => {
    if (!isAuthenticated || !token) {
      wsRef.current?.close();
      wsRef.current = null;
      setIsConnected(false);
      return;
    }

    let cancelled = false;
    let reconnectTimer: ReturnType<typeof setTimeout>;

    function connect() {
      if (cancelled) return;

      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/api/v1/ws/tasks?token=${token}`;
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        if (cancelled) return;
        setIsConnected(true);
        reconnectDelayRef.current = 1000;
      };

      ws.onmessage = (event) => {
        try {
          const message: WsMessage = JSON.parse(event.data);
          subscribersRef.current.forEach((handler) => handler(message));
        } catch {
          // Ignore malformed messages
        }
      };

      ws.onclose = () => {
        if (cancelled) return;
        setIsConnected(false);
        reconnectTimer = setTimeout(() => {
          reconnectDelayRef.current = Math.min(
            reconnectDelayRef.current * 2,
            MAX_RECONNECT_DELAY,
          );
          connect();
        }, reconnectDelayRef.current);
      };

      ws.onerror = () => {
        ws.close();
      };
    }

    connect();

    return () => {
      cancelled = true;
      clearTimeout(reconnectTimer);
      wsRef.current?.close();
      wsRef.current = null;
      setIsConnected(false);
    };
  }, [token, isAuthenticated]);

  const value: WebSocketContextValue = { subscribe, unsubscribe, isConnected };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
}
