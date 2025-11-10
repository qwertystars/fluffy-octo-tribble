"""
AI Code Generator - FastAPI Web Interface
Web application with REST API and WebSocket support for real-time streaming.
"""

import os
import asyncio
from contextlib import asynccontextmanager
from typing import Dict
from dotenv import load_dotenv

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from langchain_core.messages import HumanMessage, AIMessage

from agent import CodeGeneratorAgent, SilentConsole
from code_tools import get_code_tools
from file_tools import get_file_tools


class ConnectionManager:
    """Manages WebSocket connections."""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        """Remove a WebSocket connection."""
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_message(self, message: dict, session_id: str):
        """Send a message to a specific session."""
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(message)


class AgentManager:
    """Manages multiple agent instances for concurrent users."""

    def __init__(self):
        self.agents: Dict[str, CodeGeneratorAgent] = {}
        self.agent_configs: Dict[str, dict] = {}

    async def get_or_create_agent(self, session_id: str) -> CodeGeneratorAgent:
        """Get existing agent or create new one for session."""
        if session_id not in self.agents:
            agent = CodeGeneratorAgent()
            # Use silent console for web (suppress terminal output)
            agent.console = SilentConsole()
            await agent.initialize()

            self.agents[session_id] = agent
            self.agent_configs[session_id] = {
                "configurable": {"thread_id": f"web_session_{session_id}"}
            }

        return self.agents[session_id]

    def get_config(self, session_id: str) -> dict:
        """Get configuration for a session."""
        return self.agent_configs.get(session_id, {})

    async def cleanup_agent(self, session_id: str):
        """Clean up agent resources."""
        if session_id in self.agents:
            await self.agents[session_id].cleanup()
            del self.agents[session_id]
            del self.agent_configs[session_id]


# Load environment variables
load_dotenv()

# Initialize managers
connection_manager = ConnectionManager()
agent_manager = AgentManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management for the FastAPI app."""
    # Startup
    print("🚀 Starting AI Code Generator Web Application...")

    # Ensure output directory exists
    output_dir = os.getenv("OUTPUT_DIR", "./generated_code")
    os.makedirs(output_dir, exist_ok=True)
    print(f"📁 Output directory: {os.path.abspath(output_dir)}")

    yield

    # Shutdown
    print("🛑 Shutting down...")
    # Cleanup all agents
    for session_id in list(agent_manager.agents.keys()):
        await agent_manager.cleanup_agent(session_id)


# Initialize FastAPI app
app = FastAPI(
    title="AI Code Generator",
    description="Generate code using AI with Claude Sonnet 4.5",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory (will create after this)
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except RuntimeError:
    # Static directory doesn't exist yet
    pass


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main web interface."""
    html_path = os.path.join(os.path.dirname(__file__), "static", "index.html")

    if os.path.exists(html_path):
        with open(html_path, "r") as f:
            return f.read()
    else:
        # Return a simple fallback interface
        return """
<!DOCTYPE html>
<html>
<head>
    <title>AI Code Generator</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: #1e1e1e;
            color: #ffffff;
        }
        h1 { color: #00d9ff; }
        .container {
            background: #2d2d2d;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        textarea {
            width: 100%;
            height: 100px;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #444;
            border-radius: 5px;
            background: #1e1e1e;
            color: #ffffff;
            font-family: monospace;
        }
        button {
            background: #00d9ff;
            color: #000;
            padding: 12px 24px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            font-size: 16px;
        }
        button:hover { background: #00b8d4; }
        #output {
            margin-top: 20px;
            padding: 15px;
            background: #1e1e1e;
            border-radius: 5px;
            min-height: 200px;
            max-height: 500px;
            overflow-y: auto;
            white-space: pre-wrap;
            border: 1px solid #444;
        }
        .message {
            margin: 10px 0;
            padding: 10px;
            border-radius: 5px;
        }
        .user { background: #1a4d2e; }
        .assistant { background: #1e3a5f; }
        .tool { background: #4a3520; font-size: 0.9em; }
        .error { background: #5f1e1e; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 AI Code Generator</h1>
        <p>Powered by Claude Sonnet 4.5 + LangGraph</p>

        <textarea id="input" placeholder="What code would you like to generate?"></textarea>
        <button onclick="generateCode()">Generate Code</button>

        <div id="output"></div>
    </div>

    <script>
        const sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        let ws = null;

        function connect() {
            ws = new WebSocket(`ws://${window.location.host}/ws/${sessionId}`);

            ws.onopen = () => {
                addMessage('system', '✓ Connected to AI Code Generator');
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);

                if (data.type === 'response') {
                    addMessage('assistant', data.content);
                } else if (data.type === 'tool') {
                    addMessage('tool', `🔧 ${data.content}`);
                } else if (data.type === 'error') {
                    addMessage('error', `❌ ${data.content}`);
                }
            };

            ws.onclose = () => {
                addMessage('system', '✗ Disconnected');
                setTimeout(connect, 2000);
            };

            ws.onerror = (error) => {
                addMessage('error', 'Connection error');
            };
        }

        function addMessage(type, content) {
            const output = document.getElementById('output');
            const msg = document.createElement('div');
            msg.className = `message ${type}`;
            msg.textContent = content;
            output.appendChild(msg);
            output.scrollTop = output.scrollHeight;
        }

        function generateCode() {
            const input = document.getElementById('input');
            const message = input.value.trim();

            if (!message) return;

            addMessage('user', message);

            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({ message: message }));
                input.value = '';
            } else {
                addMessage('error', 'Not connected. Reconnecting...');
                connect();
            }
        }

        // Connect on load
        connect();

        // Allow Enter to send (Shift+Enter for new line)
        document.getElementById('input').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                generateCode();
            }
        });
    </script>
</body>
</html>
"""


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "AI Code Generator is running"}


@app.get("/api/tools")
async def get_tools():
    """Get list of available tools."""
    code_tools = get_code_tools()
    file_tools = get_file_tools()

    return {
        "code_tools": [{"name": t.name, "description": t.description} for t in code_tools],
        "file_tools": [{"name": t.name, "description": t.description} for t in file_tools],
        "total": len(code_tools) + len(file_tools)
    }


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time code generation."""
    await connection_manager.connect(websocket, session_id)

    try:
        # Get or create agent for this session
        agent = await agent_manager.get_or_create_agent(session_id)
        config = agent_manager.get_config(session_id)

        # Send welcome message
        await connection_manager.send_message({
            "type": "system",
            "content": "Connected to AI Code Generator"
        }, session_id)

        while True:
            # Receive message from client
            data = await websocket.receive_json()
            user_message = data.get("message", "")

            if not user_message.strip():
                continue

            # Create human message
            human_message = HumanMessage(content=user_message)

            # Stream the workflow execution
            try:
                async for event in agent.agent.astream(
                    {"messages": [human_message]},
                    config,
                    stream_mode="values"
                ):
                    messages = event.get("messages", [])
                    if messages:
                        last_message = messages[-1]

                        # Send AI responses
                        if isinstance(last_message, AIMessage):
                            if last_message.content:
                                await connection_manager.send_message({
                                    "type": "response",
                                    "content": last_message.content
                                }, session_id)

                            # Send tool execution info
                            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                                for tool_call in last_message.tool_calls:
                                    await connection_manager.send_message({
                                        "type": "tool",
                                        "content": f"Executing: {tool_call['name']}"
                                    }, session_id)

            except Exception as e:
                await connection_manager.send_message({
                    "type": "error",
                    "content": str(e)
                }, session_id)

    except WebSocketDisconnect:
        connection_manager.disconnect(session_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        connection_manager.disconnect(session_id)


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
