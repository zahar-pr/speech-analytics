from abc import abstractmethod, ABC


class CRM(ABC):

    @abstractmethod
    def contacts_phone(self):
        pass

    @abstractmethod
    def post_note(self, note):
        pass
