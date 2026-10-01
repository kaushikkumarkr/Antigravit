<p align="center">
  <img src="https://img.shields.io/badge/python-3.11+-blue.svg" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License MIT">
  <img src="https://img.shields.io/badge/LLM-Local%20First-purple.svg" alt="Local LLM">
  <img src="https://img.shields.io/badge/MCP-Enabled-orange.svg" alt="MCP Enabled">
</p>

# Antigravirt

**Antigravirt** is a privacy-first, local-running AI Data Analyst that transforms natural language questions into SQL queries, executes them against your databases, and visualizes the results — all without your data ever leaving your infrastructure.

<p align="center">
  <img src="img/system/WorkingChat.png" alt="Antigravirt Chat Interface" width="800"/>
</p>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🗣️ **Natural Language to SQL** | Ask questions like "Show me monthly revenue" and get accurate SQL |
| 🔒 **Privacy First** | Runs 100% locally — your data never leaves your infrastructure |
| 📊 **Interactive Visualizations** | Auto-generates Plotly charts for data insights |
| 🔗 **Multi-Source Connectivity** | Connect multiple databases (PostgreSQL, SQLite) via MCP |
| 🤖 **Multi-Agent Architecture** | Powered by LangGraph for robust reasoning and self-correction |
| 🛡️ **Safe Execution** | Read-only permission model (SELECT only) prevents accidents |
| 📡 **Real-time Updates** | WebSocket streaming for live agent progress |
| 🔭 **Full Observability** | Arize Phoenix integration for LLM tracing |

---

## 🖼️ Screenshots

### Chat Interface with Visualization

The chat interface provides a natural conversation experience with inline visualizations:

<p align="center">
  <img src="img/system/WorkingChat.png" alt="Working Chat with Chart" width="700"/>
</p>

### Multi-Source Data Connectivity

Connect to multiple databases and data sources using the Model Context Protocol (MCP):

<p align="center">
  <img src="img/system/DataSourceMcpServers.png" alt="MCP Data Sources" width="700"/>
</p>

<p align="center">
  <img src="img/system/MultipleDataSourceConnection.png" alt="Connected Data Sources" width="700"/>
</p>

### LLM Observability with Arize Phoenix

Full visibility into your AI pipeline with trace analysis:

<p align="center">
  <img src="img/arize/ListofTraces.png" alt="Arize Phoenix - Trace List" width="700"/>
</p>

<p align="center">
  <img src="img/arize/SingleTrace.png" alt="Arize Phoenix - Single Trace" width="700"/>
</p>

### Evaluation Metrics in Phoenix

Custom evaluation metrics (Intent Accuracy, SQL Quality, Faithfulness) are logged directly to Phoenix as span annotations:

<p align="center">
  <img src="img/arize/EvaluationMetrics.png" alt="Arize Phoenix - Evaluation Metrics" width="700"/>
</p>

---

## 🛠️ Tech Stack

| Layer | Technologies |
|-------|--------------|
| **Backend** | Python 3.11, FastAPI, LangGraph, Pydantic, asyncpg |
| **Frontend** | React 18, TypeScript, Tailwind CSS, Plotly.js |
| **Database** | PostgreSQL 15, SQLite (via MCP) |
| **LLM** | Ollama, LM Studio, or Cloud APIs (OpenAI/Gemini) |
| **Protocol** | Model Context Protocol (MCP) for data connectivity |
| **Observability** | Arize Phoenix for LLM tracing |
| **Infrastructure** | Docker Compose |

---

## 🏗️ System Architecture

### Complete System Overview

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': { 'primaryColor': '#6366f1', 'primaryTextColor': '#fff', 'primaryBorderColor': '#4f46e5', 'lineColor': '#94a3b8', 'secondaryColor': '#1e293b', 'tertiaryColor': '#0f172a'}}}%%
flowchart TB
    subgraph CLIENT["🖥️ CLIENT LAYER"]
        direction TB
        UI["React Frontend<br/>━━━━━━━━━━━━━━<br/>• Chat Interface<br/>• Visualization Panel<br/>• Connection Manager"]
    end

    subgraph GATEWAY["🔌 API GATEWAY"]
        direction TB
        REST["REST API<br/>/api/*"]
        WSS["WebSocket Server<br/>/ws/chat"]
    end

    subgraph AGENTS["🤖 LANGGRAPH AGENT ORCHESTRATION"]
        direction TB
        
        subgraph ROUTING["Intent Router"]
            R{{"🧭 Router<br/>Intent Classification"}}
        end
        
        subgraph QUERY_PIPELINE["Data Query Pipeline"]
            direction LR
            ARCH["📐 Architect<br/>Schema Analysis"]
            CODE["✍️ Coder<br/>SQL Generation"]
            EXEC["⚡ Executor<br/>Query Execution"]
        end
        
        subgraph VIZ_PIPELINE["Visualization Pipeline"]
            direction LR
            VIZR{{"📊 Viz Router"}}
            VIZ["🎨 Visualizer<br/>Plotly Generation"]
        end
        
        subgraph ALT_PATHS["Alternative Paths"]
            CHAT["💬 Chat"]
            SCHEMA["📋 Schema"]
            CLARIFY["❓ Clarify"]
        end
        
        FINAL["✅ Final Responder<br/>Response Synthesis"]
    end

    subgraph MCP_LAYER["🔗 MODEL CONTEXT PROTOCOL (MCP)"]
        direction TB
        MGR["MCP Connection Manager<br/>━━━━━━━━━━━━━━━━━<br/>• Schema Caching (60s TTL)<br/>• Connection Pooling<br/>• Dynamic Server Spawning"]
        
        subgraph MCP_SERVERS["MCP Server Fleet"]
            direction LR
            PG["🐘 PostgreSQL<br/>Server<br/>━━━━━━━<br/>• query()<br/>• get_schema()<br/>• list_tables()"]
            SQLITE["📦 SQLite<br/>Server<br/>━━━━━━━<br/>• query()<br/>• get_schema()<br/>• list_tables()"]
            FS["📁 Filesystem<br/>Server<br/>━━━━━━━<br/>• read_file()<br/>• list_dir()<br/>• write_file()"]
        end
    end

    subgraph DATA["🗄️ DATA SOURCES"]
        direction LR
        DB1[("PostgreSQL<br/>Production DB")]
        DB2[("SQLite<br/>Analytics DB")]
        FILES[("Local Files<br/>CSV/JSON")]
    end

    subgraph INTELLIGENCE["🧠 INTELLIGENCE LAYER"]
        direction LR
        LLM["🤖 Local LLM<br/>━━━━━━━━━━<br/>Ollama / LM Studio<br/>qwen2.5:7b/14b"]
        PHOENIX["📊 Arize Phoenix<br/>━━━━━━━━━━━━<br/>LLM Observability<br/>Trace Analysis"]
    end

    %% Client to Gateway
    UI <-->|"WebSocket<br/>Real-time"| WSS
    UI -->|"HTTP<br/>REST"| REST

    %% Gateway to Agents
    WSS --> R
    REST --> MGR

    %% Router branching
    R -->|"DATA_QUERY"| ARCH
    R -->|"GENERAL_CHAT"| CHAT
    R -->|"SCHEMA_QUESTION"| SCHEMA
    R -->|"AMBIGUOUS"| CLARIFY

    %% Query Pipeline
    ARCH --> CODE --> EXEC
    EXEC --> VIZR
    VIZR -->|"Needs Chart"| VIZ
    VIZR -->|"Text Only"| FINAL
    VIZ --> FINAL

    %% Alt paths to output
    CHAT --> FINAL
    SCHEMA --> FINAL
    CLARIFY --> FINAL

    %% Executor to MCP
    EXEC --> MGR
    MGR --> PG & SQLITE & FS

    %% MCP to Data
    PG --> DB1
    SQLITE --> DB2
    FS --> FILES

    %% LLM connections
    R -.->|"Inference"| LLM
    ARCH -.->|"Inference"| LLM
    CODE -.->|"Inference"| LLM
    VIZ -.->|"Inference"| LLM
    FINAL -.->|"Inference"| LLM

    %% Observability
    R -.->|"Trace"| PHOENIX
    ARCH -.->|"Trace"| PHOENIX
    CODE -.->|"Trace"| PHOENIX
    EXEC -.->|"Trace"| PHOENIX
    VIZ -.->|"Trace"| PHOENIX

    %% Styling
    classDef client fill:#3b82f6,stroke:#2563eb,color:#fff
    classDef gateway fill:#8b5cf6,stroke:#7c3aed,color:#fff
    classDef agent fill:#10b981,stroke:#059669,color:#fff
    classDef mcp fill:#f59e0b,stroke:#d97706,color:#fff
    classDef data fill:#6366f1,stroke:#4f46e5,color:#fff
    classDef intel fill:#ec4899,stroke:#db2777,color:#fff

    class UI client
    class REST,WSS gateway
    class R,ARCH,CODE,EXEC,VIZR,VIZ,CHAT,SCHEMA,CLARIFY,FINAL agent
    class MGR,PG,SQLITE,FS mcp
    class DB1,DB2,FILES data
    class LLM,PHOENIX intel
```

---

### 🔗 MCP (Model Context Protocol) Deep Dive

The MCP layer provides a **unified interface** for connecting to heterogeneous data sources:

```mermaid
%%{init: {'theme': 'dark'}}%%
flowchart LR
    subgraph AGENT["Agent Layer"]
        EXEC["Executor Node"]
    end

    subgraph MCP_MANAGER["MCP Connection Manager"]
        direction TB
        CACHE["Schema Cache<br/>TTL: 60s"]
        REGISTRY["Connection Registry<br/>connections.json"]
        SPAWNER["Server Spawner<br/>subprocess.Popen"]
    end

    subgraph SERVERS["MCP Server Instances"]
        direction TB
        
        subgraph PG_SERVER["PostgreSQL MCP Server"]
            PG_QUERY["query(sql) → JSON"]
            PG_SCHEMA["get_schema() → DDL"]
            PG_TABLES["list_tables() → [str]"]
        end
        
        subgraph SQLITE_SERVER["SQLite MCP Server"]
            SQ_QUERY["query(sql) → JSON"]
            SQ_SCHEMA["get_schema() → DDL"]
            SQ_TABLES["list_tables() → [str]"]
        end
        
        subgraph FS_SERVER["Filesystem MCP Server"]
            FS_READ["read_file(path) → str"]
            FS_LIST["list_directory() → [str]"]
            FS_WRITE["write_file(path, data)"]
        end
    end

    subgraph TRANSPORT["stdio Transport"]
        STDIN["stdin (JSON-RPC)"]
        STDOUT["stdout (JSON-RPC)"]
    end

    EXEC -->|"get_tool_result()"| MCP_MANAGER
    MCP_MANAGER -->|"spawn if needed"| SERVERS
    SERVERS <-->|"JSON-RPC 2.0"| TRANSPORT

    style CACHE fill:#22c55e,stroke:#16a34a,color:#fff
    style REGISTRY fill:#3b82f6,stroke:#2563eb,color:#fff
    style SPAWNER fill:#f59e0b,stroke:#d97706,color:#fff
```

#### MCP Server Tools Reference

| Server | Tool | Input | Output | Description |
|--------|------|-------|--------|-------------|
| **PostgreSQL** | `query` | `sql: str` | `JSON` | Execute read-only SQL (SELECT only) |
| **PostgreSQL** | `get_schema` | `table_name?: str` | `DDL string` | Get table/column definitions |
| **PostgreSQL** | `list_tables` | — | `List[str]` | List all public tables |
| **SQLite** | `query` | `sql: str` | `JSON` | Execute read-only SQL |
| **SQLite** | `get_schema` | `table_name?: str` | `DDL string` | Get schema from sqlite_master |
| **SQLite** | `list_tables` | — | `List[str]` | List all tables |
| **Filesystem** | `read_file` | `path: str` | `str` | Read file (max 10MB, sandboxed) |
| **Filesystem** | `list_directory` | `path?: str` | `List[str]` | List directory contents |
| **Filesystem** | `write_file` | `path, data` | `bool` | Write to file (sandboxed) |

---

### 🔭 Arize Phoenix Observability Architecture

Full LLM observability with distributed tracing:

```mermaid
%%{init: {'theme': 'dark'}}%%
flowchart TB
    subgraph APP["Application"]
        direction TB
        OTEL["OpenTelemetry<br/>Instrumentor"]
        AGENTS["LangGraph<br/>Agents"]
    end

    subgraph PHOENIX["Arize Phoenix (localhost:6006)"]
        direction TB
        COLLECTOR["OTLP Collector<br/>gRPC/HTTP"]
        
        subgraph STORAGE["Trace Storage"]
            TRACES["Trace Store"]
            SPANS["Span Store"]
        end
        
        subgraph ANALYSIS["Analysis Engine"]
            LATENCY["Latency<br/>Analysis"]
            TOKENS["Token<br/>Counting"]
            EVALS["LLM<br/>Evaluations"]
        end
        
        subgraph UI["Phoenix UI"]
            TREE["Trace Tree<br/>Visualization"]
            METRICS["Performance<br/>Metrics"]
            INSPECT["I/O<br/>Inspector"]
        end
    end

    OTEL -->|"Auto-instrument"| AGENTS
    AGENTS -->|"OTLP Export"| COLLECTOR
    COLLECTOR --> TRACES & SPANS
    TRACES --> LATENCY & TOKENS & EVALS
    LATENCY --> TREE
    TOKENS --> METRICS
    EVALS --> INSPECT

    style OTEL fill:#6366f1,stroke:#4f46e5,color:#fff
    style COLLECTOR fill:#22c55e,stroke:#16a34a,color:#fff
    style UI fill:#f59e0b,stroke:#d97706,color:#000
```

#### Trace Structure Example

```
📊 Query: "Show me sales by status as a bar chart"
│
├── 🧭 Router [12ms] ─────────────────────────────────────────────────
│   ├── Input:  "Show me sales by status as a bar chart"
│   ├── Output: {"intent": "DATA_QUERY", "confidence": 0.95}
│   └── Tokens: 156 in / 42 out
│
├── 📐 Architect [8ms] ───────────────────────────────────────────────
│   ├── Input:  Schema context + Question
│   ├── Output: {"tables": ["orders"], "strategy": "aggregate"}
│   └── Tokens: 892 in / 67 out
│
├── ✍️ Coder [15ms] ──────────────────────────────────────────────────
│   ├── Input:  Query strategy + Schema
│   ├── Output: "SELECT status, COUNT(*) FROM orders GROUP BY status"
│   └── Tokens: 1024 in / 89 out
│
├── ⚡ Executor [3ms] ─────────────────────────────────────────────────
│   ├── Input:  SQL Query
│   ├── Output: [{"status": "completed", "count": 156}, ...]
│   └── DB Latency: 2.1ms
│
├── 🎨 Visualizer [18ms] ─────────────────────────────────────────────
│   ├── Input:  Query result + Chart request
│   ├── Output: Plotly JSON specification
│   └── Tokens: 512 in / 234 out
│
└── ✅ Final Responder [11ms] ────────────────────────────────────────
    ├── Input:  Result + Visualization
    ├── Output: "Here is the sales breakdown by order status..."
    └── Tokens: 445 in / 112 out

Total: 67ms | Total Tokens: 3,573
```

#### Key Observability Metrics

| Metric | Description | Typical Value |
|--------|-------------|---------------|
| **Trace Duration** | End-to-end latency | 60-90s (local LLM) |
| **LLM Latency** | Per-inference time | 10-20s per call |
| **Token Usage** | Input + Output tokens | 2,000-5,000 per query |
| **MCP Latency** | Database query time | 1-50ms |
| **Error Rate** | Failed queries | < 5% |

---

### 🔐 Security Architecture

```mermaid
%%{init: {'theme': 'dark'}}%%
flowchart TB
    subgraph BOUNDARIES["Security Boundaries"]
        direction TB
        
        subgraph SQL_GUARD["SQL Injection Prevention"]
            VALIDATOR["SQL Validator<br/>━━━━━━━━━━<br/>✓ SELECT only<br/>✗ INSERT/UPDATE/DELETE<br/>✗ DROP/ALTER/TRUNCATE<br/>✗ Multiple statements"]
        end
        
        subgraph FS_SANDBOX["Filesystem Sandbox"]
            SANDBOX["Path Validator<br/>━━━━━━━━━━<br/>✓ Within root_dir<br/>✗ Path traversal (../)<br/>✗ Absolute paths<br/>✗ Symlink escape"]
        end
        
        subgraph DATA_PRIVACY["Data Privacy"]
            LOCAL["Local Processing<br/>━━━━━━━━━━<br/>✓ 100% on-premise<br/>✓ No external API calls<br/>✓ Your data, your control"]
        end
    end
    
    INPUT["User Input"] --> VALIDATOR
    VALIDATOR -->|"Valid"| EXEC["Execute"]
    VALIDATOR -->|"Invalid"| REJECT["Reject"]
    
    FILE_REQ["File Request"] --> SANDBOX
    SANDBOX -->|"Safe Path"| READ["Read File"]
    SANDBOX -->|"Unsafe"| DENY["Deny Access"]
    
    LLM_REQ["LLM Request"] --> LOCAL
    LOCAL --> OLLAMA["Ollama (localhost)"]

    style VALIDATOR fill:#22c55e,stroke:#16a34a,color:#fff
    style SANDBOX fill:#3b82f6,stroke:#2563eb,color:#fff
    style LOCAL fill:#8b5cf6,stroke:#7c3aed,color:#fff
    style REJECT fill:#ef4444,stroke:#dc2626,color:#fff
    style DENY fill:#ef4444,stroke:#dc2626,color:#fff
```

---

### 📊 Performance Characteristics

| Component | Latency | Throughput | Notes |
|-----------|---------|------------|-------|
| **WebSocket RTT** | < 5ms | 1000 msg/s | Real-time bidirectional |
| **Router Classification** | 10-15s | — | Local LLM inference |
| **SQL Generation** | 15-20s | — | Complex reasoning |
| **Query Execution** | 1-50ms | — | Depends on query complexity |
| **Visualization** | 10-15s | — | Plotly spec generation |
| **Schema Cache** | < 1ms | — | In-memory, 60s TTL |

> **Note:** Latencies shown are for local LLM (qwen2.5:7b). Cloud LLMs (GPT-4, Claude) reduce inference time to 1-3s per call.

---

## 🧪 Evaluation & Benchmarking

Antigravirt includes a **production-grade evaluation framework** for systematically measuring AI system performance.

### Evaluation Metrics

| Metric | Description | Method |
|--------|-------------|--------|
| **Intent Accuracy** | Correct routing classification | Exact match vs. expected intent |
| **SQL Quality** | Semantic equivalence of generated SQL | LLM-as-a-judge comparison |
| **Faithfulness** | Response grounded in data (no hallucinations) | LLM-as-a-judge verification |

### Running Evaluations

```bash
# Run evaluation with Phoenix integration
python scripts/phoenix_experiment.py --experiment-name "baseline_v1" --limit 5

# Full evaluation (15 test cases)
python scripts/phoenix_experiment.py --experiment-name "full_eval"
```

### Evaluation Results in Phoenix

All evaluation metrics are logged directly to Arize Phoenix as **span annotations**:

- **Project Header**: Shows aggregate metrics (μ intent_accuracy, μ sql_quality)
- **Traces Table**: Annotations column with per-trace scores
- **Trace Details**: Full breakdown with label, score, and explanation

### Sample Baseline Results

| Metric | Score |
|--------|-------|
| Intent Accuracy | **100%** |
| SQL Quality | **83%** |
| Faithfulness | **100%** |

> These results demonstrate robust routing and response grounding, with SQL generation showing room for optimization on complex join queries.


## 📦 Project Structure

```
antigravirt/
├── backend/                 # FastAPI + LangGraph Agents
│   ├── agents/              # LangGraph nodes and prompts
│   │   ├── nodes/           # Router, Architect, Coder, Executor, etc.
│   │   ├── prompts/         # System prompts for each agent
│   │   ├── graph.py         # LangGraph workflow definition
│   │   └── llm.py           # LLM configuration (Ollama/OpenAI/Gemini)
│   ├── api/                 # FastAPI routes and WebSocket handlers
│   ├── mcp/                 # Model Context Protocol implementation
│   │   ├── manager.py       # Connection manager with caching
│   │   ├── servers/         # PostgreSQL, SQLite, Filesystem servers
│   │   └── tools.py         # MCP tool adapters
│   ├── observability/       # Arize Phoenix instrumentation
│   └── utils/               # Database and helper utilities
├── frontend/                # React Application
│   └── src/
│       ├── components/      # ChatPanel, Sidebar, ConnectionManager
│       ├── hooks/           # useWebSocket custom hook
│       └── types/           # TypeScript interfaces
├── infrastructure/          # Docker & Database Setup
│   ├── init.sql             # Database schema
│   └── docker-compose.yml   # PostgreSQL + Phoenix containers
├── img/                     # Documentation screenshots
│   ├── arize/               # Phoenix observability screenshots
│   └── system/              # UI screenshots
└── tests/                   # Test suite
```

---

## ⚡ Quick Start

### Prerequisites

- Python 3.11 or 3.12
- Node.js 18+
- Docker & Docker Compose
- Ollama (recommended) or LM Studio

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/kaushikkumarkr/Antigravit.git
cd antigravirt

# 2. Backend setup
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Environment configuration
cp .env.example .env
# Add your Google AI Studio API key to GOOGLE_API_KEY in .env

# 4. Start database (PostgreSQL)
docker-compose -f infrastructure/docker-compose.yml up -d

# 5. Seed sample data
python infrastructure/seed_data.py

# 6. Start backend
uvicorn backend.main:app --reload --port 8000

# 7. Start frontend (new terminal)
cd frontend
npm install
npm run dev
```

### Access the Application

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:5173 |
| **Backend API** | http://localhost:8000 |
| **API Docs** | http://localhost:8000/docs |
| **Phoenix Observability** | http://localhost:6006 |

---

## 🔭 Observability with Arize Phoenix

Antigravirt includes built-in LLM observability using [Arize Phoenix](https://github.com/Arize-ai/phoenix).

### Features

- **Trace Tree Visualization** — See the full execution flow for each query
- **Token Usage Tracking** — Monitor input/output tokens per LLM call
- **Latency Analysis** — Identify slow nodes in your agent pipeline
- **LLM I/O Inspection** — View exact prompts and responses

### Trace Structure

Each query generates a trace tree:

```
Query: "Show me order count by status as a bar chart"
└── Router (LLM) → DATA_QUERY
    └── Architect (LLM) → [orders]
        └── Coder (LLM) → SQL Query
            └── Executor (MCP) → Query Result
                └── Viz Router → Needs Visualization
                    └── Visualizer (LLM) → Plotly Chart
                        └── Final Responder (LLM) → Answer
```

---

## 🔗 API Reference

### REST Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `GET` | `/api/schema` | Get database schema from all connections |
| `POST` | `/api/query` | Execute a natural language query |
| `GET` | `/api/connections` | List all MCP connections |
| `POST` | `/api/connections` | Add a new data connection |
| `DELETE` | `/api/connections/{id}` | Remove a connection |

### WebSocket

```
ws://localhost:8000/ws/chat
```

**Message Format:**
```json
// Send
{"question": "How many customers are there?"}

// Receive (agent_update)
{"type": "agent_update", "payload": {"agent": "router", "status": "completed"}}

// Receive (final_response)
{"type": "final_response", "payload": {"answer": "...", "visualization": {...}}}
```

---

## 🧪 Example Queries

```
# Simple data queries
"How many customers are there?"
"What is the total revenue from all orders?"
"Show me the top 5 products by price"

# Visualization queries
"Show me order count by status as a bar chart"
"Show me sales distribution as a pie chart"

# Schema exploration
"What tables are in the database?"
"Describe the customers table"
```

---

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines before submitting a pull request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Built with ❤️ by <a href="https://github.com/kaushikkumarkr">Kaushik Kumar</a>
</p>
