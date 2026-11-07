"""
The agent loop: send the conversation to the local model, run any tools it asks
for, feed the results back, and stream the final answer.
"""

import inspect
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterator

import ollama

import config
import llm
import tools


@dataclass
class Event:
    kind: str          # "text" | "tool_start" | "tool_end" | "error"
    data: Any = None
    tool: str = ""


BASE_PROMPT = """You are {name}, a highly capable AI assistant. Today is {today}.

Think before you answer. For anything non-trivial, reason step by step internally, then give the user a clear, well-structured result — not your scratch work. Lead with the answer, then the key reasons; use short paragraphs, bullet points, or numbered steps when they make the answer easier to follow. Match the depth of your answer to the question: a quick question gets a tight answer, a complex one gets a thorough one.

Be precise and correct. Prefer being accurate over sounding confident: if you are unsure or something is ambiguous, say so, state your assumption, and answer the most likely interpretation rather than refusing. Don't invent facts, citations, numbers, or tool results. When a question has a definite answer, commit to it; when it's a judgement call, give your best recommendation and the trade-offs.

Be genuinely useful: anticipate the natural next step, surface relevant caveats, and give concrete specifics (names, commands, numbers, examples) instead of vague advice. Keep a warm, direct, professional tone. No filler, no needless hedging, no repeating the question back.

Language: reply in the same language the user writes in. Tanglish (Tamil in English letters) → reply in Tanglish; Tamil script → Tamil; English → English.

Tools: use a tool only when it genuinely helps (live information, files, the user's documents, to-dos, exact math, running/searching code). Think about which tool and arguments fit before calling. For greetings, reasoning, explanations, writing and general knowledge, answer directly. After a tool returns, use its real output; never fabricate results, and if a tool fails, say so plainly and continue as best you can.

{mode_prompt}"""


def _coerce_args(func, args: dict) -> dict:
    """Small models sometimes send '5' instead of 5; fix types using the function's hints."""
    hints = {name: p.annotation for name, p in inspect.signature(func).parameters.items()}
    fixed = {}
    for key, value in (args or {}).items():
        if key not in hints:
            continue  # drop made-up arguments
        hint = hints[key]
        try:
            if hint is int and not isinstance(value, int):
                value = int(float(value))
            elif hint is float and not isinstance(value, float):
                value = float(value)
            elif hint is bool and isinstance(value, str):
                value = value.strip().lower() in {"true", "yes", "1"}
            elif hint is str and not isinstance(value, str):
                value = str(value)
        except (TypeError, ValueError):
            pass
        fixed[key] = value
    return fixed


class Agent:
    def __init__(self, mode: str = config.DEFAULT_MODE, user: str = ""):
        self.mode = mode if mode in config.MODES else config.DEFAULT_MODE
        self.user = user            # "" = laptop owner; a login name on the Nanban Server
        self.history: list[dict] = []

    # ------------------------------------------------------------ setup

    def reset(self) -> None:
        self.history = []

    def system_prompt(self) -> str:
        prompt = BASE_PROMPT.format(
            name=config.AGENT_NAME,
            today=datetime.now().strftime("%A, %d %B %Y"),
            mode_prompt=config.MODES[self.mode]["prompt"],
        )
        facts = tools.load_memory(self.user)
        if facts:
            prompt += "\n\nWhat you know about the user (long-term memory):\n" + "\n".join(
                f"{i}. {fact}" for i, fact in enumerate(facts, 1))
        return prompt

    def active_tools(self) -> list:
        names = config.MODES[self.mode]["tools"]
        if not config.ALLOW_CODE_RUN:
            names = [n for n in names if n != "run_python"]
        return [tools.for_user(tools.ALL_TOOLS[n], self.user) for n in names if n in tools.ALL_TOOLS]

    def _recent_history(self) -> list[dict]:
        recent = self.history[-config.MAX_HISTORY:]
        while recent and recent[0]["role"] != "user":  # never start mid tool-exchange
            recent = recent[1:]
        return recent

    # ------------------------------------------------------------ main loop

    def run_tool(self, name: str, args: dict) -> str:
        func = {f.__name__: f for f in self.active_tools()}.get(name)
        args = {k: v for k, v in (args or {}).items() if k != "user"}
        if func is None:
            return f"Error: there is no tool called '{name}' in this mode."
        try:
            return str(func(**_coerce_args(func, args)))
        except Exception as e:
            return f"Error while running {name}: {e}"

    def stream(self, user_text: str, images: list | None = None) -> Iterator[Event]:
        user_msg = {"role": "user", "content": user_text}
        if images:
            user_msg["images_data"] = images        # list of data: URLs (vision models)
        self.history.append(user_msg)
        tool_list = self.active_tools()

        for _ in range(config.MAX_TOOL_STEPS):
            messages = [{"role": "system", "content": self.system_prompt()}] + self._recent_history()
            content, tool_calls = "", []
            try:
                for chunk in llm.chat(messages, tools=tool_list or None,
                                      options={"temperature": config.TEMPERATURE, "num_ctx": config.CONTEXT_WINDOW}):
                    if chunk.message.content:
                        content += chunk.message.content
                        yield Event("text", chunk.message.content)
                    if chunk.message.tool_calls:
                        tool_calls.extend(chunk.message.tool_calls)
            except Exception as e:
                yield Event("error", llm.error_hint(e))
                return

            message = {"role": "assistant", "content": content}
            if tool_calls:
                message["tool_calls"] = [
                    {"function": {"name": c.function.name, "arguments": dict(c.function.arguments or {})}}
                    for c in tool_calls
                ]
            self.history.append(message)

            if not tool_calls:
                return

            for call in tool_calls:
                name, args = call.function.name, dict(call.function.arguments or {})
                yield Event("tool_start", args, tool=name)
                result = self.run_tool(name, args)
                yield Event("tool_end", result, tool=name)
                self.history.append({"role": "tool", "content": result[:tools.MAX_RESULT_CHARS], "tool_name": name})

        yield Event("text", "\n\n_(I used too many tool steps for this one. Try asking more specifically.)_")
