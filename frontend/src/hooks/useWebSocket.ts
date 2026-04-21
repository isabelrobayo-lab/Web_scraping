/**
 * Hook for subscribing to WebSocket messages by type.
 *
 * Uses the WebSocketProvider context to receive typed events.
 */

import { useContext, useEffect, useRef } from 'react';

import { WebSocketContext } from '@/providers/WebSocketProvider';
import type { WsMessage, WsMessageType } from '@/types';

type MessageHandler = (message: WsMessage) => void;

export function useWebSocket(
  messageType: WsMessageType,
  handler: MessageHandler,
): void {
  const ws = useContext(WebSocketContext);
  const handlerRef = useRef(handler);
  handlerRef.current = handler;

  useEffect(() => {
    if (!ws) return;
    const callback = (msg: WsMessage) => {
      if (msg.type === messageType) {
        handlerRef.current(msg);
      }
    };
    ws.subscribe(callback);
    return () => ws.unsubscribe(callback);
  }, [ws, messageType]);
}
