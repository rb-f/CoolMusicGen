import time

import math
import wave
import struct
import random
import numpy as np

# preferences
ALL_PROGS = [
    [0, 5, 7, 0, 0, 5, 7, 0],
    [0, 4, 5, 0, 9, 4, 5, 0],
    [0, 0, 9, 9, 5, 5, 7, 7, 0, 0, 9, 9, 5, 5, 7, 7],
    [0, 0, 9, 9, 5, 7, 0, 0, 0, 0, 9, 9, 5, 7, 0, 0],
    [5, 7, 9, 0, 5, 7, 9, 0],
]

# config
if (random.random() < 0.3):
    BPM = random.randint(80, 200)
else:
    BPM = random.randint(100, 150)
KEYA = random.randint(-4, 7)

SAMPLE_RATE = 44100
CHANNELS = 1
AMPLITUDE = 0.6
CHUNK_DURATION = (0.25 / BPM) * 60

MODULATION_CHANCE = 0.1

# set the musical properties
SCALE = [0, 2, 4, 7, 9, 12, 16]
SCALE = [440*(2**((i - 9) / 12)) for i in SCALE]
SCALE.append(0)

PROG = [9, 0, 5, 7]

def export_random_music(fname, length_secs):
    """Generate random music, export as WAV"""
    print(f"Starting export {fname} with length {length_secs}s")
    
    samples_per_chunk = int(SAMPLE_RATE * CHUNK_DURATION)
    total_chunks = int(length_secs / CHUNK_DURATION)
    note_duration_chunks = 4
    
    ke = random.randint(-4, 7)
    
    note_i = 2
    bass_1 = 0
    phase = 0.0
    phase2 = 0.0
    chunk_counter = 0
    curr_prog = random.choice(ALL_PROGS)
    
    drum_value = 0
    
    with wave.open(fname, 'wb') as wav_file:
        wav_file.setnchannels(CHANNELS)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        
        for chunk_i in range(total_chunks):
            if chunk_counter >= note_duration_chunks:
                note_i += random.randint(-2, 2)
                note_i = (note_i % len(SCALE))
                chunk_counter = 0
            
            if drum_value >= 16:
                drum_value = 0

            if bass_1 >= len(curr_prog):
                bass_1 = 0
                curr_prog = random.choice(ALL_PROGS)
                if (random.random() < MODULATION_CHANCE):
                    if (random.random() < 0.4):
                        ke = random.randint(-4, 7)
                    else:
                        ke += random.randint(1,2)
                        if (ke > 7):
                            ke -= 12

            freq = SCALE[note_i] * 2**(ke / 12)
            
            t = (np.arange(samples_per_chunk) + phase) / SAMPLE_RATE
            d3 = 0
            d4 = 2
            if (drum_value % 2 == 0):
                d3 = 2
                d4 = 12
            if (drum_value % 4 == 0):
                d3 = 4
                d4 = 3
            if (drum_value % 8 == 0):
                d3 = 24
                d4 = 2
            if (d3 > 0):
                d1 = samples_per_chunk // d3 // d4
                d2 = samples_per_chunk - d1
                d = np.append(np.repeat(np.random.random(d1) - 0.5, d3), np.repeat([0], d2))
            else:
                d = np.repeat([0], samples_per_chunk)
            
            bf = curr_prog[bass_1] % 12
            bassfreq = 110 * 2**((bf - 9) / 12) * 2**(ke / 12)
            freq3 = 220 * 2**((bf - 9) / 12) * 2**(ke / 12)
            freq4 = 220 * 2**((bf - (5 if bf in [0, 4, 5, 7] else 6)) / 12) * 2**(ke / 12)
            t2 = (np.arange(samples_per_chunk) + phase2) / SAMPLE_RATE
            
            bass = (((t2 * bassfreq) % 1) - 0.5) * 2
            sine = np.sin(2 * np.pi * freq * t)
            square = np.sign(sine)
            drum = np.resize(d,samples_per_chunk)
            mood1 = np.sin(2 * np.pi * freq3 * t)
            mood2 = np.sin(2 * np.pi * freq4 * t)
            
            synth_wave = (sine * 0.3) + (square * 0) + (drum * 0.4) + (bass * 0.2) + (mood1 * 0.15) + (mood2 * 0.15)
            
            normalized = synth_wave * AMPLITUDE
            
            int_samps = (normalized * 32767).astype(np.int16)
            
            binary_data = struct.pack(f'<{len(int_samps)}h', *int_samps)
            wav_file.writeframes(binary_data)
            
            phase += samples_per_chunk
            phase2 += samples_per_chunk
            chunk_counter += 1
            drum_value += 1
            if (drum_value > 15):
                bass_1 += 1
            
    print("Export complete")
    
if __name__ == "__main__":
    seconds = int(input("How long (seconds)? "))
    export_random_music(f"Res/{int(time.time() * 1000)}.wav", seconds)