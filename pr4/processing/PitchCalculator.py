import json
from scipy.signal import find_peaks 
import numpy as np
import torch
import torch.nn.functional as F

class PitchCalculator:
    def __init__(self):
        self.es_note_frequencies = json.load(open('notes/data/piano_freq.json', 'r'))
        self.en_note_frequencies = json.load(open('notes/data/guitar_freq.json', 'r'))

        self.piano_chords = json.load(open('notes/data/piano_chords.json', 'r'))
        self.guitar_chords = json.load(open('notes/data/guitar_chords.json', 'r'))

    def get_pitch(self, xf, yf, instrument='piano'):
        max_index = yf.argmax()
        max_freq = xf[max_index]
        pitch = self.get_pitch_from_frequency(max_freq, instrument)

        return pitch
    
    def get_pitches(self, xf, yf, n=5, distance=100, instrument='piano'):
        peaks, _ = find_peaks(yf, height=0, distance=distance)
        sorted_peaks = peaks[np.argsort(yf[peaks])][::-1]
        amplitude = yf[sorted_peaks]

        pitches = []
        for i in range(n):
            pitch = self.get_pitch_from_frequency(xf[sorted_peaks[i]], instrument)
            pitches.append(pitch)

        return sorted_peaks[:n], amplitude, pitches
    
    def get_chord(self, xf, yf, distance, instrument='guitarra'):
        chord = self.get_chord_from_frequencies(xf, yf, distance, instrument)
        return chord
    
    def get_chord_from_frequencies(self, xf, yf, distance, instrument):
        chords = self.chords(instrument)

        frequencies, _, _ = self.get_pitches(xf, yf, n=12, distance=distance, instrument=instrument)
        frequencies = xf[frequencies]
        actual_chord = None

        for chord, chord_freqs in chords.items():
            keys = self.satisfied_keys(frequencies, chord_freqs)
            if keys == len(chord_freqs):
                actual_chord = chord

        return actual_chord

    def satisfied_keys(self, frequencies, chord_freqs):
        keys = []
        for chord_freq in chord_freqs:
            for freq in frequencies:
                diff = abs(freq - chord_freq)
                if diff < 8:
                    keys.append(freq)
                    break
        return len(keys)
    
    def get_pitch_from_frequency(self, frequency, instrument):
        min_diff = 9999999
        closest_note = None

        for note, note_freq in self.note_frequencies(instrument).items():
            diff = abs(frequency - note_freq)
            if diff < min_diff:
                min_diff = diff
                closest_note = note
        
        return closest_note
        
    def chords(self, instrument):
        if instrument == 'piano':
            return self.piano_chords
        else:
            return self.guitar_chords
        
    def note_frequencies(self, instrument):
        if instrument == 'piano':
            return self.es_note_frequencies
        else:
            return self.en_note_frequencies