# RPG DM Agent

An LLM-powered Python RPG Dungeon Master Agent that behaves as a Dungeon Master — guiding players through adventures, managing rules, narrating in an engaging and immersive tone, and interacting through a chat-based UI.

## Features

### 🎲 Core Functionality
- **AI-Powered Storytelling**: Uses OpenAI's GPT models for immersive narrative generation
- **Rule System**: Reads game rules from JSON files in the `rules/` folder
- **Character Management**: Creates and manages character sheets with full progression
- **Adventure Journal**: Beautifully formatted Markdown journals for each adventure
- **Dice Mechanics**: Comprehensive dice rolling system with transparent results
- **Experience System**: Automatic XP tracking and level-up mechanics
- **Media Integration**: Image generation and management for enhanced storytelling

### 🧛 Vampire: The Masquerade Support
- Pre-configured with Vampire: The Masquerade rules and character templates
- Character creation with attributes, skills, and disciplines
- Combat system with dice rolls and damage calculation
- Experience tracking and character progression

### 🎮 User Interface
- **Streamlit Chat Interface**: Modern, responsive web-based chat UI
- **Character Dashboard**: Real-time character information display
- **Quick Actions**: One-click common actions (look, talk, attack, move)
- **Dice Roller**: Integrated dice rolling with transparent results
- **Session Management**: Save/load adventures and character progress

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd RPG_DM_Agent
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up OpenAI API key** (optional but recommended):
   ```bash
   export OPENAI_API_KEY="your-openai-api-key-here"
   ```

4. **Run the application**:
   ```bash
   streamlit run main.py
   ```

## Usage

### Starting a New Adventure

1. **Launch the app** by running `streamlit run main.py`
2. **Open your browser** to the provided URL (usually `http://localhost:8501`)
3. **Click "Start New Adventure"** in the startup screen
4. **Enter character details**:
   - Character name
   - Character class (Brujah, Gangrel, Malkavian, etc.)
   - Adventure title
   - Custom attributes (optional)
5. **Click "Start Adventure"** to begin

### Continuing an Adventure

1. **Click "Continue Adventure"** in the startup screen
2. **Select your character** from the dropdown
3. **Click "Continue Adventure"** to resume

### Playing the Game

- **Type your actions** in the chat input field
- **Use quick actions** for common activities (look, talk, attack, move)
- **Roll dice** using the sidebar dice roller or quick actions
- **View character info** in the sidebar
- **Save your progress** using the "Save Session" button

### Game Mechanics

#### Dice Rolling
- Use standard dice notation: `2d6+3`, `1d20`, `3d4-2`
- All rolls are logged and displayed transparently
- The DM explains results in narrative terms

#### Character Progression
- Gain experience points for successful actions
- Level up when you have enough XP
- Choose how to spend XP on improvements

#### Combat System
- Roll initiative to determine turn order
- Attack rolls against target's Armor Class
- Damage rolls with appropriate modifiers
- Status effects and conditions

## File Structure

```
RPG_DM_Agent/
├── main.py                 # Main application entry point
├── streamlit_ui.py        # Streamlit web interface
├── dm_agent.py            # Core DM Agent class
├── character_manager.py   # Character creation and management
├── rule_engine.py         # Game rules and mechanics
├── journal_manager.py     # Adventure journal system
├── experience_system.py    # XP and leveling system
├── media_manager.py       # Image generation and media
├── logging_system.py      # Comprehensive logging
├── dice_roller.py         # Dice rolling mechanics
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── rules/                 # Game rule JSON files
│   ├── vampire_quick_rules_reference.json
│   └── Vampire_The_Masquerade_Character_Creation_rules.json
├── templates/             # Character templates
│   └── Vampire_The_Masquerade_Character_Sheet.json
├── characters/            # Saved character files
├── journals/              # Adventure journals (Markdown)
├── media/                 # Generated images and media
│   ├── images/
│   ├── audio/
│   └── metadata/
└── logs/                  # Session and system logs
```

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key for LLM functionality
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

### Customization

#### Adding New Rules
1. Add JSON rule files to the `rules/` directory
2. Rules should follow the existing format
3. The system will automatically load new rules

#### Custom Character Templates
1. Create JSON character templates in the `templates/` directory
2. Follow the existing character sheet format
3. Templates will be available in character creation

#### Modifying DM Personality
Edit the `dm_personality` dictionary in `dm_agent.py`:
```python
self.dm_personality = {
    'tone': 'engaging and immersive',
    'style': 'descriptive and atmospheric',
    'narrative_voice': 'fantasy novelist',
    'dice_style': 'dramatic and transparent'
}
```

## Troubleshooting

### Common Issues

1. **"No OpenAI API key" warning**:
   - Set your OpenAI API key: `export OPENAI_API_KEY="your-key"`
   - The system will work with limited functionality without it

2. **Port already in use**:
   - Streamlit will automatically find an available port
   - Or specify a port: `streamlit run main.py --server.port 8502`

3. **Character not loading**:
   - Check that character files exist in `characters/` directory
   - Verify JSON format is correct

4. **Images not generating**:
   - This is expected in the current implementation
   - Image generation requires integration with AI image services

### Logs and Debugging

- **Session logs**: Check `logs/session_*.log` for detailed session information
- **Error logs**: Check `logs/errors.log` for system errors
- **Main log**: Check `logs/rpg_dm_agent.log` for general system activity

## Development

### Adding New Features

1. **New dice mechanics**: Extend `dice_roller.py`
2. **New character attributes**: Update character templates
3. **New game rules**: Add JSON files to `rules/`
4. **New UI components**: Modify `streamlit_ui.py`

### Testing

Run the application and test:
1. Character creation
2. Dice rolling
3. Experience gain
4. Journal updates
5. Session saving/loading

## License

This project is open source. Please check the license file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs
3. Create an issue with detailed information
4. Include relevant log files

---

**Enjoy your adventures in the World of Darkness!** 🧛‍♂️
