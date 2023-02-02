import importlib
from typing import NoReturn

import View.TemplateScreen.template_screen

# We have to manually reload the view module in order to apply the
# changes made to the code on a subsequent hot reload.
# If you no longer need a hot reload, you can delete this instruction.
importlib.reload(View.TemplateScreen.template_screen)

from kivymd.tools.hotreload.app import MDApp


class TemplateScreenController:
    """
    The `MainScreenController` class represents a controller implementation.
    Coordinates work of the view with the model.
    The controller implements the strategy pattern. The controller connects to
    the view to control its actions.
    """

    def __init__(self, model):
        self.model = model  # Model.main_screen.MainScreenModel
        self.view = View.TemplateScreen.template_screen.TemplateScreenView(controller=self, model=self.model)
        self.app = MDApp.get_running_app()

    def get_view(self) -> View.TemplateScreen.template_screen:
        return self.view

    def on_tap_button_login(self) -> NoReturn:
        """Called when the `LOGIN` button is pressed."""
        self.view.show_dialog_wait()
        # self.app.screens_manager.current = "main screen"