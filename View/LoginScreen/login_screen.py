#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Login screen
"""

import os
import webbrowser
from typing import NoReturn
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.spinner import MDSpinner
from Utility.Utils import check_path
from View.base_screen import BaseScreenView


class TextFieldFileManager(MDRelativeLayout):
    text = StringProperty()
    hint_text = StringProperty()
    helper_text = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager, select_path=self.select_path
        )

    def file_manager_open(self):
        self.file_manager.show(os.path.expanduser("~"))  # output manager to the screen
        self.manager_open = True

    def select_path(self, path: str):
        self.exit_manager()
        toast(path)
        self.text = path

    def on_text(self, instance, value):
        self.text = value

    def exit_manager(self, *args):
        self.manager_open = False
        self.file_manager.close()

    def events(self, instance, keyboard, keycode, text, modifiers):
        '''Called when buttons are pressed on the mobile device.'''

        if keyboard in (1001, 27):
            if self.manager_open:
                self.file_manager.back()
        return True

    def open_file_manager(self, hint_text):
        self.file_manager.show(os.path.expanduser("~"))  # output manager to the screen
        self.manager_open = True


class SettingsContent(ScrollView):
    pass


class About(BoxLayout):
    about = StringProperty()
    license = StringProperty()
    credits = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with open('about', 'r') as file:
            content = file.read()
            self.about = content.replace('$$version$$', MDApp.get_running_app().version)\
                .replace('$$g_page$$', MDApp.get_running_app().g_page)
        with open('LICENSE', 'r') as file:
            self.license = file.read()
        with open('credits', 'r') as file:
            self.credits = file.read()

        self.ids.about_label.bind(on_ref_press=self.open_link)

    def open_link(self, instance, link):
        webbrowser.open(link)


class LoginScreenView(BaseScreenView):

    def __init__(self, **kw):
        super(LoginScreenView, self).__init__(**kw)
        self.dialog = None
        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "height": dp(56),
                "text": f"{version}",
                "on_release": lambda x=version: self.set_item(x),
            }
            for version in MDApp.get_running_app().db_versions
        ]

        self.menu = MDDropdownMenu(
            caller=self.ids.db_version,
            items=menu_items,
            position="bottom",
            width_mult=4,
        )

        self.settings_content = SettingsContent()
        self.settings_dialog = MDDialog(
            title="Advanced Settings",
            type="custom",
            content_cls=self.settings_content,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=self.settings_cancel
                ),
                MDRaisedButton(
                    text="Save",
                    theme_text_color="Custom",
                    on_release=self.settings_save
                ),
            ],
        )

        self.about = About()
        self.about_dialog = MDDialog(
            title="About",
            type="custom",
            content_cls=self.about,
        )

        self.key_file_widget = TextFieldFileManager(id='key_file', hint_text="Key",
                            pos_hint={"center_x": .5, "center_y": .5},
                            helper_text="To decrypt the database")

    def set_item(self, text__item):
        self.ids.db_version.text = text__item
        self.app.db_version = text__item
        self.menu.dismiss()

    def dialog_dismiss(self):
        self.dialog = None

    def hide_dialog(self):
        if self.dialog is not None:
            self.dialog.dismiss()

    def show_dialog(self, msg, title=None, auto_dismiss=False) -> NoReturn:
        """Displays a wait dialog while the model is processing data."""
        self.hide_dialog()
        self.dialog = MDDialog(title='Login', radius=[20, 7, 20, 7])
        self.dialog.bind(on_dismiss=lambda x: self.dialog_dismiss())
        self.dialog.auto_dismiss = auto_dismiss
        if title:
            self.dialog.title = title + '\n'
        self.dialog.text = msg
        if auto_dismiss is False:
            progress = MDSpinner(determinate=False, size_hint=(None, None), size=(48, 48), pos_hint={'right: 1'})
            self.dialog.add_widget(progress)
        self.dialog.open()

    def on_enc_checkbox(self, state, *args):
        if state:
            self.ids.key_file_container.add_widget(self.key_file_widget)
        else:
            self.ids.key_file_container.remove_widget(self.key_file_widget)

    def open_settings(self):
        print('opening settings')
        self.settings_dialog.open()

    def settings_cancel(self, *args):
        self.settings_dialog.dismiss()

    def settings_save(self, *args):
        general_font_path = self.settings_content.ids['general_font'].text
        if general_font_path == '':
            self.app.general_font = self.app.default_settings['general_font']
        else:
            if not check_path(general_font_path):
                self.show_dialog(msg=f'The path `{general_font_path}` does not exist', title='General Font error',
                                 auto_dismiss=True)
                return
            self.app.general_font = general_font_path

        #  I am exhausted, I don't want to think of any other abstraction !! Let us do it stupidly
        emojis_font_path = self.settings_content.ids['emojis_font'].text
        if emojis_font_path == '':
            self.app.emojis_font = self.app.default_settings['emojis_font']
        else:
            if not check_path(general_font_path):
                self.show_dialog(msg=f'The path `{emojis_font_path}` does not exist', title='Emojis Font error',
                                 auto_dismiss=True)
                return
            self.app.emojis_font = emojis_font_path

        # call log size
        call_log_size = self.settings_content.ids['call_log_size'].text
        if call_log_size == '':
            self.app.call_log_size = self.app.default_settings['call_log_size']
        else:
            try:
                call_log_size_int = int(call_log_size)
                self.app.call_log_size = call_log_size_int
            except Exception as e:
                self.show_dialog(msg=f'Call log size`{call_log_size}` is not a number', title='Calls log size error',
                                 auto_dismiss=True)
                return

        self.settings_dialog.dismiss()
        toast('Settings saved successfully')

    def show_toast(self, msg):
        toast(msg)

    def open_about(self):
        self.about_dialog.open()

    def open_github_page(self):
        webbrowser.open(self.app.g_page)

    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """
