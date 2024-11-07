import abc
from scipy.io import wavfile

class DataLoader(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def load(self, *args):
        pass

    @abc.abstractmethod
    def save(self, *args):
        pass


class MusicLoader(DataLoader):
    def load(self, file):
        return wavfile.read(file)
    
    def save(self, file, data, sample_rate):
        wavfile.write(file, sample_rate, data)

    def to_single_channel(self, data):
        return data[:, 0]
    

class DataLoaderFactory:
    def create(self, data_type):
        if data_type == 'music':
            return MusicLoader()
        else:
            raise ValueError('Invalid data type')