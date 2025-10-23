"""
Logging System for RPG DM Agent
Handles comprehensive logging of all system events
"""

import os
import logging
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from logging.handlers import RotatingFileHandler

class LoggingSystem:
    """Comprehensive logging system for the RPG DM Agent"""
    
    def __init__(self, logs_dir: str = "logs"):
        self.logs_dir = logs_dir
        self.logger = None
        self.session_logger = None
        self.session_id = None
        
        # Ensure logs directory exists
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # Initialize logging system
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup the logging system with multiple handlers"""
        try:
            # Create main logger
            self.logger = logging.getLogger('rpg_dm_agent')
            self.logger.setLevel(logging.INFO)
            
            # Clear existing handlers
            self.logger.handlers.clear()
            
            # Create formatters
            detailed_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            simple_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(simple_formatter)
            self.logger.addHandler(console_handler)
            
            # Main log file handler
            main_log_file = os.path.join(self.logs_dir, 'rpg_dm_agent.log')
            file_handler = RotatingFileHandler(
                main_log_file, maxBytes=10*1024*1024, backupCount=5
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(detailed_formatter)
            self.logger.addHandler(file_handler)
            
            # Error log file handler
            error_log_file = os.path.join(self.logs_dir, 'errors.log')
            error_handler = RotatingFileHandler(
                error_log_file, maxBytes=5*1024*1024, backupCount=3
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(detailed_formatter)
            self.logger.addHandler(error_handler)
            
            self.logger.info("Logging system initialized")
            
        except Exception as e:
            print(f"Error setting up logging system: {e}")
    
    def start_session(self, character_name: str, session_type: str = "adventure") -> str:
        """
        Start a new session log
        
        Args:
            character_name: Name of the character
            session_type: Type of session (adventure, combat, etc.)
            
        Returns:
            Session ID
        """
        try:
            # Generate session ID
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.session_id = f"{character_name}_{session_type}_{timestamp}"
            
            # Create session logger
            self.session_logger = logging.getLogger(f'session_{self.session_id}')
            self.session_logger.setLevel(logging.INFO)
            
            # Clear existing handlers
            self.session_logger.handlers.clear()
            
            # Session log file
            session_log_file = os.path.join(self.logs_dir, f'session_{self.session_id}.log')
            session_handler = RotatingFileHandler(
                session_log_file, maxBytes=5*1024*1024, backupCount=2
            )
            session_handler.setLevel(logging.INFO)
            
            # Session formatter
            session_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            session_handler.setFormatter(session_formatter)
            self.session_logger.addHandler(session_handler)
            
            # Log session start
            self.session_logger.info(f"Session started: {character_name} - {session_type}")
            self.logger.info(f"Started session: {self.session_id}")
            
            return self.session_id
            
        except Exception as e:
            self.logger.error(f"Error starting session: {e}")
            return None
    
    def end_session(self):
        """End the current session"""
        try:
            if self.session_logger:
                self.session_logger.info(f"Session ended: {self.session_id}")
                self.logger.info(f"Ended session: {self.session_id}")
                
                # Close session logger
                for handler in self.session_logger.handlers:
                    handler.close()
                self.session_logger.handlers.clear()
                
                self.session_logger = None
                self.session_id = None
                
        except Exception as e:
            self.logger.error(f"Error ending session: {e}")
    
    def log_dice_roll(self, roll_result: Dict[str, Any], character_name: str = None):
        """
        Log a dice roll
        
        Args:
            roll_result: Result of the dice roll
            character_name: Name of the character who rolled
        """
        try:
            if self.session_logger:
                character_info = f"{character_name}: " if character_name else ""
                self.session_logger.info(
                    f"DICE ROLL - {character_info}{roll_result.get('expression', 'unknown')} = "
                    f"{roll_result.get('total', 0)} (rolls: {roll_result.get('individual_rolls', [])})"
                )
            
            self.logger.info(f"Dice roll: {roll_result}")
            
        except Exception as e:
            self.logger.error(f"Error logging dice roll: {e}")
    
    def log_character_action(self, character_name: str, action: str, 
                           result: str = None, details: Dict[str, Any] = None):
        """
        Log a character action
        
        Args:
            character_name: Name of the character
            action: Action performed
            result: Result of the action
            details: Additional details
        """
        try:
            log_message = f"CHARACTER ACTION - {character_name}: {action}"
            
            if result:
                log_message += f" -> {result}"
            
            if details:
                log_message += f" (Details: {details})"
            
            if self.session_logger:
                self.session_logger.info(log_message)
            
            self.logger.info(log_message)
            
        except Exception as e:
            self.logger.error(f"Error logging character action: {e}")
    
    def log_combat_event(self, event_type: str, participants: List[str], 
                        details: Dict[str, Any] = None):
        """
        Log a combat event
        
        Args:
            event_type: Type of combat event
            participants: List of participants
            details: Additional details
        """
        try:
            log_message = f"COMBAT EVENT - {event_type}: {', '.join(participants)}"
            
            if details:
                log_message += f" (Details: {details})"
            
            if self.session_logger:
                self.session_logger.info(log_message)
            
            self.logger.info(log_message)
            
        except Exception as e:
            self.logger.error(f"Error logging combat event: {e}")
    
    def log_experience_gain(self, character_name: str, amount: int, source: str = None):
        """
        Log experience gain
        
        Args:
            character_name: Name of the character
            amount: Amount of experience gained
            source: Source of the experience
        """
        try:
            log_message = f"EXPERIENCE GAIN - {character_name}: +{amount} XP"
            
            if source:
                log_message += f" (from {source})"
            
            if self.session_logger:
                self.session_logger.info(log_message)
            
            self.logger.info(log_message)
            
        except Exception as e:
            self.logger.error(f"Error logging experience gain: {e}")
    
    def log_level_up(self, character_name: str, old_level: int, new_level: int, 
                    choices: List[str] = None):
        """
        Log a level up
        
        Args:
            character_name: Name of the character
            old_level: Previous level
            new_level: New level
            choices: Level-up choices made
        """
        try:
            log_message = f"LEVEL UP - {character_name}: Level {old_level} -> {new_level}"
            
            if choices:
                log_message += f" (Choices: {', '.join(choices)})"
            
            if self.session_logger:
                self.session_logger.info(log_message)
            
            self.logger.info(log_message)
            
        except Exception as e:
            self.logger.error(f"Error logging level up: {e}")
    
    def log_file_operation(self, operation: str, file_path: str, success: bool, 
                          details: str = None):
        """
        Log a file operation
        
        Args:
            operation: Type of operation (save, load, create, etc.)
            file_path: Path to the file
            success: Whether the operation was successful
            details: Additional details
        """
        try:
            status = "SUCCESS" if success else "FAILED"
            log_message = f"FILE OPERATION - {operation}: {file_path} -> {status}"
            
            if details:
                log_message += f" (Details: {details})"
            
            if self.session_logger:
                self.session_logger.info(log_message)
            
            self.logger.info(log_message)
            
        except Exception as e:
            self.logger.error(f"Error logging file operation: {e}")
    
    def log_rule_reference(self, rule_name: str, rule_path: str, result: Any):
        """
        Log a rule reference
        
        Args:
            rule_name: Name of the rule file
            rule_path: Path to the specific rule
            result: Result of the rule lookup
        """
        try:
            log_message = f"RULE REFERENCE - {rule_name}.{rule_path}: {result}"
            
            if self.session_logger:
                self.session_logger.info(log_message)
            
            self.logger.info(log_message)
            
        except Exception as e:
            self.logger.error(f"Error logging rule reference: {e}")
    
    def log_error(self, error_message: str, exception: Exception = None, 
                  context: Dict[str, Any] = None):
        """
        Log an error
        
        Args:
            error_message: Error message
            exception: Exception object
            context: Additional context
        """
        try:
            log_message = f"ERROR - {error_message}"
            
            if exception:
                log_message += f" (Exception: {str(exception)})"
            
            if context:
                log_message += f" (Context: {context})"
            
            if self.session_logger:
                self.session_logger.error(log_message)
            
            self.logger.error(log_message)
            
        except Exception as e:
            print(f"Error logging error: {e}")
    
    def log_system_event(self, event_type: str, details: Dict[str, Any] = None):
        """
        Log a system event
        
        Args:
            event_type: Type of system event
            details: Event details
        """
        try:
            log_message = f"SYSTEM EVENT - {event_type}"
            
            if details:
                log_message += f" (Details: {details})"
            
            if self.session_logger:
                self.session_logger.info(log_message)
            
            self.logger.info(log_message)
            
        except Exception as e:
            self.logger.error(f"Error logging system event: {e}")
    
    def get_session_log(self, session_id: str) -> Optional[str]:
        """
        Get the log content for a specific session
        
        Args:
            session_id: ID of the session
            
        Returns:
            Log content or None if not found
        """
        try:
            session_log_file = os.path.join(self.logs_dir, f'session_{session_id}.log')
            
            if not os.path.exists(session_log_file):
                return None
            
            with open(session_log_file, 'r', encoding='utf-8') as f:
                return f.read()
                
        except Exception as e:
            self.logger.error(f"Error getting session log: {e}")
            return None
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """
        List all available sessions
        
        Returns:
            List of session information
        """
        try:
            sessions = []
            
            for filename in os.listdir(self.logs_dir):
                if filename.startswith('session_') and filename.endswith('.log'):
                    session_id = filename.replace('session_', '').replace('.log', '')
                    session_file = os.path.join(self.logs_dir, filename)
                    
                    session_info = {
                        'session_id': session_id,
                        'filename': filename,
                        'file_path': session_file,
                        'size': os.path.getsize(session_file),
                        'modified': os.path.getmtime(session_file)
                    }
                    sessions.append(session_info)
            
            return sessions
            
        except Exception as e:
            self.logger.error(f"Error listing sessions: {e}")
            return []
    
    def cleanup_old_logs(self, days_old: int = 30) -> int:
        """
        Clean up old log files
        
        Args:
            days_old: Age threshold in days
            
        Returns:
            Number of files cleaned up
        """
        try:
            import time
            cutoff_time = time.time() - (days_old * 24 * 60 * 60)
            cleaned_count = 0
            
            for filename in os.listdir(self.logs_dir):
                if filename.startswith('session_') and filename.endswith('.log'):
                    file_path = os.path.join(self.logs_dir, filename)
                    if os.path.getmtime(file_path) < cutoff_time:
                        os.remove(file_path)
                        cleaned_count += 1
            
            self.logger.info(f"Cleaned up {cleaned_count} old log files")
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old logs: {e}")
            return 0
