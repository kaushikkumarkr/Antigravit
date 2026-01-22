
import React, { useState, useEffect } from 'react';
import { Plus, Trash2, Database, Folder, HardDrive, X, ArrowLeft } from 'lucide-react';
import type { ConnectionConfig } from '../../types/connection';

interface ConnectionManagerProps {
    onBack: () => void;
}

const ConnectionIcon = ({ type }: { type: string }) => {
    switch (type) {
        case 'postgres': return <Database className="text-blue-400" size={20} />;
        case 'sqlite': return <HardDrive className="text-green-400" size={20} />;
        case 'filesystem': return <Folder className="text-yellow-400" size={20} />;
        default: return <Database className="text-slate-400" size={20} />;
    }
};

export const ConnectionManager: React.FC<ConnectionManagerProps> = ({ onBack }) => {
    const [connections, setConnections] = useState<ConnectionConfig[]>([]);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [isLoading, setIsLoading] = useState(true);

    const fetchConnections = async () => {
        try {
            const res = await fetch('http://localhost:8000/api/connections');
            if (res.ok) {
                const data = await res.json();
                setConnections(data);
            }
        } catch (e) {
            console.error("Failed to fetch connections", e);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchConnections();
    }, []);

    const handleDelete = async (id: string) => {
        if (!confirm("Are you sure you want to remove this connection?")) return;
        try {
            await fetch(`http://localhost:8000/api/connections/${id}`, { method: 'DELETE' });
            fetchConnections();
        } catch (e) {
            console.error(e);
        }
    };

    return (
        <div className="p-8 h-full bg-slate-900 text-slate-100 overflow-y-auto">
            <div className="max-w-4xl mx-auto">
                <div className="flex justify-between items-center mb-8">
                    <div className="flex items-center gap-4">
                        <button onClick={onBack} className="p-2 hover:bg-slate-800 rounded-full transition-colors md:hidden">
                            <ArrowLeft size={24} />
                        </button>
                        <div>
                            <h1 className="text-2xl font-bold mb-2">Data Sources</h1>
                            <p className="text-slate-400">Manage your database and filesystem connections.</p>
                        </div>
                    </div>
                    <button
                        onClick={() => setIsModalOpen(true)}
                        className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
                    >
                        <Plus size={18} /> Add Connection
                    </button>
                </div>

                {isLoading ? (
                    <div className="text-center py-12 text-slate-500">Loading...</div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {connections.map(conn => (
                            <div key={conn.id} className="bg-slate-800 border border-slate-700 rounded-xl p-6 hover:border-slate-600 transition-all">
                                <div className="flex justify-between items-start mb-4">
                                    <div className="flex items-center gap-3">
                                        <div className="p-2 bg-slate-900 rounded-lg">
                                            <ConnectionIcon type={conn.type} />
                                        </div>
                                        <div>
                                            <h3 className="font-semibold">{conn.name}</h3>
                                            <span className="text-xs text-slate-500 uppercase tracking-wider">{conn.type}</span>
                                        </div>
                                    </div>
                                    <button
                                        onClick={() => handleDelete(conn.id)}
                                        className="text-slate-500 hover:text-rose-500 transition-colors p-2"
                                    >
                                        <Trash2 size={18} />
                                    </button>
                                </div>
                                <div className="text-sm text-slate-400 font-mono bg-slate-900 rounded p-3 overflow-x-auto">
                                    {conn.type === 'postgres' && (
                                        <>
                                            <div>Host: {conn.params.host}:{conn.params.port}</div>
                                            <div>DB: {conn.params.dbname}</div>
                                        </>
                                    )}
                                    {conn.type === 'sqlite' && (
                                        <div>Path: {conn.params.path}</div>
                                    )}
                                    {conn.type === 'filesystem' && (
                                        <div>Root: {conn.params.root_dir}</div>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {isModalOpen && (
                <AddConnectionModal
                    onClose={() => setIsModalOpen(false)}
                    onSuccess={() => { setIsModalOpen(false); fetchConnections(); }}
                />
            )}
        </div>
    );
};

interface AddConnectionModalProps {
    onClose: () => void;
    onSuccess: () => void;
}

const AddConnectionModal: React.FC<AddConnectionModalProps> = ({ onClose, onSuccess }) => {
    const [type, setType] = useState<'postgres' | 'sqlite' | 'filesystem'>('postgres');
    const [name, setName] = useState('');
    const [params, setParams] = useState<any>({});
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSubmitting(true);

        try {
            const id = name.toLowerCase().replace(/[^a-z0-9]/g, '-');
            const body = {
                id,
                name,
                type,
                params: { ...params }
            };

            // Set defaults if empty
            if (type === 'postgres') {
                if (!body.params.port) body.params.port = 5432;
                if (!body.params.host) body.params.host = 'localhost';
            }

            const res = await fetch('http://localhost:8000/api/connections', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });

            if (res.ok) {
                onSuccess();
            } else {
                alert("Failed to add connection");
            }
        } catch (e) {
            console.error(e);
            alert("Error adding connection");
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-slate-900 border border-slate-700 rounded-xl w-full max-w-lg shadow-2xl overflow-hidden">
                <div className="flex justify-between items-center p-6 border-b border-slate-800">
                    <h2 className="text-xl font-bold">Add Data Source</h2>
                    <button onClick={onClose} className="text-slate-400 hover:text-white">
                        <X size={24} />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="p-6 space-y-4">
                    <div className="space-y-2">
                        <label className="text-sm font-medium text-slate-300">Type</label>
                        <div className="grid grid-cols-3 gap-2">
                            {(['postgres', 'sqlite', 'filesystem'] as const).map(t => (
                                <button
                                    key={t}
                                    type="button"
                                    onClick={() => setType(t)}
                                    className={`p-3 rounded-lg border text-sm capitalize transition-all ${type === t
                                        ? 'bg-indigo-600 border-indigo-500 text-white'
                                        : 'bg-slate-800 border-slate-700 text-slate-400 hover:border-slate-600'
                                        }`}
                                >
                                    {t}
                                </button>
                            ))}
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-slate-300 mb-1">Name</label>
                        <input
                            required
                            className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-white focus:ring-2 focus:ring-indigo-500 outline-none"
                            placeholder="My Database"
                            value={name}
                            onChange={e => setName(e.target.value)}
                        />
                    </div>

                    {type === 'postgres' && (
                        <div className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-slate-300 mb-1">Host</label>
                                    <input className="input-field" placeholder="localhost" value={params.host || ''} onChange={e => setParams({ ...params, host: e.target.value })} />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-slate-300 mb-1">Port</label>
                                    <input className="input-field" placeholder="5432" type="number" value={params.port || ''} onChange={e => setParams({ ...params, port: parseInt(e.target.value) })} />
                                </div>
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-slate-300 mb-1">User</label>
                                    <input className="input-field" placeholder="postgres" value={params.user || ''} onChange={e => setParams({ ...params, user: e.target.value })} />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-slate-300 mb-1">Password</label>
                                    <input className="input-field" type="password" placeholder="••••••" value={params.password || ''} onChange={e => setParams({ ...params, password: e.target.value })} />
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-1">Database Name</label>
                                <input className="input-field" placeholder="analytics_db" value={params.dbname || ''} onChange={e => setParams({ ...params, dbname: e.target.value })} />
                            </div>
                        </div>
                    )}

                    {type === 'sqlite' && (
                        <div>
                            <label className="block text-sm font-medium text-slate-300 mb-1">Database Path</label>
                            <input
                                className="input-field"
                                placeholder="/path/to/db.sqlite"
                                value={params.path || ''}
                                onChange={e => setParams({ ...params, path: e.target.value })}
                            />
                        </div>
                    )}

                    {type === 'filesystem' && (
                        <div>
                            <label className="block text-sm font-medium text-slate-300 mb-1">Root Directory</label>
                            <input
                                className="input-field"
                                placeholder="/path/to/data"
                                value={params.root_dir || ''}
                                onChange={e => setParams({ ...params, root_dir: e.target.value })}
                            />
                            <p className="text-xs text-slate-500 mt-1">Agents will be restricted to this directory.</p>
                        </div>
                    )}

                    <div className="pt-4 flex justify-end gap-3">
                        <button
                            type="button"
                            onClick={onClose}
                            className="px-4 py-2 text-slate-300 hover:text-white transition-colors"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={isSubmitting}
                            className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-lg font-medium transition-colors disabled:opacity-50"
                        >
                            {isSubmitting ? 'Adding...' : 'Add Connection'}
                        </button>
                    </div>
                </form>
            </div>

            <style>{`
                .input-field {
                    width: 100%;
                    background-color: rgb(30 41 59);
                    border: 1px solid rgb(51 65 85);
                    border-radius: 0.5rem;
                    padding: 0.625rem;
                    color: white;
                    outline: none;
                }
                .input-field:focus {
                    ring-width: 2px;
                    ring-color: rgb(99 102 241);
                }
            `}</style>
        </div>
    );
};
