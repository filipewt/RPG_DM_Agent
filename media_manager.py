"""
Media Management System for RPG DM Agent
Handles image generation and media file management
"""

import os
import requests
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import hashlib
import json

class MediaManager:
    """Handles image generation and media file management"""
    
    def __init__(self, media_dir: str = "media"):
        self.media_dir = media_dir
        self.logger = logging.getLogger(__name__)
        
        # Ensure media directory exists
        os.makedirs(self.media_dir, exist_ok=True)
        
        # Create subdirectories
        self.images_dir = os.path.join(self.media_dir, "images")
        self.audio_dir = os.path.join(self.media_dir, "audio")
        self.metadata_dir = os.path.join(self.media_dir, "metadata")
        
        os.makedirs(self.images_dir, exist_ok=True)
        os.makedirs(self.audio_dir, exist_ok=True)
        os.makedirs(self.metadata_dir, exist_ok=True)
    
    def generate_image(self, prompt: str, style: str = "fantasy", 
                      size: str = "1024x1024", character_name: str = None) -> Optional[str]:
        """
        Generate an image using AI (placeholder implementation)
        
        Args:
            prompt: Text description for image generation
            style: Art style for the image
            size: Image dimensions
            character_name: Character name for file naming
            
        Returns:
            Path to generated image file or None if failed
        """
        try:
            # Create filename based on prompt and timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:8]
            
            if character_name:
                filename = f"{character_name}_{timestamp}_{prompt_hash}.png"
            else:
                filename = f"generated_{timestamp}_{prompt_hash}.png"
            
            image_path = os.path.join(self.images_dir, filename)
            
            # Placeholder implementation - in a real system, this would call an AI image generation API
            # For now, we'll create a placeholder image or download a stock image
            success = self._create_placeholder_image(image_path, prompt, style)
            
            if success:
                # Save metadata
                self._save_image_metadata(image_path, prompt, style, size)
                self.logger.info(f"Generated image: {image_path}")
                return image_path
            else:
                self.logger.error(f"Failed to generate image for prompt: {prompt}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error generating image: {e}")
            return None
    
    def _create_placeholder_image(self, image_path: str, prompt: str, style: str) -> bool:
        """
        Create a placeholder image (placeholder implementation)
        
        Args:
            image_path: Path where to save the image
            prompt: Image prompt
            style: Art style
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # This is a placeholder implementation
            # In a real system, you would integrate with an AI image generation service
            # like DALL-E, Midjourney, Stable Diffusion, etc.
            
            # For now, we'll create a simple text file as a placeholder
            placeholder_content = f"""Generated Image Placeholder
Prompt: {prompt}
Style: {style}
Generated: {datetime.now().isoformat()}

This is a placeholder for an AI-generated image.
In a real implementation, this would be an actual image file.
"""
            
            with open(image_path.replace('.png', '.txt'), 'w', encoding='utf-8') as f:
                f.write(placeholder_content)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating placeholder image: {e}")
            return False
    
    def _save_image_metadata(self, image_path: str, prompt: str, style: str, size: str):
        """Save metadata for generated image"""
        try:
            metadata = {
                'filename': os.path.basename(image_path),
                'prompt': prompt,
                'style': style,
                'size': size,
                'generated_at': datetime.now().isoformat(),
                'file_size': 0,  # Would be actual file size in real implementation
                'format': 'png'
            }
            
            metadata_file = os.path.join(self.metadata_dir, f"{os.path.basename(image_path)}.json")
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error saving image metadata: {e}")
    
    def download_image(self, url: str, filename: str = None) -> Optional[str]:
        """
        Download an image from a URL
        
        Args:
            url: URL of the image to download
            filename: Custom filename (optional)
            
        Returns:
            Path to downloaded image or None if failed
        """
        try:
            # Generate filename if not provided
            if not filename:
                url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"downloaded_{timestamp}_{url_hash}.jpg"
            
            image_path = os.path.join(self.images_dir, filename)
            
            # Download the image
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Save the image
            with open(image_path, 'wb') as f:
                f.write(response.content)
            
            # Save metadata
            metadata = {
                'filename': filename,
                'source_url': url,
                'downloaded_at': datetime.now().isoformat(),
                'file_size': len(response.content),
                'format': 'jpg'
            }
            
            metadata_file = os.path.join(self.metadata_dir, f"{filename}.json")
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            
            self.logger.info(f"Downloaded image: {image_path}")
            return image_path
            
        except Exception as e:
            self.logger.error(f"Error downloading image from {url}: {e}")
            return None
    
    def get_character_portrait(self, character_name: str, description: str = None) -> Optional[str]:
        """
        Get or generate a character portrait
        
        Args:
            character_name: Name of the character
            description: Character description for generation
            
        Returns:
            Path to character portrait or None if failed
        """
        try:
            # Check if portrait already exists
            portrait_filename = f"{character_name}_portrait.png"
            portrait_path = os.path.join(self.images_dir, portrait_filename)
            
            if os.path.exists(portrait_path):
                return portrait_path
            
            # Generate new portrait
            if not description:
                description = f"A portrait of {character_name}, a fantasy character"
            
            prompt = f"Character portrait: {description}, detailed fantasy art, professional character design"
            return self.generate_image(prompt, "character_portrait", "512x512", character_name)
            
        except Exception as e:
            self.logger.error(f"Error getting character portrait: {e}")
            return None
    
    def get_scene_image(self, scene_description: str, character_name: str = None) -> Optional[str]:
        """
        Get or generate a scene image
        
        Args:
            scene_description: Description of the scene
            character_name: Character name for file naming
            
        Returns:
            Path to scene image or None if failed
        """
        try:
            prompt = f"Fantasy scene: {scene_description}, detailed environment, atmospheric lighting"
            return self.generate_image(prompt, "environment", "1024x1024", character_name)
            
        except Exception as e:
            self.logger.error(f"Error getting scene image: {e}")
            return None
    
    def get_combat_image(self, combat_description: str, character_name: str = None) -> Optional[str]:
        """
        Get or generate a combat scene image
        
        Args:
            combat_description: Description of the combat
            character_name: Character name for file naming
            
        Returns:
            Path to combat image or None if failed
        """
        try:
            prompt = f"Fantasy combat scene: {combat_description}, dynamic action, dramatic lighting"
            return self.generate_image(prompt, "action", "1024x1024", character_name)
            
        except Exception as e:
            self.logger.error(f"Error getting combat image: {e}")
            return None
    
    def list_media_files(self, media_type: str = "all") -> List[Dict[str, Any]]:
        """
        List all media files
        
        Args:
            media_type: Type of media to list (images, audio, all)
            
        Returns:
            List of media file information
        """
        try:
            media_files = []
            
            if media_type in ["all", "images"]:
                for filename in os.listdir(self.images_dir):
                    if filename.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                        file_path = os.path.join(self.images_dir, filename)
                        file_info = {
                            'filename': filename,
                            'path': file_path,
                            'type': 'image',
                            'size': os.path.getsize(file_path),
                            'modified': os.path.getmtime(file_path)
                        }
                        media_files.append(file_info)
            
            if media_type in ["all", "audio"]:
                for filename in os.listdir(self.audio_dir):
                    if filename.endswith(('.mp3', '.wav', '.ogg')):
                        file_path = os.path.join(self.audio_dir, filename)
                        file_info = {
                            'filename': filename,
                            'path': file_path,
                            'type': 'audio',
                            'size': os.path.getsize(file_path),
                            'modified': os.path.getmtime(file_path)
                        }
                        media_files.append(file_info)
            
            return media_files
            
        except Exception as e:
            self.logger.error(f"Error listing media files: {e}")
            return []
    
    def get_media_metadata(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a media file
        
        Args:
            filename: Name of the media file
            
        Returns:
            Metadata dictionary or None if not found
        """
        try:
            metadata_file = os.path.join(self.metadata_dir, f"{filename}.json")
            
            if not os.path.exists(metadata_file):
                return None
            
            with open(metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            self.logger.error(f"Error getting media metadata: {e}")
            return None
    
    def cleanup_old_media(self, days_old: int = 30) -> int:
        """
        Clean up old media files
        
        Args:
            days_old: Age threshold in days
            
        Returns:
            Number of files cleaned up
        """
        try:
            import time
            cutoff_time = time.time() - (days_old * 24 * 60 * 60)
            cleaned_count = 0
            
            # Clean up images
            for filename in os.listdir(self.images_dir):
                file_path = os.path.join(self.images_dir, filename)
                if os.path.getmtime(file_path) < cutoff_time:
                    os.remove(file_path)
                    cleaned_count += 1
                    
                    # Remove metadata file
                    metadata_file = os.path.join(self.metadata_dir, f"{filename}.json")
                    if os.path.exists(metadata_file):
                        os.remove(metadata_file)
            
            # Clean up audio
            for filename in os.listdir(self.audio_dir):
                file_path = os.path.join(self.audio_dir, filename)
                if os.path.getmtime(file_path) < cutoff_time:
                    os.remove(file_path)
                    cleaned_count += 1
            
            self.logger.info(f"Cleaned up {cleaned_count} old media files")
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old media: {e}")
            return 0
