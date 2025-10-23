"""
Rule Engine for RPG DM Agent
Handles game rules, mechanics, and rule resolution
"""

import json
import os
import logging
from typing import Dict, Any, List, Optional, Tuple
from dice_roller import DiceRoller

class RuleEngine:
    """Handles game rules and mechanics"""
    
    def __init__(self, rules_dir: str = "rules"):
        self.rules_dir = rules_dir
        self.logger = logging.getLogger(__name__)
        self.dice_roller = DiceRoller()
        self.rules_cache = {}
        
        # Load all rule files
        self._load_rules()
    
    def _load_rules(self):
        """Load all rule files from the rules directory"""
        try:
            if not os.path.exists(self.rules_dir):
                self.logger.warning(f"Rules directory not found: {self.rules_dir}")
                return
            
            for filename in os.listdir(self.rules_dir):
                if filename.endswith('.json'):
                    rule_name = filename[:-5]  # Remove .json extension
                    rule_file = os.path.join(self.rules_dir, filename)
                    
                    try:
                        with open(rule_file, 'r', encoding='utf-8') as f:
                            rules = json.load(f)
                        self.rules_cache[rule_name] = rules
                        self.logger.info(f"Loaded rules: {rule_name}")
                    except Exception as e:
                        self.logger.error(f"Error loading rule file {filename}: {e}")
                        
        except Exception as e:
            self.logger.error(f"Error loading rules: {e}")
    
    def get_rule(self, rule_name: str, rule_path: str = None) -> Any:
        """
        Get a specific rule from the loaded rules
        
        Args:
            rule_name: Name of the rule file
            rule_path: Dot-separated path to specific rule (e.g., 'combat.damage')
            
        Returns:
            Rule data or None if not found
        """
        try:
            if rule_name not in self.rules_cache:
                self.logger.warning(f"Rule file not found: {rule_name}")
                return None
            
            rules = self.rules_cache[rule_name]
            
            if rule_path is None:
                return rules
            
            # Navigate to specific rule using dot notation
            keys = rule_path.split('.')
            current = rules
            
            for key in keys:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    self.logger.warning(f"Rule path not found: {rule_name}.{rule_path}")
                    return None
            
            return current
            
        except Exception as e:
            self.logger.error(f"Error getting rule {rule_name}.{rule_path}: {e}")
            return None
    
    def calculate_ability_modifier(self, ability_score: int) -> int:
        """
        Calculate ability modifier from ability score
        
        Args:
            ability_score: Raw ability score
            
        Returns:
            Ability modifier
        """
        return (ability_score - 10) // 2
    
    def calculate_skill_bonus(self, character: Dict[str, Any], skill_name: str) -> int:
        """
        Calculate skill bonus for a character
        
        Args:
            character: Character data
            skill_name: Name of the skill
            
        Returns:
            Skill bonus
        """
        try:
            # Get base ability modifier
            skill_info = self.get_rule('character_creation', f'skills.{skill_name}')
            if not skill_info:
                return 0
            
            ability_name = skill_info.get('ability', 'intelligence')
            ability_score = character.get('attributes', {}).get(ability_name, 10)
            ability_modifier = self.calculate_ability_modifier(ability_score)
            
            # Get skill ranks
            skill_ranks = character.get('skills', {}).get(skill_name, 0)
            
            # Calculate total bonus
            total_bonus = ability_modifier + skill_ranks
            
            # Add any miscellaneous bonuses
            misc_bonus = character.get('skill_bonuses', {}).get(skill_name, 0)
            total_bonus += misc_bonus
            
            return total_bonus
            
        except Exception as e:
            self.logger.error(f"Error calculating skill bonus for {skill_name}: {e}")
            return 0
    
    def resolve_ability_check(self, character: Dict[str, Any], ability_name: str, 
                             difficulty: int = 10, advantage: bool = False, 
                             disadvantage: bool = False) -> Dict[str, Any]:
        """
        Resolve an ability check
        
        Args:
            character: Character data
            ability_name: Name of the ability
            difficulty: Difficulty class
            advantage: Whether character has advantage
            disadvantage: Whether character has disadvantage
            
        Returns:
            Dictionary with check results
        """
        try:
            ability_score = character.get('attributes', {}).get(ability_name, 10)
            ability_modifier = self.calculate_ability_modifier(ability_score)
            
            # Roll with advantage/disadvantage
            if advantage and not disadvantage:
                roll1 = self.dice_roller.roll_ability_check(ability_score, difficulty)
                roll2 = self.dice_roller.roll_ability_check(ability_score, difficulty)
                
                if roll1['total'] >= roll2['total']:
                    result = roll1
                    result['advantage_used'] = True
                else:
                    result = roll2
                    result['advantage_used'] = True
                    
            elif disadvantage and not advantage:
                roll1 = self.dice_roller.roll_ability_check(ability_score, difficulty)
                roll2 = self.dice_roller.roll_ability_check(ability_score, difficulty)
                
                if roll1['total'] <= roll2['total']:
                    result = roll1
                    result['disadvantage_used'] = True
                else:
                    result = roll2
                    result['disadvantage_used'] = True
            else:
                result = self.dice_roller.roll_ability_check(ability_score, difficulty)
            
            result['ability_name'] = ability_name
            result['ability_score'] = ability_score
            result['ability_modifier'] = ability_modifier
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error resolving ability check: {e}")
            return {'error': str(e), 'success': False}
    
    def resolve_skill_check(self, character: Dict[str, Any], skill_name: str, 
                           difficulty: int = 10, advantage: bool = False, 
                           disadvantage: bool = False) -> Dict[str, Any]:
        """
        Resolve a skill check
        
        Args:
            character: Character data
            skill_name: Name of the skill
            difficulty: Difficulty class
            advantage: Whether character has advantage
            disadvantage: Whether character has disadvantage
            
        Returns:
            Dictionary with check results
        """
        try:
            skill_bonus = self.calculate_skill_bonus(character, skill_name)
            
            # Roll with advantage/disadvantage
            if advantage and not disadvantage:
                roll1 = self.dice_roller.roll_skill_check(skill_bonus, difficulty)
                roll2 = self.dice_roller.roll_skill_check(skill_bonus, difficulty)
                
                if roll1['total'] >= roll2['total']:
                    result = roll1
                    result['advantage_used'] = True
                else:
                    result = roll2
                    result['advantage_used'] = True
                    
            elif disadvantage and not advantage:
                roll1 = self.dice_roller.roll_skill_check(skill_bonus, difficulty)
                roll2 = self.dice_roller.roll_skill_check(skill_bonus, difficulty)
                
                if roll1['total'] <= roll2['total']:
                    result = roll1
                    result['disadvantage_used'] = True
                else:
                    result = roll2
                    result['disadvantage_used'] = True
            else:
                result = self.dice_roller.roll_skill_check(skill_bonus, difficulty)
            
            result['skill_name'] = skill_name
            result['skill_bonus'] = skill_bonus
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error resolving skill check: {e}")
            return {'error': str(e), 'success': False}
    
    def resolve_combat_attack(self, attacker: Dict[str, Any], target: Dict[str, Any], 
                             weapon: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Resolve a combat attack
        
        Args:
            attacker: Attacking character data
            target: Target character data
            weapon: Weapon data (optional)
            
        Returns:
            Dictionary with attack results
        """
        try:
            # Calculate attack bonus
            attack_bonus = 0
            
            # Base attack bonus from level/class
            level = attacker.get('level', 1)
            base_attack_bonus = (level - 1) // 4 + 1  # Simplified BAB progression
            
            # Ability modifier (usually Strength for melee, Dexterity for ranged)
            if weapon and weapon.get('type') == 'ranged':
                ability_modifier = self.calculate_ability_modifier(
                    attacker.get('attributes', {}).get('dexterity', 10)
                )
            else:
                ability_modifier = self.calculate_ability_modifier(
                    attacker.get('attributes', {}).get('strength', 10)
                )
            
            attack_bonus = base_attack_bonus + ability_modifier
            
            # Weapon bonus
            if weapon:
                attack_bonus += weapon.get('attack_bonus', 0)
            
            # Roll attack
            attack_roll = self.dice_roller.roll_dice(f"1d20+{attack_bonus}")
            
            # Calculate target AC
            target_ac = self.calculate_armor_class(target)
            
            # Determine hit
            hit = attack_roll['total'] >= target_ac
            critical_hit = attack_roll['individual_rolls'][0] == 20
            
            result = {
                'attack_roll': attack_roll,
                'attack_bonus': attack_bonus,
                'target_ac': target_ac,
                'hit': hit,
                'critical_hit': critical_hit,
                'damage': None
            }
            
            # Calculate damage if hit
            if hit:
                if weapon:
                    damage_roll = self.dice_roller.roll_damage(weapon.get('damage', '1d4'))
                    damage_bonus = ability_modifier if weapon.get('type') != 'ranged' else 0
                    damage_roll['total'] += damage_bonus
                    result['damage'] = damage_roll
                else:
                    # Unarmed strike
                    damage_roll = self.dice_roller.roll_damage('1d3')
                    damage_roll['total'] += ability_modifier
                    result['damage'] = damage_roll
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error resolving combat attack: {e}")
            return {'error': str(e), 'hit': False}
    
    def calculate_armor_class(self, character: Dict[str, Any]) -> int:
        """
        Calculate armor class for a character
        
        Args:
            character: Character data
            
        Returns:
            Armor class value
        """
        try:
            # Base AC is 10
            ac = 10
            
            # Dexterity modifier
            dexterity = character.get('attributes', {}).get('dexterity', 10)
            dexterity_modifier = self.calculate_ability_modifier(dexterity)
            ac += dexterity_modifier
            
            # Armor bonus
            armor = character.get('equipment', {}).get('armor')
            if armor:
                ac += armor.get('ac_bonus', 0)
            
            # Shield bonus
            shield = character.get('equipment', {}).get('shield')
            if shield:
                ac += shield.get('ac_bonus', 0)
            
            # Natural armor bonus
            ac += character.get('natural_armor', 0)
            
            # Miscellaneous bonuses
            ac += character.get('ac_bonuses', {}).get('misc', 0)
            
            return ac
            
        except Exception as e:
            self.logger.error(f"Error calculating armor class: {e}")
            return 10
    
    def calculate_hit_points(self, character: Dict[str, Any]) -> int:
        """
        Calculate total hit points for a character
        
        Args:
            character: Character data
            
        Returns:
            Total hit points
        """
        try:
            # Base hit points from class and level
            level = character.get('level', 1)
            constitution = character.get('attributes', {}).get('constitution', 10)
            constitution_modifier = self.calculate_ability_modifier(constitution)
            
            # Simplified HP calculation (class-based)
            class_name = character.get('class', 'fighter')
            base_hp_per_level = {
                'fighter': 10,
                'wizard': 6,
                'rogue': 8,
                'cleric': 8
            }.get(class_name, 8)
            
            # Calculate total HP
            total_hp = base_hp_per_level + constitution_modifier
            total_hp += (level - 1) * (base_hp_per_level + constitution_modifier)
            
            return max(1, total_hp)
            
        except Exception as e:
            self.logger.error(f"Error calculating hit points: {e}")
            return 10
    
    def get_experience_requirements(self, level: int) -> int:
        """
        Get experience points required for a given level
        
        Args:
            level: Character level
            
        Returns:
            Experience points required
        """
        # Simplified XP table
        xp_table = {
            1: 0,
            2: 1000,
            3: 3000,
            4: 6000,
            5: 10000,
            6: 15000,
            7: 21000,
            8: 28000,
            9: 36000,
            10: 45000
        }
        
        return xp_table.get(level, level * 5000)
    
    def check_level_up(self, character: Dict[str, Any]) -> bool:
        """
        Check if character can level up
        
        Args:
            character: Character data
            
        Returns:
            True if character can level up
        """
        try:
            current_level = character.get('level', 1)
            current_xp = character.get('experience_points', 0)
            required_xp = self.get_experience_requirements(current_level + 1)
            
            return current_xp >= required_xp
            
        except Exception as e:
            self.logger.error(f"Error checking level up: {e}")
            return False
    
    def get_character_creation_info(self) -> Dict[str, Any]:
        """
        Get character creation information from rules
        
        Returns:
            Dictionary with character creation rules
        """
        try:
            creation_rules = self.get_rule('Vampire_The_Masquerade_Character_Creation_rules', 'character_creation')
            if not creation_rules:
                return {}
            
            return {
                'attributes': creation_rules.get('attributes', {}),
                'skills': creation_rules.get('skills', {}),
                'derived_traits': creation_rules.get('derived_traits', {}),
                'steps': creation_rules.get('steps', [])
            }
            
        except Exception as e:
            self.logger.error(f"Error getting character creation info: {e}")
            return {}
    
    def validate_character_creation(self, character: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate character creation against rules
        
        Args:
            character: Character data to validate
            
        Returns:
            Dictionary with validation results
        """
        try:
            validation_result = {
                'valid': True,
                'errors': [],
                'warnings': []
            }
            
            # Get creation rules
            creation_rules = self.get_rule('Vampire_The_Masquerade_Character_Creation_rules', 'character_creation')
            if not creation_rules:
                validation_result['warnings'].append("Character creation rules not found")
                return validation_result
            
            # Validate attributes
            attr_validation = self._validate_attributes(character, creation_rules)
            validation_result['errors'].extend(attr_validation['errors'])
            validation_result['warnings'].extend(attr_validation['warnings'])
            
            # Validate skills
            skill_validation = self._validate_skills(character, creation_rules)
            validation_result['errors'].extend(skill_validation['errors'])
            validation_result['warnings'].extend(skill_validation['warnings'])
            
            # Check if character is valid
            if validation_result['errors']:
                validation_result['valid'] = False
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Error validating character creation: {e}")
            return {'valid': False, 'errors': [f"Validation error: {e}"], 'warnings': []}
    
    def _validate_attributes(self, character: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate character attributes against rules"""
        result = {'errors': [], 'warnings': []}
        
        try:
            attributes = character.get('attributes', {})
            attr_categories = rules.get('attributes', {}).get('categories', {})
            
            # Check if all required attributes are present
            for category, attrs in attr_categories.items():
                if category not in attributes:
                    result['errors'].append(f"Missing {category} attributes")
                    continue
                
                category_attrs = attributes[category]
                for attr in attrs:
                    attr_lower = attr.lower()
                    if attr_lower not in category_attrs:
                        result['warnings'].append(f"Missing {attr} in {category} attributes")
                    elif not isinstance(category_attrs[attr_lower], int) or category_attrs[attr_lower] < 1 or category_attrs[attr_lower] > 5:
                        result['errors'].append(f"Invalid {attr} value: {category_attrs[attr_lower]} (must be 1-5)")
            
            return result
            
        except Exception as e:
            result['errors'].append(f"Error validating attributes: {e}")
            return result
    
    def _validate_skills(self, character: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate character skills against rules"""
        result = {'errors': [], 'warnings': []}
        
        try:
            skills = character.get('skills', {})
            skill_categories = rules.get('skills', {}).get('categories', {})
            
            # Check if all required skills are present
            for category, skill_list in skill_categories.items():
                if category not in skills:
                    result['errors'].append(f"Missing {category} skills")
                    continue
                
                category_skills = skills[category]
                for skill in skill_list:
                    skill_lower = skill.lower().replace(' ', '_')
                    if skill_lower not in category_skills:
                        result['warnings'].append(f"Missing {skill} in {category} skills")
                    elif not isinstance(category_skills[skill_lower], int) or category_skills[skill_lower] < 0 or category_skills[skill_lower] > 5:
                        result['errors'].append(f"Invalid {skill} value: {category_skills[skill_lower]} (must be 0-5)")
            
            return result
            
        except Exception as e:
            result['errors'].append(f"Error validating skills: {e}")
            return result