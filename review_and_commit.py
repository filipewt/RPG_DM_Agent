#!/usr/bin/env python3
"""
Review and Commit Script for RPG DM Agent
Performs comprehensive checks before committing to GitHub.
"""

import os
import sys
import subprocess
import ast
import importlib.util
from pathlib import Path

def check_python_syntax(file_path):
    """
    Check Python syntax of a file.
    
    Args:
        file_path (str): Path to the Python file to check
    
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Parse the AST to check syntax
        ast.parse(source)
        return True, None
    except SyntaxError as e:
        return False, f"Syntax Error in {file_path}: {e}"
    except Exception as e:
        return False, f"Error reading {file_path}: {e}"

def check_imports(file_path):
    """
    Check if all imports in a file are valid.
    
    Args:
        file_path (str): Path to the Python file to check
    
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        # Get the module name
        module_name = os.path.splitext(os.path.basename(file_path))[0]
        
        # Load the module spec
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None:
            return False, f"Could not load module spec for {file_path}"
        
        # Create the module
        module = importlib.util.module_from_spec(spec)
        
        # Try to execute the module (this will catch import errors)
        spec.loader.exec_module(module)
        return True, None
    except ImportError as e:
        return False, f"Import Error in {file_path}: {e}"
    except Exception as e:
        return False, f"Error checking imports in {file_path}: {e}"

def run_streamlit_check():
    """
    Run Streamlit-specific checks.
    
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        # Try to import streamlit
        import streamlit as st
        return True, None
    except ImportError as e:
        return False, f"Streamlit import error: {e}"

def check_git_status():
    """
    Check git status and return information about changes.
    
    Returns:
        dict: Git status information
    """
    try:
        # Check git status
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, check=True)
        
        changes = result.stdout.strip().split('\n') if result.stdout.strip() else []
        
        # Check if we're on a clean working directory
        is_clean = len(changes) == 0
        
        return {
            'is_clean': is_clean,
            'changes': changes,
            'has_changes': len(changes) > 0
        }
    except subprocess.CalledProcessError as e:
        return {
            'is_clean': False,
            'changes': [],
            'has_changes': False,
            'error': f"Git status error: {e}"
        }

def run_comprehensive_review():
    """
    Run comprehensive review of the project.
    
    Returns:
        dict: Review results
    """
    print("Starting comprehensive review...")
    
    critical_files = [
        "streamlit_ui.py",
        "dm_agent.py", 
        "character_manager.py",
        "dice_roller.py",
        "journal_manager.py",
        "rule_engine.py",
        "main.py"
    ]
    
    review_results = {
        'syntax_errors': [],
        'import_errors': [],
        'streamlit_errors': [],
        'git_status': None,
        'overall_status': 'PASS'
    }
    
    # Check syntax for all critical files
    print("\nChecking Python syntax...")
    for file_path in critical_files:
        if os.path.exists(file_path):
            is_valid, error = check_python_syntax(file_path)
            if not is_valid:
                review_results['syntax_errors'].append(error)
                print(f"ERROR: {error}")
            else:
                print(f"OK: {file_path} - Syntax OK")
        else:
            print(f"WARNING: {file_path} - File not found")
    
    # Check imports for all critical files
    print("\nChecking imports...")
    for file_path in critical_files:
        if os.path.exists(file_path):
            is_valid, error = check_imports(file_path)
            if not is_valid:
                review_results['import_errors'].append(error)
                print(f"ERROR: {error}")
            else:
                print(f"OK: {file_path} - Imports OK")
    
    # Check Streamlit
    print("\nChecking Streamlit...")
    is_valid, error = run_streamlit_check()
    if not is_valid:
        review_results['streamlit_errors'].append(error)
        print(f"ERROR: {error}")
    else:
        print("OK: Streamlit - OK")
    
    # Check git status
    print("\nChecking Git status...")
    review_results['git_status'] = check_git_status()
    if review_results['git_status']['has_changes']:
        print("Changes detected:")
        for change in review_results['git_status']['changes']:
            print(f"   {change}")
    else:
        print("OK: Working directory is clean")
    
    # Determine overall status
    total_errors = (len(review_results['syntax_errors']) + 
                   len(review_results['import_errors']) + 
                   len(review_results['streamlit_errors']))
    
    if total_errors > 0:
        review_results['overall_status'] = 'FAIL'
    
    return review_results

def commit_to_github(commit_message="Update RPG DM Agent"):
    """
    Commit changes to GitHub after review passes.
    
    Args:
        commit_message (str): Commit message
    
    Returns:
        bool: Success status
    """
    try:
        print(f"\nCommitting to GitHub with message: '{commit_message}'")
        
        # Add all changes
        subprocess.run(['git', 'add', '.'], check=True)
        print("SUCCESS: Files staged")
        
        # Commit
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        print("SUCCESS: Changes committed")
        
        # Push to GitHub
        subprocess.run(['git', 'push'], check=True)
        print("SUCCESS: Changes pushed to GitHub")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Git operation failed: {e}")
        return False

def main():
    """Main function to run review and commit process."""
    print("RPG DM Agent - Review and Commit Process")
    print("=" * 50)
    
    # Run comprehensive review
    review_results = run_comprehensive_review()
    
    print("\n" + "=" * 50)
    print("REVIEW SUMMARY")
    print("=" * 50)
    
    # Display results
    if review_results['overall_status'] == 'PASS':
        print("SUCCESS: ALL CHECKS PASSED - Ready for commit!")
        
        # Ask for commit message
        commit_message = input("\nEnter commit message (or press Enter for default): ").strip()
        if not commit_message:
            commit_message = "Update RPG DM Agent"
        
        # Commit to GitHub
        if commit_to_github(commit_message):
            print("\nSUCCESS: Changes committed and pushed to GitHub!")
        else:
            print("\nFAILED: Could not commit to GitHub")
            sys.exit(1)
    else:
        print("FAILED: REVIEW FAILED - Fix errors before committing")
        print("\nErrors found:")
        
        for error in review_results['syntax_errors']:
            print(f"  Syntax Error: {error}")
        
        for error in review_results['import_errors']:
            print(f"  Import Error: {error}")
        
        for error in review_results['streamlit_errors']:
            print(f"  Streamlit Error: {error}")
        
        print("\nPlease fix all errors and run the review again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
