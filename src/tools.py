"""
MCP tools for Anki operations using AnkiConnect.
"""

from typing import Dict, List, Any, Optional
from .anki_client import AnkiClient, AnkiConnectError


class AnkiTools:
    """Collection of MCP tools for Anki operations."""
    
    def __init__(self, anki_client: AnkiClient):
        """
        Initialize AnkiTools.
        
        Args:
            anki_client: AnkiClient instance for communicating with Anki
        """
        self.anki_client = anki_client
    
    def list_decks(self) -> Dict[str, Any]:
        """
        List all available Anki decks.
        
        Returns:
            Dictionary containing list of decks and count
        """
        try:
            decks = self.anki_client.get_deck_names()
            return {
                "decks": decks,
                "count": len(decks)
            }
        except AnkiConnectError as e:
            raise Exception(f"Failed to list decks: {str(e)}")
    
    def create_deck(self, name: str) -> Dict[str, Any]:
        """
        Create a new Anki deck.
        
        Args:
            name: Name of the deck to create
            
        Returns:
            Dictionary containing deck ID and name
        """
        if not name:
            raise ValueError("Deck name is required")
        
        try:
            deck_id = self.anki_client.create_deck(name)
            return {
                "deck_id": deck_id,
                "name": name,
                "success": True
            }
        except AnkiConnectError as e:
            raise Exception(f"Failed to create deck '{name}': {str(e)}")
    
    def create_note(
        self,
        deck: str,
        note_type: str,
        fields: Dict[str, str],
        tags: Optional[List[str]] = None,
        allow_duplicate: bool = False
    ) -> Dict[str, Any]:
        """
        Create a new note in Anki.
        
        Args:
            deck: Name of the deck
            note_type: Name of the note type/model
            fields: Dictionary of field names to values
            tags: List of tags (optional)
            allow_duplicate: Whether to allow duplicate notes
            
        Returns:
            Dictionary containing note ID and creation details
        """
        if not deck:
            raise ValueError("Deck name is required")
        if not note_type:
            raise ValueError("Note type is required")
        if not fields:
            raise ValueError("Fields are required")
        
        try:
            # Check if deck exists, create if not
            existing_decks = self.anki_client.get_deck_names()
            if deck not in existing_decks:
                self.anki_client.create_deck(deck)
            
            # Check if note type exists
            existing_models = self.anki_client.get_model_names()
            if note_type not in existing_models:
                raise ValueError(f"Note type '{note_type}' does not exist")
            
            # Get valid field names for the model
            valid_fields = self.anki_client.get_model_field_names(note_type)
            
            # Normalize fields to match model field names
            normalized_fields = {}
            for field_name in valid_fields:
                # Try exact match first, then case-insensitive match
                if field_name in fields:
                    normalized_fields[field_name] = fields[field_name]
                else:
                    # Case-insensitive lookup
                    for provided_field, value in fields.items():
                        if provided_field.lower() == field_name.lower():
                            normalized_fields[field_name] = value
                            break
                    else:
                        # Field not provided, set to empty string
                        normalized_fields[field_name] = ""
            
            note_id = self.anki_client.add_note(
                deck_name=deck,
                model_name=note_type,
                fields=normalized_fields,
                tags=tags or [],
                allow_duplicate=allow_duplicate
            )
            
            if note_id is None:
                return {
                    "success": False,
                    "message": "Note was not created (likely a duplicate)",
                    "deck": deck,
                    "note_type": note_type
                }
            
            return {
                "note_id": note_id,
                "deck": deck,
                "note_type": note_type,
                "success": True
            }
            
        except AnkiConnectError as e:
            raise Exception(f"Failed to create note: {str(e)}")
        except ValueError as e:
            raise Exception(str(e))
    
    def batch_create_notes(
        self,
        notes: List[Dict[str, Any]],
        allow_duplicate: bool = False,
        stop_on_error: bool = False
    ) -> Dict[str, Any]:
        """
        Create multiple notes at once.
        
        Args:
            notes: List of note dictionaries with keys: deck, note_type, fields, tags
            allow_duplicate: Whether to allow duplicate notes
            stop_on_error: Whether to stop on first error
            
        Returns:
            Dictionary containing results for each note
        """
        if not notes:
            raise ValueError("Notes list cannot be empty")
        
        results = []
        successful = 0
        failed = 0
        
        try:
            # Prepare notes for batch creation
            formatted_notes = []
            
            for i, note in enumerate(notes):
                try:
                    deck = note.get("deck")
                    note_type = note.get("note_type")
                    fields = note.get("fields")
                    tags = note.get("tags", [])
                    
                    if not deck:
                        raise ValueError(f"Note {i}: Deck name is required")
                    if not note_type:
                        raise ValueError(f"Note {i}: Note type is required")
                    if not fields:
                        raise ValueError(f"Note {i}: Fields are required")
                    
                    # Check if deck exists, create if not
                    existing_decks = self.anki_client.get_deck_names()
                    if deck not in existing_decks:
                        self.anki_client.create_deck(deck)
                    
                    # Check if note type exists
                    existing_models = self.anki_client.get_model_names()
                    if note_type not in existing_models:
                        raise ValueError(f"Note {i}: Note type '{note_type}' does not exist")
                    
                    # Get valid field names for the model
                    valid_fields = self.anki_client.get_model_field_names(note_type)
                    
                    # Normalize fields
                    normalized_fields = {}
                    for field_name in valid_fields:
                        if field_name in fields:
                            normalized_fields[field_name] = fields[field_name]
                        else:
                            # Case-insensitive lookup
                            for provided_field, value in fields.items():
                                if provided_field.lower() == field_name.lower():
                                    normalized_fields[field_name] = value
                                    break
                            else:
                                normalized_fields[field_name] = ""
                    
                    formatted_note = {
                        "deckName": deck,
                        "modelName": note_type,
                        "fields": normalized_fields,
                        "tags": tags,
                        "allowDuplicate": allow_duplicate
                    }
                    formatted_notes.append(formatted_note)
                    
                    results.append({
                        "index": i,
                        "success": True,
                        "prepared": True
                    })
                    
                except Exception as e:
                    results.append({
                        "index": i,
                        "success": False,
                        "error": str(e),
                        "prepared": False
                    })
                    failed += 1
                    
                    if stop_on_error:
                        break
            
            # Add notes in batch
            if formatted_notes:
                note_ids = self.anki_client.add_notes(formatted_notes)
                
                # Update results with note IDs
                formatted_index = 0
                for i, result in enumerate(results):
                    if result.get("prepared"):
                        note_id = note_ids[formatted_index]
                        if note_id is not None:
                            result["note_id"] = note_id
                            successful += 1
                        else:
                            result["success"] = False
                            result["error"] = "Note creation failed (likely duplicate)"
                            failed += 1
                        formatted_index += 1
            
            return {
                "results": results,
                "total": len(notes),
                "successful": successful,
                "failed": failed,
                "stopped_on_error": stop_on_error and failed > 0
            }
            
        except AnkiConnectError as e:
            raise Exception(f"Failed to create notes: {str(e)}")
        except Exception as e:
            raise Exception(f"Batch note creation error: {str(e)}")