from gemini_client import invoke_gemini_client
from threading import Thread

from textual.app import App, ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import Input, Static, Markdown


AI_NAME = "Maya"
MODEL_NAME = "gemini-3.5-flash-lite"


class MayaCLI(App):
    TITLE = AI_NAME

    CSS = """
    Screen {
        background: #101010;
    }

    #header {
        dock: top;
        height: 3;
        padding: 1 2;
        background: #202020;
    }

    #brand {
        width: 1fr;
        color: #f5c46b;
        text-style: bold;
    }

    #model {
        width: auto;
        color: #80cbc4;
        text-align: right;
    }

    #chat {
        height: 1fr;
        padding: 1 2;
    }

    .user-message {
        color: #80cbc4;
        margin-top: 1;
    }

    .assistant-message {
        color: #eeeeee;
        margin-bottom: 1;
    }

    #input-bar {
        dock: bottom;
        height: 3;
        padding: 0 1;
        background: #202020;
    }

    #prompt {
        width: 3;
        color: #80cbc4;
        content-align: center middle;
    }

    #user-input {
        width: 1fr;
        border: none;
        background: #202020;
    }

    #footer {
        dock: bottom;
        height: 1;
        padding: 0 2;
        color: #888888;
        background: #181818;
    }
    """

    def compose(self) -> ComposeResult:
        with Horizontal(id="header"):
            yield Static(AI_NAME, id="brand")
            yield Static(f"Model: {MODEL_NAME}", id="model")

        yield VerticalScroll(id="chat")

        with Horizontal(id="input-bar"):
            yield Static("❯", id="prompt")
            yield Input(
                placeholder="Ask anything...",
                id="user-input",
            )

        yield Static(
            "Ctrl+Q  Quit    •    Enter  Send",
            id="footer",
        )

    def on_mount(self) -> None:
        self.query_one("#user-input", Input).focus()

    def add_message(self, css_class: str, text: str) -> Static:
        chat = self.query_one("#chat", VerticalScroll)
        message = Static(text, classes=css_class)
        chat.mount(message)
        chat.scroll_end(animate=False)
        return message

    def on_input_submitted(self, event: Input.Submitted) -> None:
        user_text = event.value.strip()

        if not user_text:
            return

        event.input.value = ""
        event.input.disabled = True

        if user_text.lower() in {"/exit", "/quit"}:
            self.exit()
            return

        if user_text == "/clear":
            self.query_one("#chat", VerticalScroll).remove_children()
            return

        if user_text == "/help":
            self.add_message(
                "assistant-message",
                "Commands: /help, /clear, /exit",
            )
            return

        self.add_message("user-message", f"❯ {user_text}")

        # Display a placeholder while Gemini is working.
        placeholder = self.add_message(
            "assistant-message",
            f"{AI_NAME} is thinking...",
        )

        Thread(
            target=self.generate_response,
            args=(user_text, placeholder),
            daemon=True,
        ).start()

    def update_activity(self, widget: Static, text: str) -> None:
        widget.update(text)
        self.query_one("#chat", VerticalScroll).scroll_end(animate=False)

    def generate_response(
        self,
        user_text: str,
        placeholder: Static,
    ) -> None:
        try:
            response = invoke_gemini_client(
                model=MODEL_NAME,
                input_text=user_text,
                on_tool_activity=lambda activity: self.call_from_thread(
                    self.update_activity,
                    placeholder,
                    f"{activity}",
                ),
            )

            self.call_from_thread(
                self.finish_response,
                placeholder,
                response,
            )

        except Exception as exc:
            self.call_from_thread(
                self.finish_response,
                placeholder,
                f"Error: {exc}",
            )

    def finish_response(self, widget: Static, text: str) -> None:
        chat = self.query_one("#chat", VerticalScroll)

        markdown = Markdown(text)
        markdown.add_class("assistant-message")

        widget.remove()
        chat.mount(markdown)
        chat.scroll_end(animate=False)

        user_input = self.query_one("#user-input", Input)
        user_input.disabled = False
        user_input.focus()


if __name__ == "__main__":
    MayaCLI().run()
