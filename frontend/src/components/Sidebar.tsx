
import React, { useEffect, useState } from 'react';
import { Table, Layers, Activity } from 'lucide-react';
// import axios from 'axios'; // We'll just fetch with fetch() for simplicity

interface SidebarProps {
    isConnected: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({ isConnected }) => {
    const [tables, setTables] = useState<string[]>([]);

    useEffect(() => {
        // Fetch schema on mount
        const fetchSchema = async () => {
            try {
                const res = await fetch('http://localhost:8000/api/schema');
                if (res.ok) {
                    const data = await res.json();
                    setTables(data.tables || []);
                }
            } catch (e) {
                console.error("Failed to fetch schema", e);
            }
        };
        fetchSchema();
    }, []);

    return (
        <div className="w-64 bg-slate-950 border-r border-slate-800 flex flex-col h-full text-slate-300">
            <div className="p-4 border-b border-slate-800 flex items-center gap-2">
                <Layers className="text-indigo-500" />
                <h1 className="font-bold text-lg text-slate-100">Antigravirt</h1>
            </div>

            {/* Status */}
            <div className="p-4 border-b border-slate-800">
                <div className="flex items-center gap-2 text-xs font-mono uppercase tracking-wider">
                    <Activity size={14} className={isConnected ? "text-emerald-500" : "text-rose-500"} />
                    <span className={isConnected ? "text-emerald-500" : "text-rose-500"}>
                        {isConnected ? "System Online" : "Disconnected"}
                    </span>
                </div>
            </div>

            {/* Schema Browser */}
            <div className="flex-1 overflow-y-auto p-4">
                <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">Database Schema</h2>
                <div className="space-y-1">
                    {tables.length === 0 && (
                        <div className="text-xs text-slate-600 italic">No tables found (or backend offline)</div>
                    )}

                    {tables.map(table => (
                        <div key={table} className="flex items-center gap-2 p-2 hover:bg-slate-900 rounded cursor-default text-sm group">
                            <Table size={14} className="text-slate-500 group-hover:text-indigo-400" />
                            <span>{table}</span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};
