
export interface ConnectionParams {
    host?: string;
    port?: number;
    user?: string;
    password?: string;
    dbname?: string;
    path?: string;
    root_dir?: string;
}

export interface ConnectionConfig {
    id: string;
    type: 'postgres' | 'sqlite' | 'filesystem';
    name: string;
    params: ConnectionParams;
}
