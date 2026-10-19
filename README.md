# Maya (AI Coding Assistant & Bridge)

Maya is an AI coding assistant and interactive platform powered by Google Gemini, featuring a Textual-based terminal user interface (CLI), tool integration capabilities, and WhatsApp bridge support.

## Features

- **Terminal UI (`terminal_ui.py`)**: An interactive, responsive terminal UI built with [Textual](https://textual.textualize.io/) featuring live status updates, Markdown rendering, and command support (`/help`, `/clear`, `/exit`).
- **Gemini Client (`gemini_client.py`)**: Integrates with Google Gemini models (`gemini-3.5-flash-lite`) to process user queries and coordinate tool execution.
- **Tool System (`tools/`)**: Modular tool architecture including:
  - **`filesystem.py`**: Robust file operations (`list_files`, `read_file`, `edit_file`, `write_file`, `move_file`, `copy_file`, `delete_file`, and `git_diff`).
  - **`terminal.py`**: Safe terminal command execution (`run_command`).
- **WhatsApp Bridge (`whatsapp_bridge.py`, `whatsapp_mcp.py`, `whatsapp_bot/`)**: Node.js and Python bridge components allowing integration with WhatsApp.

---

## 🚧 Planned Tools & Roadmap

| Tool         | Description / What Maya could do                                     | Status              |
|:-------------|:---------------------------------------------------------------------|:--------------------|
| **`git.py`** | Advanced Git repository management (commit, branch management, logs) | *To be Implemented* |

---

## Project Structure

```text
├── terminal_ui.py        # Textual-based terminal user interface for Maya
├── gemini_client.py      # Google Gemini client and orchestration
├── whatsapp_bridge.py    # WhatsApp bridge controller
├── whatsapp_mcp.py       # Model Context Protocol (MCP) server integration
├── tools/
│   ├── __init__.py       # Tool registry/loader
│   ├── filesystem.py     # File system tools & git diff
│   ├── terminal.py       # Terminal execution tool
│   └── git.py            # Git integration tool (To be Implemented)
└── whatsapp_bot/         # WhatsApp bot Node.js service
```

## Getting Started

1. Install dependencies for Python components and Node.js (`whatsapp_bot`).
2. Configure your API keys and environment variables (`GEMINI_API_KEY` in `.env`).
3. Launch the terminal interface:
   ```bash
   python terminal_ui.py
   ```
