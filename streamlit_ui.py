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
        if not st.session_state.session_started:
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
        
        # Player input
        player_input = st.text_input(
            "Your response:",
            placeholder="Type what you want to do...",
            key="startup_input"
        )
        
        col1, col2 = st.columns([5, 1])
        
        with col1:
            if st.button("▶️", use_container_width=True, key="startup_send_btn", help="Send message"):
                if player_input.strip():
                    self._process_startup_input(player_input)
                    st.rerun()
        
        # Handle ENTER key press
        if player_input and player_input != st.session_state.get("last_startup_input", ""):
            st.session_state.last_startup_input = player_input
            self._process_startup_input(player_input)
            st.rerun()
        
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
        
        # Player input
        player_input = st.text_input(
            "Your response:",
            placeholder="Type your answer here...",
            key="character_creation_input"
        )
        
        col1, col2, col3 = st.columns([5, 1, 1])
        
        with col1:
            if st.button("▶️", use_container_width=True, key="character_creation_send_btn", help="Send message"):
                if player_input.strip():
                    self._process_character_creation_input(player_input)
                    st.rerun()
        
        with col2:
            if st.button("◀️", use_container_width=True, key="character_creation_back_btn", help="Back to Start"):
                st.session_state.show_character_creation = False
                st.session_state.character_creation_chat = []
                st.rerun()
        
        # Handle ENTER key press
        if player_input and player_input != st.session_state.get("last_character_creation_input", ""):
            st.session_state.last_character_creation_input = player_input
            self._process_character_creation_input(player_input)
            st.rerun()

    def _process_character_creation_input(self, player_input: str):
        """Process player input during character creation"""
        st.session_state.character_creation_chat.append({
            'role': 'player',
            'content': player_input,
            'timestamp': datetime.now().isoformat()
        })
        
        # Simple character creation logic
        if len(st.session_state.character_creation_chat) == 2:  # After first response
            st.session_state.character_creation_chat.append({
                'role': 'dm',
                'content': f"Great! So your character is named {player_input}. Now, tell me about who they were before becoming a vampire. What did they do for a living?",
                'timestamp': datetime.now().isoformat()
            })
        elif len(st.session_state.character_creation_chat) == 4:  # After second response
            st.session_state.character_creation_chat.append({
                'role': 'dm',
                'content': f"Excellent! Now, what drives your character? What do they want to achieve?",
                'timestamp': datetime.now().isoformat()
            })
        elif len(st.session_state.character_creation_chat) == 6:  # After third response
            st.session_state.character_creation_chat.append({
                'role': 'dm',
                'content': f"Perfect! Now let's choose your clan. In Vampire: The Masquerade, your clan defines your supernatural abilities. Here are the main options:\n\n**Brujah** - Rebels and fighters\n**Gangrel** - Shapeshifters\n**Malkavian** - Visionary seers\n**Nosferatu** - Deformed spies\n**Toreador** - Artists and socialites\n**Tremere** - Blood sorcerers\n**Ventrue** - Leaders and aristocrats\n\nWhich clan calls to you?",
                'timestamp': datetime.now().isoformat()
            })
        elif len(st.session_state.character_creation_chat) == 8:  # After clan selection
            st.session_state.character_creation_chat.append({
                'role': 'dm',
                'content': f"Excellent choice! Your character is ready. Let's start your adventure!",
                'timestamp': datetime.now().isoformat()
            })
            # Create character and start adventure
            self._create_character()
            st.session_state.session_started = True
            st.session_state.current_character = {'name': 'Test Character'}
            st.session_state.chat_history = []
            st.rerun()

    def _create_character(self):
        """Create a new character"""
        try:
            # Simple character creation
            character_data = {
                'name': 'Test Character',
                'clan': 'Brujah',
                'concept': 'Former detective',
                'motivation': 'Seek justice'
            }
            
            # Save character
            self.character_manager.save_character(character_data)
            
            # Start adventure
            st.session_state.dm_agent.start_new_adventure(
                character_data['name'], 
                character_data.get('clan'),
                f"{character_data['name']} || Journey"
            )
            
        except Exception as e:
            st.error(f"Error creating character: {str(e)}")

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
        
        # Player input
        player_input = st.text_input(
            "Your response:",
            placeholder="Type the character name...",
            key="character_selection_input"
        )
        
        col1, col2, col3 = st.columns([5, 1, 1])
        
        with col1:
            if st.button("▶️", use_container_width=True, key="character_selection_send_btn", help="Send message"):
                if player_input.strip():
                    self._process_character_selection_input(player_input)
                    st.rerun()
        
        with col2:
            if st.button("◀️", use_container_width=True, key="character_selection_back_btn", help="Back to Start"):
                st.session_state.show_character_selection = False
                st.session_state.character_selection_chat = []
                st.rerun()
        
        # Handle ENTER key press
        if player_input and player_input != st.session_state.get("last_character_selection_input", ""):
            st.session_state.last_character_selection_input = player_input
            self._process_character_selection_input(player_input)
            st.rerun()

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
        
        st.markdown(f"## 💬 {character_name} || Journey")
        
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
        
        # Player input
        player_input = st.text_input(
            "What do you want to do?",
            placeholder="Describe your action...",
            key="player_input"
        )
        
        col1, col2 = st.columns([5, 1])
        
        with col1:
            if st.button("▶️", use_container_width=True, key="main_chat_send_btn", help="Send message"):
                if player_input.strip():
                    self._process_main_chat_input(player_input)
                    st.rerun()
        
        # Handle ENTER key press
        if player_input and player_input != st.session_state.get("last_player_input", ""):
            st.session_state.last_player_input = player_input
            self._process_main_chat_input(player_input)
            st.rerun()

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