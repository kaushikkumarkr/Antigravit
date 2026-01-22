
export interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: number;
    visualization?: any; // Plotly JSON
    status?: 'thinking' | 'completed' | 'error';
    agent?: string; // which agent is working
}

export interface WebSocketMessage {
    type: 'agent_update' | 'final_response' | 'error';
    payload: any;
}

export interface AgentUpdatePayload {
    agent: string;
    status: string;
    message: string;
}

export interface FinalResponsePayload {
    answer: string;
    visualization?: any;
}

export interface SchemaTable {
    name: string;
    columns?: string[];
}
