"""
Code Generator Agent
Core agent implementation using LangGraph StateGraph for workflow orchestration.
"""

import os
import re
from typing import Annotated, Sequence, Literal
from typing_extensions import TypedDict

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.aiosqlite import AsyncSqliteSaver

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt

from code_tools import get_code_tools
from file_tools import get_file_tools


class AgentState(TypedDict):
    """State management for the code generator workflow."""
    messages: Annotated[Sequence[BaseMessage], add_messages]


class CodeGeneratorAgent:
    """AI Code Generator Agent with LangGraph workflow orchestration."""

    def __init__(self):
        """Initialize the agent with LLM, tools, and workflow."""
        # Initialize console for output
        self.console = Console()

        # Initialize LLM (Claude Sonnet 4.5)
        self.llm = ChatAnthropic(
            model="claude-sonnet-4-5-20250929",
            temperature=0.7,
            max_tokens=8192
        )

        # Load tools
        self.tools = get_code_tools() + get_file_tools()
        self.llm_with_tools = self.llm.bind_tools(self.tools)

        # Initialize StateGraph workflow
        self.workflow = StateGraph(AgentState)
        self._setup_workflow()

        # Checkpointer (initialized in async initialize method)
        self.checkpointer = None
        self._checkpointer_ctx = None
        self.agent = None

    def _setup_workflow(self):
        """Set up the LangGraph workflow with nodes and edges."""
        # Add nodes
        self.workflow.add_node("model_response", self.model_response)
        self.workflow.add_node("tool_use", self.tool_use)

        # Set entry point
        self.workflow.set_entry_point("model_response")

        # Add edges
        self.workflow.add_edge("tool_use", "model_response")

        # Add conditional edges
        self.workflow.add_conditional_edges(
            "model_response",
            self.check_tool_use,
            {
                "tool_use": "tool_use",
                END: END,
            },
        )

    async def initialize(self):
        """Async initialization for SQLite checkpointer."""
        db_path = os.path.join(os.getcwd(), "code_generator_checkpoints.db")
        self._checkpointer_ctx = AsyncSqliteSaver.from_conn_string(db_path)
        self.checkpointer = await self._checkpointer_ctx.__aenter__()

        # Compile workflow with checkpointer
        self.agent = self.workflow.compile(checkpointer=self.checkpointer)

    async def cleanup(self):
        """Clean up resources."""
        if self._checkpointer_ctx:
            await self._checkpointer_ctx.__aexit__(None, None, None)

    def model_response(self, state: AgentState) -> dict:
        """Node: Get response from the LLM."""
        messages = state["messages"]

        # Add system message on first interaction
        if len(messages) == 1 or not any(isinstance(m, SystemMessage) for m in messages):
            system_message = SystemMessage(content="""You are an expert AI code generator assistant. Your purpose is to generate high-quality, production-ready code based on user requirements.

CRITICAL RULES:
1. When generating code, ALWAYS write it to files using the write_file tool
2. You MUST provide BOTH file_path AND content parameters to write_file
3. Generate complete, runnable code - not snippets or placeholders
4. Include proper error handling, documentation, and best practices
5. Create appropriate project structures with multiple files when needed
6. After generating code, provide a clear summary of what you created

WORKFLOW PATTERN:
1. Understand the user's requirements
2. Plan the code structure (use create_project_structure for multi-file projects)
3. Generate the actual code content
4. Use write_file tool to save each file
5. Confirm what was created and provide usage instructions

TOOL USAGE:
- generate_code: Signal your intent to generate code
- write_file: REQUIRED to actually save code to disk (must include content parameter!)
- create_project_structure: For multi-file projects
- read_file/analyze_code: To read existing code
- list_files: To see what exists

ERROR RECOVERY:
If you get an error about missing content parameter:
- Extract the code from your previous response
- Call write_file again with the correct parameters

Remember: You're not just chatting - you're creating actual code files!
""")
            messages = [system_message] + list(messages)

        # Invoke LLM with tools
        response = self.llm_with_tools.invoke(messages)

        return {"messages": [response]}

    def tool_use(self, state: AgentState) -> dict:
        """Node: Execute tools requested by the LLM."""
        messages = state["messages"]
        last_message = messages[-1]

        if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
            return {"messages": []}

        tool_calls = last_message.tool_calls
        tool_messages = []

        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"].copy()

            # Display tool execution
            self._display_tool_execution(tool_name, tool_args)

            # Auto-fix mechanism: Extract missing content from prior responses
            if tool_name == "write_file" and not tool_args.get("content"):
                # Try to extract code from previous AI response
                content = self._extract_code_from_response(last_message.content)
                if content:
                    tool_args["content"] = content
                    self.console.print("[yellow]  ↳ Auto-extracted code content[/yellow]")

            # Find and invoke the tool
            tool = next((t for t in self.tools if t.name == tool_name), None)

            if tool is None:
                result = f"Error: Tool '{tool_name}' not found"
            else:
                try:
                    result = tool.invoke(tool_args)
                except Exception as e:
                    result = f"Error executing {tool_name}: {str(e)}"

            # Create tool message
            tool_messages.append(
                ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call["id"]
                )
            )

        return {"messages": tool_messages}

    def check_tool_use(self, state: AgentState) -> Literal["tool_use", END]:
        """Conditional edge: Check if tools were requested."""
        last_message = state["messages"][-1]

        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tool_use"
        return END

    def _extract_code_from_response(self, response_content: str) -> str:
        """Extract code blocks from markdown-formatted response."""
        if not response_content:
            return ""

        # Try to find code blocks with language specifier
        code_block_pattern = r"```(?:\w+)?\n(.*?)```"
        matches = re.findall(code_block_pattern, response_content, re.DOTALL)

        if matches:
            # Return the first (usually largest) code block
            return matches[0].strip()

        # If no code blocks found, return empty
        return ""

    def _display_tool_execution(self, tool_name: str, tool_args: dict):
        """Display tool execution in a formatted way."""
        self.console.print(f"\n[cyan]🔧 Executing tool:[/cyan] [bold]{tool_name}[/bold]")
        arg_names = list(tool_args.keys())
        if arg_names:
            self.console.print(f"   Arguments: {arg_names}")

    async def run(self):
        """Run the interactive CLI loop."""
        # Display welcome banner
        self._display_banner()

        # Display available tools
        self._display_tools()

        # Configuration for the agent
        config = {
            "configurable": {
                "thread_id": "code_generator_session"
            }
        }

        # Main interaction loop
        while True:
            try:
                # Get user input
                user_input = Prompt.ask("\n[bold green]💬 What code would you like to generate?[/bold green]")

                if user_input.lower() in ["exit", "quit", "q"]:
                    self.console.print("\n[yellow]👋 Goodbye![/yellow]")
                    break

                if not user_input.strip():
                    continue

                # Create human message
                human_message = HumanMessage(content=user_input)

                # Display thinking indicator
                self.console.print("\n[dim]🤔 Generating code...[/dim]")

                # Stream the workflow execution
                async for event in self.agent.astream(
                    {"messages": [human_message]},
                    config,
                    stream_mode="values"
                ):
                    # Get the last message
                    messages = event.get("messages", [])
                    if messages:
                        last_message = messages[-1]

                        # Display AI responses
                        if isinstance(last_message, AIMessage) and last_message.content:
                            # Only display if it's a new message (not tool call only)
                            if not last_message.tool_calls:
                                self._display_response(last_message.content)

                        # Tool results are displayed inline during execution

            except KeyboardInterrupt:
                self.console.print("\n\n[yellow]⚠️  Interrupted. Type 'exit' to quit.[/yellow]")
                continue
            except Exception as e:
                self.console.print(f"\n[red]❌ Error: {str(e)}[/red]")
                continue

    def _display_banner(self):
        """Display welcome banner."""
        banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   🚀  AI CODE GENERATOR  🚀                              ║
║                                                           ║
║   ▸ Powered by Claude Sonnet 4.5 + LangGraph            ║
║   ▸ Generate code from natural language                 ║
║   ▸ Type 'exit' or 'quit' to terminate                  ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
"""
        self.console.print(Panel(banner, style="bold blue"))

    def _display_tools(self):
        """Display available tools."""
        self.console.print("\n[bold cyan]🔧 Loading tools...[/bold cyan]")

        code_tools = get_code_tools()
        file_tools = get_file_tools()

        self.console.print(f"[green]✓ Loaded {len(code_tools)} code generation tools[/green]")
        self.console.print(f"[green]✓ Loaded {len(file_tools)} file operation tools[/green]")

    def _display_response(self, content: str):
        """Display AI response with rich formatting."""
        self.console.print("\n[bold magenta]🤖 Response:[/bold magenta]")

        # Render as markdown for better formatting
        md = Markdown(content)
        self.console.print(Panel(md, border_style="magenta"))


class SilentConsole:
    """Silent console for web interface (suppresses output)."""

    def print(self, *args, **kwargs):
        pass
