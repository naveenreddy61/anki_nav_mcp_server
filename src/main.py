#!/usr/bin/env python3
"""
Anki MCP Server - A Model Context Protocol server for Anki integration.

This server provides tools for interacting with Anki through the AnkiConnect add-on,
allowing LLMs to create and manage Anki flashcards programmatically.
"""

import sys
import logging
from typing import Dict, List, Any, Optional

from fastmcp import FastMCP
from .anki_client import AnkiClient, AnkiConnectError
from .tools import AnkiTools


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP(
    name="anki-connect-server",
    instructions="""
    This server provides tools for interacting with Anki flashcard software through AnkiConnect.
    
    Prerequisites:
    1. Anki must be running
    2. AnkiConnect add-on must be installed and enabled
    
    Available tools:
    - list_decks: List all available Anki decks
    - create_deck: Create a new deck
    - create_note: Create a new flashcard note
    - batch_create_notes: Create multiple notes at once
    """
)

# Initialize Anki client and tools
anki_client = AnkiClient()
anki_tools = AnkiTools(anki_client)


@mcp.tool
def list_decks() -> Dict[str, Any]:
    """
    List all available Anki decks.
    
    Returns:
        Dictionary containing list of deck names and count
    """
    try:
        anki_client.check_connection()
        return anki_tools.list_decks()
    except Exception as e:
        logger.error(f"Failed to list decks: {e}")
        raise


@mcp.tool
def create_deck(name: str) -> Dict[str, Any]:
    """
    Create a new Anki deck.
    
    Args:
        name: Name of the deck to create
        
    Returns:
        Dictionary containing deck creation details
    """
    try:
        anki_client.check_connection()
        return anki_tools.create_deck(name)
    except Exception as e:
        logger.error(f"Failed to create deck '{name}': {e}")
        raise


@mcp.tool
def create_note(
    deck: str,
    note_type: str,
    fields: Dict[str, str],
    tags: Optional[List[str]] = None,
    allow_duplicate: bool = False
) -> Dict[str, Any]:
    """
    Create a new note (flashcard) in Anki.
    
    Args:
        deck: Name of the deck to add the note to
        note_type: Type of note (e.g., "Basic", "Cloze", "Basic (and reversed card)")
        fields: Dictionary mapping field names to their values (e.g., {"Front": "Question", "Back": "Answer"})
        tags: Optional list of tags to add to the note
        allow_duplicate: Whether to allow creating duplicate notes
        
    Returns:
        Dictionary containing note creation details
        
    Example:
        create_note(
            deck="My Deck",
            note_type="Basic", 
            fields={"Front": "What is 2+2?", "Back": "4"},
            tags=["math", "basic"]
        )
    """
    try:
        anki_client.check_connection()
        return anki_tools.create_note(
            deck=deck,
            note_type=note_type,
            fields=fields,
            tags=tags,
            allow_duplicate=allow_duplicate
        )
    except Exception as e:
        logger.error(f"Failed to create note in deck '{deck}': {e}")
        raise


@mcp.tool
def batch_create_notes(
    notes: List[Dict[str, Any]],
    allow_duplicate: bool = False,
    stop_on_error: bool = False
) -> Dict[str, Any]:
    """
    Create multiple notes at once.
    
    Args:
        notes: List of note dictionaries, each containing:
            - deck: Name of the deck
            - note_type: Type of note
            - fields: Dictionary of field names to values
            - tags: Optional list of tags
        allow_duplicate: Whether to allow duplicate notes
        stop_on_error: Whether to stop processing on first error
        
    Returns:
        Dictionary containing batch creation results
        
    Example:
        batch_create_notes([
            {
                "deck": "Spanish",
                "note_type": "Basic",
                "fields": {"Front": "hola", "Back": "hello"},
                "tags": ["spanish", "greetings"]
            },
            {
                "deck": "Spanish", 
                "note_type": "Basic",
                "fields": {"Front": "adiós", "Back": "goodbye"},
                "tags": ["spanish", "greetings"]
            }
        ])
    """
    try:
        anki_client.check_connection()
        return anki_tools.batch_create_notes(
            notes=notes,
            allow_duplicate=allow_duplicate,
            stop_on_error=stop_on_error
        )
    except Exception as e:
        logger.error(f"Failed to batch create notes: {e}")
        raise


def main():
    """Main entry point for the Anki MCP server."""
    try:
        logger.info("Starting Anki MCP Server...")
        
        # Test connection to AnkiConnect on startup
        try:
            anki_client.check_connection()
            logger.info("Successfully connected to AnkiConnect")
        except AnkiConnectError as e:
            logger.warning(f"AnkiConnect connection test failed: {e}")
            logger.warning("Server will still start, but tools may fail until Anki is running")
        
        # Run the server
        mcp.run()
        
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()