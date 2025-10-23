"""
Main entry point for the RPG DM Agent application
"""

import os
import sys
import streamlit as st
from streamlit_ui import StreamlitUI
from dotenv import load_dotenv

def main():
    """Main function to run the RPG DM Agent"""
    try:
        # Load environment variables from .env file
        load_dotenv()
        
        # Check for required environment variables
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not openai_api_key:
            print("Warning: OPENAI_API_KEY environment variable not set.")
            print("The DM Agent will have limited functionality without OpenAI integration.")
            print("To enable full functionality, set your OpenAI API key in the .env file:")
            print("OPENAI_API_KEY=your-api-key-here")
            print()
        else:
            print("SUCCESS: OpenAI API key found! Full LLM functionality enabled.")
        
        # Run the Streamlit UI
        ui = StreamlitUI()
        ui.run()
        
    except Exception as e:
        print(f"Error starting RPG DM Agent: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
