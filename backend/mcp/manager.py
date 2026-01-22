
from typing import Dict, Optional, Any, List
import os
import json
import asyncio
import logging
import time
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = logging.getLogger(__name__)

CONNECTIONS_FILE = os.path.join(os.getcwd(), "connections.json")
SCHEMA_CACHE_TTL = 60  # seconds

class MCPConnectionManager:
    _instance = None
    
    def __init__(self):
        self.configs: Dict[str, Dict[str, Any]] = {}
        self._schema_cache: Dict[str, Dict[str, Any]] = {}  # {conn_id: {"schema": str, "timestamp": float}}
        self._load_configs()
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = MCPConnectionManager()
        return cls._instance

    def _load_configs(self):
        """Load connection configs from file."""
        if os.path.exists(CONNECTIONS_FILE):
            try:
                with open(CONNECTIONS_FILE, 'r') as f:
                    self.configs = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load connections: {e}")
                self.configs = {}

    def _save_configs(self):
        """Save configs to file."""
        try:
            with open(CONNECTIONS_FILE, 'w') as f:
                json.dump(self.configs, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save connections: {e}")

    async def initialize_default_connection(self):
        """Ensure default connection exists."""
        if "default" not in self.configs:
            # Add default postgres from env
            self.add_connection({
                "id": "default",
                "type": "postgres",
                "name": "Default Database",
                "params": {} # Empty means use env vars
            })

    def add_connection(self, config: Dict[str, Any]):
        """Add or update a connection configuration."""
        conn_id = config.get("id")
        if not conn_id:
            raise ValueError("Connection ID is required")
        
        self.configs[conn_id] = config
        # Invalidate cache for this connection
        if conn_id in self._schema_cache:
            del self._schema_cache[conn_id]
        self._save_configs()
        logger.info(f"Added connection: {conn_id}")

    def remove_connection(self, conn_id: str):
        if conn_id in self.configs:
            del self.configs[conn_id]
            if conn_id in self._schema_cache:
                del self._schema_cache[conn_id]
            self._save_configs()

    def list_connections(self) -> List[Dict[str, Any]]:
        return list(self.configs.values())

    def get_connection_config(self, conn_id: str) -> Optional[Dict[str, Any]]:
        return self.configs.get(conn_id)
    
    def get_cached_schema(self, conn_id: str) -> Optional[str]:
        """Get cached schema if still valid."""
        cached = self._schema_cache.get(conn_id)
        if cached and (time.time() - cached["timestamp"]) < SCHEMA_CACHE_TTL:
            logger.debug(f"Using cached schema for {conn_id}")
            return cached["schema"]
        return None
    
    def set_cached_schema(self, conn_id: str, schema: str):
        """Cache schema result."""
        self._schema_cache[conn_id] = {"schema": schema, "timestamp": time.time()}

    async def get_tool_result(self, connection_id: str, tool_name: str, tool_args: dict) -> Any:
        """Execute a tool on a specific connection."""
        config = self.configs.get(connection_id)
        if not config:
             raise ValueError(f"Unknown connection: {connection_id}")

        conn_type = config.get("type")
        params = config.get("params", {})
        
        import sys
        python_exe = sys.executable
        env = os.environ.copy()
        
        # Determine script and env based on type
        base_dir = os.path.dirname(__file__)
        
        if conn_type == "postgres":
            script = os.path.join(base_dir, "servers", "postgres.py")
            # If params provided, override env
            if params.get("host"): env["DB_HOST"] = params["host"]
            if params.get("port"): env["DB_PORT"] = str(params["port"])
            if params.get("user"): env["DB_USER"] = params["user"]
            if params.get("password"): env["DB_PASSWORD"] = params["password"]
            if params.get("dbname"): env["DB_NAME"] = params["dbname"]
            
        elif conn_type == "sqlite":
            script = os.path.join(base_dir, "servers", "sqlite.py")
            if params.get("path"): env["DB_PATH"] = params["path"]
            
        elif conn_type == "filesystem":
            script = os.path.join(base_dir, "servers", "filesystem.py")
            if params.get("root_dir"): env["ROOT_DIR"] = params["root_dir"]
            
        else:
            raise ValueError(f"Unsupported connection type: {conn_type}")

        server_params = StdioServerParameters(
            command=python_exe,
            args=[script],
            env=env
        )
        
        # Execute tool via stdio client
        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool(tool_name, arguments=tool_args)
                    return result
        except Exception as e:
            logger.error(f"MCP Tool Execution Failed ({connection_id}/{tool_name}): {e}")
            raise e

# Global access
manager = MCPConnectionManager()
