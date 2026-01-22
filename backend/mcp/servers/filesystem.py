
from mcp.server.fastmcp import FastMCP
import os
import glob

class FilesystemServer:
    def __init__(self, name: str, root_dir: str):
        self.mcp = FastMCP(name)
        self.root_dir = os.path.abspath(root_dir)
        # Ensure root dir exists
        os.makedirs(self.root_dir, exist_ok=True)
        self._register_tools()

    def _validate_path(self, path: str) -> str:
        """Ensure path is within root_dir to prevent directory traversal."""
        full_path = os.path.abspath(os.path.join(self.root_dir, path))
        if not full_path.startswith(self.root_dir):
            raise ValueError(f"Access denied: Path '{path}' is outside sandbox.")
        return full_path

    def _register_tools(self):
        @self.mcp.tool()
        async def list_directory(path: str = ".") -> list[str]:
            """List files and directories in a path relative to root."""
            try:
                full_path = self._validate_path(path)
                if not os.path.exists(full_path):
                    return []
                return os.listdir(full_path)
            except Exception as e:
                return [f"Error: {e}"]

        @self.mcp.tool()
        async def read_file(path: str) -> str:
            """Read content of a file."""
            try:
                full_path = self._validate_path(path)
                if not os.path.exists(full_path):
                    return "Error: File not found."
                
                # Check file size to prevent reading huge files
                if os.path.getsize(full_path) > 10 * 1024 * 1024: # 10MB limit
                    return "Error: File too large (>10MB)."

                with open(full_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                return f"Error reading file: {e}"

        @self.mcp.tool()
        async def write_file(path: str, content: str) -> str:
            """Write content to a file. Overwrites if exists."""
            try:
                full_path = self._validate_path(path)
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content)
                return f"Successfully wrote to {path}"
            except Exception as e:
                return f"Error writing file: {e}"

    def run(self):
        self.mcp.run()

if __name__ == "__main__":
    import os
    import logging
    
    logging.basicConfig(level=logging.ERROR)
    
    # Get Root Dir from environment
    root_dir = os.getenv("ROOT_DIR", "./workspace_data")
    
    server = FilesystemServer("filesystem-mcp", root_dir)
    server.run()
