"""
Dice Rolling System for RPG DM Agent
Handles dice expressions and roll mechanics for Vampire: The Masquerade V5
"""

import random
import re
import logging
from typing import List, Tuple, Dict, Any

class DiceRoller:
    """Handles dice rolling mechanics for Vampire: The Masquerade V5 system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def roll_dice_pool(self, attribute: int, skill: int, difficulty: int = 2, hunger: int = 1) -> Dict[str, Any]:
        """
        Roll a dice pool for Vampire: The Masquerade V5
        
        Args:
            attribute: Attribute dots (1-5)
            skill: Skill dots (0-5)
            difficulty: Target number of successes needed (default 2)
            hunger: Hunger level (1-5)
            
        Returns:
            Dictionary with roll results, successes, and special effects
        """
        try:
            # Calculate dice pool size
            pool_size = attribute + skill
            
            if pool_size <= 0:
                return {
                    'pool_size': 0,
                    'attribute': attribute,
                    'skill': skill,
                    'difficulty': difficulty,
                    'hunger': hunger,
                    'successes': 0,
                    'total_successes': 0,
                    'critical': False,
                    'bestial_failure': False,
                    'messy_critical': False,
                    'error': 'Dice pool must be at least 1 die'
                }
            
            # Roll normal dice (d10s)
            normal_dice = min(pool_size, pool_size - hunger)
            hunger_dice = min(hunger, pool_size)
            
            normal_rolls = []
            hunger_rolls = []
            
            # Roll normal dice
            for _ in range(normal_dice):
                roll = random.randint(1, 10)
                normal_rolls.append(roll)
            
            # Roll hunger dice
            for _ in range(hunger_dice):
                roll = random.randint(1, 10)
                hunger_rolls.append(roll)
            
            # Count successes (6+ = 1 success, 10 = 2 successes)
            successes = 0
            for roll in normal_rolls + hunger_rolls:
                if roll >= 6:
                    successes += 1
                if roll == 10:
                    successes += 1  # 10s are worth 2 successes
            
            # Check for critical (two 10s)
            tens = normal_rolls.count(10) + hunger_rolls.count(10)
            critical = tens >= 2
            
            # Check for bestial failure (fail with 1s on hunger dice)
            ones_on_hunger = hunger_rolls.count(1)
            bestial_failure = successes == 0 and ones_on_hunger > 0
            
            # Check for messy critical (critical with hunger dice involved)
            messy_critical = critical and len(hunger_rolls) > 0
            
            # Calculate total successes (critical gives 4 total successes)
            total_successes = 4 if critical else successes
            
            result = {
                'pool_size': pool_size,
                'attribute': attribute,
                'skill': skill,
                'difficulty': difficulty,
                'hunger': hunger,
                'normal_rolls': normal_rolls,
                'hunger_rolls': hunger_rolls,
                'all_rolls': normal_rolls + hunger_rolls,
                'successes': successes,
                'total_successes': total_successes,
                'critical': critical,
                'bestial_failure': bestial_failure,
                'messy_critical': messy_critical,
                'success': total_successes >= difficulty
            }
            
            self.logger.info(f"Vampire dice pool: {attribute}+{skill} dice, hunger {hunger}, difficulty {difficulty}")
            self.logger.info(f"Rolls: {normal_rolls} (normal) + {hunger_rolls} (hunger) = {total_successes} successes")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error rolling Vampire dice pool: {e}")
            return {
                'pool_size': 0,
                'attribute': attribute,
                'skill': skill,
                'difficulty': difficulty,
                'hunger': hunger,
                'successes': 0,
                'total_successes': 0,
                'critical': False,
                'bestial_failure': False,
                'messy_critical': False,
                'error': str(e)
            }
    
    def roll_rouse_check(self, hunger: int = 1) -> Dict[str, Any]:
        """
        Roll a Rouse Check (1d10) - used when activating Disciplines
        
        Args:
            hunger: Current hunger level
            
        Returns:
            Dictionary with roll results and hunger change
        """
        try:
            roll = random.randint(1, 10)
            success = roll >= 6
            hunger_change = 0 if success else 1
            
            result = {
                'roll': roll,
                'success': success,
                'hunger_change': hunger_change,
                'new_hunger': hunger + hunger_change
            }
            
            self.logger.info(f"Rouse check: d10({roll}) - {'SUCCESS' if success else 'FAILURE'}, hunger {'+' + str(hunger_change) if hunger_change > 0 else 'unchanged'}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error rolling Rouse check: {e}")
            return {
                'roll': 0,
                'success': False,
                'hunger_change': 1,
                'new_hunger': hunger + 1,
                'error': str(e)
            }
    
    def roll_willpower(self, willpower: int) -> Dict[str, Any]:
        """
        Roll Willpower dice (1-3 dice based on willpower dots)
        
        Args:
            willpower: Willpower dots (1-5)
            
        Returns:
            Dictionary with roll results and successes
        """
        try:
            # Willpower dice are normal dice (not hunger dice)
            num_dice = min(willpower, 3)  # Max 3 dice
            rolls = [random.randint(1, 10) for _ in range(num_dice)]
            
            # Count successes (6+ = 1 success, 10 = 2 successes)
            successes = 0
            for roll in rolls:
                if roll >= 6:
                    successes += 1
                if roll == 10:
                    successes += 1  # 10s are worth 2 successes
            
            # Check for critical (two 10s)
            tens = rolls.count(10)
            critical = tens >= 2
            
            # Calculate total successes (critical gives 4 total successes)
            total_successes = 4 if critical else successes
            
            result = {
                'willpower_dots': willpower,
                'num_dice': num_dice,
                'rolls': rolls,
                'successes': successes,
                'total_successes': total_successes,
                'critical': critical
            }
            
            self.logger.info(f"Willpower roll: {num_dice} dice = {rolls} = {total_successes} successes")
            return result
            
        except Exception as e:
            self.logger.error(f"Error rolling Willpower: {e}")
            return {
                'willpower_dots': willpower,
                'num_dice': 0,
                'rolls': [],
                'successes': 0,
                'total_successes': 0,
                'critical': False,
                'error': str(e)
            }
    
    def roll_dice(self, expression: str) -> Dict[str, Any]:
        """
        Legacy method for backward compatibility - now redirects to Vampire dice system
        Parse and execute dice expressions like '2d6+3', '1d20', '3d4-2'
        
        Args:
            expression: Dice expression string
            
        Returns:
            Dictionary with roll results, individual dice, total, and modifiers
        """
        try:
            # Parse the dice expression
            parsed = self._parse_dice_expression(expression)
            
            # Roll the dice
            dice_results = []
            for _ in range(parsed['num_dice']):
                roll = random.randint(1, parsed['dice_size'])
                dice_results.append(roll)
            
            # Calculate total
            total = sum(dice_results) + parsed['modifier']
            
            result = {
                'expression': expression,
                'num_dice': parsed['num_dice'],
                'dice_size': parsed['dice_size'],
                'modifier': parsed['modifier'],
                'individual_rolls': dice_results,
                'total': total,
                'success': total >= parsed.get('target', 0) if 'target' in parsed else None
            }
            
            self.logger.info(f"Dice roll: {expression} = {dice_results} + {parsed['modifier']} = {total}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error rolling dice '{expression}': {e}")
            return {
                'expression': expression,
                'error': str(e),
                'total': 0
            }
    
    def _parse_dice_expression(self, expression: str) -> Dict[str, int]:
        """Parse dice expression into components"""
        # Remove whitespace
        expression = expression.replace(' ', '')
        
        # Pattern to match dice expressions: XdY+Z, XdY-Z, XdY
        pattern = r'(\d+)d(\d+)([+-]\d+)?'
        match = re.match(pattern, expression)
        
        if not match:
            raise ValueError(f"Invalid dice expression: {expression}")
        
        num_dice = int(match.group(1))
        dice_size = int(match.group(2))
        modifier_str = match.group(3)
        
        modifier = 0
        if modifier_str:
            modifier = int(modifier_str)
        
        return {
            'num_dice': num_dice,
            'dice_size': dice_size,
            'modifier': modifier
        }
    
    def roll_ability_check(self, ability_score: int, difficulty: int = 10) -> Dict[str, Any]:
        """
        Roll a d20 ability check against a difficulty class
        
        Args:
            ability_score: Character's ability score
            difficulty: Difficulty class (default 10)
            
        Returns:
            Dictionary with roll results and success/failure
        """
        # Roll d20
        d20_roll = random.randint(1, 20)
        
        # Calculate modifier (ability score - 10) / 2, rounded down
        ability_modifier = (ability_score - 10) // 2
        
        total = d20_roll + ability_modifier
        success = total >= difficulty
        
        result = {
            'expression': f"1d20+{ability_modifier}",
            'd20_roll': d20_roll,
            'ability_modifier': ability_modifier,
            'total': total,
            'difficulty': difficulty,
            'success': success,
            'critical_success': d20_roll == 20,
            'critical_failure': d20_roll == 1
        }
        
        self.logger.info(f"Ability check: d20({d20_roll}) + {ability_modifier} = {total} vs DC {difficulty} - {'SUCCESS' if success else 'FAILURE'}")
        return result
    
    def roll_skill_check(self, skill_bonus: int, difficulty: int = 10) -> Dict[str, Any]:
        """
        Roll a d20 skill check against a difficulty class
        
        Args:
            skill_bonus: Character's skill bonus
            difficulty: Difficulty class (default 10)
            
        Returns:
            Dictionary with roll results and success/failure
        """
        # Roll d20
        d20_roll = random.randint(1, 20)
        
        total = d20_roll + skill_bonus
        success = total >= difficulty
        
        result = {
            'expression': f"1d20+{skill_bonus}",
            'd20_roll': d20_roll,
            'skill_bonus': skill_bonus,
            'total': total,
            'difficulty': difficulty,
            'success': success,
            'critical_success': d20_roll == 20,
            'critical_failure': d20_roll == 1
        }
        
        self.logger.info(f"Skill check: d20({d20_roll}) + {skill_bonus} = {total} vs DC {difficulty} - {'SUCCESS' if success else 'FAILURE'}")
        return result
    
    def roll_damage(self, damage_dice: str) -> Dict[str, Any]:
        """
        Roll damage dice
        
        Args:
            damage_dice: Dice expression for damage (e.g., "2d6+3")
            
        Returns:
            Dictionary with damage roll results
        """
        result = self.roll_dice(damage_dice)
        result['damage_type'] = 'physical'  # Could be extended for different damage types
        
        self.logger.info(f"Damage roll: {damage_dice} = {result['total']} damage")
        return result
    
    def roll_initiative(self, dexterity_modifier: int) -> Dict[str, Any]:
        """
        Roll initiative (d20 + Dexterity modifier)
        
        Args:
            dexterity_modifier: Character's Dexterity modifier
            
        Returns:
            Dictionary with initiative roll results
        """
        d20_roll = random.randint(1, 20)
        total = d20_roll + dexterity_modifier
        
        result = {
            'expression': f"1d20+{dexterity_modifier}",
            'd20_roll': d20_roll,
            'dexterity_modifier': dexterity_modifier,
            'total': total
        }
        
        self.logger.info(f"Initiative: d20({d20_roll}) + {dexterity_modifier} = {total}")
        return result
