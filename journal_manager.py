"""
Journal Management System for RPG DM Agent
Handles adventure journal creation and updates
"""

import logging
import os
from datetime import datetime

import markdown


class JournalManager:
    """Manages adventure journals and narrative content"""

    def __init__(self, journals_dir: str = "journals", media_dir: str = "media"):
        self.journals_dir = journals_dir
        self.media_dir = media_dir
        self.logger = logging.getLogger(__name__)

        # Ensure directories exist
        os.makedirs(self.journals_dir, exist_ok=True)
        os.makedirs(self.media_dir, exist_ok=True)

    def create_journal(self, character_name: str, adventure_title: str = None) -> str:
        """
        Create a new adventure journal

        Args:
            character_name: Name of the character
            adventure_title: Title of the adventure (optional)

        Returns:
            Path to the created journal file
        """
        try:
            if not adventure_title:
                adventure_title = f"{character_name}'s Adventure"

            journal_filename = f"{character_name}_journey.md"
            journal_path = os.path.join(self.journals_dir, journal_filename)

            # Create initial journal content
            journal_content = self._create_journal_template(
                character_name, adventure_title
            )

            with open(journal_path, "w", encoding="utf-8") as f:
                f.write(journal_content)

            self.logger.info(f"Created journal: {journal_path}")
            return journal_path

        except Exception as e:
            self.logger.error(f"Error creating journal for {character_name}: {e}")
            raise

    def _create_journal_template(
        self, character_name: str, adventure_title: str
    ) -> str:
        """Create the initial journal template"""
        current_date = datetime.now().strftime("%B %d, %Y")

        template = f"""# {adventure_title}

**Character:** {character_name}
**Date:** {current_date}
**Status:** Active Adventure

---

## Chapter 1: The Beginning

*The adventure begins...*

---

## Session Log

### Session 1 - {current_date}

*The story unfolds as our hero embarks on their journey...*

---

## Character Development

### Experience Gained
- *Experience points and character growth will be tracked here*

### Notable Achievements
- *Significant accomplishments and milestones*

### Equipment Changes
- *New items acquired or lost*

---

## World Notes

### Locations Visited
- *Places discovered and explored*

### NPCs Met
- *Important characters encountered*

### Lore Discovered
- *World-building information and secrets*

---

## Combat Encounters

### Battle Log
- *Significant combat encounters and their outcomes*

---

*This journal will be updated as the adventure progresses...*
"""
        return template

    def add_journal_entry(
        self,
        character_name: str,
        entry_text: str,
        entry_type: str = "narrative",
        image_paths: list[str] = None,
        session_number: int = None,
    ) -> bool:
        """
        Add an entry to the character's journal

        Args:
            character_name: Name of the character
            entry_text: Text content of the entry
            entry_type: Type of entry (narrative, combat, dialogue, etc.)
            image_paths: List of image file paths to include
            session_number: Session number (optional)

        Returns:
            True if successful, False otherwise
        """
        try:
            journal_path = os.path.join(
                self.journals_dir, f"{character_name}_journey.md"
            )

            if not os.path.exists(journal_path):
                # Create journal if it doesn't exist
                self.create_journal(character_name)

            # Read current journal content
            with open(journal_path, encoding="utf-8") as f:
                current_content = f.read()

            # Create new entry
            entry = self._format_journal_entry(
                entry_text, entry_type, image_paths, session_number
            )

            # Insert entry before the final section
            if "## World Notes" in current_content:
                # Insert before World Notes section
                sections = current_content.split("## World Notes")
                new_content = sections[0] + entry + "\n\n## World Notes" + sections[1]
            else:
                # Append to end
                new_content = current_content + "\n\n" + entry

            # Write updated content
            with open(journal_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            self.logger.info(f"Added {entry_type} entry to {character_name}'s journal")
            return True

        except Exception as e:
            self.logger.error(f"Error adding journal entry: {e}")
            return False

    def _format_journal_entry(
        self,
        entry_text: str,
        entry_type: str,
        image_paths: list[str] = None,
        session_number: int = None,
    ) -> str:
        """Format a journal entry with proper Markdown"""
        timestamp = datetime.now().strftime("%H:%M")

        # Create entry header
        if session_number:
            header = f"### Session {session_number} - {timestamp}"
        else:
            header = f"### {entry_type.title()} Entry - {timestamp}"

        # Format entry text
        formatted_text = entry_text.strip()

        # Add images if provided
        image_section = ""
        if image_paths:
            image_section = "\n\n"
            for image_path in image_paths:
                # Convert to relative path for Markdown
                relative_path = os.path.relpath(image_path, self.journals_dir)
                image_section += f"![Scene Image]({relative_path})\n\n"

        # Combine all parts
        entry = f"{header}\n\n{formatted_text}{image_section}\n\n---\n\n"

        return entry

    def update_character_section(
        self, character_name: str, section_name: str, content: str
    ) -> bool:
        """
        Update a specific section in the character's journal

        Args:
            character_name: Name of the character
            section_name: Name of the section to update
            content: New content for the section

        Returns:
            True if successful, False otherwise
        """
        try:
            journal_path = os.path.join(
                self.journals_dir, f"{character_name}_journey.md"
            )

            if not os.path.exists(journal_path):
                self.logger.warning(f"Journal not found: {journal_path}")
                return False

            # Read current content
            with open(journal_path, encoding="utf-8") as f:
                current_content = f.read()

            # Find and replace section
            section_header = f"### {section_name}"
            if section_header in current_content:
                # Replace existing section
                start_marker = section_header
                end_marker = "### "

                start_idx = current_content.find(start_marker)
                if start_idx != -1:
                    # Find next section or end of file
                    next_section_idx = current_content.find(
                        end_marker, start_idx + len(start_marker)
                    )
                    if next_section_idx == -1:
                        # Replace to end of file
                        new_content = (
                            current_content[:start_idx]
                            + f"{section_header}\n\n{content}\n\n"
                        )
                    else:
                        # Replace to next section
                        new_content = (
                            current_content[:start_idx]
                            + f"{section_header}\n\n{content}\n\n"
                            + current_content[next_section_idx:]
                        )
                else:
                    # Section not found, append
                    new_content = (
                        current_content + f"\n\n{section_header}\n\n{content}\n\n"
                    )
            else:
                # Section doesn't exist, append
                new_content = current_content + f"\n\n{section_header}\n\n{content}\n\n"

            # Write updated content
            with open(journal_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            self.logger.info(
                f"Updated {section_name} section in {character_name}'s journal"
            )
            return True

        except Exception as e:
            self.logger.error(f"Error updating journal section: {e}")
            return False

    def add_combat_entry(
        self,
        character_name: str,
        combat_description: str,
        participants: list[str] = None,
        outcome: str = None,
    ) -> bool:
        """
        Add a combat encounter to the journal

        Args:
            character_name: Name of the character
            combat_description: Description of the combat
            participants: List of combat participants
            outcome: Outcome of the combat

        Returns:
            True if successful, False otherwise
        """
        try:
            entry_text = f"**Combat Encounter**\n\n{combat_description}"

            if participants:
                entry_text += f"\n\n**Participants:** {', '.join(participants)}"

            if outcome:
                entry_text += f"\n\n**Outcome:** {outcome}"

            return self.add_journal_entry(character_name, entry_text, "combat")

        except Exception as e:
            self.logger.error(f"Error adding combat entry: {e}")
            return False

    def add_dialogue_entry(
        self, character_name: str, speaker: str, dialogue: str, context: str = None
    ) -> bool:
        """
        Add a dialogue entry to the journal

        Args:
            character_name: Name of the character
            speaker: Name of the speaker
            dialogue: The spoken text
            context: Additional context (optional)

        Returns:
            True if successful, False otherwise
        """
        try:
            entry_text = f'**{speaker}:** "{dialogue}"'

            if context:
                entry_text += f"\n\n*{context}*"

            return self.add_journal_entry(character_name, entry_text, "dialogue")

        except Exception as e:
            self.logger.error(f"Error adding dialogue entry: {e}")
            return False

    def add_experience_entry(
        self, character_name: str, amount: int, source: str = None
    ) -> bool:
        """
        Add an experience gain entry to the journal

        Args:
            character_name: Name of the character
            amount: Amount of experience gained
            source: Source of the experience (optional)

        Returns:
            True if successful, False otherwise
        """
        try:
            entry_text = f"Gained {amount} experience points"

            if source:
                entry_text += f" from {source}"

            return self.update_character_section(
                character_name, "Experience Gained", entry_text
            )

        except Exception as e:
            self.logger.error(f"Error adding experience entry: {e}")
            return False

    def add_equipment_entry(
        self,
        character_name: str,
        item_name: str,
        action: str = "acquired",
        description: str = None,
    ) -> bool:
        """
        Add an equipment change entry to the journal

        Args:
            character_name: Name of the character
            item_name: Name of the item
            action: Action taken (acquired, lost, used, etc.)
            description: Additional description (optional)

        Returns:
            True if successful, False otherwise
        """
        try:
            entry_text = f"{action.title()} {item_name}"

            if description:
                entry_text += f" - {description}"

            return self.update_character_section(
                character_name, "Equipment Changes", entry_text
            )

        except Exception as e:
            self.logger.error(f"Error adding equipment entry: {e}")
            return False

    def get_journal_content(self, character_name: str) -> str | None:
        """
        Get the full content of a character's journal

        Args:
            character_name: Name of the character

        Returns:
            Journal content or None if not found
        """
        try:
            journal_path = os.path.join(
                self.journals_dir, f"{character_name}_journey.md"
            )

            if not os.path.exists(journal_path):
                return None

            with open(journal_path, encoding="utf-8") as f:
                return f.read()

        except Exception as e:
            self.logger.error(f"Error reading journal: {e}")
            return None

    def convert_to_html(self, character_name: str) -> str | None:
        """
        Convert journal to HTML format

        Args:
            character_name: Name of the character

        Returns:
            HTML content or None if conversion fails
        """
        try:
            journal_content = self.get_journal_content(character_name)
            if not journal_content:
                return None

            # Configure markdown extensions
            md = markdown.Markdown(extensions=["tables", "fenced_code", "toc"])
            html_content = md.convert(journal_content)

            return html_content

        except Exception as e:
            self.logger.error(f"Error converting journal to HTML: {e}")
            return None

    def list_journals(self) -> list[str]:
        """
        List all available journals

        Returns:
            List of character names with journals
        """
        try:
            journals = []
            for filename in os.listdir(self.journals_dir):
                if filename.endswith("_journey.md"):
                    character_name = filename.replace("_journey.md", "")
                    journals.append(character_name)

            return journals

        except Exception as e:
            self.logger.error(f"Error listing journals: {e}")
            return []
