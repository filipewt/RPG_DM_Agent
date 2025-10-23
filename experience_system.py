"""
Experience and Leveling System for RPG DM Agent
Handles character progression and level-up mechanics
"""

import logging
from typing import Any

from character_manager import CharacterManager
from rule_engine import RuleEngine


class ExperienceSystem:
    """Handles character experience and leveling"""

    def __init__(self, character_manager: CharacterManager, rule_engine: RuleEngine):
        self.character_manager = character_manager
        self.rule_engine = rule_engine
        self.logger = logging.getLogger(__name__)

    def award_experience(
        self, character: dict[str, Any], amount: int, source: str = None
    ) -> bool:
        """
        Award experience points to a character

        Args:
            character: Character data dictionary
            amount: Amount of experience to award
            source: Source of the experience (optional)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Add experience
            success = self.character_manager.add_experience(character, amount)

            if success:
                # Log the experience gain
                if source:
                    self.logger.info(
                        f"Awarded {amount} XP to {character.get('name', 'character')} from {source}"
                    )
                else:
                    self.logger.info(
                        f"Awarded {amount} XP to {character.get('name', 'character')}"
                    )

                # Check for level up
                if self.rule_engine.check_level_up(character):
                    self.logger.info(
                        f"{character.get('name', 'character')} is ready to level up!"
                    )

            return success

        except Exception as e:
            self.logger.error(f"Error awarding experience: {e}")
            return False

    def check_level_up_available(self, character: dict[str, Any]) -> bool:
        """
        Check if character can level up

        Args:
            character: Character data dictionary

        Returns:
            True if character can level up
        """
        return self.rule_engine.check_level_up(character)

    def get_level_up_options(self, character: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Get available level-up options for a character

        Args:
            character: Character data dictionary

        Returns:
            List of level-up options
        """
        try:
            current_level = character.get("level", 1)
            class_name = character.get("class", "fighter")

            # Get class-specific level-up options
            level_up_rules = self.rule_engine.get_rule(
                "character_creation", f"leveling.{class_name}"
            )

            if not level_up_rules:
                # Default level-up options
                return self._get_default_level_up_options(current_level)

            options = []

            # Attribute improvements
            if level_up_rules.get("attribute_improvements", False):
                options.append(
                    {
                        "type": "attribute",
                        "name": "Improve Attribute",
                        "description": "Increase one attribute by 1 point",
                        "cost": level_up_rules.get("attribute_cost", 1000),
                        "max_uses": level_up_rules.get("max_attribute_improvements", 1),
                    }
                )

            # Skill improvements
            if level_up_rules.get("skill_improvements", False):
                options.append(
                    {
                        "type": "skill",
                        "name": "Improve Skill",
                        "description": "Increase one skill by 1 rank",
                        "cost": level_up_rules.get("skill_cost", 500),
                        "max_uses": level_up_rules.get("max_skill_improvements", 2),
                    }
                )

            # New abilities
            if level_up_rules.get("new_abilities", False):
                for ability in level_up_rules.get("abilities", []):
                    if ability.get("level", 1) <= current_level:
                        options.append(
                            {
                                "type": "ability",
                                "name": ability.get("name", "New Ability"),
                                "description": ability.get(
                                    "description", "A new ability"
                                ),
                                "cost": ability.get("cost", 1000),
                                "ability_data": ability,
                            }
                        )

            return options

        except Exception as e:
            self.logger.error(f"Error getting level-up options: {e}")
            return []

    def _get_default_level_up_options(self, level: int) -> list[dict[str, Any]]:
        """Get default level-up options if no class-specific rules exist"""
        options = []

        # Every 4 levels, allow attribute improvement
        if level % 4 == 0:
            options.append(
                {
                    "type": "attribute",
                    "name": "Improve Attribute",
                    "description": "Increase one attribute by 1 point",
                    "cost": 1000,
                    "max_uses": 1,
                }
            )

        # Every level, allow skill improvements
        options.append(
            {
                "type": "skill",
                "name": "Improve Skill",
                "description": "Increase one skill by 1 rank",
                "cost": 500,
                "max_uses": 2,
            }
        )

        return options

    def apply_level_up(
        self, character: dict[str, Any], option: dict[str, Any], details: dict[str, Any]
    ) -> bool:
        """
        Apply a level-up option to a character

        Args:
            character: Character data dictionary
            option: Level-up option chosen
            details: Specific details for the option (e.g., which attribute/skill)

        Returns:
            True if successful, False otherwise
        """
        try:
            option_type = option.get("type")

            if option_type == "attribute":
                return self._apply_attribute_improvement(character, details)
            elif option_type == "skill":
                return self._apply_skill_improvement(character, details)
            elif option_type == "ability":
                return self._apply_ability_gain(character, option, details)
            else:
                self.logger.error(f"Unknown level-up option type: {option_type}")
                return False

        except Exception as e:
            self.logger.error(f"Error applying level-up: {e}")
            return False

    def _apply_attribute_improvement(
        self, character: dict[str, Any], details: dict[str, Any]
    ) -> bool:
        """Apply attribute improvement"""
        try:
            attribute_name = details.get("attribute")
            if not attribute_name:
                self.logger.error("No attribute specified for improvement")
                return False

            # Get current attribute value
            current_value = character.get("attributes", {}).get(attribute_name, 10)

            # Increase attribute
            new_value = current_value + 1

            # Update character
            success = self.character_manager.update_character_attribute(
                character, f"attributes.{attribute_name}", new_value
            )

            if success:
                self.logger.info(
                    f"Increased {attribute_name} from {current_value} to {new_value}"
                )

            return success

        except Exception as e:
            self.logger.error(f"Error applying attribute improvement: {e}")
            return False

    def _apply_skill_improvement(
        self, character: dict[str, Any], details: dict[str, Any]
    ) -> bool:
        """Apply skill improvement"""
        try:
            skill_name = details.get("skill")
            if not skill_name:
                self.logger.error("No skill specified for improvement")
                return False

            # Get current skill value
            current_value = character.get("skills", {}).get(skill_name, 0)

            # Increase skill
            new_value = current_value + 1

            # Update character
            success = self.character_manager.update_character_attribute(
                character, f"skills.{skill_name}", new_value
            )

            if success:
                self.logger.info(
                    f"Increased {skill_name} from {current_value} to {new_value}"
                )

            return success

        except Exception as e:
            self.logger.error(f"Error applying skill improvement: {e}")
            return False

    def _apply_ability_gain(
        self, character: dict[str, Any], option: dict[str, Any], details: dict[str, Any]
    ) -> bool:
        """Apply ability gain"""
        try:
            ability_name = option.get("name")
            ability_data = option.get("ability_data", {})

            # Add ability to character
            if "abilities" not in character:
                character["abilities"] = []

            character["abilities"].append(
                {
                    "name": ability_name,
                    "description": ability_data.get("description", ""),
                    "gained_at": character.get("level", 1),
                    "details": ability_data,
                }
            )

            # Update timestamp
            character["last_updated"] = (
                self.character_manager.datetime.now().isoformat()
            )

            self.logger.info(f"Gained new ability: {ability_name}")
            return True

        except Exception as e:
            self.logger.error(f"Error applying ability gain: {e}")
            return False

    def complete_level_up(self, character: dict[str, Any]) -> bool:
        """
        Complete the level-up process for a character

        Args:
            character: Character data dictionary

        Returns:
            True if successful, False otherwise
        """
        try:
            # Increase level
            current_level = character.get("level", 1)
            new_level = current_level + 1

            # Update level
            success = self.character_manager.update_character_attribute(
                character, "level", new_level
            )

            if success:
                # Update hit points
                new_hp = self.rule_engine.calculate_hit_points(character)
                self.character_manager.update_character_attribute(
                    character, "max_hit_points", new_hp
                )

                # Update current hit points if they were at maximum
                current_hp = character.get(
                    "current_hit_points", character.get("max_hit_points", new_hp)
                )
                if current_hp == character.get("max_hit_points", new_hp):
                    self.character_manager.update_character_attribute(
                        character, "current_hit_points", new_hp
                    )

                self.logger.info(
                    f"{character.get('name', 'character')} leveled up to level {new_level}!"
                )
                return True

            return False

        except Exception as e:
            self.logger.error(f"Error completing level-up: {e}")
            return False

    def get_experience_progress(self, character: dict[str, Any]) -> dict[str, Any]:
        """
        Get experience progress information for a character

        Args:
            character: Character data dictionary

        Returns:
            Dictionary with experience progress information
        """
        try:
            current_level = character.get("level", 1)
            current_xp = character.get("experience_points", 0)

            # Get XP requirements
            current_level_xp = self.rule_engine.get_experience_requirements(
                current_level
            )
            next_level_xp = self.rule_engine.get_experience_requirements(
                current_level + 1
            )

            # Calculate progress
            xp_needed = next_level_xp - current_level_xp
            xp_gained = current_xp - current_level_xp
            progress_percentage = (
                (xp_gained / xp_needed * 100) if xp_needed > 0 else 100
            )

            return {
                "current_level": current_level,
                "current_xp": current_xp,
                "current_level_xp": current_level_xp,
                "next_level_xp": next_level_xp,
                "xp_needed": xp_needed,
                "xp_gained": xp_gained,
                "progress_percentage": progress_percentage,
                "can_level_up": self.rule_engine.check_level_up(character),
            }

        except Exception as e:
            self.logger.error(f"Error getting experience progress: {e}")
            return {}

    def calculate_encounter_xp(
        self,
        encounter_type: str,
        difficulty: str = "medium",
        participant_level: int = 1,
    ) -> int:
        """
        Calculate experience points for an encounter

        Args:
            encounter_type: Type of encounter (combat, social, exploration, etc.)
            difficulty: Difficulty level (easy, medium, hard, deadly)
            participant_level: Average level of participants

        Returns:
            Experience points to award
        """
        try:
            # Base XP by encounter type
            base_xp = {
                "combat": 100,
                "social": 50,
                "exploration": 75,
                "puzzle": 60,
                "roleplay": 40,
            }.get(encounter_type, 50)

            # Difficulty multipliers
            difficulty_multipliers = {
                "easy": 0.5,
                "medium": 1.0,
                "hard": 1.5,
                "deadly": 2.0,
            }

            multiplier = difficulty_multipliers.get(difficulty, 1.0)

            # Level scaling
            level_multiplier = 1 + (participant_level - 1) * 0.2

            # Calculate final XP
            final_xp = int(base_xp * multiplier * level_multiplier)

            return max(10, final_xp)  # Minimum 10 XP

        except Exception as e:
            self.logger.error(f"Error calculating encounter XP: {e}")
            return 50  # Default fallback
