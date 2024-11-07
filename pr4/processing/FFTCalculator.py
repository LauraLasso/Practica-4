import numpy as np

class FourierCalculator:
    def __init__(self):
        pass

    def get_fft(self, data, sample_rate):
        fft_result = np.fft.fft(data)
        fft_magnitude = np.abs(fft_result)
        fft_phase = np.angle(fft_result)

        frequencies = np.fft.fftfreq(len(fft_result), d=1/sample_rate)

        return frequencies, fft_magnitude, fft_phase
    
    def get_inverse_fft(self, fft_magnitude, fft_phase):
        if len(fft_magnitude) != len(fft_phase):
            raise Exception('The length of the magnitudes and phases must be the same')

        fft_result = fft_magnitude * np.exp(1j * fft_phase)
        reconstructed_signal = np.fft.ifft(fft_result).real
        return reconstructed_signal