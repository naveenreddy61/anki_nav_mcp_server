# Anki MCP Server

A Model Context Protocol (MCP) server that enables LLMs to interact with Anki flashcard software through AnkiConnect. This server allows Claude and other MCP-compatible LLMs to create and manage Anki decks and flashcards programmatically.

## Features

### Core Tools
- **list_decks** - List all available Anki decks
- **create_deck** - Create a new Anki deck
- **create_note** - Create a new flashcard note (Basic or Cloze)
- **batch_create_notes** - Create multiple notes at once

### Capabilities
- Automatic deck creation if target deck doesn't exist
- Case-insensitive field mapping for note types
- Duplicate detection and handling
- Batch operations with error handling
- Support for tags and custom note types

## Prerequisites

1. **Anki Desktop Application**
   - Download and install from [apps.ankiweb.net](https://apps.ankiweb.net/)
   - Anki must be running when using the server

2. **AnkiConnect Add-on**
   - Install from Anki: Tools � Add-ons � Get Add-ons
   - Add-on code: `2055492159`
   - Or visit: [AnkiConnect on AnkiWeb](https://ankiweb.net/shared/info/2055492159)

3. **Python 3.12+**
   - Required for running the server

## Installation

### For Development

1. Clone or download this repository
2. Navigate to the project directory:
   ```bash
   cd anki_naveen_mcp_server
   ```

3. Install dependencies:
   ```bash
   uv sync
   ```

### For Usage with Claude Desktop

1. Add the server configuration to your Claude Desktop config file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

2. Add this configuration:
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

   Replace `/path/to/anki_naveen_mcp_server` with the actual path to this project.

3. Restart Claude Desktop

## Usage Examples

### Basic Flashcard Creation

```
Create an Anki card in the "Spanish" deck with:
Front: hola
Back: hello
Tags: spanish, greetings
```

### Multiple Cards at Once

```
Create these flashcards in my "Math" deck:
1. What is 2+2? � 4
2. What is 3�3? � 9
3. What is 10�2? � 5
```

### Creating a New Deck

```
Create a new Anki deck called "Programming Concepts"
```

### Cloze Deletion Cards

```
Create a cloze card in "Biology" deck:
The {{c1::mitochondria}} is the {{c2::powerhouse}} of the cell.
```

## Configuration

The server uses these default settings:
- **AnkiConnect URL**: `http://localhost:8765`
- **Timeout**: 10 seconds
- **Default behavior**: Create decks if they don't exist

## Troubleshooting

### "Failed to connect to AnkiConnect"
- Ensure Anki is running
- Verify AnkiConnect add-on is installed and enabled
- Check if Anki is showing any dialog boxes (close them)
- Restart Anki if needed

### "Note type 'X' does not exist"
- Use exact note type names (e.g., "Basic", "Cloze", "Basic (and reversed card)")
- Check available note types in Anki: Tools � Manage Note Types

### Permission or Path Issues
- Ensure the path in Claude Desktop config is correct
- Check that `uv` is installed and accessible
- Verify Python 3.12+ is available

### Testing the Connection

You can test the server manually:

```bash
# Run the server directly
uv run anki-naveen-mcp-server

# Test AnkiConnect directly
curl -X POST http://localhost:8765 \
  -H "Content-Type: application/json" \
  -d '{"action": "version", "version": 6}'
```

## Development

### Project Structure

```
anki_naveen_mcp_server/
   src/
      __init__.py
      anki_naveen_mcp_server/
          # Package entry point
         server.py         # FastMCP server and tool registration
      anki_client.py    # AnkiConnect HTTP client
      tools.py          # Business logic for Anki operations
   pyproject.toml        # Project configuration
   CLAUDE.md             # Development guidance
   README.md             # This file
```

### Adding New Features

1. Add AnkiConnect API methods to `AnkiClient` class
2. Implement business logic in `AnkiTools` class
3. Register new tools with `@mcp.tool` decorator in `main.py`

### Running Locally

```bash
uv run anki-naveen-mcp-server
```

## API Reference

### list_decks()
Returns all available Anki decks.

**Returns**: `{"decks": ["Default", "Spanish", ...], "count": 3}`

### create_deck(name: str)
Creates a new deck.

**Parameters**:
- `name`: Deck name

**Returns**: `{"deck_id": 123, "name": "My Deck", "success": true}`

### create_note(deck, note_type, fields, tags?, allow_duplicate?)
Creates a single note.

**Parameters**:
- `deck`: Deck name
- `note_type`: Note type (e.g., "Basic", "Cloze")
- `fields`: Field values (e.g., `{"Front": "Question", "Back": "Answer"}`)
- `tags`: Optional list of tags
- `allow_duplicate`: Allow duplicate notes (default: false)

**Returns**: `{"note_id": 456, "deck": "My Deck", "success": true}`

### batch_create_notes(notes, allow_duplicate?, stop_on_error?)
Creates multiple notes at once.

**Parameters**:
- `notes`: List of note objects
- `allow_duplicate`: Allow duplicates (default: false)
- `stop_on_error`: Stop on first error (default: false)

**Returns**: Detailed results for each note creation attempt

## License

This project is provided as-is for educational and personal use. See the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## Acknowledgments

- [AnkiConnect](https://foosoft.net/projects/anki-connect/) for providing the API
- [FastMCP](https://github.com/jlowin/fastmcp) for the MCP framework
- [Anki](https://apps.ankiweb.net/) for the amazing spaced repetition software
