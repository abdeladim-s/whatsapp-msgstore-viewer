from Model.base_model import BaseScreenModel
from dbs.abstract_db import AbstractDatabase


class ChatScreenModel(BaseScreenModel):
    """
    Implements the logic of the
    :class:`~View.main_screen.ChatScreen.ChatScreenView` class.
    """
    def __init__(self, base):
        self.base: AbstractDatabase = base

    def get_chat(self, chat_id):
        return self.base.fetch_chat(chat_id)
