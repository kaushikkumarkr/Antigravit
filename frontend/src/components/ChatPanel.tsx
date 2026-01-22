
import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2 } from 'lucide-react';
import Plot from 'react-plotly.js';
import type { Message } from '../types';
import clsx from 'clsx';

interface ChatPanelProps {
    messages: Message[];
    onSendMessage: (msg: string) => void;
    isProcessing: boolean;
}

export const ChatPanel: React.FC<ChatPanelProps> = ({ messages, onSendMessage, isProcessing }) => {
    const [input, setInput] = useState('');
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [messages]);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || isProcessing) return;
        onSendMessage(input);
        setInput('');
    };

    return (
        <div className="flex flex-col h-full bg-slate-900 text-slate-100">
            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-6">
                {messages.length === 0 && (
                    <div className="flex flex-col items-center justify-center h-full text-slate-500">
                        <Bot size={48} className="mb-4 opacity-50" />
                        <p>Ready to help. Ask me about your data!</p>
                    </div>
                )}

                {messages.map((msg) => (
                    <div
                        key={msg.id}
                        className={clsx(
                            "flex gap-3 max-w-3xl mx-auto",
                            msg.role === 'user' ? "flex-row-reverse" : "flex-row"
                        )}
                    >
                        <div className={clsx(
                            "w-8 h-8 rounded-full flex items-center justify-center shrink-0",
                            msg.role === 'user' ? "bg-indigo-600" : "bg-emerald-600"
                        )}>
                            {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
                        </div>

                        <div className={clsx(
                            "p-4 rounded-lg text-sm leading-relaxed",
                            msg.visualization ? "max-w-[90%] min-w-[550px]" : "max-w-[80%]",
                            msg.role === 'user'
                                ? "bg-indigo-600/10 border border-indigo-500/20 text-indigo-100"
                                : "bg-slate-800 border border-slate-700 text-slate-200"
                        )}>
                            {/* Agent Status Indicator */}
                            {msg.status === 'thinking' && (
                                <div className="flex items-center gap-2 text-xs text-emerald-400 mb-2 font-mono">
                                    <Loader2 size={12} className="animate-spin" />
                                    <span>{msg.agent ? `${msg.agent} is working...` : "Thinking..."}</span>
                                </div>
                            )}

                            <div className="whitespace-pre-wrap">{msg.content}</div>

                            {/* Inline Visualization */}
                            {msg.visualization && (
                                <div className="mt-4 p-4 bg-slate-950 rounded-lg border border-slate-700 min-w-[500px] max-w-[800px]">
                                    <Plot
                                        data={msg.visualization.data}
                                        layout={{
                                            paper_bgcolor: '#0f172a',
                                            plot_bgcolor: '#0f172a',
                                            font: {
                                                color: '#e2e8f0',
                                                family: 'Inter, sans-serif',
                                                size: 12
                                            },
                                            ...msg.visualization.layout,
                                            autosize: true,
                                            margin: { t: 50, r: 40, b: 80, l: 80 },
                                            height: 400
                                        }}
                                        useResizeHandler={true}
                                        style={{ width: '100%', minWidth: '450px', height: '400px' }}
                                        config={{
                                            responsive: true,
                                            displayModeBar: true,
                                            displaylogo: false,
                                            modeBarButtonsToRemove: ['lasso2d', 'select2d']
                                        }}
                                    />
                                </div>
                            )}
                        </div>
                    </div>
                ))}
                <div ref={scrollRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 border-t border-slate-800 bg-slate-900/50 backdrop-blur">
                <form onSubmit={handleSubmit} className="max-w-3xl mx-auto relative">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        disabled={isProcessing}
                        placeholder="Ask a question about your database..."
                        className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 pr-12 text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all disabled:opacity-50"
                    />
                    <button
                        type="submit"
                        disabled={!input.trim() || isProcessing}
                        className="absolute right-2 top-2 p-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg disabled:opacity-0 transition-all shadow-lg shadow-indigo-500/20"
                    >
                        <Send size={18} />
                    </button>
                </form>
            </div>
        </div>
    );
};
