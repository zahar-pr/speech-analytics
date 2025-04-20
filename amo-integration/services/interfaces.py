from abc import abstractmethod, ABC

class Telephony(ABC):

    @abstractmethod
    @property
    def mp3_url(self):
        pass

    @abstractmethod
    def _get_mp3(self):
        pass

    @abstractmethod
    def __call__(self):
        pass