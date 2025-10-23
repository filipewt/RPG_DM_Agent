"""
Dice Rolling System for RPG DM Agent.

This module handles dice expressions and roll mechanics for Vampire: The Masquerade V5,
providing comprehensive dice rolling functionality for the RPG DM Agent.
"""

import logging
import random
import re
from typing import Any


class DiceRoller:
    """
    Handles dice rolling mechanics for Vampire: The Masquerade V5 system.

    This class provides comprehensive dice rolling functionality including
    dice pools, rouse checks, willpower rolls, and legacy dice expressions.
    """

    def __init__(self) -> None:
        """Initialize the DiceRoller."""
        self.logger = logging.getLogger(__name__)

    def roll_dice_pool(
        self, attribute: int, skill: int, difficulty: int = 2, hunger: int = 1
    ) -> dict[str, Any]:
        """
        Roll a dice pool for Vampire: The Masquerade V5.

        Args:
            attribute: Attribute dots (1-5).
            skill: Skill dots (0-5).
            difficulty: Target number of successes needed (default 2).
            hunger: Hunger level (1-5).

        Returns:
            Dictionary with roll results, successes, and special effects.
        """
        try:
            pool_size = attribute + skill

            if pool_size <= 0:
                return self._create_error_result(
                    attribute,
                    skill,
                    difficulty,
                    hunger,
                    "Dice pool must be at least 1 die",
                )

            normal_rolls, hunger_rolls = self._roll_dice_pool_dice(pool_size, hunger)
            successes = self._count_successes(normal_rolls + hunger_rolls)
            special_effects = self._check_special_effects(
                normal_rolls, hunger_rolls, successes
            )
            total_successes = self._calculate_total_successes(
                successes, special_effects
            )

            result = self._build_dice_pool_result(
                attribute,
                skill,
                difficulty,
                hunger,
                pool_size,
                normal_rolls,
                hunger_rolls,
                successes,
                total_successes,
                special_effects,
            )

            self._log_dice_pool_result(
                attribute,
                skill,
                hunger,
                difficulty,
                normal_rolls,
                hunger_rolls,
                total_successes,
            )
            return result

        except Exception as e:
            self.logger.error(f"Error rolling Vampire dice pool: {e}")
            return self._create_error_result(
                attribute, skill, difficulty, hunger, str(e)
            )

    def _create_error_result(
        self, attribute: int, skill: int, difficulty: int, hunger: int, error_msg: str
    ) -> dict[str, Any]:
        """Create an error result for dice pool roll."""
        return {
            "pool_size": 0,
            "attribute": attribute,
            "skill": skill,
            "difficulty": difficulty,
            "hunger": hunger,
            "successes": 0,
            "total_successes": 0,
            "critical": False,
            "bestial_failure": False,
            "messy_critical": False,
            "error": error_msg,
        }

    def _roll_dice_pool_dice(
        self, pool_size: int, hunger: int
    ) -> tuple[list[int], list[int]]:
        """Roll the dice for a dice pool."""
        normal_dice = min(pool_size, pool_size - hunger)
        hunger_dice = min(hunger, pool_size)

        normal_rolls = [random.randint(1, 10) for _ in range(normal_dice)]
        hunger_rolls = [random.randint(1, 10) for _ in range(hunger_dice)]

        return normal_rolls, hunger_rolls

    def _count_successes(self, rolls: list[int]) -> int:
        """Count successes in dice rolls (6+ = 1 success, 10 = 2 successes)."""
        successes = 0
        for roll in rolls:
            if roll >= 6:
                successes += 1
            if roll == 10:
                successes += 1  # 10s are worth 2 successes
        return successes

    def _check_special_effects(
        self, normal_rolls: list[int], hunger_rolls: list[int], successes: int
    ) -> dict[str, bool]:
        """Check for special effects in dice rolls."""
        tens = normal_rolls.count(10) + hunger_rolls.count(10)
        critical = tens >= 2
        bestial_failure = successes == 0 and hunger_rolls.count(1) > 0
        messy_critical = critical and len(hunger_rolls) > 0

        return {
            "critical": critical,
            "bestial_failure": bestial_failure,
            "messy_critical": messy_critical,
        }

    def _calculate_total_successes(
        self, successes: int, special_effects: dict[str, bool]
    ) -> int:
        """Calculate total successes including special effects."""
        return 4 if special_effects["critical"] else successes

    def _build_dice_pool_result(
        self,
        attribute: int,
        skill: int,
        difficulty: int,
        hunger: int,
        pool_size: int,
        normal_rolls: list[int],
        hunger_rolls: list[int],
        successes: int,
        total_successes: int,
        special_effects: dict[str, bool],
    ) -> dict[str, Any]:
        """Build the complete dice pool result dictionary."""
        return {
            "pool_size": pool_size,
            "attribute": attribute,
            "skill": skill,
            "difficulty": difficulty,
            "hunger": hunger,
            "normal_rolls": normal_rolls,
            "hunger_rolls": hunger_rolls,
            "all_rolls": normal_rolls + hunger_rolls,
            "successes": successes,
            "total_successes": total_successes,
            "critical": special_effects["critical"],
            "bestial_failure": special_effects["bestial_failure"],
            "messy_critical": special_effects["messy_critical"],
            "success": total_successes >= difficulty,
        }

    def _log_dice_pool_result(
        self,
        attribute: int,
        skill: int,
        hunger: int,
        difficulty: int,
        normal_rolls: list[int],
        hunger_rolls: list[int],
        total_successes: int,
    ) -> None:
        """Log the dice pool result."""
        self.logger.info(
            f"Vampire dice pool: {attribute}+{skill} dice, hunger {hunger}, difficulty {difficulty}"
        )
        self.logger.info(
            f"Rolls: {normal_rolls} (normal) + {hunger_rolls} (hunger) = {total_successes} successes"
        )

    def roll_rouse_check(self, hunger: int = 1) -> dict[str, Any]:
        """
        Roll a Rouse Check (1d10) - used when activating Disciplines.

        Args:
            hunger: Current hunger level.

        Returns:
            Dictionary with roll results and hunger change.
        """
        try:
            roll = random.randint(1, 10)
            success = roll >= 6
            hunger_change = 0 if success else 1

            result = {
                "roll": roll,
                "success": success,
                "hunger_change": hunger_change,
                "new_hunger": hunger + hunger_change,
            }

            self._log_rouse_check_result(roll, success, hunger_change)
            return result

        except Exception as e:
            self.logger.error(f"Error rolling Rouse check: {e}")
            return {
                "roll": 0,
                "success": False,
                "hunger_change": 1,
                "new_hunger": hunger + 1,
                "error": str(e),
            }

    def _log_rouse_check_result(
        self, roll: int, success: bool, hunger_change: int
    ) -> None:
        """Log the rouse check result."""
        status = "SUCCESS" if success else "FAILURE"
        hunger_status = f"+{hunger_change}" if hunger_change > 0 else "unchanged"
        self.logger.info(f"Rouse check: d10({roll}) - {status}, hunger {hunger_status}")

    def roll_willpower(self, willpower: int) -> dict[str, Any]:
        """
        Roll Willpower dice (1-3 dice based on willpower dots).

        Args:
            willpower: Willpower dots (1-5).

        Returns:
            Dictionary with roll results and successes.
        """
        try:
            num_dice = min(willpower, 3)  # Max 3 dice
            rolls = [random.randint(1, 10) for _ in range(num_dice)]
            successes = self._count_successes(rolls)
            critical = rolls.count(10) >= 2
            total_successes = 4 if critical else successes

            result = {
                "willpower_dots": willpower,
                "num_dice": num_dice,
                "rolls": rolls,
                "successes": successes,
                "total_successes": total_successes,
                "critical": critical,
            }

            self.logger.info(
                f"Willpower roll: {num_dice} dice = {rolls} = {total_successes} successes"
            )
            return result

        except Exception as e:
            self.logger.error(f"Error rolling Willpower: {e}")
            return {
                "willpower_dots": willpower,
                "num_dice": 0,
                "rolls": [],
                "successes": 0,
                "total_successes": 0,
                "critical": False,
                "error": str(e),
            }

    def roll_dice(self, expression: str) -> dict[str, Any]:
        """
        Legacy method for backward compatibility.

        Parse and execute dice expressions like '2d6+3', '1d20', '3d4-2'.

        Args:
            expression: Dice expression string.

        Returns:
            Dictionary with roll results, individual dice, total, and modifiers.
        """
        try:
            parsed = self._parse_dice_expression(expression)
            dice_results = self._roll_legacy_dice(parsed)
            total = sum(dice_results) + parsed["modifier"]

            result = {
                "expression": expression,
                "num_dice": parsed["num_dice"],
                "dice_size": parsed["dice_size"],
                "modifier": parsed["modifier"],
                "individual_rolls": dice_results,
                "total": total,
                "success": (
                    total >= parsed.get("target", 0) if "target" in parsed else None
                ),
            }

            self.logger.info(
                f"Dice roll: {expression} = {dice_results} + {parsed['modifier']} = {total}"
            )
            return result

        except Exception as e:
            self.logger.error(f"Error rolling dice '{expression}': {e}")
            return {"expression": expression, "error": str(e), "total": 0}

    def _roll_legacy_dice(self, parsed: dict[str, int]) -> list[int]:
        """Roll dice for legacy dice expressions."""
        return [
            random.randint(1, parsed["dice_size"]) for _ in range(parsed["num_dice"])
        ]

    def _parse_dice_expression(self, expression: str) -> dict[str, int]:
        """
        Parse dice expression into components.

        Args:
            expression: Dice expression string.

        Returns:
            Dictionary with parsed components.

        Raises:
            ValueError: If expression is invalid.
        """
        expression = expression.replace(" ", "")
        pattern = r"(\d+)d(\d+)([+-]\d+)?"
        match = re.match(pattern, expression)

        if not match:
            raise ValueError(f"Invalid dice expression: {expression}")

        num_dice = int(match.group(1))
        dice_size = int(match.group(2))
        modifier_str = match.group(3)

        modifier = 0
        if modifier_str:
            modifier = int(modifier_str)

        return {"num_dice": num_dice, "dice_size": dice_size, "modifier": modifier}

    def roll_ability_check(
        self, ability_score: int, difficulty: int = 10
    ) -> dict[str, Any]:
        """
        Roll a d20 ability check against a difficulty class.

        Args:
            ability_score: Character's ability score.
            difficulty: Difficulty class (default 10).

        Returns:
            Dictionary with roll results and success/failure.
        """
        d20_roll = random.randint(1, 20)
        ability_modifier = (ability_score - 10) // 2
        total = d20_roll + ability_modifier
        success = total >= difficulty

        result = {
            "expression": f"1d20+{ability_modifier}",
            "d20_roll": d20_roll,
            "ability_modifier": ability_modifier,
            "total": total,
            "difficulty": difficulty,
            "success": success,
            "critical_success": d20_roll == 20,
            "critical_failure": d20_roll == 1,
        }

        self._log_ability_check_result(
            d20_roll, ability_modifier, total, difficulty, success
        )
        return result

    def _log_ability_check_result(
        self,
        d20_roll: int,
        ability_modifier: int,
        total: int,
        difficulty: int,
        success: bool,
    ) -> None:
        """Log the ability check result."""
        status = "SUCCESS" if success else "FAILURE"
        self.logger.info(
            f"Ability check: d20({d20_roll}) + {ability_modifier} = {total} vs DC {difficulty} - {status}"
        )

    def roll_skill_check(
        self, skill_bonus: int, difficulty: int = 10
    ) -> dict[str, Any]:
        """
        Roll a d20 skill check against a difficulty class.

        Args:
            skill_bonus: Character's skill bonus.
            difficulty: Difficulty class (default 10).

        Returns:
            Dictionary with roll results and success/failure.
        """
        d20_roll = random.randint(1, 20)
        total = d20_roll + skill_bonus
        success = total >= difficulty

        result = {
            "expression": f"1d20+{skill_bonus}",
            "d20_roll": d20_roll,
            "skill_bonus": skill_bonus,
            "total": total,
            "difficulty": difficulty,
            "success": success,
            "critical_success": d20_roll == 20,
            "critical_failure": d20_roll == 1,
        }

        self._log_skill_check_result(d20_roll, skill_bonus, total, difficulty, success)
        return result

    def _log_skill_check_result(
        self,
        d20_roll: int,
        skill_bonus: int,
        total: int,
        difficulty: int,
        success: bool,
    ) -> None:
        """Log the skill check result."""
        status = "SUCCESS" if success else "FAILURE"
        self.logger.info(
            f"Skill check: d20({d20_roll}) + {skill_bonus} = {total} vs DC {difficulty} - {status}"
        )

    def roll_damage(self, damage_dice: str) -> dict[str, Any]:
        """
        Roll damage dice.

        Args:
            damage_dice: Dice expression for damage (e.g., "2d6+3").

        Returns:
            Dictionary with damage roll results.
        """
        result = self.roll_dice(damage_dice)
        result["damage_type"] = (
            "physical"  # Could be extended for different damage types
        )

        self.logger.info(f"Damage roll: {damage_dice} = {result['total']} damage")
        return result

    def roll_initiative(self, dexterity_modifier: int) -> dict[str, Any]:
        """
        Roll initiative (d20 + Dexterity modifier).

        Args:
            dexterity_modifier: Character's Dexterity modifier.

        Returns:
            Dictionary with initiative roll results.
        """
        d20_roll = random.randint(1, 20)
        total = d20_roll + dexterity_modifier

        result = {
            "expression": f"1d20+{dexterity_modifier}",
            "d20_roll": d20_roll,
            "dexterity_modifier": dexterity_modifier,
            "total": total,
        }

        self.logger.info(
            f"Initiative: d20({d20_roll}) + {dexterity_modifier} = {total}"
        )
        return result
