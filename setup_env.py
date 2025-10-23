"""
Setup script for .env file configuration
"""

import os

def setup_env_file():
    """Setup the .env file with OpenAI API key"""
    print("OpenAI API Key Setup")
    print("=" * 50)
    
    # Check if .env file exists
    if os.path.exists('.env'):
        print(".env file found!")
        
        # Read current content
        with open('.env', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'your-openai-api-key-here' in content:
            print("Please update your OpenAI API key in the .env file")
            print("Replace 'your-openai-api-key-here' with your actual API key")
        else:
            print(".env file appears to be configured")
    else:
        print(".env file not found. Creating one...")
        
        # Create .env file
        with open('.env', 'w', encoding='utf-8') as f:
            f.write("OPENAI_API_KEY=your-openai-api-key-here\n")
        
        print(".env file created!")
        print("Please edit the .env file and add your OpenAI API key")
    
    print("\nTo edit the .env file:")
    print("   1. Open the .env file in your text editor")
    print("   2. Replace 'your-openai-api-key-here' with your actual API key")
    print("   3. Save the file")
    print("\nThen run: python -m streamlit run main.py")

if __name__ == "__main__":
    setup_env_file()
