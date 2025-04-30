from abc import ABC, abstractmethod
class Telephony(ABC):

    @abstractmethod
    def mp3_url(self):
        pass

    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass