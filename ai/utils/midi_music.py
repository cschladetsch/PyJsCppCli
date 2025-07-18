"""
Context-aware MIDI music generation based on input/output
"""
import os
import sys
import json
import random
import hashlib
import struct
from pathlib import Path
from typing import List, Tuple, Optional, Dict
from datetime import datetime

class MidiMusicGenerator:
    """Generates MIDI music based on conversation context"""
    
    MIDI_FILE_PATH = Path.home() / ".config" / "claude" / "music.mid"
    MAX_FILE_SIZE = 500 * 1024  # 500KB
    
    # Bar lengths in beats
    BAR_LENGTHS = [3, 5, 9]
    
    # Note mappings for different moods/contexts
    SCALES = {
        'happy': [60, 62, 64, 65, 67, 69, 71, 72],  # C major
        'thoughtful': [57, 59, 60, 62, 64, 65, 67, 69],  # A minor
        'energetic': [62, 64, 66, 67, 69, 71, 73, 74],  # D major
        'mysterious': [64, 66, 68, 69, 71, 73, 75, 76],  # E minor
        'technical': [65, 67, 69, 70, 72, 74, 76, 77],  # F major
        'creative': [67, 69, 71, 72, 74, 76, 78, 79],  # G major
        'error': [57, 59, 60, 62, 64, 65, 67, 69],  # A minor (sad/error)
        'success': [60, 62, 64, 65, 67, 69, 71, 72],  # C major (happy/success)
    }
    
    @classmethod
    def analyze_context(cls, input_text: str, output_text: str = "") -> Dict[str, any]:
        """Analyze input/output to determine musical parameters"""
        combined_text = f"{input_text} {output_text}".lower()
        
        # Check if this is an error or success response first
        if output_text.lower() == 'error':
            mood = 'error'  # Minor key for errors
        elif output_text.lower().startswith('success:'):
            # For successful responses, analyze the content after SUCCESS:
            content = output_text[8:].lower()  # Skip "SUCCESS:"
            combined_text = f"{input_text} {content}".lower()
            
            # Determine mood based on keywords for successful responses
            mood = 'success'  # Default to major key for success
            if any(word in combined_text for word in ['happy', 'great', 'awesome', 'love', 'excellent']):
                mood = 'happy'
            elif any(word in combined_text for word in ['fast', 'quick', 'speed', 'run', 'energy']):
                mood = 'energetic'
            elif any(word in combined_text for word in ['mystery', 'strange', 'unknown', 'puzzle']):
                mood = 'mysterious'
            elif any(word in combined_text for word in ['code', 'function', 'algorithm', 'data']):
                mood = 'technical'
            elif any(word in combined_text for word in ['create', 'design', 'art', 'music', 'build']):
                mood = 'creative'
        else:
            # Fallback to thoughtful (minor) if we can't determine
            mood = 'thoughtful'
        
        # Determine tempo based on text length and energy
        text_length = len(combined_text)
        base_tempo = 120  # BPM
        if text_length < 50:
            tempo = base_tempo + 20  # Short = faster
        elif text_length > 200:
            tempo = base_tempo - 20  # Long = slower
        else:
            tempo = base_tempo
        
        # Use hash to create deterministic but varied rhythm
        text_hash = hashlib.md5(combined_text.encode()).hexdigest()
        rhythm_seed = int(text_hash[:8], 16)
        
        # Choose bar length based on input characteristics
        if '?' in input_text:
            bar_length = 5  # Questions get 5/4 time
        elif len(input_text.split()) < 5:
            bar_length = 3  # Short inputs get 3/4 time
        else:
            bar_length = 9  # Complex inputs get 9/8 time
        
        return {
            'mood': mood,
            'tempo': tempo,
            'rhythm_seed': rhythm_seed,
            'bar_length': bar_length,
            'scale': cls.SCALES[mood]
        }
    
    @classmethod
    def generate_melody(cls, context: Dict, num_notes: int = 16) -> List[Tuple[int, int, int]]:
        """Generate a melody based on context (note, velocity, duration)"""
        random.seed(context['rhythm_seed'])
        scale = context['scale']
        bar_length = context['bar_length']
        
        melody = []
        beat_count = 0
        
        for i in range(num_notes):
            # Pick note from scale
            note_index = random.randint(0, len(scale) - 1)
            
            # Add occasional leaps for interest
            if random.random() < 0.2:
                note_index = (note_index + random.choice([-3, -2, 2, 3])) % len(scale)
            
            note = scale[note_index]
            
            # Velocity based on beat position
            if beat_count % bar_length == 0:
                velocity = random.randint(80, 100)  # Strong beat
            else:
                velocity = random.randint(50, 80)   # Weak beat
            
            # Duration variation
            durations = [120, 240, 480]  # 8th, quarter, half notes
            if bar_length == 3:
                durations = [160, 320, 480]  # Triplet feel
            elif bar_length == 9:
                durations = [80, 160, 240]   # Faster subdivisions
            
            duration = random.choice(durations)
            melody.append((note, velocity, duration))
            
            beat_count += 1
            
        return melody
    
    @classmethod
    def create_midi_track(cls, melody: List[Tuple[int, int, int]], tempo: int) -> bytes:
        """Create a MIDI track from melody data"""
        track_data = bytearray()
        
        # Track header
        track_data.extend(b'MTrk')
        track_length_pos = len(track_data)
        track_data.extend(b'\x00\x00\x00\x00')  # Placeholder for length
        
        # Set tempo (microseconds per quarter note)
        tempo_value = 60000000 // tempo
        track_data.extend(b'\x00\xFF\x51\x03')
        track_data.extend(tempo_value.to_bytes(3, 'big'))
        
        # Time signature (variable based on bar_length)
        # This is simplified - in real MIDI we'd need proper time sig
        
        # Add notes
        current_time = 0
        for note, velocity, duration in melody:
            # Note on
            track_data.extend(cls._variable_length_quantity(0))
            track_data.extend(bytes([0x90, note, velocity]))
            
            # Note off
            track_data.extend(cls._variable_length_quantity(duration))
            track_data.extend(bytes([0x80, note, 0]))
        
        # End of track
        track_data.extend(b'\x00\xFF\x2F\x00')
        
        # Update track length
        track_length = len(track_data) - track_length_pos - 4
        track_data[track_length_pos:track_length_pos+4] = track_length.to_bytes(4, 'big')
        
        return bytes(track_data)
    
    @classmethod
    def _variable_length_quantity(cls, value: int) -> bytes:
        """Encode integer as MIDI variable length quantity"""
        if value == 0:
            return b'\x00'
        
        result = []
        while value > 0:
            result.append(value & 0x7F)
            value >>= 7
        
        result.reverse()
        for i in range(len(result) - 1):
            result[i] |= 0x80
        
        return bytes(result)
    
    @classmethod
    def create_midi_file(cls, track_data: bytes) -> bytes:
        """Create complete MIDI file with header and track"""
        midi_data = bytearray()
        
        # MIDI header
        midi_data.extend(b'MThd')
        midi_data.extend(b'\x00\x00\x00\x06')  # Header length
        midi_data.extend(b'\x00\x00')  # Format 0
        midi_data.extend(b'\x00\x01')  # 1 track
        midi_data.extend(b'\x01\xe0')  # 480 ticks per quarter note
        
        # Add track
        midi_data.extend(track_data)
        
        return bytes(midi_data)
    
    @classmethod
    def parse_midi_file(cls, file_path: Path) -> Optional[List[bytes]]:
        """Parse existing MIDI file and extract tracks"""
        if not file_path.exists():
            return None
            
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
                
            # Check MIDI header
            if len(data) < 14 or data[:4] != b'MThd':
                return None
                
            # Skip header
            tracks = []
            pos = 14
            
            # Find all tracks
            while pos < len(data) - 8:
                if data[pos:pos+4] == b'MTrk':
                    track_len = struct.unpack('>I', data[pos+4:pos+8])[0]
                    track_data = data[pos:pos+8+track_len]
                    tracks.append(track_data)
                    pos += 8 + track_len
                else:
                    pos += 1
                    
            return tracks
        except:
            return None
    
    @classmethod
    def merge_midi_tracks(cls, tracks: List[bytes], max_size: int) -> bytes:
        """Merge multiple MIDI tracks into a single file, keeping within size limit"""
        # Create new MIDI header for format 0 (single track)
        midi_data = bytearray()
        midi_data.extend(b'MThd')
        midi_data.extend(b'\x00\x00\x00\x06')  # Header length
        midi_data.extend(b'\x00\x00')  # Format 0
        midi_data.extend(b'\x00\x01')  # 1 track
        midi_data.extend(b'\x01\xe0')  # 480 ticks per quarter note
        
        # Merge all track data (removing individual track headers)
        merged_track = bytearray()
        merged_track.extend(b'MTrk')
        track_length_pos = len(merged_track)
        merged_track.extend(b'\x00\x00\x00\x00')  # Placeholder for length
        
        # Add events from all tracks
        for track in tracks:
            if len(track) > 8 and track[:4] == b'MTrk':
                # Extract track events (skip header and end-of-track)
                track_events = track[8:-4]  # Skip MTrk header and end marker
                merged_track.extend(track_events)
        
        # Add end of track
        merged_track.extend(b'\x00\xFF\x2F\x00')
        
        # Update track length
        track_length = len(merged_track) - track_length_pos - 4
        merged_track[track_length_pos:track_length_pos+4] = track_length.to_bytes(4, 'big')
        
        midi_data.extend(merged_track)
        
        # If too large, keep only recent tracks
        if len(midi_data) > max_size:
            # Keep only the last few tracks that fit
            kept_tracks = []
            current_size = 14  # Header size
            
            for track in reversed(tracks):
                if current_size + len(track) < max_size:
                    kept_tracks.insert(0, track)
                    current_size += len(track)
                else:
                    break
                    
            return cls.merge_midi_tracks(kept_tracks, max_size)
            
        return bytes(midi_data)
    
    @classmethod
    def append_to_midi_file(cls, new_midi_data: bytes):
        """Append new MIDI data to existing file, merging tracks"""
        cls.MIDI_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # Parse existing file
        existing_tracks = cls.parse_midi_file(cls.MIDI_FILE_PATH) or []
        
        # Parse new MIDI data to extract its track
        new_tracks = cls.parse_midi_file(Path('/tmp/temp.mid'))
        if not new_tracks:
            # If parsing fails, treat new_midi_data as a complete file
            with open('/tmp/temp.mid', 'wb') as f:
                f.write(new_midi_data)
            new_tracks = cls.parse_midi_file(Path('/tmp/temp.mid')) or []
            
        # Add new track to existing tracks
        all_tracks = existing_tracks + new_tracks
        
        # Merge and save
        merged_midi = cls.merge_midi_tracks(all_tracks, cls.MAX_FILE_SIZE)
        with open(cls.MIDI_FILE_PATH, 'wb') as f:
            f.write(merged_midi)
    
    @classmethod
    def generate_and_save(cls, input_text: str, output_text: str = "") -> Dict[str, any]:
        """Generate context-aware music and save to MIDI file"""
        # Analyze context
        context = cls.analyze_context(input_text, output_text)
        
        # Generate melody
        melody = cls.generate_melody(context)
        
        # Create MIDI track
        track_data = cls.create_midi_track(melody, context['tempo'])
        
        # Create MIDI file
        midi_data = cls.create_midi_file(track_data)
        
        # Save to file
        cls.append_to_midi_file(midi_data)
        
        return {
            'mood': context['mood'],
            'tempo': context['tempo'],
            'bar_length': context['bar_length'],
            'notes_generated': len(melody),
            'file_size': len(midi_data)
        }