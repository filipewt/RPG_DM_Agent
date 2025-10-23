"""
Main entry point for the RPG DM Agent application.

This module provides the main entry point for the RPG DM Agent application,
handling environment setup and launching the Streamlit UI.
"""

import os
import sys

from dotenv import load_dotenv

from streamlit_ui import StreamlitUI


def check_environment() -> bool:
    """
    Check if required environment variables are set.

    Returns:
        True if environment is properly configured, False otherwise.
    """
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")

    if not openai_api_key:
        print("Warning: OPENAI_API_KEY environment variable not set.")
        print(
            "The DM Agent will have limited functionality without OpenAI integration."
        )
        print("To enable full functionality, set your OpenAI API key in the .env file:")
        print("OPENAI_API_KEY=your-api-key-here")
        print()
        return False

    print("SUCCESS: OpenAI API key found! Full LLM functionality enabled.")
    return True


def main() -> None:
    """
    Main function to run the RPG DM Agent.

    Handles environment setup, configuration validation, and launches the UI.
    """
    try:
        # Load environment variables from .env file
        load_dotenv()

        # Check environment configuration
        check_environment()

        # Run the Streamlit UI
        ui = StreamlitUI()
        ui.run()

    except Exception as e:
        print(f"Error starting RPG DM Agent: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
