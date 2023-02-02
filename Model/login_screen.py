from Model.base_model import BaseScreenModel


class LoginScreenModel(BaseScreenModel):
    def __init__(self, base):
        self.base = base
        self._observers = []
