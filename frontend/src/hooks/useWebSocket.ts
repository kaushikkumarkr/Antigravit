
import { useState, useEffect, useRef, useCallback } from 'react';
import type { WebSocketMessage } from '../types';

interface UseWebSocketReturn {
    isConnected: boolean;
    sendMessage: (question: string) => void;
    lastMessage: WebSocketMessage | null;
}

export const useWebSocket = (url: string, onMessage?: (msg: WebSocketMessage) => void): Omit<UseWebSocketReturn, 'lastMessage'> => {
    const [isConnected, setIsConnected] = useState(false);
    const wsRef = useRef<WebSocket | null>(null);
    const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
    const onMessageRef = useRef(onMessage);

    // Keep the ref updated with the latest callback
    useEffect(() => {
        onMessageRef.current = onMessage;
    }, [onMessage]);

    const connect = useCallback(() => {
        // Avoid duplicate connections
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            return;
        }

        try {
            console.log('Attempting WebSocket connection to:', url);
            const ws = new WebSocket(url);

            ws.onopen = () => {
                console.log('WS Connected');
                setIsConnected(true);
                if (reconnectTimeoutRef.current) {
                    clearTimeout(reconnectTimeoutRef.current);
                    reconnectTimeoutRef.current = null;
                }
            };

            ws.onclose = (event) => {
                console.log('WS Disconnected', event.code, event.reason);
                setIsConnected(false);
                wsRef.current = null;
                // Reconnect after 3 seconds
                reconnectTimeoutRef.current = setTimeout(connect, 3000);
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    // Use the ref to call the latest callback
                    if (onMessageRef.current) {
                        onMessageRef.current(data);
                    }
                } catch (e) {
                    console.error("Failed to parse WS message", e);
                }
            };

            ws.onerror = (err) => {
                console.error("WS Error", err);
                // Don't close here - let onclose handle it
            };

            wsRef.current = ws;
        } catch (e) {
            console.error("Connection failed", e);
            reconnectTimeoutRef.current = setTimeout(connect, 3000);
        }
    }, [url]); // Only depend on url, not onMessage

    useEffect(() => {
        connect();
        return () => {
            if (wsRef.current) {
                wsRef.current.close();
                wsRef.current = null;
            }
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
                reconnectTimeoutRef.current = null;
            }
        };
    }, [connect]);

    const sendMessage = useCallback((question: string) => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            console.log('Sending message:', question);
            wsRef.current.send(JSON.stringify({ question }));
        } else {
            console.error("WebSocket not connected, readyState:", wsRef.current?.readyState);
        }
    }, []);

    return { isConnected, sendMessage };
};
