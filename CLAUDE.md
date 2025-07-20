# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Anki MCP (Model Context Protocol) server that enables LLMs to interact with Anki flashcard software through the AnkiConnect add-on. The server provides tools for creating and managing Anki decks and notes programmatically.

## Architecture

- **FastMCP Framework**: Uses FastMCP for MCP protocol implementation with STDIO transport
- **AnkiConnect Integration**: HTTP client communicating with AnkiConnect API at `http://localhost:8765`
- **Core Components**:
  - `src/anki_client.py`: HTTP client for AnkiConnect API communication
  - `src/tools.py`: Business logic for Anki operations
  - `src/main.py`: FastMCP server setup and tool registration

## Prerequisites

1. **Anki Desktop App**: Must be installed and running
2. **AnkiConnect Add-on**: Must be installed in Anki (add-on ID: 2055492159)
3. **Python 3.12+**: Required for the server

## Development Commands

- **Run server locally**: `uv run anki-naveen-mcp-server`
- **Install dependencies**: `uv sync`
- **Test AnkiConnect connection**: Ensure Anki is running, then start server

## Claude Desktop Integration

Add this configuration to Claude Desktop's `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "anki": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/anki_naveen_mcp_server",
        "run",
        "anki-naveen-mcp-server"
      ]
    }
  }
}
```

## Core MCP Tools

1. **list_decks()**: Returns all available Anki decks
2. **create_deck(name)**: Creates a new deck
3. **create_note(deck, note_type, fields, tags?, allow_duplicate?)**: Creates a single note
4. **batch_create_notes(notes, allow_duplicate?, stop_on_error?)**: Creates multiple notes

## Key Implementation Details

### AnkiConnect API Format
- All requests are POST to `http://localhost:8765`
- Request format: `{"action": "actionName", "version": 6, "params": {...}}`
- Response format: `{"result": ..., "error": null}`

### Error Handling
- Connection errors when Anki/AnkiConnect unavailable
- Field validation and normalization for different note types
- Duplicate detection (unless allow_duplicate=True)

### Field Mapping
- Case-insensitive field matching between provided fields and note type schema
- Missing fields filled with empty strings
- Automatic deck creation if target deck doesn't exist

## Common Development Tasks

### Adding New Tools
1. Add method to `AnkiTools` class in `src/tools.py`
2. Add corresponding AnkiConnect method to `AnkiClient` if needed
3. Register tool with `@mcp.tool` decorator in `src/main.py`

### Testing AnkiConnect Locally
```python
from src.anki_client import AnkiClient
client = AnkiClient()
client.check_connection()  # Should return True if Anki is running
```

### Debugging Connection Issues
- Verify Anki is running
- Check AnkiConnect add-on is enabled in Anki > Tools > Add-ons
- Test direct HTTP request: `curl -X POST http://localhost:8765 -d '{"action":"version","version":6}'`

## Error Scenarios

- **"Failed to connect to AnkiConnect"**: Anki not running or AnkiConnect not installed
- **"Note type 'X' does not exist"**: Invalid note type name provided
- **"Note was not created (likely duplicate)"**: Duplicate note detected when allow_duplicate=False
- **Field validation errors**: Missing required fields or field name mismatches