#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main Screen
"""

from typing import NoReturn
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.tab import MDTabsBase
from Utility.Utils import fix_emojis
from View.base_screen import BaseScreenView


class Tab(MDFloatLayout, MDTabsBase):
    pass


class MLabel(MDLabel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ChatListItem(MDCard):
    controller = ObjectProperty()
    id = ObjectProperty()
    jid = StringProperty()
    contact_name = StringProperty()
    last_message = StringProperty()
    timestamp = StringProperty()


class CallListItem(MDCard):
    # controller = ObjectProperty()
    id = ObjectProperty()
    jid = StringProperty()
    user = StringProperty()
    from_me = NumericProperty()
    timestamp = StringProperty()
    video_call = NumericProperty()
    duration = StringProperty()


class MainScreenView(BaseScreenView):

    def __init__(self, **kw):
        super(MainScreenView, self).__init__(**kw)
        self.dialog = MDDialog()

    def show_dialog_wait(self) -> NoReturn:
        """Displays a wait dialog while the model is processing data."""
        self.dialog.auto_dismiss = True
        self.dialog.text = "Loading ..."
        self.dialog.open()

    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """
        pass

    def show_chats_list(self, contact_chats):
        for chat in contact_chats:
            chatitem = ChatListItem()
            chatitem.controller = self.controller
            chatitem.id = chat['_id']
            chatitem.contact_name = chat["user"]
            if chat['text_data'] is not None:
                chatitem.last_message = fix_emojis(chat['text_data'], self.app.emojis_font)
            else:
                chatitem.last_message = ''
            chatitem.timestamp = '\n'.join(chat['timestamp'].split(' '))
            chatitem.jid = chat['raw_string_jid']
            self.ids['contact_chat_list'].add_widget(chatitem)

    def build_group_chat_list(self, group_chats):
        for chat in group_chats:
            user = fix_emojis(chat['user'], self.app.emojis_font)
            last_message = ''
            if chat['text_data'] is not None:
                last_message = fix_emojis(chat['text_data'], self.app.emojis_font)
            timestamp = '\n'.join(chat['timestamp'].split(' '))
            item = ChatListItem(id=chat['_id'],
                                contact_name=user,
                                last_message=last_message,
                                timestamp=timestamp,
                                controller=self.controller)
            self.ids['group_chat_list'].add_widget(item)

    def build_calls_list(self, calls):
        for call in calls:
            id = call['_id']
            jid = call['raw_string_jid']
            user = fix_emojis(call['user'], self.app.emojis_font)
            from_me = call['from_me']
            video_call = call['video_call']
            timestamp = call['timestamp']
            duration = str(call['duration'])
            item = CallListItem(id=id,
                                jid=jid,
                                user=user,
                                from_me=from_me,
                                video_call=video_call,
                                timestamp=timestamp,
                                duration=duration
                                )
            self.ids['calls'].add_widget(item)
