import os
import json
import requests
from typing import Dict, Any, Optional

class JeanClient:
    """
    A simple Python client for the Jean Memory Agent REST API.
    """
    def __init__(self, token: Optional[str] = None, client_name: str = "default-agent"):
        self.api_token = token or os.environ.get("JEAN_API_KEY")
        if not self.api_token:
            raise ValueError("API Key not found. Pass it to the constructor or set JEAN_API_KEY.")
        
        self.base_url = "https://jean-memory-api.onrender.com/agent/v1/mcp/messages/"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "X-Client-Name": client_name,
        }

    def _make_request(self, method: str, params: Dict[str, Any]) -> Optional[Dict]:
        """Helper to construct and send a JSON-RPC 2.0 request."""
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1 
        }
        try:
            response = requests.post(self.base_url, headers=self.headers, data=json.dumps(payload))
            response.raise_for_status()
            return response.json().get("result")
        except requests.exceptions.HTTPError as err:
            print(f"❌ API Error for method '{method}': {err.response.status_code} {err.response.reason}")
            print(f"   Response: {err.response.text}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

    def add_memory(self, text: str) -> Optional[Dict]:
        """Adds a single memory."""
        print(f"🧠 Adding memory: '{text}'")
        return self._make_request("tools/call", {
            "name": "add_memories",
            "arguments": {"text": text}
        })

    def search_memories(self, query: str) -> Optional[Dict]:
        """Searches for memories."""
        print(f"🤔 Searching for: '{query}'")
        return self._make_request("tools/call", {
            "name": "search_memory",
            "arguments": {"query": query}
        })

    def list_tools(self) -> Optional[Dict]:
        """Lists available tools."""
        print("🛠️ Listing available tools...")
        return self._make_request("tools/list", {})

    def list_memories(self, limit: int = 20) -> Optional[Dict]:
        """Lists the most recent memories in the current context."""
        print(f"📋 Listing recent memories (limit: {limit})...")
        return self._make_request("tools/call", {
            "name": "list_memories",
            "arguments": {"limit": limit}
        }) 