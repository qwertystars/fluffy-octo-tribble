"""
AI Code Generator - CLI Interface
Main entry point for the command-line interface using Rich for terminal UI.
"""

import os
import sys
import asyncio
from dotenv import load_dotenv
from rich.console import Console

from agent import CodeGeneratorAgent

console = Console()


async def main():
    """Main entry point for the CLI application."""
    # Load environment variables
    load_dotenv()

    # Initialize output directory
    output_dir = os.getenv("OUTPUT_DIR", "./generated_code")
    os.makedirs(output_dir, exist_ok=True)

    console.print(f"[dim]📁 Output directory: {os.path.abspath(output_dir)}[/dim]")

    try:
        # Create and initialize agent (API key validation happens here)
        agent = CodeGeneratorAgent()

        # Initialize async resources
        await agent.initialize()

        # Run the interactive loop
        await agent.run()

    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Goodbye![/yellow]")
    except ValueError as e:
        # API configuration error
        console.print(f"\n[bold red]❌ Configuration Error:[/bold red]")
        console.print(f"[yellow]{str(e)}[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]❌ Fatal error: {str(e)}[/bold red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        sys.exit(1)
    finally:
        # Cleanup resources
        if 'agent' in locals():
            await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
