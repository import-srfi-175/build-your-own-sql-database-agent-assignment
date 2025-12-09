import os
import sqlite3
import re, json
from typing import Union
from pathlib import PosixPath
from dotenv import load_dotenv
import google.generativeai as genai
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from Tools import ALL_TOOLS, TOOL_REGISTRY

load_dotenv()
genai.configure(api_key=os.environ.get("GEMINI_API"))
console = Console()


def summarize_schema(db_cursor: sqlite3.Cursor):
    db_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    table_names = [table[0] for table in db_cursor.fetchall()]
    table_details = []
    for table in table_names:
        db_cursor.execute(f"PRAGMA table_info({table});")
        columns = [col[1] for col in db_cursor.fetchall()]
        table_details.append(f"- {table} ({', '.join(columns)})")
    return "\n".join(table_details)


class Agent:
    def __init__(self, database_path: Union[str, PosixPath], model_name: str, max_steps: int = 10):
        self.db_path = database_path
        self.model_name = model_name
        self.db_connection = sqlite3.connect(database_path)
        self.db_cursor = self.db_connection.cursor()
        self.available_tools = ALL_TOOLS
        self.tool_registry = TOOL_REGISTRY
        self.step_limit = max_steps
        schema_text = summarize_schema(self.db_cursor)
        self.system_instruction = f"""
You are a helpful SQL Database Agent that interacts with a SQLite database in read-only mode.

Database schema:
{schema_text}

Respond strictly in this reasoning structure:
THOUGHT: <reasoning>
ACTION: <tool_name>{{"<arg>":"<value>"}}
OBSERVATION: <tool output>
THOUGHT: <final reasoning>
FINAL ANSWER: <answer to user>
Rules:
- Use only SELECT statements.
- Never modify the database.
- Match column and table names exactly.
"""
        self.chat_model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=self.system_instruction,
            tools=self.available_tools
        )
        self.chat_session = self.chat_model.start_chat(enable_automatic_function_calling=False)

    def _format_result(self, result):
        if result is None:
            return "No result returned."
        if isinstance(result, dict) and "columns" in result and "rows" in result:
            table = Table(show_header=True, header_style="bold cyan")
            for column_name in result["columns"]:
                table.add_column(str(column_name))
            for row in result["rows"]:
                table.add_row(*[str(value) for value in row])
            with console.capture() as capture:
                console.print(table)
            return capture.get()
        elif isinstance(result, list):
            return "\n".join([str(item) for item in result])
        else:
            return str(result)

    def _parse_response(self, text: str):
        thought_match = re.search(r"THOUGHT:(.*?)(?=ACTION:|FINAL ANSWER:|$)", text, re.DOTALL)
        action_match = re.search(r"ACTION:\s*(\w+)\s*(\{.*?\})", text, re.DOTALL)
        final_match = re.search(r"FINAL ANSWER:(.*)", text, re.DOTALL)
        thought = thought_match.group(1).strip() if thought_match else None
        action_name, action_args, final = None, {}, final_match.group(1).strip() if final_match else None
        if action_match:
            action_name = action_match.group(1).strip()
            try:
                action_args = json.loads(action_match.group(2))
            except:
                action_args = {}
        return thought, action_name, action_args, final

    def run(self, user_query: str):
        console.print(Panel(f"[bold cyan]{user_query}[/bold cyan]", title="User", border_style="cyan"))
        conversation_history = [user_query]
        for step in range(self.step_limit):
            response = self.chat_session.send_message("\n".join(conversation_history) + "\nAlways follow the THOUGHT–ACTION–OBSERVATION–FINAL ANSWER structure.")
            part = response.candidates[0].content.parts[0]
            if hasattr(part, "function_call") and part.function_call:
                function_call = part.function_call
                name, args = function_call.name, dict(function_call.args)
                thought_text = f"I will call the tool '{name}' with arguments {args} to retrieve the required data."
                console.print(Panel(thought_text, title=f"Step {step+1}: Thought", border_style="white"))
                console.print(Panel(f"{name}({args})", title=f"Step {step+1}: Action", border_style="yellow"))
                observation = None
                if name in self.tool_registry:
                    try:
                        observation = self.tool_registry[name](cursor=self.db_cursor, **args)
                    except Exception as e:
                        observation = f"Tool error: {e}"
                observation_text = self._format_result(observation)
                console.print(Panel(Text(observation_text), title="Observation", border_style="blue"))
                conversation_history.append(f"THOUGHT: {thought_text}")
                conversation_history.append(f"OBSERVATION: {observation_text}")
                continue
            text = getattr(response, "text", "")
            thought, action, args, final = self._parse_response(text)
            if thought:
                console.print(Panel(thought, title=f"Step {step+1}: Thought", border_style="white"))
                conversation_history.append(f"THOUGHT: {thought}")
            if action:
                console.print(Panel(f"{action}({args})", title=f"Step {step+1}: Action", border_style="yellow"))
                observation = None
                if action in self.tool_registry:
                    try:
                        observation = self.tool_registry[action](cursor=self.db_cursor, **args)
                    except Exception as e:
                        observation = f"Tool error: {e}"
                observation_text = self._format_result(observation)
                console.print(Panel(Text(observation_text), title="Observation", border_style="blue"))
                conversation_history.append(f"OBSERVATION: {observation_text}")
            if final:
                console.print(Panel(f"[bold green]{final}[/bold green]", title="Final Answer", border_style="green"))
                break

    def __del__(self):
        self.db_connection.close()
