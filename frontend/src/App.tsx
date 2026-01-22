
import { useState, useCallback } from 'react';
import { Sidebar } from './components/Sidebar';
import { ChatPanel } from './components/ChatPanel';
import { ConnectionManager } from './components/connections/ConnectionManager';

import { useWebSocket } from './hooks/useWebSocket';
import type { Message } from './types';
import { Toaster, toast } from 'sonner';


function App() {
  const wsUrl = `${import.meta.env.VITE_WS_URL || 'ws://localhost:8000'}/ws/chat`;
  const [messages, setMessages] = useState<Message[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentView, setCurrentView] = useState<'chat' | 'sources'>('chat');

  const handleMessage = useCallback((message: any) => {
    if (message.type === 'agent_update') {
      const { agent, message: msgContent } = message.payload;
      setMessages(prev => {
        const last = prev[prev.length - 1];
        if (last && last.role === 'assistant' && last.status === 'thinking') {
          return [
            ...prev.slice(0, -1),
            { ...last, content: `${last.content}\n> ${msgContent}`, agent: agent }
          ];
        } else {
          // Note: In a real app we might want to ensure we target the right message ID
          return prev;
        }
      });
    }

    if (message.type === 'final_response') {
      const { answer, visualization } = message.payload;
      setIsProcessing(false);

      setMessages(prev => {
        const last = prev[prev.length - 1];
        if (last && last.role === 'assistant') {
          return [
            ...prev.slice(0, -1),
            {
              ...last,
              content: answer,
              status: 'completed',
              visualization: visualization
            }
          ];
        }
        return prev;
      });
    }

    if (message.type === 'error') {
      setIsProcessing(false);
      setMessages(prev => {
        const last = prev[prev.length - 1];
        if (last && last.role === 'assistant') {
          return [
            ...prev.slice(0, -1),
            { ...last, content: `Error: ${message.payload.message}`, status: 'error' }
          ];
        }
        return prev;
      });
      toast.error(message.payload.message || "An error occurred");
    }
  }, []);

  const { isConnected, sendMessage } = useWebSocket(wsUrl, handleMessage);

  const handleSendMessage = (text: string) => {
    console.log('[DEBUG] handleSendMessage called with:', text);
    console.log('[DEBUG] isConnected:', isConnected);

    // Add User Message
    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: Date.now()
    };

    // Add Assistant Placeholder
    const assistantMsg: Message = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: "Thinking...",
      status: 'thinking',
      timestamp: Date.now()
    };

    setMessages(prev => [...prev, userMsg, assistantMsg]);
    setIsProcessing(true);
    console.log('[DEBUG] About to call sendMessage');
    sendMessage(text);
    console.log('[DEBUG] sendMessage called');
  };

  return (
    <div className="flex h-screen bg-slate-900 overflow-hidden">
      {/* Sidebar */}
      <Sidebar
        isConnected={isConnected}
        currentView={currentView}
        onNavigate={setCurrentView}
      />
      <Toaster position="top-right" theme="dark" />

      {/* Main Content */}
      <div className="flex-1 overflow-hidden h-full">
        {currentView === 'chat' ? (
          <ChatPanel
            messages={messages}
            onSendMessage={handleSendMessage}
            isProcessing={isProcessing}
          />
        ) : (
          <ConnectionManager onBack={() => setCurrentView('chat')} />
        )}
      </div>
    </div>
  );
}

export default App;
