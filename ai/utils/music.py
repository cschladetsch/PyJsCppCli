"""
Music player for startup sound - plays a melodic 3-key progression
"""
import os
import sys
import json
import random
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

class MusicPlayer:
    """Handles playing startup music and tracking history"""
    
    MUSIC_HISTORY_FILE = Path.home() / ".config" / "claude" / "music.json"
    MAX_HISTORY_SIZE = 3000  # Maximum characters for history
    
    # Musical progressions (frequency in Hz, duration in ms)
    PROGRESSIONS = [
        # C major - C E G (happy, uplifting)
        [(261.63, 200), (329.63, 200), (392.00, 400)],
        # A minor - A C E (thoughtful, contemplative)
        [(440.00, 200), (523.25, 200), (659.25, 400)],
        # F major - F A C (warm, friendly)
        [(349.23, 200), (440.00, 200), (523.25, 400)],
        # D major - D F# A (bright, confident)
        [(293.66, 200), (369.99, 200), (440.00, 400)],
        # G major - G B D (open, expansive)
        [(392.00, 200), (493.88, 200), (587.33, 400)],
        # E minor - E G B (mysterious, intriguing)
        [(329.63, 200), (392.00, 200), (493.88, 400)],
    ]
    
    @classmethod
    def is_enabled(cls) -> bool:
        """Check if music is enabled in config"""
        from .config_loader import ConfigLoader
        model_prefs = ConfigLoader.get_model_preferences()
        return model_prefs.get('startup_music', True)
    
    @classmethod
    def play_progression(cls) -> Optional[Dict]:
        """Play a random 3-key progression and return the played notes"""
        if not cls.is_enabled():
            return None
            
        # Select random progression
        progression = random.choice(cls.PROGRESSIONS)
        progression_name = cls._get_progression_name(progression)
        
        # Try to play using different methods
        played = False
        method = None
        
        # Method 1: Try using sox (play command)
        if cls._play_with_sox(progression):
            played = True
            method = "sox"
        # Method 2: Try using beep command
        elif cls._play_with_beep(progression):
            played = True
            method = "beep"
        # Method 3: Try using speaker-test
        elif cls._play_with_speaker_test(progression):
            played = True
            method = "speaker-test"
        
        if played:
            # Record in history
            history_entry = {
                "timestamp": datetime.now().isoformat(),
                "progression": progression_name,
                "notes": [(f, d) for f, d in progression],
                "method": method
            }
            cls._save_to_history(history_entry)
            return history_entry
        
        return None
    
    @classmethod
    def _play_with_sox(cls, progression: List[tuple]) -> bool:
        """Try to play using sox (play command)"""
        try:
            # Check if play command exists
            result = subprocess.run(['which', 'play'], capture_output=True)
            if result.returncode != 0:
                return False
            
            # Build play command
            cmd = ['play', '-n']
            for freq, duration in progression:
                cmd.extend(['synth', f'{duration/1000}', 'sine', str(freq)])
                
            subprocess.run(cmd, capture_output=True, timeout=2)
            return True
        except:
            return False
    
    @classmethod
    def _play_with_beep(cls, progression: List[tuple]) -> bool:
        """Try to play using beep command"""
        try:
            # Check if beep exists
            result = subprocess.run(['which', 'beep'], capture_output=True)
            if result.returncode != 0:
                return False
                
            # Play each note
            for freq, duration in progression:
                subprocess.run(['beep', '-f', str(int(freq)), '-l', str(duration)], 
                             capture_output=True, timeout=1)
            return True
        except:
            return False
    
    @classmethod
    def _play_with_speaker_test(cls, progression: List[tuple]) -> bool:
        """Try to play using speaker-test (fallback)"""
        try:
            # This is a very basic implementation - just plays a short tone
            subprocess.run(['speaker-test', '-t', 'sine', '-f', '440', '-l', '1'], 
                         capture_output=True, timeout=0.5)
            return True
        except:
            return False
    
    @classmethod
    def _get_progression_name(cls, progression: List[tuple]) -> str:
        """Get a friendly name for the progression based on frequencies"""
        # Map first frequency to chord name
        first_freq = progression[0][0]
        chord_map = {
            261.63: "C major",
            440.00: "A minor",
            349.23: "F major",
            293.66: "D major",
            392.00: "G major",
            329.63: "E minor"
        }
        return chord_map.get(first_freq, "Unknown")
    
    @classmethod
    def _save_to_history(cls, entry: Dict):
        """Save entry to history file, trimming if necessary"""
        cls.MUSIC_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing history
        history = []
        if cls.MUSIC_HISTORY_FILE.exists():
            try:
                with open(cls.MUSIC_HISTORY_FILE, 'r') as f:
                    history = json.load(f)
            except:
                history = []
        
        # Add new entry
        history.append(entry)
        
        # Trim history if too large
        history_str = json.dumps(history)
        while len(history_str) > cls.MAX_HISTORY_SIZE and len(history) > 1:
            history.pop(0)  # Remove oldest entry
            history_str = json.dumps(history)
        
        # Save trimmed history
        with open(cls.MUSIC_HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
    
    @classmethod
    def get_history(cls) -> List[Dict]:
        """Get music history"""
        if cls.MUSIC_HISTORY_FILE.exists():
            try:
                with open(cls.MUSIC_HISTORY_FILE, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []