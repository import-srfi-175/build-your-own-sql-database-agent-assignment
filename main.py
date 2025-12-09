import sys
from Agent import Agent
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# --- CONFIGURATION ---
LIBRARY_DB_FILE = "library.db"
GEMINI_MODEL_NAME = "gemini-2.5-flash"
MAX_AGENT_STEPS = 10


# ---------------------

def main():
    console = Console()

    console.print(Panel(
        Text(
            "ReAct SQL Agent\nType 'exit' or 'quit' to end session.",
            justify="center",
            style="bold magenta"
        ),
        title="Welcome",
        border_style="magenta"
    ))

    try:
        sql_agent = Agent(
            database_path=LIBRARY_DB_FILE,
            model_name=GEMINI_MODEL_NAME,
            max_steps=MAX_AGENT_STEPS
        )

        while True:
            user_query = console.input(
                Text("\n[Query] ", style="bold cyan"),
            )

            if user_query.lower().strip() in ["exit", "quit"]:
                console.print(Panel(
                    "[bold green]Session ended. Goodbye![/bold green]",
                    title="Exit",
                    border_style="green"
                ))
                break

            if not user_query:
                continue

            sql_agent.run(user_query)

    except FileNotFoundError:
        console.print(Panel(
            f"[bold red]Error: Database file '{LIBRARY_DB_FILE}' not found.\nPlease run 'python Setup_dummy_db.py' to create it.[/bold red]",
            title="Database Error",
            border_style="red"
        ))
    except KeyboardInterrupt:
        console.print(Panel(
            "\n[bold yellow]Session interrupted by user. Goodbye![/bold yellow]",
            title="Exit",
            border_style="yellow"
        ))
    except Exception as e:
        console.print(Panel(
            f"[bold red]An unexpected error occurred: {e}[/bold red]",
            title="Critical Error",
            border_style="red"
        ))
    finally:
        sys.exit(0)


if __name__ == "__main__":
    main()