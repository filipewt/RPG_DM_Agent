"""
Character Management System for RPG DM Agent
Handles character creation, loading, and updates
"""

import json
import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

class CharacterManager:
    """Manages character creation, loading, and updates"""
    
    def __init__(self, characters_dir: str = "characters", templates_dir: str = "templates"):
        self.characters_dir = characters_dir
        self.templates_dir = templates_dir
        self.logger = logging.getLogger(__name__)
        
        # Ensure directories exist
        os.makedirs(self.characters_dir, exist_ok=True)
        os.makedirs(self.templates_dir, exist_ok=True)
    
    def create_character(self, character_name: str, template_name: str = "default", 
                        custom_attributes: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a new character from a template
        
        Args:
            character_name: Name of the character
            template_name: Name of the template to use
            custom_attributes: Custom attributes to override template defaults
            
        Returns:
            Character data dictionary
        """
        try:
            # Load template
            template = self.load_template(template_name)
            
            # Create character from template
            character = template.copy()
            
            # Set character name and creation info
            character['name'] = character_name
            character['created_at'] = datetime.now().isoformat()
            character['last_updated'] = datetime.now().isoformat()
            
            # Apply custom attributes if provided
            if custom_attributes:
                character.update(custom_attributes)
            
            # Initialize experience and level if not present
            if 'experience_points' not in character:
                character['experience_points'] = 0
            if 'level' not in character:
                character['level'] = 1
            
            # Initialize status effects if not present
            if 'status_effects' not in character:
                character['status_effects'] = []
            
            # Initialize inventory if not present
            if 'inventory' not in character:
                character['inventory'] = []
            
            # Initialize journal entries if not present
            if 'journal_entries' not in character:
                character['journal_entries'] = []
            
            # Save character
            self.save_character(character)
            
            self.logger.info(f"Created new character: {character_name}")
            return character
            
        except Exception as e:
            self.logger.error(f"Error creating character '{character_name}': {e}")
            raise
    
    def load_character(self, character_name: str) -> Optional[Dict[str, Any]]:
        """
        Load an existing character
        
        Args:
            character_name: Name of the character to load
            
        Returns:
            Character data dictionary or None if not found
        """
        try:
            character_file = os.path.join(self.characters_dir, f"{character_name}.json")
            
            if not os.path.exists(character_file):
                self.logger.warning(f"Character file not found: {character_file}")
                return None
            
            with open(character_file, 'r', encoding='utf-8') as f:
                character = json.load(f)
            
            self.logger.info(f"Loaded character: {character_name}")
            return character
            
        except Exception as e:
            self.logger.error(f"Error loading character '{character_name}': {e}")
            return None
    
    def save_character(self, character: Dict[str, Any]) -> bool:
        """
        Save character data to file
        
        Args:
            character: Character data dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            character_name = character.get('name', 'unnamed')
            character_file = os.path.join(self.characters_dir, f"{character_name}.json")
            
            # Update last_updated timestamp
            character['last_updated'] = datetime.now().isoformat()
            
            with open(character_file, 'w', encoding='utf-8') as f:
                json.dump(character, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved character: {character_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving character: {e}")
            return False
    
    def load_template(self, template_name: str) -> Dict[str, Any]:
        """
        Load a character template
        
        Args:
            template_name: Name of the template to load
            
        Returns:
            Template data dictionary
        """
        try:
            template_file = os.path.join(self.templates_dir, f"{template_name}.json")
            
            if not os.path.exists(template_file):
                # Try with .json extension if not provided
                if not template_name.endswith('.json'):
                    template_file = os.path.join(self.templates_dir, f"{template_name}.json")
                
                if not os.path.exists(template_file):
                    raise FileNotFoundError(f"Template not found: {template_name}")
            
            with open(template_file, 'r', encoding='utf-8') as f:
                template = json.load(f)
            
            self.logger.info(f"Loaded template: {template_name}")
            return template
            
        except Exception as e:
            self.logger.error(f"Error loading template '{template_name}': {e}")
            raise
    
    def list_characters(self) -> List[str]:
        """
        List all available characters
        
        Returns:
            List of character names
        """
        try:
            characters = []
            for filename in os.listdir(self.characters_dir):
                if filename.endswith('.json'):
                    character_name = filename[:-5]  # Remove .json extension
                    characters.append(character_name)
            
            return characters
            
        except Exception as e:
            self.logger.error(f"Error listing characters: {e}")
            return []
    
    def list_templates(self) -> List[str]:
        """
        List all available templates
        
        Returns:
            List of template names
        """
        try:
            templates = []
            for filename in os.listdir(self.templates_dir):
                if filename.endswith('.json'):
                    template_name = filename[:-5]  # Remove .json extension
                    templates.append(template_name)
            
            return templates
            
        except Exception as e:
            self.logger.error(f"Error listing templates: {e}")
            return []
    
    def update_character_attribute(self, character: Dict[str, Any], 
                                 attribute_path: str, value: Any) -> bool:
        """
        Update a specific character attribute
        
        Args:
            character: Character data dictionary
            attribute_path: Dot-separated path to attribute (e.g., 'attributes.strength')
            value: New value for the attribute
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Navigate to the attribute using dot notation
            keys = attribute_path.split('.')
            current = character
            
            # Navigate to the parent of the target attribute
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            
            # Set the final attribute
            current[keys[-1]] = value
            
            # Update timestamp
            character['last_updated'] = datetime.now().isoformat()
            
            self.logger.info(f"Updated character attribute {attribute_path} to {value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating character attribute {attribute_path}: {e}")
            return False
    
    def add_experience(self, character: Dict[str, Any], amount: int) -> bool:
        """
        Add experience points to a character
        
        Args:
            character: Character data dictionary
            amount: Amount of experience to add
            
        Returns:
            True if successful, False otherwise
        """
        try:
            current_xp = character.get('experience_points', 0)
            character['experience_points'] = current_xp + amount
            
            # Update timestamp
            character['last_updated'] = datetime.now().isoformat()
            
            self.logger.info(f"Added {amount} XP to {character.get('name', 'character')} (total: {character['experience_points']})")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding experience: {e}")
            return False
    
    def add_status_effect(self, character: Dict[str, Any], effect_name: str, 
                         duration: int = -1, description: str = "") -> bool:
        """
        Add a status effect to a character
        
        Args:
            character: Character data dictionary
            effect_name: Name of the status effect
            duration: Duration in turns (-1 for permanent until removed)
            description: Description of the effect
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if 'status_effects' not in character:
                character['status_effects'] = []
            
            effect = {
                'name': effect_name,
                'duration': duration,
                'description': description,
                'applied_at': datetime.now().isoformat()
            }
            
            character['status_effects'].append(effect)
            
            # Update timestamp
            character['last_updated'] = datetime.now().isoformat()
            
            self.logger.info(f"Added status effect '{effect_name}' to {character.get('name', 'character')}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding status effect: {e}")
            return False
    
    def remove_status_effect(self, character: Dict[str, Any], effect_name: str) -> bool:
        """
        Remove a status effect from a character
        
        Args:
            character: Character data dictionary
            effect_name: Name of the status effect to remove
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if 'status_effects' not in character:
                return True
            
            # Remove all effects with the given name
            character['status_effects'] = [
                effect for effect in character['status_effects'] 
                if effect.get('name') != effect_name
            ]
            
            # Update timestamp
            character['last_updated'] = datetime.now().isoformat()
            
            self.logger.info(f"Removed status effect '{effect_name}' from {character.get('name', 'character')}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error removing status effect: {e}")
            return False
