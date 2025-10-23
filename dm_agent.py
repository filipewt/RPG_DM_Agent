"""
Dungeon Master Agent for RPG DM Agent
Main AI-powered DM that handles storytelling, rule resolution, and player interaction
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import openai
from openai import OpenAI

from character_manager import CharacterManager
from rule_engine import RuleEngine
from journal_manager import JournalManager
from experience_system import ExperienceSystem
from media_manager import MediaManager
from logging_system import LoggingSystem
from dice_roller import DiceRoller

class DMAgent:
    """Main Dungeon Master Agent that orchestrates the RPG experience"""
    
    def __init__(self, openai_api_key: str = None):
        # Initialize components
        self.character_manager = CharacterManager()
        self.rule_engine = RuleEngine()
        self.journal_manager = JournalManager()
        self.experience_system = ExperienceSystem(self.character_manager, self.rule_engine)
        self.media_manager = MediaManager()
        self.logging_system = LoggingSystem()
        self.dice_roller = DiceRoller()
        
        # Initialize OpenAI client
        if openai_api_key:
            self.client = OpenAI(api_key=openai_api_key)
        else:
            # Try to get from environment
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                self.client = OpenAI(api_key=api_key)
            else:
                self.client = None
                self.logging_system.logger.warning("No OpenAI API key provided. LLM features will be limited.")
        
        # Session state
        self.current_character = None
        self.current_session_id = None
        self.conversation_history = []
        self.game_state = {
            'current_scene': None,
            'active_encounters': [],
            'npc_relationships': {},
            'world_state': {}
        }
        
        # DM personality and style
        self.dm_personality = {
            'tone': 'engaging and immersive',
            'style': 'descriptive and atmospheric',
            'narrative_voice': 'fantasy novelist',
            'dice_style': 'dramatic and transparent'
        }
    
    def start_new_adventure(self, character_name: str, character_class: str = None, 
                          adventure_title: str = None, custom_attributes: Dict[str, Any] = None) -> bool:
        """
        Start a new adventure with a character
        
        Args:
            character_name: Name of the character
            character_class: Class of the character
            adventure_title: Title of the adventure
            custom_attributes: Custom character attributes
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Start session logging
            self.current_session_id = self.logging_system.start_session(character_name, "adventure")
            
            # Create or load character
            if custom_attributes is None:
                custom_attributes = {}
            
            if character_class:
                custom_attributes['class'] = character_class
            
            self.current_character = self.character_manager.create_character(
                character_name, "Vampire_The_Masquerade_Character_Sheet", custom_attributes
            )
            
            if not self.current_character:
                self.logging_system.log_error("Failed to create character", context={'character_name': character_name})
                return False
            
            # Create adventure journal
            if not adventure_title:
                adventure_title = f"{character_name}'s Vampire Adventure"
            
            journal_path = self.journal_manager.create_journal(character_name, adventure_title)
            
            # Log the start
            self.logging_system.log_system_event("adventure_started", {
                'character_name': character_name,
                'character_class': character_class,
                'adventure_title': adventure_title,
                'journal_path': journal_path
            })
            
            # Generate opening narrative
            opening_narrative = self._generate_opening_narrative(character_name, character_class)
            
            # Add to journal
            self.journal_manager.add_journal_entry(
                character_name, opening_narrative, "narrative"
            )
            
            # Generate character portrait
            portrait_path = self.media_manager.get_character_portrait(
                character_name, self._get_character_description()
            )
            
            if portrait_path:
                self.journal_manager.add_journal_entry(
                    character_name, "", "narrative", [portrait_path]
                )
            
            return True
            
        except Exception as e:
            self.logging_system.log_error(f"Error starting new adventure: {e}")
            return False
    
    def continue_adventure(self, character_name: str) -> bool:
        """
        Continue an existing adventure
        
        Args:
            character_name: Name of the character
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Start session logging
            self.current_session_id = self.logging_system.start_session(character_name, "adventure")
            
            # Load character
            self.current_character = self.character_manager.load_character(character_name)
            
            if not self.current_character:
                self.logging_system.log_error(f"Character not found: {character_name}")
                return False
            
            # Log the continuation
            self.logging_system.log_system_event("adventure_continued", {
                'character_name': character_name,
                'character_level': self.current_character.get('level', 1),
                'character_xp': self.current_character.get('experience_points', 0)
            })
            
            return True
            
        except Exception as e:
            self.logging_system.log_error(f"Error continuing adventure: {e}")
            return False
    
    def process_player_input(self, player_input: str) -> str:
        """
        Process player input and generate DM response
        
        Args:
            player_input: Player's input text
            
        Returns:
            DM's response
        """
        try:
            if not self.current_character:
                return "No active character. Please start or continue an adventure first."
            
            # Add to conversation history
            self.conversation_history.append({
                'role': 'player',
                'content': player_input,
                'timestamp': datetime.now().isoformat()
            })
            
            # Log the input
            self.logging_system.log_character_action(
                self.current_character['name'], "player_input", player_input
            )
            
            # Check if this is a skill check action
            test_info = self._identify_skill_check(player_input)
            
            if test_info:
                # Show test description first
                test_description = self._create_test_description(test_info)
                
                # Add test description to conversation history
                self.conversation_history.append({
                    'role': 'dm',
                    'content': test_description,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Perform hidden dice roll and get narrative outcome
                outcome = self._perform_hidden_dice_roll(
                    test_info['dice_pool'], 
                    test_info['difficulty'], 
                    test_info['action_type']
                )
                
                # Add outcome to conversation history
                self.conversation_history.append({
                    'role': 'dm',
                    'content': outcome,
                    'timestamp': datetime.now().isoformat()
                })
                
                return f"{test_description}\n\n{outcome}"
            else:
                # Process the input and generate response normally
                dm_response = self._generate_dm_response(player_input)
                
                # Add DM response to conversation history
                self.conversation_history.append({
                    'role': 'dm',
                    'content': dm_response,
                    'timestamp': datetime.now().isoformat()
                })
                
                return dm_response
            
        except Exception as e:
            self.logging_system.log_error(f"Error processing player input: {e}")
            return "I apologize, but I encountered an error processing your input. Please try again."
    
    def _generate_dm_response(self, player_input: str) -> str:
        """Generate DM response using LLM"""
        try:
            if not self.client:
                return self._generate_fallback_response(player_input)
            
            # Build context for the LLM
            context = self._build_llm_context()
            
            # Create the prompt
            system_prompt = self._create_system_prompt()
            user_prompt = f"Player says: {player_input}\n\nContext: {context}"
            
            # Generate response using OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=500,
                temperature=0.8
            )
            
            dm_response = response.choices[0].message.content
            
            # Process any dice rolls or rule references in the response
            dm_response = self._process_response_mechanics(dm_response)
            
            return dm_response
            
        except Exception as e:
            self.logging_system.log_error(f"Error generating DM response: {e}")
            return self._generate_fallback_response(player_input)
    
    def _generate_fallback_response(self, player_input: str) -> str:
        """Generate a fallback response when LLM is not available"""
        # Simple keyword-based responses with test descriptions and hidden dice rolling
        input_lower = player_input.lower()
        
        if any(word in input_lower for word in ['attack', 'fight', 'combat']):
            # Show test description for combat action
            if self.current_character:
                # Get character's combat abilities
                attrs = self.current_character.get('attributes', {})
                physical = attrs.get('physical', {})
                strength = physical.get('strength', 2)
                
                # Get relevant skills (simplified - could be enhanced)
                skills = self.current_character.get('skills', {})
                physical_skills = skills.get('physical', {})
                brawl = physical_skills.get('brawl', 0)
                
                dice_pool = strength + brawl
                difficulty = 2  # Standard difficulty
                
                return f"You prepare for combat, your muscles tensing with predatory grace. This will be a **Strength + Brawl** test (pool: {dice_pool}, difficulty: {difficulty}). You strike with supernatural force!"
            else:
                return "You prepare for combat. What would you like to do? (Attack, Defend, Use an ability, or try something else)"
        
        elif any(word in input_lower for word in ['look', 'examine', 'search', 'investigate']):
            # Show test description for perception/investigation
            if self.current_character:
                attrs = self.current_character.get('attributes', {})
                mental = attrs.get('mental', {})
                wits = mental.get('wits', 2)
                
                skills = self.current_character.get('skills', {})
                mental_skills = skills.get('mental', {})
                awareness = mental_skills.get('awareness', 0)
                
                dice_pool = wits + awareness
                difficulty = 2  # Standard difficulty
                
                return f"You focus your enhanced vampire senses on your surroundings. This will be a **Wits + Awareness** test (pool: {dice_pool}, difficulty: {difficulty}). Your supernatural perception reveals hidden details!"
            else:
                return "You take a moment to examine your surroundings. What specifically would you like to look at?"
        
        elif any(word in input_lower for word in ['talk', 'speak', 'say', 'ask']):
            # Show test description for social interaction
            if self.current_character:
                attrs = self.current_character.get('attributes', {})
                social = attrs.get('social', {})
                charisma = social.get('charisma', 2)
                
                skills = self.current_character.get('skills', {})
                social_skills = skills.get('social', {})
                persuasion = social_skills.get('persuasion', 0)
                
                dice_pool = charisma + persuasion
                difficulty = 2  # Standard difficulty
                
                return f"You draw upon your supernatural charisma to communicate. This will be a **Charisma + Persuasion** test (pool: {dice_pool}, difficulty: {difficulty}). Your words carry otherworldly magnetism!"
            else:
                return "You attempt to communicate. What would you like to say or ask?"
        
        elif any(word in input_lower for word in ['move', 'go', 'walk', 'run']):
            # Show test description for movement/stealth
            if self.current_character:
                attrs = self.current_character.get('attributes', {})
                physical = attrs.get('physical', {})
                dexterity = physical.get('dexterity', 2)
                
                skills = self.current_character.get('skills', {})
                physical_skills = skills.get('physical', {})
                stealth = physical_skills.get('stealth', 0)
                
                dice_pool = dexterity + stealth
                difficulty = 2  # Standard difficulty
                
                return f"You move with supernatural grace. This will be a **Dexterity + Stealth** test (pool: {dice_pool}, difficulty: {difficulty}). You move like a shadow through the darkness!"
            else:
                return "You decide to move. Where would you like to go?"
        
        else:
            return "I understand. How would you like to proceed with your action?"
    
    def _perform_hidden_dice_roll(self, dice_pool: int, difficulty: int, action_type: str) -> str:
        """Perform a dice roll and return only the narrative outcome"""
        try:
            # Roll the dice
            result = self.roll_dice(f"{dice_pool}d10")
            
            if 'error' in result:
                return f"Something goes wrong with your {action_type} attempt."
            
            # Count successes (6+ on d10)
            successes = sum(1 for roll in result['individual_rolls'] if roll >= 6)
            
            # Determine outcome based on successes vs difficulty
            if successes >= difficulty:
                if successes >= difficulty + 2:  # Exceptional success
                    return f"Your {action_type} is executed with exceptional skill! The supernatural power flows through you effortlessly."
                else:  # Regular success
                    return f"Your {action_type} succeeds! You accomplish your goal with supernatural grace."
            else:  # Failure
                if successes == 0:  # Dramatic failure
                    return f"Your {action_type} fails catastrophically! The supernatural forces work against you."
                else:  # Regular failure
                    return f"Your {action_type} doesn't quite succeed. You'll need to try a different approach."
                    
        except Exception as e:
            self.logging_system.log_error(f"Error in hidden dice roll: {e}")
            return f"Something goes wrong with your {action_type} attempt."
    
    def _identify_skill_check(self, player_input: str) -> dict:
        """Identify if the player input requires a skill check and return test info"""
        input_lower = player_input.lower()
        
        # Combat actions
        if any(word in input_lower for word in ['attack', 'fight', 'combat', 'strike', 'hit']):
            if self.current_character:
                attrs = self.current_character.get('attributes', {})
                physical = attrs.get('physical', {})
                strength = physical.get('strength', 2)
                
                skills = self.current_character.get('skills', {})
                physical_skills = skills.get('physical', {})
                brawl = physical_skills.get('brawl', 0)
                
                return {
                    'action_type': 'combat',
                    'attribute': 'Strength',
                    'skill': 'Brawl',
                    'dice_pool': strength + brawl,
                    'difficulty': 2
                }
        
        # Perception/Investigation actions
        elif any(word in input_lower for word in ['look', 'examine', 'search', 'investigate', 'observe', 'watch']):
            if self.current_character:
                attrs = self.current_character.get('attributes', {})
                mental = attrs.get('mental', {})
                wits = mental.get('wits', 2)
                
                skills = self.current_character.get('skills', {})
                mental_skills = skills.get('mental', {})
                awareness = mental_skills.get('awareness', 0)
                
                return {
                    'action_type': 'perception',
                    'attribute': 'Wits',
                    'skill': 'Awareness',
                    'dice_pool': wits + awareness,
                    'difficulty': 2
                }
        
        # Social actions
        elif any(word in input_lower for word in ['talk', 'speak', 'say', 'ask', 'persuade', 'convince', 'charm']):
            if self.current_character:
                attrs = self.current_character.get('attributes', {})
                social = attrs.get('social', {})
                charisma = social.get('charisma', 2)
                
                skills = self.current_character.get('skills', {})
                social_skills = skills.get('social', {})
                persuasion = social_skills.get('persuasion', 0)
                
                return {
                    'action_type': 'social',
                    'attribute': 'Charisma',
                    'skill': 'Persuasion',
                    'dice_pool': charisma + persuasion,
                    'difficulty': 2
                }
        
        # Movement/Stealth actions
        elif any(word in input_lower for word in ['move', 'go', 'walk', 'run', 'sneak', 'hide', 'stealth']):
            if self.current_character:
                attrs = self.current_character.get('attributes', {})
                physical = attrs.get('physical', {})
                dexterity = physical.get('dexterity', 2)
                
                skills = self.current_character.get('skills', {})
                physical_skills = skills.get('physical', {})
                stealth = physical_skills.get('stealth', 0)
                
                return {
                    'action_type': 'movement',
                    'attribute': 'Dexterity',
                    'skill': 'Stealth',
                    'dice_pool': dexterity + stealth,
                    'difficulty': 2
                }
        
        return None
    
    def _create_test_description(self, test_info: dict) -> str:
        """Create a test description showing the test that will be made"""
        action_descriptions = {
            'combat': "You prepare for combat, your muscles tensing with predatory grace.",
            'perception': "You focus your enhanced vampire senses on your surroundings.",
            'social': "You draw upon your supernatural charisma to communicate.",
            'movement': "You move with supernatural grace."
        }
        
        action_desc = action_descriptions.get(test_info['action_type'], "You attempt your action.")
        
        return f"{action_desc} This will be a **{test_info['attribute']} + {test_info['skill']}** test (pool: {test_info['dice_pool']}, difficulty: {test_info['difficulty']})."
    
    def _build_llm_context(self) -> str:
        """Build context information for the LLM"""
        context_parts = []
        
        # Character information
        if self.current_character:
            context_parts.append(f"Character: {self.current_character.get('name', 'Unknown')}")
            context_parts.append(f"Level: {self.current_character.get('level', 1)}")
            context_parts.append(f"Class: {self.current_character.get('class', 'Unknown')}")
            
            # Attributes
            attributes = self.current_character.get('attributes', {})
            if attributes:
                attr_str = ", ".join([f"{k}: {v}" for k, v in attributes.items()])
                context_parts.append(f"Attributes: {attr_str}")
        
        # Game state
        if self.game_state['current_scene']:
            context_parts.append(f"Current Scene: {self.game_state['current_scene']}")
        
        # Recent conversation
        if len(self.conversation_history) > 0:
            recent_messages = self.conversation_history[-3:]  # Last 3 messages
            recent_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_messages])
            context_parts.append(f"Recent conversation:\n{recent_str}")
        
        return "\n".join(context_parts)
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt for the LLM"""
        return f"""You are a Dungeon Master for a Vampire: The Masquerade RPG game. Your role is to:

1. **Narrate the story** in an engaging, immersive way that draws the player into the world
2. **Manage the rules** of Vampire: The Masquerade, including dice rolls, character abilities, and combat
3. **Respond to player actions** with appropriate consequences and narrative
4. **Maintain the atmosphere** of the World of Darkness - dark, gothic, and mysterious
5. **Be descriptive** about environments, NPCs, and situations
6. **Ask for clarification** when player actions are ambiguous
7. **Automatically roll dice** when the player attempts actions that require skill checks
8. **Award experience** for successful actions and roleplay

**Dice Rolling:**
- When a player attempts an action that requires a skill check, describe the test first
- Show the Attribute + Skill combination and difficulty (e.g., "Strength + Brawl test, pool: 5, difficulty: 2")
- Then perform the dice roll behind the scenes
- Only show the narrative outcome - never reveal the actual dice results
- Focus on the story consequences, not the mechanics

**Your Style:**
- Write like a fantasy novelist - vivid, atmospheric, and engaging
- Use the second person ("You see...", "You feel...")
- Never show dice roll results - only narrative outcomes
- Never show raw mechanics in narrative - only outcomes and story
- Keep the tone dark and gothic, fitting for Vampire: The Masquerade

**Current Character:** {self.current_character.get('name', 'Unknown') if self.current_character else 'None'}

**Remember:** You are the storyteller, not just a rule enforcer. Make the story come alive!"""
    
    def _process_response_mechanics(self, response: str) -> str:
        """Process any mechanics mentioned in the DM response"""
        # Check if the response mentions dice rolling or skill checks
        # If so, we should automatically roll dice based on the character's abilities
        
        # For now, we'll enhance this to automatically roll dice when appropriate
        # This could be expanded to detect specific action types and roll appropriate dice
        
        return response
    
    def _generate_opening_narrative(self, character_name: str, character_class: str = None) -> str:
        """Generate opening narrative for new adventure"""
        if not self.client:
            return f"""# The Beginning of {character_name}'s Journey

The night air is thick with the scent of rain and something else... something metallic. You find yourself in the shadows of the city, where the neon lights flicker like dying stars. This is your world now, a world of darkness and secrets.

As {character_name}, you are about to embark on a journey that will test your limits and reveal the true nature of the night. The city holds many secrets, and you are about to discover them.

What would you like to do first?"""
        
        try:
            prompt = f"""Write an engaging opening narrative for a Vampire: The Masquerade character named {character_name}. 
            The character is a {character_class or 'vampire'}. 
            Set the scene in a dark, gothic urban environment. 
            Make it atmospheric and engaging, drawing the player into the world. 
            End with a question about what the character wants to do first."""
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a master storyteller writing opening scenes for Vampire: The Masquerade RPG. Write in second person, be atmospheric and engaging."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.8
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logging_system.log_error(f"Error generating opening narrative: {e}")
            return f"Welcome to the World of Darkness, {character_name}. Your journey begins now..."
    
    def _get_character_description(self) -> str:
        """Get character description for image generation"""
        if not self.current_character:
            return "A mysterious vampire character"
        
        attributes = self.current_character.get('attributes', {})
        class_name = self.current_character.get('class', 'vampire')
        
        description = f"A {class_name} character"
        
        # Add attribute-based descriptions
        if attributes.get('strength', 0) > 12:
            description += ", physically imposing"
        if attributes.get('intelligence', 0) > 12:
            description += ", with keen intelligence"
        if attributes.get('charisma', 0) > 12:
            description += ", charismatic and alluring"
        
        return description
    
    def roll_dice_pool(self, attribute: int, skill: int, difficulty: int = 2, hunger: int = 1) -> Dict[str, Any]:
        """Roll a Vampire: The Masquerade dice pool"""
        try:
            result = self.dice_roller.roll_dice_pool(attribute, skill, difficulty, hunger)
            
            # Log the roll
            character_name = self.current_character.get('name') if self.current_character else None
            self.logging_system.log_dice_roll(result, character_name)
            
            return result
            
        except Exception as e:
            self.logging_system.log_error(f"Error rolling dice pool: {e}")
            return {
                'error': str(e),
                'success': False
            }
    
    def roll_dice(self, expression: str) -> Dict[str, Any]:
        """Roll dice and log the result (legacy method)"""
        try:
            result = self.dice_roller.roll_dice(expression)
            
            # Log the roll
            self.logging_system.log_dice_roll(result, self.current_character.get('name') if self.current_character else None)
            
            return result
            
        except Exception as e:
            self.logging_system.log_error(f"Error rolling dice: {e}")
            return {'error': str(e), 'total': 0}
    
    def award_experience(self, amount: int, source: str = None) -> bool:
        """Award experience to the current character"""
        try:
            if not self.current_character:
                return False
            
            success = self.experience_system.award_experience(self.current_character, amount, source)
            
            if success:
                # Log the experience gain
                self.logging_system.log_experience_gain(
                    self.current_character['name'], amount, source
                )
                
                # Check for level up
                if self.experience_system.check_level_up_available(self.current_character):
                    self.logging_system.log_system_event("level_up_available", {
                        'character_name': self.current_character['name'],
                        'current_level': self.current_character.get('level', 1)
                    })
            
            return success
            
        except Exception as e:
            self.logging_system.log_error(f"Error awarding experience: {e}")
            return False
    
    def save_session(self) -> bool:
        """Save the current session"""
        try:
            if not self.current_character:
                return False
            
            # Save character
            success = self.character_manager.save_character(self.current_character)
            
            if success:
                # Log the save
                self.logging_system.log_file_operation(
                    "save_character", 
                    f"characters/{self.current_character['name']}.json", 
                    True
                )
            
            return success
            
        except Exception as e:
            self.logging_system.log_error(f"Error saving session: {e}")
            return False
    
    def end_session(self):
        """End the current session"""
        try:
            # Save character
            if self.current_character:
                self.save_session()
            
            # End session logging
            self.logging_system.end_session()
            
            # Clear session state
            self.current_character = None
            self.current_session_id = None
            self.conversation_history = []
            self.game_state = {
                'current_scene': None,
                'active_encounters': [],
                'npc_relationships': {},
                'world_state': {}
            }
            
        except Exception as e:
            self.logging_system.log_error(f"Error ending session: {e}")
    
    def get_available_characters(self) -> List[str]:
        """Get list of available characters"""
        return self.character_manager.list_characters()
    
    def get_character_info(self) -> Optional[Dict[str, Any]]:
        """Get current character information"""
        return self.current_character
