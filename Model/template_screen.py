from Model.base_model import BaseScreenModel


class TemplateScreenModel(BaseScreenModel):
    """
    Implements the logic of the
    :class:`~View.main_screen.MainScreen.MainScreenView` class.
    """
    def __init__(self, base):
        self.base = base