from processing.FFTCalculator import FourierCalculator
from processing.PitchCalculator import PitchCalculator

import vlc
import sounddevice as sd

class Signal:
    def __init__(self, sample_rate, note, instrument, filename):
        self.note = self.get_mono(note)
        self.sample_rate = sample_rate
        self.instrument = instrument
        self.fft_calculator = FourierCalculator()
        self.pitcher = PitchCalculator()
        self.filename = filename

        self.tmin = 0
        self.tmax = len(note)

    def get_mono(self, note):
        try:
            return note[:, 0]
        except IndexError:
            return note

    def get_fft(self, low=0, high=2000):
        frequencies, fft_magnitude, fft_phase = self.fft_calculator.get_fft(self.note[self.tmin:self.tmax], self.sample_rate)

        mask = (frequencies >= low) & (frequencies <= high)
        xf_filtered = frequencies[mask]
        yf_filtered = fft_magnitude[mask]
        fft_phase_filtered = fft_phase[mask]

        return xf_filtered, yf_filtered, fft_phase_filtered
    
    def pitches(self, n, distance, low=0, high=2000):
        frequencies, fft_magnitude, _ = self.get_fft(low, high)
        peaks, amplitude, pitches = self.pitcher.get_pitches(frequencies, fft_magnitude, n, distance, self.instrument)
        return peaks, amplitude, pitches
    
    def get_chord(self, distance):
        frequencies, fft_magnitude, _ = self.get_fft()
        chord = self.pitcher.get_chord(frequencies, fft_magnitude, distance, self.instrument)
        return chord
    
    def get_signal(self, tmin, tmax):
        self.tmin = tmin

        if tmax:
            self.tmax = tmax

        return self.note[self.tmin:self.tmax]
    
    def play(self):
        if self.filename:
            player = vlc.MediaPlayer(self.filename)
            player.play()

        else:
            sd.play(self.note, self.sample_rate)
            sd.wait()