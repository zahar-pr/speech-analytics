from abc import abstractmethod, ABC


class Telephony(ABC):

    @abstractmethod
    @property
    def mp3_url(self):
        pass

    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass


class CRM(ABC):

    @abstractmethod
    @property
    def contacts_phone(self):
        pass

    @abstractmethod
    def post_note(self, note):
        pass
