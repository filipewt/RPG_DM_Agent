"""
Streamlit UI for RPG DM Agent
A minimal working version with essential functionality
"""

import streamlit as st
from datetime import datetime
from dm_agent import DMAgent
from character_manager import CharacterManager
from dice_roller import DiceRoller
from journal_manager import JournalManager

class StreamlitUI:
    def __init__(self):
        self.character_manager = CharacterManager()
        self.dice_roller = DiceRoller()
        self.journal_manager = JournalManager()
        self.initialize_session_state()

    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'dm_agent' not in st.session_state:
            st.session_state.dm_agent = DMAgent()
        
        if 'session_started' not in st.session_state:
            st.session_state.session_started = False
        
        if 'current_character' not in st.session_state:
            st.session_state.current_character = None
        
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        if 'show_character_creation' not in st.session_state:
            st.session_state.show_character_creation = False
        
        if 'show_character_selection' not in st.session_state:
            st.session_state.show_character_selection = False
        
        if 'startup_chat' not in st.session_state:
            st.session_state.startup_chat = []
        
        if 'character_creation_chat' not in st.session_state:
            st.session_state.character_creation_chat = []
        
        if 'character_selection_chat' not in st.session_state:
            st.session_state.character_selection_chat = []

    def run(self):
        """Main application entry point"""
        st.set_page_config(
            page_title="RPG DM Agent",
            page_icon="🧛",
            layout="wide"
        )
        
        # Custom CSS
        st.markdown("""
        <style>
        .dm-message {
            background-color: #2b2b2b;
            padding: 10px;
            border-radius: 5px;
            margin: 5px 0;
            color: white;
        }
        .player-message {
            background-color: #1e3a8a;
            padding: 10px;
            border-radius: 5px;
            margin: 5px 0;
            color: white;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Main application logic
        if st.session_state.get('show_character_creation', False):
            self.render_character_creation()
        elif st.session_state.get('show_character_selection', False):
            self.render_character_selection()
        elif not st.session_state.session_started:
            self.render_startup_screen()
        else:
            self.render_main_chat()

    def render_startup_screen(self):
        """Render the startup screen"""
        st.markdown("## 🧛‍♂️ Welcome to the World of Darkness")
        
        # Display chat history
        for message in st.session_state.startup_chat:
            if message['role'] == 'dm':
                st.markdown(f"""
                <div class="dm-message">
                    <strong>🧛‍♂️ DM:</strong> {message['content']}
                </div>
                """, unsafe_allow_html=True)
        
        # Add initial DM message if chat is empty
        if not st.session_state.startup_chat:
            st.session_state.startup_chat.append({
                'role': 'dm',
                'content': "Welcome to the World of Darkness! I'm your Dungeon Master, and I'm here to guide you through your vampire adventure. What would you like to do?\n\n• **Start a new adventure** - Create a new character and begin your journey\n• **Continue an adventure** - Resume with an existing character\n\nJust tell me what you'd like to do!",
                'timestamp': datetime.now().isoformat()
            })
            st.rerun()
        
        # Input area
        st.markdown("---")
        
        # Player input with button
        col1, col2 = st.columns([5, 1])
        
        with col1:
            player_input = st.text_input(
                "Your response:",
                placeholder="Type what you want to do...",
                key="startup_input",
                label_visibility="collapsed"
            )
        
        with col2:
            if st.button("▶️", key="startup_send_btn", help="Send message"):
                if player_input.strip():
                    self._process_startup_input(player_input)
                    st.rerun()
        
        # Handle ENTER key press using form
        if player_input and player_input.strip():
            if not st.session_state.get("processing_startup", False):
                st.session_state.processing_startup = True
                self._process_startup_input(player_input)
                # Clear the input after processing
                st.session_state.startup_input = ""
                st.rerun()
            else:
                # Reset processing flag after rerun
                st.session_state.processing_startup = False
        
        # Character creation screen
        if st.session_state.get('show_character_creation', False):
            self.render_character_creation()
        
        # Character selection screen
        if st.session_state.get('show_character_selection', False):
            self.render_character_selection()

    def _process_startup_input(self, player_input: str):
        """Process player input on startup screen"""
        st.session_state.startup_chat.append({
            'role': 'player',
            'content': player_input,
            'timestamp': datetime.now().isoformat()
        })
        
        input_lower = player_input.lower()
        
        # Check for new adventure keywords
        if any(word in input_lower for word in ['new', 'start', 'create', 'begin', 'adventure']):
            st.session_state.startup_chat.append({
                'role': 'dm',
                'content': "Excellent! Let's create a new character for your adventure. I'll guide you through the process step by step.",
                'timestamp': datetime.now().isoformat()
            })
            st.session_state.show_character_creation = True
            st.session_state.character_creation_step = 0
            st.session_state.character_creation_chat = []
            st.session_state.character_data = {}
            st.session_state.startup_chat = []
        
        # Check for continue adventure keywords
        elif any(word in input_lower for word in ['continue', 'resume', 'existing', 'load', 'character']):
            st.session_state.startup_chat.append({
                'role': 'dm',
                'content': "Great! Let's continue with one of your existing characters. I'll show you what's available.",
                'timestamp': datetime.now().isoformat()
            })
            st.session_state.show_character_selection = True
            st.session_state.startup_chat = []
        
        else:
            st.session_state.startup_chat.append({
                'role': 'dm',
                'content': "I'm not sure what you'd like to do. You can:\n\n• **Start a new adventure** - Say 'new adventure' or 'create character'\n• **Continue an adventure** - Say 'continue' or 'load character'\n\nWhat would you like to do?",
                'timestamp': datetime.now().isoformat()
            })

    def render_character_creation(self):
        """Render character creation screen"""
        st.markdown("## 📝 Character Creation")
        
        # Display chat history
        for message in st.session_state.character_creation_chat:
            if message['role'] == 'dm':
                st.markdown(f"""
                <div class="dm-message">
                    <strong>🧛‍♂️ DM:</strong> {message['content']}
                </div>
                """, unsafe_allow_html=True)
        
        # Add initial DM message if chat is empty
        if not st.session_state.character_creation_chat:
            st.session_state.character_creation_chat.append({
                'role': 'dm',
                'content': "Welcome to character creation! I'll guide you through creating your vampire character step by step. Let's start with the basics - what's your character's name?",
                'timestamp': datetime.now().isoformat()
            })
            st.rerun()
        
        # Input area
        st.markdown("---")
        
        # Player input with buttons
        col1, col2, col3 = st.columns([5, 1, 1])
        
        with col1:
            player_input = st.text_input(
                "Your response:",
                placeholder="Type your answer here...",
                key="character_creation_input",
                label_visibility="collapsed"
            )
        
        with col2:
            if st.button("▶️", key="character_creation_send_btn", help="Send message"):
                if player_input.strip():
                    self._process_character_creation_input(player_input)
                    st.rerun()
        
        with col3:
            if st.button("◀️", key="character_creation_back_btn", help="Back to Start"):
                st.session_state.show_character_creation = False
                st.session_state.character_creation_chat = []
                st.rerun()
        
        # Handle ENTER key press using form
        if player_input and player_input.strip():
            if not st.session_state.get("processing_character_creation", False):
                st.session_state.processing_character_creation = True
                self._process_character_creation_input(player_input)
                # Clear the input after processing
                st.session_state.character_creation_input = ""
                st.rerun()
            else:
                # Reset processing flag after rerun
                st.session_state.processing_character_creation = False

    def _process_character_creation_input(self, player_input: str):
        """Process player input during character creation with LLM validation"""
        st.session_state.character_creation_chat.append({
            'role': 'player',
            'content': player_input,
            'timestamp': datetime.now().isoformat()
        })
        
        # Get current step
        current_step = st.session_state.get('character_creation_step', 0)
        
        # Process based on current step
        if current_step == 0:  # Name step
            if self._validate_name_input(player_input):
                st.session_state.character_data = {'name': player_input.strip()}
                st.session_state.character_creation_step = 1
                st.session_state.character_creation_chat.append({
                    'role': 'dm',
                    'content': f"Excellent! So your character is named **{player_input.strip()}**. Now, tell me about who they were before becoming a vampire. What did they do for a living? What was their background?",
                    'timestamp': datetime.now().isoformat()
                })
            else:
                st.session_state.character_creation_chat.append({
                    'role': 'dm',
                    'content': "That doesn't look like a proper character name. Please provide a clear name for your character, like 'Marcus' or 'Elena'.",
                    'timestamp': datetime.now().isoformat()
                })
        
        elif current_step == 1:  # Concept step
            if self._validate_concept_input(player_input):
                st.session_state.character_data['concept'] = player_input.strip()
                st.session_state.character_creation_step = 2
                st.session_state.character_creation_chat.append({
                    'role': 'dm',
                    'content': f"Fascinating! A {player_input.strip()}. Now, what drives **{st.session_state.character_data['name']}**? What do they want to achieve? What is their motivation?",
                    'timestamp': datetime.now().isoformat()
                })
            else:
                st.session_state.character_creation_chat.append({
                    'role': 'dm',
                    'content': "Please tell me about your character's background in more detail. What did they do for a living? For example: 'Former detective', 'Art gallery owner', or 'Street musician'.",
                    'timestamp': datetime.now().isoformat()
                })
        
        elif current_step == 2:  # Motivation step
            if self._validate_motivation_input(player_input):
                st.session_state.character_data['motivation'] = player_input.strip()
                st.session_state.character_creation_step = 3
                clan_options = {
                    'brujah': 'Rebels and fighters',
                    'gangrel': 'Shapeshifters',
                    'malkavian': 'Visionary seers',
                    'nosferatu': 'Deformed spies',
                    'toreador': 'Artists and socialites',
                    'tremere': 'Blood sorcerers',
                    'ventrue': 'Leaders and aristocrats'
                }
                clan_list = "\n".join([f"**{clan.title()}** - {desc}" for clan, desc in clan_options.items()])
                st.session_state.character_creation_chat.append({
                    'role': 'dm',
                    'content': f"Perfect! Now let's choose your clan. In Vampire: The Masquerade, your clan defines your supernatural abilities. Here are the main options:\n\n{clan_list}\n\nWhich clan calls to you?",
                    'timestamp': datetime.now().isoformat()
                })
            else:
                st.session_state.character_creation_chat.append({
                    'role': 'dm',
                    'content': "Please tell me more about what drives your character. What do they want to achieve? For example: 'Seek justice', 'Protect the innocent', or 'Gain power'.",
                    'timestamp': datetime.now().isoformat()
                })
        
        elif current_step == 3:  # Clan selection
            clan_options = {
                'brujah': 'Brujah',
                'gangrel': 'Gangrel', 
                'malkavian': 'Malkavian',
                'nosferatu': 'Nosferatu',
                'toreador': 'Toreador',
                'tremere': 'Tremere',
                'ventrue': 'Ventrue'
            }
            if self._validate_clan_selection(player_input, clan_options):
                selected_clan = self._extract_clan_from_input(player_input, clan_options)
                st.session_state.character_data['clan'] = selected_clan
                st.session_state.character_creation_step = 4
                st.session_state.character_creation_chat.append({
                    'role': 'dm',
                    'content': f"Excellent choice! **{st.session_state.character_data['name']}** the {selected_clan} is ready. Let's start your adventure!",
                    'timestamp': datetime.now().isoformat()
                })
                # Create character and start adventure
                self._create_character()
                st.session_state.session_started = True
                st.session_state.show_character_creation = False
                st.session_state.current_character = st.session_state.character_data.copy()
                st.session_state.chat_history = []
                st.rerun()
            else:
                st.session_state.character_creation_chat.append({
                    'role': 'dm',
                    'content': "Please choose one of the available clans: Brujah, Gangrel, Malkavian, Nosferatu, Toreador, Tremere, or Ventrue.",
                    'timestamp': datetime.now().isoformat()
                })

    def _create_character(self):
        """Create a new character using collected data"""
        try:
            # Use the collected character data
            character_data = st.session_state.character_data.copy()
            character_data['last_updated'] = datetime.now().isoformat()
            
            # Save character
            self.character_manager.save_character(character_data)
            
            # Start adventure
            st.session_state.dm_agent.start_new_adventure(
                character_data['name'], 
                character_data.get('clan'),
                f"{character_data['name']}'s Journey"
            )
            
        except Exception as e:
            st.error(f"Error creating character: {str(e)}")
    
    def _validate_name_input(self, input_text: str) -> bool:
        """Validate character name input using LLM"""
        try:
            if not st.session_state.dm_agent.client:
                # Fallback validation without LLM
                return len(input_text.strip()) >= 2 and input_text.strip().replace(' ', '').isalpha()
            
            # Use LLM to validate name
            prompt = f"""Is "{input_text.strip()}" a valid character name for a vampire character? 
            A valid name should be:
            - A proper name (first name, optionally with last name)
            - Not just numbers or symbols
            - Appropriate for a vampire character
            - Not empty or just spaces
            
            Respond with only "YES" or "NO"."""
            
            response = st.session_state.dm_agent.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip().upper()
            return result == "YES"
            
        except Exception as e:
            # Fallback to simple validation
            return len(input_text.strip()) >= 2 and input_text.strip().replace(' ', '').isalpha()
    
    def _validate_concept_input(self, input_text: str) -> bool:
        """Validate character concept input using LLM"""
        try:
            if not st.session_state.dm_agent.client:
                # Fallback validation without LLM
                return len(input_text.strip()) >= 5
            
            # Use LLM to validate concept
            prompt = f"""Is "{input_text.strip()}" a valid character concept/background for a vampire character? 
            A valid concept should be:
            - A profession, role, or background (like "Former detective", "Art gallery owner", "Street musician")
            - Not just a single word
            - Appropriate for a vampire character's mortal past
            - Descriptive of who they were before becoming a vampire
            
            Respond with only "YES" or "NO"."""
            
            response = st.session_state.dm_agent.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip().upper()
            return result == "YES"
            
        except Exception as e:
            # Fallback to simple validation
            return len(input_text.strip()) >= 5
    
    def _validate_motivation_input(self, input_text: str) -> bool:
        """Validate character motivation input using LLM"""
        try:
            if not st.session_state.dm_agent.client:
                # Fallback validation without LLM
                return len(input_text.strip()) >= 5
            
            # Use LLM to validate motivation
            prompt = f"""Is "{input_text.strip()}" a valid character motivation for a vampire character? 
            A valid motivation should be:
            - A clear goal or driving force (like "Seek justice", "Protect the innocent", "Gain power")
            - Not just a single word
            - Something that would drive a vampire's actions
            - A meaningful purpose or desire
            
            Respond with only "YES" or "NO"."""
            
            response = st.session_state.dm_agent.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip().upper()
            return result == "YES"
            
        except Exception as e:
            # Fallback to simple validation
            return len(input_text.strip()) >= 5
    
    def _validate_clan_selection(self, input_text: str, clan_options: dict) -> bool:
        """Validate clan selection input using LLM"""
        try:
            if not st.session_state.dm_agent.client:
                # Fallback validation without LLM
                input_lower = input_text.lower().strip()
                return any(clan in input_lower for clan in clan_options.keys())
            
            # Use LLM to validate clan selection
            clans_list = ", ".join(clan_options.keys())
            prompt = f"""Does the input "{input_text.strip()}" contain a valid Vampire: The Masquerade clan selection?
            
            Valid clans are: {clans_list}
            
            The input should contain one of these clan names (case insensitive).
            Respond with only "YES" or "NO"."""
            
            response = st.session_state.dm_agent.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip().upper()
            return result == "YES"
            
        except Exception as e:
            # Fallback to simple validation
            input_lower = input_text.lower().strip()
            return any(clan in input_lower for clan in clan_options.keys())
    
    def _extract_clan_from_input(self, input_text: str, clan_options: dict) -> str:
        """Extract clan name from input text"""
        input_lower = input_text.lower().strip()
        for clan_key, clan_name in clan_options.items():
            if clan_key in input_lower:
                return clan_name
        return clan_options.get('brujah', 'Brujah')  # Default fallback

    def render_character_selection(self):
        """Render character selection screen"""
        st.markdown("## 📖 Continue Adventure")
        
        # Display chat history
        for message in st.session_state.character_selection_chat:
            if message['role'] == 'dm':
                st.markdown(f"""
                <div class="dm-message">
                    <strong>🧛‍♂️ DM:</strong> {message['content']}
                </div>
                """, unsafe_allow_html=True)
        
        # Add initial DM message if chat is empty
        if not st.session_state.character_selection_chat:
            st.session_state.character_selection_chat.append({
                'role': 'dm',
                'content': "Welcome back! I see you have some existing characters. Which one would you like to continue with?\n\n• Test Character\n\nJust tell me the name of the character you want to play.",
                'timestamp': datetime.now().isoformat()
            })
            st.rerun()
        
        # Input area
        st.markdown("---")
        
        # Player input with buttons
        col1, col2, col3 = st.columns([5, 1, 1])
        
        with col1:
            player_input = st.text_input(
                "Your response:",
                placeholder="Type the character name...",
                key="character_selection_input",
                label_visibility="collapsed"
            )
        
        with col2:
            if st.button("▶️", key="character_selection_send_btn", help="Send message"):
                if player_input.strip():
                    self._process_character_selection_input(player_input)
                    st.rerun()
        
        with col3:
            if st.button("◀️", key="character_selection_back_btn", help="Back to Start"):
                st.session_state.show_character_selection = False
                st.session_state.character_selection_chat = []
                st.rerun()
        
        # Handle ENTER key press using form
        if player_input and player_input.strip():
            if not st.session_state.get("processing_character_selection", False):
                st.session_state.processing_character_selection = True
                self._process_character_selection_input(player_input)
                # Clear the input after processing
                st.session_state.character_selection_input = ""
                st.rerun()
            else:
                # Reset processing flag after rerun
                st.session_state.processing_character_selection = False

    def _process_character_selection_input(self, player_input: str):
        """Process player input during character selection"""
        st.session_state.character_selection_chat.append({
            'role': 'player',
            'content': player_input,
            'timestamp': datetime.now().isoformat()
        })
        
        # Simple character selection logic
        if 'test' in player_input.lower():
            st.session_state.character_selection_chat.append({
                'role': 'dm',
                'content': f"Perfect! Loading Test Character's adventure. Let's continue where you left off!",
                'timestamp': datetime.now().isoformat()
            })
            st.session_state.session_started = True
            st.session_state.show_character_selection = False
            st.session_state.current_character = {'name': 'Test Character'}
            st.session_state.chat_history = []
            st.rerun()
        else:
            st.session_state.character_selection_chat.append({
                'role': 'dm',
                'content': f"I didn't find a character named '{player_input}'. Please try again.",
                'timestamp': datetime.now().isoformat()
            })

    def render_main_chat(self):
        """Render the main chat interface"""
        # Get character name for title
        character_name = "Unknown"
        if st.session_state.current_character:
            character_name = st.session_state.current_character.get('name', 'Unknown')
        
        st.markdown(f"## 💬 {character_name}'s Journey")
        
        # Chat history - Show only DM messages
        for message in st.session_state.chat_history:
            if message['role'] == 'dm':
                st.markdown(f"""
                <div class="dm-message">
                    <strong>🧛 DM:</strong> {message['content']}
                </div>
                """, unsafe_allow_html=True)
        
        # Add initial DM message if chat is empty
        if not st.session_state.chat_history:
            st.session_state.chat_history.append({
                'role': 'dm',
                'content': f"Welcome to your adventure, {character_name}! The night is young and full of possibilities. What would you like to do?",
                'timestamp': datetime.now().isoformat()
            })
            st.rerun()
        
        # Input area
        st.markdown("---")
        
        # Player input with button
        col1, col2 = st.columns([5, 1])
        
        with col1:
            player_input = st.text_input(
                "What do you want to do?",
                placeholder="Describe your action...",
                key="player_input",
                label_visibility="collapsed"
            )
        
        with col2:
            if st.button("▶️", key="main_chat_send_btn", help="Send message"):
                if player_input.strip():
                    self._process_main_chat_input(player_input)
                    st.rerun()
        
        # Handle ENTER key press using form
        if player_input and player_input.strip():
            if not st.session_state.get("processing_main_chat", False):
                st.session_state.processing_main_chat = True
                self._process_main_chat_input(player_input)
                # Clear the input after processing
                st.session_state.player_input = ""
                st.rerun()
            else:
                # Reset processing flag after rerun
                st.session_state.processing_main_chat = False

    def _process_main_chat_input(self, player_input: str):
        """Process player input in main chat"""
        # Add player message to chat
        st.session_state.chat_history.append({
            'role': 'player',
            'content': player_input,
            'timestamp': datetime.now().isoformat()
        })
        
        # Process with DM agent
        try:
            dm_response = st.session_state.dm_agent.process_player_input(player_input)
            
            # Add DM response to chat
            st.session_state.chat_history.append({
                'role': 'dm',
                'content': dm_response,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            # Fallback response
            st.session_state.chat_history.append({
                'role': 'dm',
                'content': f"I understand you want to {player_input.lower()}. That's an interesting choice. What happens next?",
                'timestamp': datetime.now().isoformat()
            })

def main():
    """Main function to run the Streamlit app"""
    ui = StreamlitUI()
    ui.run()

if __name__ == "__main__":
    main()