#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Chat Screen
"""

import os
from typing import NoReturn
from PIL import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import OptionProperty, StringProperty, DictProperty, NumericProperty, ObjectProperty
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.behaviors import RectangularRippleBehavior, CommonElevationBehavior
from kivymd.uix.spinner import MDSpinner
from Utility.Utils import fix_emojis, check_path
from View.MainScreen.main_screen import MLabel
from View.base_screen import BaseScreenView
import webbrowser


class RV(RecycleView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Attachment(ButtonBehavior, RectangularRippleBehavior, CommonElevationBehavior, MLabel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Quote(MLabel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ChatMessage(RecycleDataViewBehavior, MDBoxLayout):
    index = 0
    txt_data = StringProperty()
    from_me = NumericProperty()  # 1 -> me;
    timestamp = StringProperty()
    media_filename = StringProperty()
    file_path = ObjectProperty(allownone=True)
    text_width = NumericProperty()
    msg_quoted_text_data = StringProperty()
    message_quoted_from_me = NumericProperty(allownone=True)
    dialog = None

    def dialog_dismiss(self):
        del self.dialog

    def hide_dialog(self):
        self.dialog.dismiss()

    def show_dialog(self, msg, title=None, auto_dismiss=True) -> NoReturn:
        """Displays a wait dialog while the model is processing data."""
        self.dialog = MDDialog(title='Login', radius=[20, 7, 20, 7])
        self.dialog.bind(on_dismiss=lambda x: self.dialog_dismiss())
        self.dialog.auto_dismiss = auto_dismiss
        if title:
            self.dialog.title = title + '\n'
        self.dialog.text = msg
        if not auto_dismiss:
            progress = MDSpinner(determinate=False, size_hint=(None, None), size=(48, 48), pos_hint={'right: 1'})
            self.dialog.add_widget(progress)
        self.dialog.open()

    def open_media(self, file_path):
        print(f'Opening {file_path}')
        if MDApp.get_running_app().wp_dir is None:
            self.show_dialog(msg='No Whatsapp directory has been provided.\n'
                                 'To View this file, provide the `Whatsapp directory path` in the login screen', title='Error')
            return
        path = os.path.join(MDApp.get_running_app().wp_dir, file_path)
        if not check_path(path):
            self.show_dialog(msg=f'{path}\n'
                                 'Does not exist, Maybe the file was removed or you provided an incorrect'
                                 '`Whatsapp directory path`',
                             title='Error')
            return
        webbrowser.open(path)

    def get_msg_widget(self):
        return self.ids['msg_content']

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.txt_data = fix_emojis(data['text_data'], MDApp.get_running_app().emojis_font)
        if data['file_path'] is not None:
            self.media_filename = data['file_path'].split('/')[-1]
        else:
            self.media_filename = ''

        if data['message_quoted_text_data'] is not None:
            self.msg_quoted_text_data = fix_emojis(data['message_quoted_text_data'], MDApp.get_running_app().emojis_font)
        else:
            self.msg_quoted_text_data = ''

        return super().refresh_view_attrs(rv, index, data)

    def refresh_view_layout(self, rv, index, layout, viewport):
        return super().refresh_view_layout(rv, index, layout, viewport)


class ChatScreenView(BaseScreenView):
    active = True
    text = 'text'
    image = 'image'
    selected_user = StringProperty()
    status = StringProperty()

    def __init__(self, **kw):
        super(ChatScreenView, self).__init__(**kw)
        self.dialog = MDDialog()
        self.dialog.bind(on_dismiss=lambda x: print('run something on dialog dismissed'))
        self.image = 'image'
        self.selected_user = self.app.selected_user

    def dialog_dismiss(self):
        del self.dialog

    def hide_dialog(self):
        self.dialog.dismiss()

    def show_dialog(self, msg, title=None, auto_dismiss=True) -> NoReturn:
        self.dialog = MDDialog(title='Login', radius=[20, 7, 20, 7])
        self.dialog.bind(on_dismiss=lambda x: self.dialog_dismiss())
        self.dialog.auto_dismiss = auto_dismiss
        if title:
            self.dialog.title = title + '\n'
        self.dialog.text = msg
        if not auto_dismiss:
            progress = MDSpinner(determinate=False, size_hint=(None, None), size=(48, 48), pos_hint={'right: 1'})
            self.dialog.add_widget(progress)
        self.dialog.open()

    def show_chat_messages(self, chat_messages):
        self.ids.rvbox.clear_widgets()
        self.ids.rv.data = chat_messages

    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """
