# ⚡ Quick Start Guide

Get up and running with the AI Code Generator in 5 minutes!

## Prerequisites

- Python 3.8+ installed
- Anthropic API key ([Get one here](https://console.anthropic.com/))

## Installation (5 steps)

### 1. Clone and Navigate

```bash
git clone <repository-url>
cd fluffy-octo-tribble
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Activate (choose your OS)
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Key

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your API key
# ANTHROPIC_API_KEY=sk-ant-...
```

On Windows, you can edit with:
```bash
notepad .env
```

On macOS/Linux:
```bash
nano .env
```

### 5. Run the Application

**Option A: CLI Interface** (Terminal)
```bash
python main.py
```

**Option B: Web Interface** (Browser)
```bash
python app.py
# Then open: http://localhost:8000
```

## First Code Generation

### CLI Example

```
💬 What code would you like to generate?
> Create a Python script that reads a CSV file and converts it to JSON

🤔 Generating code...

🔧 Executing tool: write_file
   Arguments: ['file_path', 'content']
✓ Successfully wrote 523 characters to ./generated_code/csv_to_json.py

🤖 Response:
I've created a Python script that reads CSV files and converts them to JSON!

Features:
- Reads CSV with proper encoding
- Handles headers automatically
- Pretty-prints JSON output
- Error handling included

To use:
python generated_code/csv_to_json.py input.csv output.json
```

### Web Example

1. Open browser to `http://localhost:8000`
2. Type in the text box:
   ```
   Create a FastAPI REST API with user authentication
   ```
3. Click "Generate Code"
4. Watch as the AI generates complete files in real-time!

## Common Commands

### Stop the Application

**CLI**: Press `Ctrl+C` or type `exit`

**Web**: Press `Ctrl+C` in terminal

### View Generated Code

```bash
# List generated files
ls generated_code/

# View a file (Unix/Mac)
cat generated_code/filename.py

# View a file (Windows)
type generated_code\filename.py
```

### Clear Generated Code

```bash
# Unix/Mac
rm -rf generated_code/*

# Windows
del /q generated_code\*
```

## Example Prompts to Try

### 1. Web API
```
Create a FastAPI REST API for a todo list with CRUD operations
```

### 2. Data Processing
```
Build a Python script that processes log files and generates statistics
```

### 3. CLI Tool
```
Create a command-line calculator that supports basic arithmetic operations
```

### 4. Web Scraper
```
Generate a web scraper using BeautifulSoup to extract article titles from a news site
```

### 5. Complete Project
```
Create a Flask blog application with user authentication, post creation,
and SQLite database, including all necessary files
```

## Troubleshooting

### "ANTHROPIC_API_KEY not found"

**Solution**: Make sure `.env` file exists and contains:
```
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

### "Module not found" errors

**Solution**: Make sure virtual environment is activated and dependencies are installed:
```bash
# Activate venv (if not already)
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Web interface won't load

**Solution**: Check if port 8000 is already in use:
```bash
# Check port (Unix/Mac)
lsof -i :8000

# Check port (Windows)
netstat -ano | findstr :8000

# Use different port
# Edit .env and set: PORT=8080
```

### Generated code not appearing

**Solution**: Check output directory:
```bash
# Unix/Mac
ls -la generated_code/

# Windows
dir generated_code\
```

If empty, check for error messages in the console.

## Tips for Best Results

### 1. Be Specific
❌ "Create a web app"
✅ "Create a FastAPI web app with user registration, login, and profile management"

### 2. Specify Technologies
❌ "Create an API"
✅ "Create a REST API using FastAPI with SQLAlchemy for database operations"

### 3. Request Multiple Files
✅ "Create a complete project structure with main.py, models.py, and requirements.txt"

### 4. Ask for Documentation
✅ "Include docstrings and a README explaining how to run the code"

### 5. Specify Error Handling
✅ "Include proper error handling and input validation"

## Next Steps

1. **Read the full README**: `README.md` for detailed features
2. **Explore the architecture**: `ARCHITECTURE.md` for technical details
3. **Try complex projects**: Generate multi-file applications
4. **Customize the agent**: Modify tools in `code_tools.py` and `file_tools.py`

## Getting Help

- Check `README.md` for detailed documentation
- Review error messages carefully
- Verify your API key is valid
- Ensure you have internet connection (for API calls)

## What's Next?

Now that you're set up, try:

1. Generate a simple script
2. Create a web API
3. Build a complete application
4. Analyze and modify existing code

**Happy coding! 🚀**
