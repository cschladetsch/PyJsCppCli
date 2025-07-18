"""
Music player for startup sound - plays context-aware music
"""
import os
import sys
import json
import random
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

class MusicPlayer:
    """Handles playing startup music and tracking history"""
    
    MUSIC_HISTORY_FILE = Path.home() / ".config" / "claude" / "music.json"
    MAX_HISTORY_SIZE = 3000  # Maximum characters for history
    
    # Musical progressions - more interesting and varied patterns
    # Mix of rhythms, intervals, and melodic shapes for variety
    PROGRESSIONS = [
        # Jazz-inspired ii-V-I progression (Dm7-G7-Cmaj)
        [(293.66, 100), (349.23, 100), (392.00, 100), (261.63, 200)],
        
        # Ascending melodic sequence with rhythm variation
        [(261.63, 150), (329.63, 75), (392.00, 75), (523.25, 200)],
        
        # Call and response pattern (question-answer)
        [(440.00, 100), (493.88, 100), (440.00, 50), (349.23, 250)],
        
        # Syncopated funk pattern with octave jumps
        [(329.63, 75), (659.25, 75), (329.63, 150), (493.88, 200)],
        
        # Classical turn ornament (C-D-C-B-C)
        [(523.25, 80), (587.33, 80), (523.25, 80), (493.88, 80), (523.25, 180)],
        
        # Blues-inspired bent note simulation (minor to major third)
        [(261.63, 150), (311.13, 50), (329.63, 100), (261.63, 200)],
        
        # Whole tone scale fragment (mysterious)
        [(261.63, 125), (293.66, 125), (329.63, 125), (369.99, 125)],
        
        # Rhythmic motif with triplet feel
        [(392.00, 83), (392.00, 83), (392.00, 84), (523.25, 250)],
        
        # Descending cascade (waterfall effect)
        [(880.00, 75), (659.25, 75), (523.25, 75), (392.00, 275)],
        
        # Pentatonic with grace note
        [(493.88, 50), (440.00, 150), (349.23, 150), (293.66, 150)],
        
        # Modal interchange (borrowing from parallel minor)
        [(261.63, 125), (311.13, 125), (349.23, 125), (261.63, 125)],
        
        # Alberti bass pattern simulation
        [(261.63, 100), (329.63, 100), (392.00, 100), (329.63, 200)],
    ]
    
    @classmethod
    def is_enabled(cls) -> bool:
        """Check if music is enabled in config"""
        from .config_loader import ConfigLoader
        model_prefs = ConfigLoader.get_model_preferences()
        return model_prefs.get('startup_music', True)
    
    @classmethod
    def _is_wsl2(cls) -> bool:
        """Check if running in WSL2"""
        try:
            with open('/proc/version', 'r') as f:
                return 'microsoft' in f.read().lower()
        except:
            return False
    
    @classmethod
    def get_volume(cls) -> float:
        """Get volume setting from config (0.0 to 1.0)"""
        from .config_loader import ConfigLoader
        model_prefs = ConfigLoader.get_model_preferences()
        volume = model_prefs.get('music_volume', 0.5)
        # Clamp between 0.0 and 1.0
        return max(0.0, min(1.0, float(volume)))
    
    @classmethod
    def play_progression(cls, input_text: str = "", output_text: str = "") -> Optional[Dict]:
        """Play a context-aware musical phrase based on input/output"""
        if not cls.is_enabled():
            return None
            
        # Get volume setting
        volume = cls.get_volume()
        
        # Generate context-aware MIDI
        from .midi_music import MidiMusicGenerator
        midi_context = MidiMusicGenerator.generate_and_save(input_text, output_text)
        
        # Convert MIDI context to playable progression
        progression = cls._midi_to_progression(midi_context, input_text, output_text)
        progression_name = f"{midi_context['mood']} ({midi_context['bar_length']}/4)"
        
        # Try to play using different methods
        played = False
        method = None
        
        # If WSL2, try Windows audio methods
        if cls._is_wsl2():
            if cls._play_with_windows_audio(progression, volume):
                played = True
                method = "windows-audio"
            elif cls._play_with_powershell(progression, volume):
                played = True
                method = "powershell"
        # Method 1: Try using sox (play command)
        elif cls._play_with_sox(progression, volume):
            played = True
            method = "sox"
        # Method 2: Try using beep command
        elif cls._play_with_beep(progression, volume):
            played = True
            method = "beep"
        # Method 3: Try using speaker-test
        elif cls._play_with_speaker_test(progression, volume):
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
    def _play_with_sox(cls, progression: List[tuple], volume: float) -> bool:
        """Try to play using sox (play command)"""
        try:
            # Check if play command exists
            result = subprocess.run(['which', 'play'], capture_output=True)
            if result.returncode != 0:
                return False
            
            # Build play command with volume
            cmd = ['play', '-n', '-v', str(volume)]
            for freq, duration in progression:
                cmd.extend(['synth', f'{duration/1000}', 'sine', str(freq)])
                
            subprocess.run(cmd, capture_output=True, timeout=2)
            return True
        except:
            return False
    
    @classmethod
    def _play_with_beep(cls, progression: List[tuple], volume: float) -> bool:
        """Try to play using beep command"""
        try:
            # Check if beep exists
            result = subprocess.run(['which', 'beep'], capture_output=True)
            if result.returncode != 0:
                return False
                
            # Play each note (beep doesn't support volume, so we ignore it)
            for freq, duration in progression:
                subprocess.run(['beep', '-f', str(int(freq)), '-l', str(duration)], 
                             capture_output=True, timeout=1)
            return True
        except:
            return False
    
    @classmethod
    def _play_with_speaker_test(cls, progression: List[tuple], volume: float) -> bool:
        """Try to play using speaker-test (fallback)"""
        try:
            # This is a very basic implementation - just plays a short tone
            # speaker-test doesn't support volume control
            subprocess.run(['speaker-test', '-t', 'sine', '-f', '440', '-l', '1'], 
                         capture_output=True, timeout=0.5)
            return True
        except:
            return False
    
    @classmethod
    def _play_with_powershell(cls, progression: List[tuple], volume: float) -> bool:
        """Try to play using PowerShell on WSL2"""
        try:
            # Check if powershell.exe is available
            result = subprocess.run(['which', 'powershell.exe'], capture_output=True)
            if result.returncode != 0:
                return False
            
            # Build PowerShell command to play beeps
            # Console beeps don't support volume, so we ignore it
            ps_commands = []
            for freq, duration in progression:
                ps_commands.append(f'[console]::beep({int(freq)},{duration})')
            
            ps_script = '; '.join(ps_commands)
            cmd = ['powershell.exe', '-Command', ps_script]
            
            subprocess.run(cmd, capture_output=True, timeout=5)
            return True
        except Exception as e:
            return False
    
    @classmethod
    def _play_with_windows_audio(cls, progression: List[tuple], volume: float) -> bool:
        """Try to play using Windows audio synthesis"""
        try:
            # Create a PowerShell script that uses Windows audio
            # Convert volume from 0-1 to 0-127 for amplitude
            amplitude = int(127 * volume)
            ps_script = f"""
Add-Type -TypeDefinition @'
using System;
using System.Media;
using System.IO;
public class TonePlayer {{
    public static void PlayTone(int frequency, int duration, int amplitude) {{
        using (var stream = new MemoryStream()) {{
            var writer = new BinaryWriter(stream);
            // Write WAV header
            writer.Write("RIFF".ToCharArray());
            writer.Write(36 + duration * 44100 / 1000);
            writer.Write("WAVE".ToCharArray());
            writer.Write("fmt ".ToCharArray());
            writer.Write(16);
            writer.Write((short)1);
            writer.Write((short)1);
            writer.Write(44100);
            writer.Write(44100);
            writer.Write((short)1);
            writer.Write((short)8);
            writer.Write("data".ToCharArray());
            writer.Write(duration * 44100 / 1000);
            
            // Generate sine wave with volume control
            for (int i = 0; i < duration * 44100 / 1000; i++) {{
                double angle = ((double)i / 44100) * frequency * 2 * Math.PI;
                writer.Write((byte)(128 + amplitude * Math.Sin(angle)));
            }}
            
            stream.Position = 0;
            using (var player = new SoundPlayer(stream)) {{
                player.PlaySync();
            }}
        }}
    }}
}}
'@ -ReferencedAssemblies System.dll

"""
            for freq, duration in progression:
                ps_script += f"[TonePlayer]::PlayTone({int(freq)}, {duration}, {amplitude})\n"
            
            cmd = ['powershell.exe', '-Command', ps_script]
            subprocess.run(cmd, capture_output=True, timeout=10)
            return True
        except:
            return False
    
    @classmethod
    def _midi_to_progression(cls, midi_context: Dict, input_text: str, output_text: str) -> List[tuple]:
        """Convert MIDI context to playable audio progression"""
        # Use text hash to generate deterministic but varied progression
        combined_text = f"{input_text} {output_text}"
        text_hash = hashlib.md5(combined_text.encode()).hexdigest()
        random.seed(int(text_hash[:8], 16))
        
        # Get scale from MIDI context
        scale_map = {
            'happy': [261.63, 329.63, 392.00, 523.25],  # C major chord
            'thoughtful': [220.00, 261.63, 329.63, 440.00],  # A minor chord
            'energetic': [293.66, 369.99, 440.00, 587.33],  # D major chord  
            'mysterious': [329.63, 392.00, 493.88, 659.25],  # E minor chord
            'technical': [349.23, 440.00, 523.25, 698.46],  # F major chord
            'creative': [392.00, 493.88, 587.33, 783.99],  # G major chord
            'error': [220.00, 261.63, 329.63, 440.00],  # A minor chord (sad/error)
            'success': [261.63, 329.63, 392.00, 523.25],  # C major chord (happy/success)
        }
        
        base_freqs = scale_map.get(midi_context['mood'], scale_map['thoughtful'])
        bar_length = midi_context['bar_length']
        
        # Generate progression based on bar length
        progression = []
        beat_duration = 60000 // midi_context['tempo'] // 4 // 2  # ms per beat (2x speed)
        
        for i in range(bar_length):
            # Pick frequency based on text content
            freq_index = (ord(combined_text[i % len(combined_text)]) + i) % len(base_freqs)
            freq = base_freqs[freq_index]
            
            # Vary frequency slightly for interest
            if i % 2 == 1:
                freq *= random.choice([0.5, 1.5, 2.0])  # Octave variations
            
            duration = beat_duration
            if i == bar_length - 1:  # Last beat slightly longer
                duration = int(duration * 1.5)
            
            progression.append((freq, duration))
        
        return progression
    
    @classmethod
    def _get_progression_name(cls, progression: List[tuple]) -> str:
        """Get a friendly name for the progression based on pattern characteristics"""
        # Map based on first frequency and pattern length
        first_freq = progression[0][0]
        pattern_length = len(progression)
        
        # Special patterns based on structure
        if pattern_length == 5 and first_freq == 523.25:
            return "Classical turn"
        elif pattern_length == 3 and progression[0][1] < 90:
            return "Triplet rhythm"
        elif first_freq == 880.00:
            return "Descending cascade"
        elif first_freq == 493.88 and progression[0][1] == 50:
            return "Grace note phrase"
        
        # Map by starting frequency
        progression_map = {
            293.66: "Jazz ii-V-I",
            261.63: "Melodic sequence" if pattern_length == 4 else "Modal interchange",
            440.00: "Call and response",
            329.63: "Funk syncopation",
            311.13: "Blues bend",
            392.00: "Rhythmic motif",
        }
        
        return progression_map.get(first_freq, f"Pattern #{hash(str(progression)) % 100}")
    
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