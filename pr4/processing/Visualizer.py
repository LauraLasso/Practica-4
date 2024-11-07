from matplotlib import pyplot as plt
import numpy as np
import cv2
import os

from processing.PitchCalculator import PitchCalculator

class Visualizer:
    def __init__(self, instrument):
        self.instrument = instrument
        print(instrument)

    def show_fft_cv2(self, signal, minfreq=0, maxfeq=2000):
        self.signal = signal
        
        def update_freq(val):
            try:
                min_freq = cv2.getTrackbarPos('Min Freq', 'Transformada de Fourier')
                max_freq = cv2.getTrackbarPos('Max Freq', 'Transformada de Fourier')
                n_peaks = cv2.getTrackbarPos('Max Peaks', 'Transformada de Fourier')
                distance = cv2.getTrackbarPos('P. Distance', 'Transformada de Fourier')
                self._plot_with_freq_range(min_freq, max_freq, n_peaks, distance)

            except Exception as e:
                pass

        cv2.namedWindow('Transformada de Fourier')

        xf, yf, _ = self.signal.get_fft(minfreq, maxfeq)
        
        cv2.createTrackbar('Min Freq', 'Transformada de Fourier', minfreq, int(max(xf)), update_freq)
        cv2.createTrackbar('Max Freq', 'Transformada de Fourier', maxfeq, int(max(xf)), update_freq)
        cv2.createTrackbar('Max Peaks', 'Transformada de Fourier', 1, 20, update_freq)
        cv2.createTrackbar('P. Distance', 'Transformada de Fourier', 1, 200, update_freq)

        cv2.setTrackbarPos('P. Distance', 'Transformada de Fourier', 100)

        update_freq(0)

        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return self.signal

    def _plot_with_freq_range(self, min_freq, max_freq, n, distance):
        xf_filtered, yf_filtered, _ = self.signal.get_fft(low=min_freq, high=max_freq)

        plt.figure(figsize=(10, 5))
        plt.plot(xf_filtered, yf_filtered)

        if n != 0:
            peaks, _, pitches = self.signal.pitches(n, distance, min_freq, max_freq)

            for peak in peaks:
                plt.axvline(x=xf_filtered[peak], color='r', linestyle='--')

            for i, pitch in enumerate(pitches):
                plt.text(xf_filtered[peaks[i]], yf_filtered[peaks[i]], f'{pitch}\n{xf_filtered[peaks[i]]:.2f} Hz', fontsize=10, color='r')

        chord = self.signal.get_chord(distance)

        plt.title(f'Transformada de Fourier\nDetected Chord: {chord}')
        plt.xlabel('Frecuencia (Hz)')
        plt.ylabel('Magnitud')
        plt.grid()
        
        temp_file = 'processing/resources/fft_plot.png'
        plt.savefig(temp_file)
        plt.close()
        
        image = cv2.imread(temp_file)

        cv2.imshow('Transformada de Fourier', image)

        if os.path.exists(temp_file):
            os.remove(temp_file)

    def show_audio_signal_cv2(self, signal, tmin=0, tmax=None):
        self.signal = signal
        self.signal_length = len(signal.note)
        self.sample_rate = signal.sample_rate

        cv2.namedWindow('Audio')
        
        cv2.createTrackbar('Start', 'Audio', 0, self.signal_length - 1, self.update_signal)
        cv2.createTrackbar('End', 'Audio', self.signal_length - 1, self.signal_length - 1, self.update_signal)

        cv2.setTrackbarPos('Start', 'Audio', tmin)
        if tmax:
            cv2.setTrackbarPos('End', 'Audio', tmax)


        self.update_signal(0)

        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

            elif key == ord('r'):
                signal.play()

        cv2.destroyAllWindows()

        return signal

    def update_signal(self, val):
        start = cv2.getTrackbarPos('Start', 'Audio')
        end = cv2.getTrackbarPos('End', 'Audio')

        if end <= start:
            end = start + 1

        signal_segment = self.signal.get_signal(start, end)
    
        plt.figure(figsize=(14, 6))
        plt.plot(signal_segment)

        plt.title('Señal de Audio')
        plt.xlabel('Tiempo (s)')
        plt.ylabel('Amplitud')
        plt.grid()

        temp_file = 'processing/resources/audio_plot.png'
        plt.savefig(temp_file)
        plt.close()

        image = cv2.imread(temp_file)

        cv2.imshow('Audio', image)

        if os.path.exists(temp_file):
            os.remove(temp_file)

        self.segment = signal_segment