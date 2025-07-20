"""
AnkiConnect HTTP client for communicating with Anki through AnkiConnect add-on.
"""

import json
import requests
from typing import Dict, List, Any, Optional, Union


class AnkiConnectError(Exception):
    """Exception raised when AnkiConnect returns an error."""
    
    def __init__(self, message: str, error_code: Optional[str] = None):
        super().__init__(message)
        self.error_code = error_code


class AnkiClient:
    """Client for communicating with AnkiConnect API."""
    
    def __init__(self, url: str = "http://localhost:8765", timeout: int = 10):
        """
        Initialize AnkiConnect client.
        
        Args:
            url: AnkiConnect server URL (default: http://localhost:8765)
            timeout: Request timeout in seconds (default: 10)
        """
        self.url = url
        self.timeout = timeout
    
    def _request(self, action: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Send a request to AnkiConnect.
        
        Args:
            action: The action to perform
            params: Parameters for the action
            
        Returns:
            The result from AnkiConnect
            
        Raises:
            AnkiConnectError: If the request fails or AnkiConnect returns an error
        """
        payload = {
            "action": action,
            "version": 6
        }
        
        if params is not None:
            payload["params"] = params
        
        try:
            response = requests.post(
                self.url,
                json=payload,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
        except requests.exceptions.ConnectionError:
            raise AnkiConnectError(
                "Failed to connect to AnkiConnect. Please ensure Anki is running "
                "and the AnkiConnect add-on is installed and enabled."
            )
        except requests.exceptions.Timeout:
            raise AnkiConnectError(
                f"Request to AnkiConnect timed out after {self.timeout} seconds."
            )
        except requests.exceptions.RequestException as e:
            raise AnkiConnectError(f"HTTP request failed: {str(e)}")
        
        try:
            result = response.json()
        except json.JSONDecodeError:
            raise AnkiConnectError("Invalid JSON response from AnkiConnect.")
        
        if "error" in result and result["error"] is not None:
            raise AnkiConnectError(f"AnkiConnect error: {result['error']}")
        
        return result.get("result")
    
    def check_connection(self) -> bool:
        """
        Check if AnkiConnect is available.
        
        Returns:
            True if connection is successful
            
        Raises:
            AnkiConnectError: If connection fails
        """
        version = self._request("version")
        if version != 6:
            raise AnkiConnectError(f"Unsupported AnkiConnect version: {version}")
        return True
    
    def get_deck_names(self) -> List[str]:
        """
        Get all deck names.
        
        Returns:
            List of deck names
        """
        return self._request("deckNames")
    
    def create_deck(self, name: str) -> int:
        """
        Create a new deck.
        
        Args:
            name: Name of the deck to create
            
        Returns:
            Deck ID
        """
        result = self._request("createDeck", {"deck": name})
        return result
    
    def get_model_names(self) -> List[str]:
        """
        Get all note type (model) names.
        
        Returns:
            List of model names
        """
        return self._request("modelNames")
    
    def get_model_field_names(self, model_name: str) -> List[str]:
        """
        Get field names for a specific model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            List of field names
        """
        return self._request("modelFieldNames", {"modelName": model_name})
    
    def add_note(
        self,
        deck_name: str,
        model_name: str,
        fields: Dict[str, str],
        tags: Optional[List[str]] = None,
        allow_duplicate: bool = False
    ) -> Optional[int]:
        """
        Add a new note.
        
        Args:
            deck_name: Name of the deck
            model_name: Name of the note type/model
            fields: Dictionary of field names to values
            tags: List of tags (optional)
            allow_duplicate: Whether to allow duplicate notes
            
        Returns:
            Note ID if successful, None if duplicate and not allowed
        """
        note = {
            "deckName": deck_name,
            "modelName": model_name,
            "fields": fields,
            "tags": tags or [],
            "options": {
                "allowDuplicate": allow_duplicate,
                "duplicateScope": "deck"
            }
        }
        
        return self._request("addNote", {"note": note})
    
    def add_notes(self, notes: List[Dict[str, Any]]) -> List[Optional[int]]:
        """
        Add multiple notes at once.
        
        Args:
            notes: List of note dictionaries with keys: deckName, modelName, fields, tags
            
        Returns:
            List of note IDs (None for failed notes)
        """
        formatted_notes = []
        for note in notes:
            formatted_note = {
                "deckName": note["deckName"],
                "modelName": note["modelName"], 
                "fields": note["fields"],
                "tags": note.get("tags", []),
                "options": {
                    "allowDuplicate": note.get("allowDuplicate", False),
                    "duplicateScope": "deck"
                }
            }
            formatted_notes.append(formatted_note)
        
        return self._request("addNotes", {"notes": formatted_notes})
    
    def find_notes(self, query: str) -> List[int]:
        """
        Find notes using Anki search syntax.
        
        Args:
            query: Anki search query
            
        Returns:
            List of note IDs
        """
        return self._request("findNotes", {"query": query})
    
    def notes_info(self, note_ids: List[int]) -> List[Dict[str, Any]]:
        """
        Get detailed information about notes.
        
        Args:
            note_ids: List of note IDs
            
        Returns:
            List of note information dictionaries
        """
        return self._request("notesInfo", {"notes": note_ids})
    
    def update_note_fields(self, note_id: int, fields: Dict[str, str]) -> None:
        """
        Update fields of an existing note.
        
        Args:
            note_id: ID of the note to update
            fields: Dictionary of field names to new values
        """
        note = {
            "id": note_id,
            "fields": fields
        }
        self._request("updateNoteFields", {"note": note})
    
    def delete_notes(self, note_ids: List[int]) -> None:
        """
        Delete notes.
        
        Args:
            note_ids: List of note IDs to delete
        """
        self._request("deleteNotes", {"notes": note_ids})