
#!/bin/bash

# Activate Virtual Environment
source .venv/bin/activate

# Start Uvicorn
echo "🚀 Starting Backend Server on http://localhost:8000"
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
