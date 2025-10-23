"""
Character Management System for RPG DM Agent.

This module handles character creation, loading, saving, and updates
for the RPG DM Agent application.
"""

import json
import logging
import os
from datetime import datetime
from typing import Any


class CharacterManager:
    """
    Manages character creation, loading, and updates.

    This class handles all character-related operations including creation,
    loading, saving, and attribute management for the RPG DM Agent.
    """

    def __init__(
        self, characters_dir: str = "characters", templates_dir: str = "templates"
    ) -> None:
        """
        Initialize the CharacterManager.

        Args:
            characters_dir: Directory to store character files.
            templates_dir: Directory containing character templates.
        """
        self.characters_dir = characters_dir
        self.templates_dir = templates_dir
        self.logger = logging.getLogger(__name__)

        self._ensure_directories_exist()

    def _ensure_directories_exist(self) -> None:
        """Ensure required directories exist."""
        os.makedirs(self.characters_dir, exist_ok=True)
        os.makedirs(self.templates_dir, exist_ok=True)

    def create_character(
        self,
        character_name: str,
        template_name: str = "default",
        custom_attributes: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Create a new character from a template.

        Args:
            character_name: Name of the character.
            template_name: Name of the template to use.
            custom_attributes: Custom attributes to override template defaults.

        Returns:
            Character data dictionary.

        Raises:
            Exception: If character creation fails.
        """
        try:
            template = self._load_template(template_name)
            character = self._build_character_from_template(
                character_name, template, custom_attributes
            )
            self._initialize_character_defaults(character)
            self.save_character(character)

            self.logger.info(f"Created new character: {character_name}")
            return character

        except Exception as e:
            self.logger.error(f"Error creating character '{character_name}': {e}")
            raise

    def _build_character_from_template(
        self,
        character_name: str,
        template: dict[str, Any],
        custom_attributes: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Build character data from template and custom attributes."""
        character = template.copy()
        character["name"] = character_name
        character["created_at"] = datetime.now().isoformat()
        character["last_updated"] = datetime.now().isoformat()

        if custom_attributes:
            character.update(custom_attributes)

        return character

    def _initialize_character_defaults(self, character: dict[str, Any]) -> None:
        """Initialize default values for character if not present."""
        defaults = {
            "experience_points": 0,
            "level": 1,
            "status_effects": [],
            "inventory": [],
            "journal_entries": [],
        }

        for key, default_value in defaults.items():
            if key not in character:
                character[key] = default_value

    def load_character(self, character_name: str) -> dict[str, Any] | None:
        """
        Load an existing character.

        Args:
            character_name: Name of the character to load.

        Returns:
            Character data dictionary or None if not found.
        """
        try:
            character_file = self._get_character_file_path(character_name)

            if not os.path.exists(character_file):
                self.logger.warning(f"Character file not found: {character_file}")
                return None

            character = self._load_character_from_file(character_file)
            self.logger.info(f"Loaded character: {character_name}")
            return character

        except Exception as e:
            self.logger.error(f"Error loading character '{character_name}': {e}")
            return None

    def _get_character_file_path(self, character_name: str) -> str:
        """Get the file path for a character."""
        return os.path.join(self.characters_dir, f"{character_name}.json")

    def _load_character_from_file(self, file_path: str) -> dict[str, Any]:
        """Load character data from a JSON file."""
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)

    def save_character(self, character: dict[str, Any]) -> bool:
        """
        Save character data to file.

        Args:
            character: Character data dictionary.

        Returns:
            True if successful, False otherwise.
        """
        try:
            character_name = character.get("name", "unnamed")
            character_file = self._get_character_file_path(character_name)

            self._update_character_timestamp(character)
            self._write_character_to_file(character, character_file)

            self.logger.info(f"Saved character: {character_name}")
            return True

        except Exception as e:
            self.logger.error(f"Error saving character: {e}")
            return False

    def _update_character_timestamp(self, character: dict[str, Any]) -> None:
        """Update the last_updated timestamp for a character."""
        character["last_updated"] = datetime.now().isoformat()

    def _write_character_to_file(
        self, character: dict[str, Any], file_path: str
    ) -> None:
        """Write character data to a JSON file."""
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(character, f, indent=2, ensure_ascii=False)

    def _load_template(self, template_name: str) -> dict[str, Any]:
        """
        Load a character template.

        Args:
            template_name: Name of the template to load.

        Returns:
            Template data dictionary.

        Raises:
            FileNotFoundError: If template file is not found.
        """
        try:
            template_file = self._get_template_file_path(template_name)
            template = self._load_character_from_file(template_file)

            self.logger.info(f"Loaded template: {template_name}")
            return template

        except Exception as e:
            self.logger.error(f"Error loading template '{template_name}': {e}")
            raise

    def _get_template_file_path(self, template_name: str) -> str:
        """Get the file path for a template."""
        if not template_name.endswith(".json"):
            template_name += ".json"
        return os.path.join(self.templates_dir, template_name)

    def list_characters(self) -> list[str]:
        """
        List all available characters.

        Returns:
            List of character names.
        """
        try:
            return self._list_files_in_directory(self.characters_dir, ".json")
        except Exception as e:
            self.logger.error(f"Error listing characters: {e}")
            return []

    def list_templates(self) -> list[str]:
        """
        List all available templates.

        Returns:
            List of template names.
        """
        try:
            return self._list_files_in_directory(self.templates_dir, ".json")
        except Exception as e:
            self.logger.error(f"Error listing templates: {e}")
            return []

    def _list_files_in_directory(self, directory: str, extension: str) -> list[str]:
        """List files in a directory with a specific extension."""
        files = []
        for filename in os.listdir(directory):
            if filename.endswith(extension):
                name = filename[: -len(extension)]  # Remove extension
                files.append(name)
        return files

    def update_character_attribute(
        self, character: dict[str, Any], attribute_path: str, value: Any
    ) -> bool:
        """
        Update a specific character attribute.

        Args:
            character: Character data dictionary.
            attribute_path: Dot-separated path to attribute (e.g., 'attributes.strength').
            value: New value for the attribute.

        Returns:
            True if successful, False otherwise.
        """
        try:
            self._set_nested_attribute(character, attribute_path, value)
            self._update_character_timestamp(character)

            self.logger.info(f"Updated character attribute {attribute_path} to {value}")
            return True

        except Exception as e:
            self.logger.error(
                f"Error updating character attribute {attribute_path}: {e}"
            )
            return False

    def _set_nested_attribute(
        self, data: dict[str, Any], path: str, value: Any
    ) -> None:
        """Set a nested attribute using dot notation."""
        keys = path.split(".")
        current = data

        # Navigate to the parent of the target attribute
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        # Set the final attribute
        current[keys[-1]] = value

    def add_experience(self, character: dict[str, Any], amount: int) -> bool:
        """
        Add experience points to a character.

        Args:
            character: Character data dictionary.
            amount: Amount of experience to add.

        Returns:
            True if successful, False otherwise.
        """
        try:
            current_xp = character.get("experience_points", 0)
            character["experience_points"] = current_xp + amount
            self._update_character_timestamp(character)

            character_name = character.get("name", "character")
            total_xp = character["experience_points"]
            self.logger.info(
                f"Added {amount} XP to {character_name} (total: {total_xp})"
            )
            return True

        except Exception as e:
            self.logger.error(f"Error adding experience: {e}")
            return False

    def add_status_effect(
        self,
        character: dict[str, Any],
        effect_name: str,
        duration: int = -1,
        description: str = "",
    ) -> bool:
        """
        Add a status effect to a character.

        Args:
            character: Character data dictionary.
            effect_name: Name of the status effect.
            duration: Duration in turns (-1 for permanent until removed).
            description: Description of the effect.

        Returns:
            True if successful, False otherwise.
        """
        try:
            self._ensure_status_effects_list(character)
            effect = self._create_status_effect(effect_name, duration, description)
            character["status_effects"].append(effect)
            self._update_character_timestamp(character)

            character_name = character.get("name", "character")
            self.logger.info(f"Added status effect '{effect_name}' to {character_name}")
            return True

        except Exception as e:
            self.logger.error(f"Error adding status effect: {e}")
            return False

    def remove_status_effect(self, character: dict[str, Any], effect_name: str) -> bool:
        """
        Remove a status effect from a character.

        Args:
            character: Character data dictionary.
            effect_name: Name of the status effect to remove.

        Returns:
            True if successful, False otherwise.
        """
        try:
            if "status_effects" not in character:
                return True

            character["status_effects"] = [
                effect
                for effect in character["status_effects"]
                if effect.get("name") != effect_name
            ]
            self._update_character_timestamp(character)

            character_name = character.get("name", "character")
            self.logger.info(
                f"Removed status effect '{effect_name}' from {character_name}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Error removing status effect: {e}")
            return False

    def _ensure_status_effects_list(self, character: dict[str, Any]) -> None:
        """Ensure character has a status_effects list."""
        if "status_effects" not in character:
            character["status_effects"] = []

    def _create_status_effect(
        self, effect_name: str, duration: int, description: str
    ) -> dict[str, Any]:
        """Create a status effect dictionary."""
        return {
            "name": effect_name,
            "duration": duration,
            "description": description,
            "applied_at": datetime.now().isoformat(),
        }
