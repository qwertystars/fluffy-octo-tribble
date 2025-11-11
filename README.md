# 🚀 AI Code Generator - LangGraph Edition

An intelligent code generation system that mimics Claude Code CLI using **LangGraph** for workflow orchestration, **AI language models** (Anthropic Claude, OpenAI, or any OpenAI-compatible API), and **FastAPI** for a modern web interface.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-0.1.0-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-teal.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## ✨ Features

- **🧠 Agentic Architecture**: Uses LangGraph's StateGraph for intelligent decision-making
- **🔌 Flexible LLM Support**: Works with Anthropic Claude, OpenAI, OpenRouter, vLLM, or any OpenAI-compatible API
- **🛠️ Tool-Augmented LLM**: AI executes tools to create files, analyze code, and build projects
- **💻 Dual Interface**: Both CLI (Rich terminal UI) and web-based (WebSocket streaming)
- **💾 Stateful Conversations**: SQLite checkpointing enables context persistence across sessions
- **🔄 Auto-Fix Mechanism**: Intelligent error recovery and self-correction
- **⚡ Production-Ready**: Async/await throughout, proper error handling, and graceful degradation

## 🏗️ Architecture Overview

### Core Components

```
┌─────────────────────────────────────────────┐
│  User Interface (CLI / Web)                 │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│  CodeGeneratorAgent                         │
│  ┌───────────────────────────────────────┐  │
│  │  StateGraph Workflow                  │  │
│  │  ┌─────────────────────────────────┐  │  │
│  │  │  1. model_response (LLM)        │  │  │
│  │  │  2. check_tool_use (Router)     │  │  │
│  │  │  3. tool_use (Executor)         │  │  │
│  │  └─────────────────────────────────┘  │  │
│  └───────────────────────────────────────┘  │
└──────────────────┬──────────────────────────┘
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
┌──────────────┐      ┌──────────────┐
│  Code Tools  │      │  File Tools  │
└──────────────┘      └──────────────┘
        │                     │
        └──────────┬──────────┘
                   ▼
        ┌─────────────────────┐
        │  SQLite Checkpointer │
        │  (State Persistence) │
        └─────────────────────┘
```

### Technology Stack

- **AI/ML**: LangGraph, LangChain, Anthropic Claude / OpenAI / OpenAI-compatible APIs
- **Web Framework**: FastAPI, Uvicorn, WebSockets
- **State Management**: AsyncSqliteSaver (LangGraph checkpointing)
- **CLI**: Rich (beautiful terminal output)
- **Utilities**: Python-dotenv, Pydantic, asyncio

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- API access to one of the following:
  - **Anthropic Claude** ([Get API key](https://console.anthropic.com/))
  - **OpenAI** ([Get API key](https://platform.openai.com/api-keys))
  - **OpenRouter** ([Get API key](https://openrouter.ai/))
  - **Any OpenAI-compatible API** (vLLM, local models, etc.)

### Setup

1. **Clone the repository**

```bash
git clone <repository-url>
cd fluffy-octo-tribble
```

2. **Create a virtual environment**

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and choose ONE of the following options:

**Option A: OpenAI-Compatible API** (OpenRouter, vLLM, local models, etc.)
```env
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=anthropic/claude-3.5-sonnet
OUTPUT_DIR=./generated_code
PORT=8000
```

**Option B: Anthropic Claude** (Direct API)
```env
ANTHROPIC_API_KEY=your_api_key_here
ANTHROPIC_MODEL=claude-sonnet-4-5-20250929
OUTPUT_DIR=./generated_code
PORT=8000
```

**Examples for different providers:**

- **OpenRouter**: `OPENAI_BASE_URL=https://openrouter.ai/api/v1`
- **Local vLLM**: `OPENAI_BASE_URL=http://localhost:8000/v1`
- **OpenAI**: `OPENAI_BASE_URL=https://api.openai.com/v1`
- **Any OpenAI-compatible endpoint**

## 🚀 Usage

### Option 1: CLI Interface (Recommended for developers)

Run the command-line interface with Rich terminal UI:

```bash
python main.py
```

**Features:**
- Beautiful terminal UI with markdown rendering
- Interactive code generation
- Real-time tool execution display
- Persistent conversation history

**Example Session:**

```
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   🚀  AI CODE GENERATOR  🚀                              ║
║                                                           ║
║   ▸ Powered by Claude Sonnet 4.5 + LangGraph            ║
║   ▸ Generate code from natural language                 ║
║   ▸ Type 'exit' or 'quit' to terminate                  ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

💬 What code would you like to generate?
> Create a FastAPI REST API for a todo list with SQLite

🤔 Generating code...

🔧 Executing tool: write_file
   Arguments: ['file_path', 'content']
✓ Successfully wrote 1247 characters to ./generated_code/main.py

🤖 Response:
I've created your FastAPI todo list API! Here's what I generated:
1. main.py - FastAPI app with CRUD endpoints
2. models.py - Pydantic models
3. database.py - SQLite setup

To run: uvicorn main:app --reload
```

### Option 2: Web Interface (Best for non-technical users)

Run the FastAPI web server:

```bash
python app.py
```

Then open your browser to: `http://localhost:8000`

**Features:**
- Modern, responsive web UI
- Real-time WebSocket streaming
- Multiple concurrent user sessions
- Mobile-friendly design

## 🛠️ Available Tools

### Code Generation Tools

1. **generate_code**: Signal intent to generate code
2. **create_project_structure**: Create multi-file projects with nested directories
3. **analyze_code**: Read and analyze existing code
4. **generate_tests**: Generate unit tests for code

### File Operation Tools

1. **write_file**: Write content to files (creates directories as needed)
2. **read_file**: Read file contents
3. **list_files**: List directory contents
4. **create_directory**: Create directories
5. **search_files**: Search for files by pattern

## 💡 Example Use Cases

### 1. Generate a Microservice

```
Create a Python microservice for user authentication with JWT tokens,
including FastAPI endpoints, SQLAlchemy models, and password hashing
```

### 2. Build a React Component

```
Generate a React login form component with validation,
using functional components and hooks
```

### 3. Create a Data Processing Pipeline

```
Build a Python script that reads CSV files, processes data with pandas,
and exports to JSON with error handling
```

### 4. Generate Tests

```
Create pytest unit tests for the file authentication.py
with test cases for login, logout, and token validation
```

## 🏛️ Project Structure

```
.
├── agent.py              # Core agent with LangGraph workflow
├── code_tools.py         # Code generation tools
├── file_tools.py         # File operation tools
├── main.py               # CLI entry point
├── app.py                # FastAPI web entry point
├── requirements.txt      # Python dependencies
├── .env                  # Environment configuration
├── static/               # Web UI assets
│   ├── index.html       # Web interface
│   ├── styles.css       # Styling
│   └── app.js           # Frontend JavaScript
└── generated_code/       # Output directory for generated code
```

## 🔧 Configuration

### Environment Variables

**API Configuration (choose ONE):**

**For OpenAI-Compatible APIs:**
- `OPENAI_BASE_URL` (**required**): Base URL for the API (e.g., `https://openrouter.ai/api/v1`)
- `OPENAI_API_KEY` (**required**): Your API key
- `OPENAI_MODEL` (optional): Model to use (default: `gpt-4`)

**For Anthropic Claude:**
- `ANTHROPIC_API_KEY` (**required**): Your Anthropic API key
- `ANTHROPIC_MODEL` (optional): Model to use (default: `claude-sonnet-4-5-20250929`)

**General Settings:**
- `LLM_TEMPERATURE` (optional): Temperature 0.0-1.0 (default: `0.7`)
- `LLM_MAX_TOKENS` (optional): Maximum tokens per response (default: `8192`)
- `OUTPUT_DIR` (optional): Directory for generated code (default: `./generated_code`)
- `PORT` (optional): Port for web server (default: `8000`)

### Model Configuration

The system supports multiple LLM providers:
- **Temperature**: 0.7 (balanced creativity and consistency)
- **Max Tokens**: 8192 (supports large code files)
- **Supported Models**: Any OpenAI-compatible model or Anthropic Claude models

**Popular Model Options:**
- Anthropic: `claude-sonnet-4-5-20250929`, `claude-3-5-sonnet-20241022`
- OpenAI: `gpt-4`, `gpt-4-turbo`, `gpt-3.5-turbo`
- OpenRouter: `anthropic/claude-3.5-sonnet`, `openai/gpt-4`
- Local/vLLM: Any model supported by your setup

## 🔄 How It Works

### Workflow Cycle

1. **User Input**: Natural language description of desired code
2. **Model Response**: LLM processes request and decides on actions
3. **Check Tool Use**: Conditional routing based on tool calls
4. **Tool Execution**: Execute requested tools (write files, analyze code, etc.)
5. **Loop**: Return to model response with tool results
6. **End**: When no more tools needed, present final response

### State Management

- **Checkpointing**: Every step is saved to SQLite
- **Persistence**: Conversations survive restarts
- **Time-Travel**: Can replay and debug workflows
- **Session Isolation**: Web sessions are independent

### Error Recovery

The system includes intelligent error recovery:
- Auto-extracts missing parameters from conversation history
- Provides helpful error messages to guide LLM corrections
- Self-correcting feedback loop

## 🧪 Testing

Run tests (if implemented):

```bash
pytest tests/ -v
```

Format code:

```bash
black *.py
```

## 📊 Performance

- **Throughput**: Handles 1-10 concurrent users (CLI + Web)
- **Latency**: Sub-second state operations
- **Scalability**: Can scale to 100+ users with PostgreSQL backend

## 🔐 Security

- API keys stored in `.env` (never committed)
- Safe file operations (path normalization, directory creation)
- WebSocket connection management
- Input validation with Pydantic

## 🐛 Troubleshooting

### "No API configuration found"
This means neither API option is properly configured. Fix by:
- Ensure `.env` file exists in the project root
- Choose **ONE** of these options:
  - **Option A**: Set `OPENAI_BASE_URL` AND `OPENAI_API_KEY`
  - **Option B**: Set `ANTHROPIC_API_KEY`
- Verify the variables are uncommented (no `#` at the start)

### API key errors
- **Anthropic**: Get your API key from [console.anthropic.com](https://console.anthropic.com/)
- **OpenAI**: Get your API key from [platform.openai.com](https://platform.openai.com/api-keys)
- **OpenRouter**: Get your API key from [openrouter.ai](https://openrouter.ai/)
- Ensure no extra spaces or quotes around the API key

### "Module not found" errors
- Run `pip install -r requirements.txt`
- Ensure virtual environment is activated

### WebSocket connection fails
- Check if port 8000 is available
- Verify firewall settings
- Try a different port in `.env`

### Generated code not appearing
- Check `OUTPUT_DIR` setting in `.env`
- Verify write permissions for output directory
- Look for error messages in console

## 🚧 Future Improvements

- [ ] Docker integration for containerized code generation
- [ ] Test execution and auto-fix failed tests
- [ ] Package management (auto-install dependencies)
- [ ] Multi-agent collaboration (frontend, backend, testing specialists)
- [ ] PostgreSQL backend for enterprise scale
- [ ] IDE plugins (VSCode, JetBrains)
- [ ] Code linting and security scanning
- [ ] Visual programming interface

## 📚 Documentation

For more details on the architecture and implementation:

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

## 🙏 Acknowledgments

- Anthropic for Claude AI
- LangChain team for LangGraph
- FastAPI for the excellent web framework
- Rich for beautiful terminal output

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Built with ❤️ using Claude Sonnet 4.5, LangGraph, and FastAPI**
