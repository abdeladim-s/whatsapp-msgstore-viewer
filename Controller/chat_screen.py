import importlib
import multitasking
from kivy.clock import mainthread

import Model.chat_screen
import View.ChatScreen.chat_screen

# We have to manually reload the view module in order to apply the
# changes made to the code on a subsequent hot reload.
# If you no longer need a hot reload, you can delete this instruction.
importlib.reload(View.ChatScreen.chat_screen)


class ChatScreenController:
    def __init__(self, model):
        self.model: Model.chat_screen.ChatScreenModel = model
        self.view = View.ChatScreen.chat_screen.ChatScreenView(controller=self, model=self.model)
        self.view.bind(on_enter=self.on_enter)

    def get_view(self) -> View.ChatScreen.chat_screen:
        return self.view

    @mainthread
    def task_finished(self, chat_messages):
        self.view.show_chat_messages(chat_messages)
        self.view.hide_dialog()

    @multitasking.task
    def get_chat(self, chat_id):
        chat_messages = self.model.get_chat(chat_id)
        self.task_finished(chat_messages)

    def on_enter(self, *args):
        chat_id = self.view.app.selected_chat_id
        self.view.selected_user = self.view.app.selected_user
        self.view.status = self.view.app.status
        self.view.show_dialog(msg='Loading chat ...', title='Please wait', auto_dismiss=False)
        self.get_chat(chat_id)

    def previous_screen(self):
        self.view.app.screens_manager.current = self.view.app.screens_manager.previous()