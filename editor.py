"""
A small full-screen code editor that runs inside the terminal.

    python editor.py <file>        (or /edit <file> inside the Nanban terminal)

Ctrl+S save · Ctrl+Q quit · Ctrl+Z undo · Ctrl+Y redo · Ctrl+F find · Ctrl+G go to line
"""

import sys
from pathlib import Path

from prompt_toolkit.application import Application
from prompt_toolkit.filters import Condition, has_focus
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import ConditionalContainer, HSplit, Layout, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import Style, merge_styles, style_from_pygments_cls
from prompt_toolkit.widgets import SearchToolbar, TextArea
from pygments.lexers import TextLexer, get_lexer_for_filename
from pygments.styles import get_style_by_name
from pygments.util import ClassNotFound


def _lexer_for(path: Path):
    try:
        return type(get_lexer_for_filename(path.name))
    except ClassNotFound:
        return TextLexer


def edit_file(path: str | Path, input=None, output=None) -> bool:
    """Open `path` in the editor. Returns True if the file was saved."""
    path = Path(path)
    original = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
    state = {"saved_text": original, "saved_once": False, "message": "", "quit_armed": False}

    search = SearchToolbar()
    area = TextArea(
        text=original, multiline=True, scrollbar=True, line_numbers=True, wrap_lines=False,
        lexer=PygmentsLexer(_lexer_for(path)), search_field=search, focus_on_click=True,
    )
    goto = TextArea(height=1, multiline=False, prompt=" Go to line: ", style="class:goto")
    goto_visible = {"on": False}

    def header():
        dirty = "●" if area.text != state["saved_text"] else " "
        row = area.document.cursor_position_row + 1
        col = area.document.cursor_position_col + 1
        return [("class:header", f" {dirty} {path.name}  ·  Ln {row}, Col {col}  ·  {len(area.document.lines)} lines ")]

    def footer():
        if state["message"]:
            return [("class:message", f" {state['message']} ")]
        return [("class:footer", " ^S Save   ^Q Quit   ^Z Undo   ^Y Redo   ^F Find   ^G Go to line ")]

    bindings = KeyBindings()

    @bindings.add("c-s")
    def _save(event):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(area.text, encoding="utf-8")
        state.update(saved_text=area.text, saved_once=True, message=f"Saved {path.name}", quit_armed=False)

    @bindings.add("c-q")
    def _quit(event):
        if area.text != state["saved_text"] and not state["quit_armed"]:
            state.update(message="Unsaved changes! Press Ctrl+Q again to quit without saving, or Ctrl+S to save.",
                         quit_armed=True)
            return
        event.app.exit(result=state["saved_once"])

    @bindings.add("c-z")
    def _undo(event):
        area.buffer.undo()

    @bindings.add("c-y")
    def _redo(event):
        area.buffer.redo()

    @bindings.add("tab", filter=has_focus(area))
    def _tab(event):
        area.buffer.insert_text("    ")

    @bindings.add("c-g")
    def _goto(event):
        goto_visible["on"] = True
        goto.text = ""
        event.app.layout.focus(goto)

    def _goto_accept(buffer):
        try:
            line = max(1, min(int(buffer.text), len(area.document.lines)))
            area.buffer.cursor_position = area.document.translate_row_col_to_index(line - 1, 0)
        except ValueError:
            pass
        goto_visible["on"] = False
        app.layout.focus(area)
        return False

    goto.accept_handler = _goto_accept

    def _clear_message(_buffer):
        state["message"] = ""
        state["quit_armed"] = False

    area.buffer.on_text_changed += _clear_message

    root = HSplit([
        Window(FormattedTextControl(header), height=1),
        area,
        search,
        ConditionalContainer(goto, filter=Condition(lambda: goto_visible["on"])),
        Window(FormattedTextControl(footer), height=1),
    ])

    style = merge_styles([
        style_from_pygments_cls(get_style_by_name("monokai")),
        Style.from_dict({
            "header": "bg:#5b4fe0 #ffffff bold",
            "footer": "bg:#2b2b3a #c8c8d8",
            "message": "bg:#e0a800 #000000 bold",
            "line-number": "#6c6c80",
            "goto": "bg:#2b2b3a #ffffff",
        }),
    ])

    app = Application(layout=Layout(root, focused_element=area), key_bindings=bindings, style=style,
                      full_screen=True, mouse_support=True, input=input, output=output)
    return bool(app.run())


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python editor.py <file>")
        sys.exit(1)
    edit_file(sys.argv[1])
