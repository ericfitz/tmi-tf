"""TMI API client wrapper."""

import logging
import sys
from pathlib import Path
from typing import List, Optional

# Add tmi-client to path
tmi_client_path = Path.home() / "Projects" / "tmi-clients" / "python-client-generated"
if tmi_client_path.exists():
    sys.path.insert(0, str(tmi_client_path))
else:
    raise ImportError(
        f"TMI Python client not found at {tmi_client_path}. "
        "Please ensure it's available at ~/Projects/tmi-clients/python-client-generated"
    )

import tmi_client
from tmi_client.api_client import ApiClient
from tmi_client.configuration import Configuration
from tmi_client.models import Note, NoteInput, Repository, ThreatModel

from tmi_tf.auth import TMIAuthenticator
from tmi_tf.config import Config

logger = logging.getLogger(__name__)


class TMIClient:
    """Wrapper around TMI API client with authentication."""

    def __init__(self, config: Config, auth_token: Optional[str] = None):
        """
        Initialize TMI client.

        Args:
            config: Application configuration
            auth_token: Optional pre-authenticated JWT token
        """
        self.config = config

        # Configure TMI API client
        tmi_config = Configuration()
        tmi_config.host = config.tmi_server_url

        # Set authentication token
        if auth_token:
            tmi_config.api_key["bearerAuth"] = auth_token
            tmi_config.api_key_prefix["bearerAuth"] = "Bearer"

        self.api_client = ApiClient(configuration=tmi_config)
        self.threat_models_api = tmi_client.ThreatModelsApi(self.api_client)
        self.sub_resources_api = tmi_client.ThreatModelSubResourcesApi(self.api_client)

        logger.info(f"TMI client initialized for {config.tmi_server_url}")

    @classmethod
    def create_authenticated(cls, config: Config, force_refresh: bool = False) -> "TMIClient":
        """
        Create authenticated TMI client.

        Args:
            config: Application configuration
            force_refresh: Force new authentication

        Returns:
            Authenticated TMI client
        """
        authenticator = TMIAuthenticator(config)
        token = authenticator.get_token(force_refresh=force_refresh)
        return cls(config, auth_token=token)

    def get_threat_model(self, threat_model_id: str) -> ThreatModel:
        """
        Get threat model by ID.

        Args:
            threat_model_id: Threat model UUID

        Returns:
            ThreatModel object with all resources
        """
        logger.info(f"Fetching threat model: {threat_model_id}")
        try:
            threat_model = self.threat_models_api.get_threat_model(threat_model_id)
            logger.info(f"Retrieved threat model: {threat_model.name}")
            return threat_model
        except Exception as e:
            logger.error(f"Failed to get threat model: {e}")
            raise

    def get_threat_model_repositories(self, threat_model_id: str) -> List[Repository]:
        """
        Get all repositories for a threat model.

        Args:
            threat_model_id: Threat model UUID

        Returns:
            List of Repository objects
        """
        logger.info(f"Fetching repositories for threat model: {threat_model_id}")
        try:
            repositories = self.sub_resources_api.get_threat_model_repositories(
                threat_model_id
            )
            logger.info(f"Retrieved {len(repositories)} repositories")
            return repositories
        except Exception as e:
            logger.error(f"Failed to get repositories: {e}")
            raise

    def create_note(
        self, threat_model_id: str, name: str, content: str, description: str = ""
    ) -> Note:
        """
        Create a note in a threat model.

        Args:
            threat_model_id: Threat model UUID
            name: Note name
            content: Note content (markdown)
            description: Note description

        Returns:
            Created Note object
        """
        logger.info(f"Creating note '{name}' in threat model {threat_model_id}")
        try:
            note_input = NoteInput(name=name, content=content, description=description)
            note = self.sub_resources_api.create_threat_model_note(
                note_input, threat_model_id
            )
            logger.info(f"Note created successfully with ID: {note.id}")
            return note
        except Exception as e:
            logger.error(f"Failed to create note: {e}")
            raise

    def get_threat_model_notes(self, threat_model_id: str) -> List[Note]:
        """
        Get all notes for a threat model.

        Args:
            threat_model_id: Threat model UUID

        Returns:
            List of Note objects
        """
        logger.info(f"Fetching notes for threat model: {threat_model_id}")
        try:
            notes = self.sub_resources_api.get_threat_model_notes(threat_model_id)
            logger.info(f"Retrieved {len(notes)} notes")
            return notes
        except Exception as e:
            logger.error(f"Failed to get notes: {e}")
            raise

    def update_note(
        self, threat_model_id: str, note_id: str, name: str, content: str, description: str = ""
    ) -> Note:
        """
        Update an existing note.

        Args:
            threat_model_id: Threat model UUID
            note_id: Note UUID
            name: Note name
            content: Note content (markdown)
            description: Note description

        Returns:
            Updated Note object
        """
        logger.info(f"Updating note {note_id} in threat model {threat_model_id}")
        try:
            note_input = NoteInput(name=name, content=content, description=description)
            note = self.sub_resources_api.update_threat_model_note(
                threat_model_id, note_id, note_input
            )
            logger.info(f"Note updated successfully")
            return note
        except Exception as e:
            logger.error(f"Failed to update note: {e}")
            raise

    def find_note_by_name(self, threat_model_id: str, note_name: str) -> Optional[Note]:
        """
        Find a note by name in a threat model.

        Args:
            threat_model_id: Threat model UUID
            note_name: Note name to search for

        Returns:
            Note object if found, None otherwise
        """
        notes = self.get_threat_model_notes(threat_model_id)
        for note in notes:
            if note.name == note_name:
                return note
        return None

    def create_or_update_note(
        self, threat_model_id: str, name: str, content: str, description: str = ""
    ) -> Note:
        """
        Create a new note or update existing one with the same name.

        Args:
            threat_model_id: Threat model UUID
            name: Note name
            content: Note content (markdown)
            description: Note description

        Returns:
            Created or updated Note object
        """
        existing_note = self.find_note_by_name(threat_model_id, name)

        if existing_note:
            logger.info(f"Note '{name}' already exists, updating...")
            return self.update_note(
                threat_model_id, existing_note.id, name, content, description
            )
        else:
            logger.info(f"Creating new note '{name}'...")
            return self.create_note(threat_model_id, name, content, description)
