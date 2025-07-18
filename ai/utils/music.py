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
        
        # Try SDL2 first for best cross-platform volume control
        try:
            if cls._play_with_sdl2(progression, volume):
                played = True
                method = "sdl2"
        except Exception as e:
            # SDL2 failed, continue to next method
            pass
        
        # Try PulseAudio (works well in WSL2 with WSLg)
        if not played and cls._play_with_pulseaudio(progression, volume):
            played = True
            method = "pulseaudio"
        # If WSL2 and above fails, try Windows audio methods
        elif cls._is_wsl2():
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
    def _play_with_pulseaudio(cls, progression: List[tuple], volume: float) -> bool:
        """Try to play using PulseAudio (for WSL2 with WSLg)"""
        try:
            import tempfile
            import wave
            import numpy as np
            
            # Check if paplay exists
            result = subprocess.run(['which', 'paplay'], capture_output=True)
            if result.returncode != 0:
                return False
            
            # Create a temporary WAV file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_filename = temp_file.name
                
                # Generate continuous audio stream with overlapping notes
                sample_rate = 44100
                
                # Calculate total duration with overlaps
                overlap_duration = 0.5  # 500ms overlap between notes (much longer)
                overlap_samples = int(overlap_duration * sample_rate)
                
                # Calculate total duration - just use the full duration without subtracting overlaps
                total_duration_ms = sum(duration for _, duration in progression)
                total_samples = int(sample_rate * total_duration_ms / 1000)
                
                # Create continuous audio buffer
                audio_data = np.zeros(total_samples)
                
                # Track current position in the audio buffer
                current_pos = 0
                
                # Generate each note with significant overlap for smooth blending
                for i, (freq, duration_ms) in enumerate(progression):
                    # Make notes longer and slower
                    extended_duration_ms = duration_ms * 2  # Double the duration
                    num_samples = int(sample_rate * extended_duration_ms / 1000)
                    t = np.linspace(0, extended_duration_ms / 1000, num_samples, False)
                    
                    # Generate smoother sine wave with subtle harmonics
                    fundamental = np.sin(2 * np.pi * freq * t)
                    second_harmonic = 0.1 * np.sin(2 * np.pi * freq * 2 * t)
                    third_harmonic = 0.03 * np.sin(2 * np.pi * freq * 3 * t)
                    wave_data = fundamental + second_harmonic + third_harmonic
                    
                    # Normalize to prevent clipping
                    max_val = np.max(np.abs(wave_data))
                    if max_val > 0:
                        wave_data = wave_data / max_val
                    
                    # Create smooth blending envelope
                    envelope = np.ones(num_samples)
                    
                    # Long fade in (except first note) for smooth blending
                    if i > 0:
                        fade_in_samples = overlap_samples
                        if fade_in_samples > 0:
                            fade_in_samples = min(fade_in_samples, num_samples)
                            # Use very smooth exponential curve
                            fade_curve = np.linspace(0, 1, fade_in_samples)
                            envelope[:fade_in_samples] = 1 - np.exp(-3 * fade_curve)
                    
                    # Long fade out (except last note) for smooth blending
                    if i < len(progression) - 1:
                        fade_out_samples = overlap_samples
                        if fade_out_samples > 0:
                            fade_out_samples = min(fade_out_samples, num_samples)
                            # Use very smooth exponential curve
                            fade_curve = np.linspace(0, 1, fade_out_samples)
                            envelope[-fade_out_samples:] = np.exp(-3 * fade_curve)
                    
                    # Apply envelope and volume
                    wave_data = wave_data * envelope * volume * 0.3  # Much lower volume to prevent clipping when mixing
                    
                    # Calculate position in buffer (with overlap)
                    if i == 0:
                        start_pos = 0
                    else:
                        start_pos = current_pos - overlap_samples
                        if start_pos < 0:
                            start_pos = 0
                    
                    # Add to continuous audio buffer with mixing
                    end_pos = min(start_pos + num_samples, total_samples)
                    actual_samples = end_pos - start_pos
                    if start_pos >= 0 and actual_samples > 0:
                        audio_data[start_pos:end_pos] += wave_data[:actual_samples]
                    
                    # Update position for next note (ensure forward progress)
                    note_spacing = num_samples - overlap_samples
                    if note_spacing <= 0:
                        note_spacing = num_samples // 2  # Ensure some spacing
                    current_pos += note_spacing
                
                # Apply efficient smoothing using numpy convolution
                # Simple but effective smoothing kernel
                kernel = np.array([0.1, 0.2, 0.4, 0.2, 0.1])
                audio_data = np.convolve(audio_data, kernel, mode='same')
                
                # Add bass and snare drums
                beat_duration = 0.5  # 500ms per beat
                beat_samples = int(beat_duration * sample_rate)
                
                # Generate bass drum (low frequency thump)
                bass_freq = 60  # 60Hz bass
                bass_duration = 0.15  # 150ms
                bass_samples = int(bass_duration * sample_rate)
                bass_t = np.linspace(0, bass_duration, bass_samples, False)
                bass_wave = np.sin(2 * np.pi * bass_freq * bass_t) * np.exp(-bass_t * 8)  # Quick decay
                
                # Generate better snare drum (layered sound)
                snare_duration = 0.15  # 150ms
                snare_samples = int(snare_duration * sample_rate)
                snare_t = np.linspace(0, snare_duration, snare_samples, False)
                
                # Layer 1: High frequency noise (snare wire sound)
                noise = np.random.uniform(-1, 1, snare_samples)
                # Apply band-pass filter effect by emphasizing mid-high frequencies
                noise_filtered = noise * (1 + 0.5 * np.sin(2 * np.pi * 200 * snare_t))
                
                # Layer 2: Drum body resonance (tuned percussion)
                body_freq = 200  # 200Hz resonance
                body_wave = np.sin(2 * np.pi * body_freq * snare_t) * 0.4
                
                # Layer 3: Sharp attack transient
                attack_wave = np.sin(2 * np.pi * 2000 * snare_t) * 0.2
                
                # Combine layers
                snare_wave = noise_filtered + body_wave + attack_wave
                
                # Apply realistic envelope (fast attack, medium decay)
                envelope = np.exp(-snare_t * 12)  # Faster decay
                envelope[:int(0.005 * sample_rate)] = 1  # Sharp attack for first 5ms
                
                snare_wave = snare_wave * envelope
                
                # Add drums to the mix with varying time signatures
                current_beat = 0
                bar_count = 0
                
                while current_beat * beat_samples < len(audio_data):
                    beat_pos = current_beat * beat_samples
                    
                    # Determine time signature based on bar
                    if bar_count % 3 == 0:
                        # 3/4 time (waltz pattern)
                        beats_per_bar = 3
                        # Bass on beat 1, snare on beat 3
                        if current_beat % beats_per_bar == 0:
                            end_pos = min(beat_pos + bass_samples, len(audio_data))
                            actual_bass_samples = end_pos - beat_pos
                            if actual_bass_samples > 0:
                                audio_data[beat_pos:end_pos] += bass_wave[:actual_bass_samples] * 0.3
                        elif current_beat % beats_per_bar == 2:
                            end_pos = min(beat_pos + snare_samples, len(audio_data))
                            actual_snare_samples = end_pos - beat_pos
                            if actual_snare_samples > 0:
                                audio_data[beat_pos:end_pos] += snare_wave[:actual_snare_samples] * 0.2
                    
                    elif bar_count % 3 == 1:
                        # 5/4 time (complex pattern)
                        beats_per_bar = 5
                        # Bass on beats 1 and 4, snare on beats 2 and 5
                        if current_beat % beats_per_bar == 0 or current_beat % beats_per_bar == 3:
                            end_pos = min(beat_pos + bass_samples, len(audio_data))
                            actual_bass_samples = end_pos - beat_pos
                            if actual_bass_samples > 0:
                                audio_data[beat_pos:end_pos] += bass_wave[:actual_bass_samples] * 0.3
                        elif current_beat % beats_per_bar == 1 or current_beat % beats_per_bar == 4:
                            end_pos = min(beat_pos + snare_samples, len(audio_data))
                            actual_snare_samples = end_pos - beat_pos
                            if actual_snare_samples > 0:
                                audio_data[beat_pos:end_pos] += snare_wave[:actual_snare_samples] * 0.2
                    
                    else:
                        # 7/8 time (irregular pattern)
                        beats_per_bar = 7
                        # Bass on beats 1, 3, 6, snare on beats 2, 5, 7
                        if current_beat % beats_per_bar == 0 or current_beat % beats_per_bar == 2 or current_beat % beats_per_bar == 5:
                            end_pos = min(beat_pos + bass_samples, len(audio_data))
                            actual_bass_samples = end_pos - beat_pos
                            if actual_bass_samples > 0:
                                audio_data[beat_pos:end_pos] += bass_wave[:actual_bass_samples] * 0.3
                        elif current_beat % beats_per_bar == 1 or current_beat % beats_per_bar == 4 or current_beat % beats_per_bar == 6:
                            end_pos = min(beat_pos + snare_samples, len(audio_data))
                            actual_snare_samples = end_pos - beat_pos
                            if actual_snare_samples > 0:
                                audio_data[beat_pos:end_pos] += snare_wave[:actual_snare_samples] * 0.2
                    
                    current_beat += 1
                    
                    # Update bar count based on current time signature
                    if bar_count % 3 == 0 and current_beat % 3 == 0:
                        bar_count += 1
                    elif bar_count % 3 == 1 and current_beat % 5 == 0:
                        bar_count += 1
                    elif bar_count % 3 == 2 and current_beat % 7 == 0:
                        bar_count += 1
                
                # Apply gentle limiting to prevent clipping
                max_val = np.max(np.abs(audio_data))
                if max_val > 0.2:
                    audio_data = audio_data / max_val * 0.2
                
                # Final soft limiting with doubled volume
                audio_data = np.tanh(audio_data) * 1.6  # Double the volume
                
                # Convert to 16-bit PCM
                audio_int16 = (audio_data * 32767).astype(np.int16)
                
                # Write WAV file
                with wave.open(temp_filename, 'wb') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(sample_rate)
                    wav_file.writeframes(audio_int16.tobytes())
            
            # Play using paplay (no timeout for long songs)
            subprocess.run(['paplay', temp_filename], capture_output=True)
            
            # Clean up
            os.unlink(temp_filename)
            return True
            
        except Exception as e:
            print(f"PulseAudio error: {e}")
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
            # Use square root for more perceptible volume changes
            amplitude = int(127 * (volume ** 0.5))
            ps_script = f"""
Add-Type -TypeDefinition @'
using System;
using System.Media;
using System.IO;
public class TonePlayer {{
    public static void PlayTone(int frequency, int duration, double volume) {{
        using (var stream = new MemoryStream()) {{
            var writer = new BinaryWriter(stream);
            int sampleRate = 44100;
            int numSamples = duration * sampleRate / 1000;
            short bitsPerSample = 16;
            short channels = 1;
            int byteRate = sampleRate * channels * bitsPerSample / 8;
            
            // Write WAV header for 16-bit audio
            writer.Write("RIFF".ToCharArray());
            writer.Write(36 + numSamples * 2); // 2 bytes per sample
            writer.Write("WAVE".ToCharArray());
            writer.Write("fmt ".ToCharArray());
            writer.Write(16); // fmt chunk size
            writer.Write((short)1); // PCM format
            writer.Write(channels);
            writer.Write(sampleRate);
            writer.Write(byteRate);
            writer.Write((short)(channels * bitsPerSample / 8)); // block align
            writer.Write(bitsPerSample);
            writer.Write("data".ToCharArray());
            writer.Write(numSamples * 2); // data size in bytes
            
            // Generate 16-bit sine wave with ADSR envelope
            double attackTime = 0.01; // 10ms attack
            double decayTime = 0.05;  // 50ms decay
            double sustainLevel = 0.8; // 80% sustain level
            double releaseTime = 0.1;  // 100ms release
            
            int attackSamples = (int)(attackTime * sampleRate);
            int decaySamples = (int)(decayTime * sampleRate);
            int releaseSamples = (int)(releaseTime * sampleRate);
            int sustainSamples = numSamples - attackSamples - decaySamples - releaseSamples;
            if (sustainSamples < 0) sustainSamples = 0;
            
            for (int i = 0; i < numSamples; i++) {{
                double angle = ((double)i / sampleRate) * frequency * 2 * Math.PI;
                double envelope = 1.0;
                
                if (i < attackSamples) {{
                    // Attack phase
                    envelope = (double)i / attackSamples;
                }} else if (i < attackSamples + decaySamples) {{
                    // Decay phase
                    int decayIndex = i - attackSamples;
                    envelope = 1.0 - ((1.0 - sustainLevel) * decayIndex / decaySamples);
                }} else if (i < attackSamples + decaySamples + sustainSamples) {{
                    // Sustain phase
                    envelope = sustainLevel;
                }} else {{
                    // Release phase
                    int releaseIndex = i - attackSamples - decaySamples - sustainSamples;
                    envelope = sustainLevel * (1.0 - (double)releaseIndex / releaseSamples);
                }}
                
                short sample = (short)(32767 * volume * envelope * Math.Sin(angle));
                writer.Write(sample);
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
                ps_script += f"[TonePlayer]::PlayTone({int(freq)}, {duration}, {volume})\n"
            
            cmd = ['powershell.exe', '-Command', ps_script]
            subprocess.run(cmd, capture_output=True, timeout=10)
            return True
        except:
            return False
    
    @classmethod
    def _play_with_sdl2(cls, progression: List[tuple], volume: float) -> bool:
        """Try to play using SDL2 for better cross-platform audio"""
        try:
            # Try to set SDL2 DLL path for different platforms
            import os
            import platform
            
            # Common SDL2 library paths
            if platform.system() == "Linux":
                # Try common Linux paths
                sdl2_paths = [
                    "/usr/lib/x86_64-linux-gnu/libSDL2-2.0.so.0",
                    "/usr/lib/libSDL2-2.0.so.0",
                    "/usr/local/lib/libSDL2-2.0.so.0"
                ]
                for path in sdl2_paths:
                    if os.path.exists(path):
                        os.environ["PYSDL2_DLL_PATH"] = os.path.dirname(path)
                        break
            
            import sdl2
            import sdl2.ext
            import numpy as np
            import struct
            
            # Initialize SDL2 audio
            sdl2.SDL_Init(sdl2.SDL_INIT_AUDIO)
            
            # Audio specs
            sample_rate = 44100
            channels = 1
            samples = 2048
            
            # Generate audio data for all notes
            audio_data = bytearray()
            
            for freq, duration_ms in progression:
                # Calculate number of samples
                num_samples = int(sample_rate * duration_ms / 1000)
                
                # Generate sine wave
                t = np.linspace(0, duration_ms / 1000, num_samples, False)
                wave = np.sin(2 * np.pi * freq * t)
                
                # Apply ADSR envelope for smooth blending
                attack_time = 0.01  # 10ms
                decay_time = 0.05   # 50ms
                sustain_level = 0.8 # 80%
                release_time = 0.1  # 100ms
                
                attack_samples = int(attack_time * sample_rate)
                decay_samples = int(decay_time * sample_rate)
                release_samples = int(release_time * sample_rate)
                sustain_samples = num_samples - attack_samples - decay_samples - release_samples
                if sustain_samples < 0:
                    sustain_samples = 0
                
                # Create envelope
                envelope = np.ones(num_samples)
                
                # Attack
                if attack_samples > 0:
                    envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
                
                # Decay
                if decay_samples > 0:
                    start = attack_samples
                    end = start + decay_samples
                    envelope[start:end] = np.linspace(1, sustain_level, decay_samples)
                
                # Sustain
                if sustain_samples > 0:
                    start = attack_samples + decay_samples
                    end = start + sustain_samples
                    envelope[start:end] = sustain_level
                
                # Release
                if release_samples > 0:
                    start = attack_samples + decay_samples + sustain_samples
                    envelope[start:] = np.linspace(sustain_level, 0, min(release_samples, num_samples - start))
                
                # Apply envelope and volume
                wave = wave * envelope * volume
                
                # Convert to 16-bit signed integer
                wave_int16 = (wave * 32767).astype(np.int16)
                
                # Add to audio data
                audio_data.extend(wave_int16.tobytes())
            
            # Define audio spec
            audio_spec = sdl2.SDL_AudioSpec(
                sample_rate,  # freq
                sdl2.AUDIO_S16SYS,  # format
                channels,  # channels
                samples,  # samples
                None,  # callback (we'll use SDL_QueueAudio)
                None   # userdata
            )
            
            # Open audio device
            device = sdl2.SDL_OpenAudioDevice(None, 0, audio_spec, None, 0)
            if device == 0:
                return False
            
            # Queue and play audio
            sdl2.SDL_QueueAudio(device, audio_data, len(audio_data))
            sdl2.SDL_PauseAudioDevice(device, 0)  # Start playing
            
            # Wait for audio to finish
            while sdl2.SDL_GetQueuedAudioSize(device) > 0:
                sdl2.SDL_Delay(100)
            
            # Clean up
            sdl2.SDL_CloseAudioDevice(device)
            sdl2.SDL_Quit()
            
            return True
            
        except Exception as e:
            print(f"SDL2 audio error: {e}")
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
        beat_duration = 60000 // midi_context['tempo'] // 4  # ms per beat (normal speed)
        
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
    
    @classmethod
    def play_midi_file(cls) -> Optional[Dict]:
        """Play the entire accumulated MIDI file"""
        from .midi_music import MidiMusicGenerator
        
        midi_path = MidiMusicGenerator.MIDI_FILE_PATH
        if not midi_path.exists():
            return None
        
        # Get volume setting
        volume = cls.get_volume()
        
        # Parse MIDI file to extract all tracks
        tracks = MidiMusicGenerator.parse_midi_file(midi_path)
        if not tracks:
            return None
        
        # Convert MIDI tracks to playable progression
        # This is a simplified approach - we'll play all notes sequentially
        progression = cls._midi_tracks_to_progression(tracks)
        
        if not progression:
            return None
        
        # Try to play using different methods
        played = False
        method = None
        
        # Try SDL2 first for best cross-platform volume control
        try:
            if cls._play_with_sdl2(progression, volume):
                played = True
                method = "sdl2"
        except Exception as e:
            # SDL2 failed, continue to next method
            pass
        
        # Try PulseAudio (works well in WSL2 with WSLg)
        if not played and cls._play_with_pulseaudio(progression, volume):
            played = True
            method = "pulseaudio"
        # If WSL2 and above fails, try Windows audio methods
        elif cls._is_wsl2():
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
            return {"method": method, "notes": len(progression)}
        
        return None
    
    @classmethod
    def _midi_tracks_to_progression(cls, tracks: List[bytes]) -> List[tuple]:
        """Convert MIDI tracks to a playable progression of (frequency, duration) tuples"""
        progression = []
        
        # MIDI note to frequency conversion
        def midi_to_freq(midi_note):
            return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))
        
        # Parse each track
        for track in tracks:
            if len(track) < 8 or track[:4] != b'MTrk':
                continue
            
            # Skip MTrk header and length
            pos = 8
            track_end = len(track)
            
            # Default tempo (120 BPM)
            tempo = 500000  # microseconds per quarter note
            
            while pos < track_end - 3:
                # Read delta time (simplified - assumes single byte)
                delta_time = track[pos]
                pos += 1
                
                # Read event
                if pos >= track_end:
                    break
                    
                event = track[pos]
                pos += 1
                
                # Check for tempo change
                if event == 0xFF and pos + 2 < track_end:
                    meta_type = track[pos]
                    meta_length = track[pos + 1]
                    if meta_type == 0x51 and meta_length == 3 and pos + 5 < track_end:
                        # Tempo change
                        tempo = (track[pos + 2] << 16) | (track[pos + 3] << 8) | track[pos + 4]
                        pos += 5
                    else:
                        pos += 2 + meta_length
                # Note on event
                elif (event & 0xF0) == 0x90 and pos + 1 < track_end:
                    note = track[pos]
                    velocity = track[pos + 1]
                    pos += 2
                    
                    if velocity > 0:  # Note on with velocity > 0
                        freq = midi_to_freq(note)
                        # Simplified duration calculation (assume quarter note)
                        duration_ms = tempo // 1000  # Convert microseconds to milliseconds
                        progression.append((freq, duration_ms))
                # Note off event
                elif (event & 0xF0) == 0x80 and pos + 1 < track_end:
                    pos += 2  # Skip note and velocity
                # Other events - skip
                else:
                    if event < 0x80:
                        # Running status - this is data, not an event
                        pos -= 1
                    elif event >= 0xC0 and event <= 0xDF:
                        # Program change or channel pressure - 1 data byte
                        pos += 1
                    elif event >= 0x80:
                        # Most other events have 2 data bytes
                        pos += 2
        
        # Limit progression length to prevent very long playback
        max_notes = 200
        if len(progression) > max_notes:
            # Take a sample from throughout the song
            step = len(progression) // max_notes
            progression = progression[::step][:max_notes]
        
        return progression