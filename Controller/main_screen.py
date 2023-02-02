import importlib
from typing import NoReturn
import View.MainScreen.main_screen
import View.screens

# We have to manually reload the view module in order to apply the
# changes made to the code on a subsequent hot reload.
# If you no longer need a hot reload, you can delete this instruction.
importlib.reload(View.MainScreen.main_screen)


class MainScreenController:
    """
    The `MainScreenController` class represents a controller implementation.
    Coordinates work of the view with the model.
    The controller implements the strategy pattern. The controller connects to
    the view to control its actions.
    """

    def __init__(self, model):
        self.model = model  # Model.main_screen.MainScreenModel
        self.view = View.MainScreen.main_screen.MainScreenView(controller=self, model=self.model)

    def get_view(self) -> View.MainScreen.main_screen:
        return self.view

    def on_tap_button_login(self) -> NoReturn:
        """Called when the `LOGIN` button is pressed."""
        self.view.show_dialog_wait()

    def on_enter(self, *args):
        self.view.show_dialog_wait()
        contact_chats = self.model.get_contact_chats()
        self.view.show_chats_list(contact_chats)
        group_chats = self.model.get_group_chats()
        self.view.build_group_chat_list(group_chats)
        calls = self.model.get_calls(how_many=self.view.app.call_log_size)
        self.view.build_calls_list(calls)
        self.view.dialog.dismiss()

    def show_chat_screen(self, chat_id, user, jid):
        self.view.app.selected_chat_id = chat_id
        self.view.app.selected_user = user
        self.view.app.status = self.model.get_status(jid)
        self.view.app.screens_manager.current = "chat screen"

    def clear_session(self):
        for screen in View.screens.screens:
            if screen == 'login screen':
                continue
            self.view.screens_manager.remove_widget(self.view.screens_manager.get_screen(screen))

    def log_out(self, *args):
        print('Logging out ...')
        self.view.app.screens_manager.current = 'login screen'
        # clear
        self.clear_session()
