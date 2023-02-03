#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This file describes how the database should look like and what it should return.
Because this app is only a reverse engineering attempt of the Whatsapp database, it is very likely that it might break
in case there have been any updates to the database.

The `schema` variable and the `AbstractDatabase` class are introduced to make it easy to add support to
different versions of databases.
"""

import sqlite3
from abc import ABC, abstractmethod


class AbstractDatabase(ABC):

    def __init__(self, msgstore, wa=None, schema=None):
        self.msgstore = msgstore
        self.wa = wa
        self.contacts = None
        self.schema: dict = schema  # a simple map between the (tables, attributes) used in the code and their real
        # in the database, see the `check_database_schema` method for more details

        msgstore_con = sqlite3.connect(self.msgstore, check_same_thread=False)
        msgstore_con.row_factory = lambda c, r: dict([(col[0], r[idx]) for idx, col in enumerate(c.description)])
        self.msgstore_cursor = msgstore_con.cursor()
        if wa is not None:
            wa_con = sqlite3.connect(self.wa, check_same_thread=False)
            wa_con.row_factory = lambda c, r: dict([(col[0], r[idx]) for idx, col in enumerate(c.description)])
            self.wa_cursor = wa_con.cursor()
            self.load_contacts(self.wa_cursor)

    @abstractmethod
    def get_chat_views(self):
        pass

    @abstractmethod
    def fetch_contact_chats(self):
        """
        This function should return a table of the available contact chat views,
        i.e. the main activity of WP
        The table should look like the following
        chat_id; user; last_message; time
        """
        pass

    @abstractmethod
    def fetch_group_chats(self):
        """
        This function should return a table of the available contact chat views,
        i.e. the main activity of WP
        The table should look like the following
        chat_id; user; last_message; timestamp
        """
        pass

    @abstractmethod
    def fetch_calls(self, how_many=None):
        """
        This function should return a table of the available contact chat views,
        i.e. the main activity of WP
        The table should look like the following
        chat_id; user; last_message; timestamp
        """
        pass

    @abstractmethod
    def fetch_chat(self, chat_id):
        """
        This function should return a table of the messages of a specific chat identified by chat_id
        The table should look like the following

        _id, key_id, from_me, timestamp, text_data, message_type, mim_type, file_path,
        width, height, message_url, thumbnail
        """
        pass

    def load_contacts(self, wa_cursor):
        sql_query = """
        SELECT 
            jid,
            status,
            display_name,
            number,
            given_name,
            family_name
        FROM 
            wa_contacts
        """
        contacts_list = wa_cursor.execute(sql_query).fetchall()
        self.contacts = {}
        for contact in contacts_list:
            self.contacts[contact['jid']] = contact

    def check_database_schema(self):
        """
        This method checks that the database contains the tables and attributes provided with its schema
        It will fail in case a table (or attribute) does not exist, or it has a different name
        """
        if self.schema is None:
            raise Exception('No schema has been provided!')
        for table in self.schema:
            table_name = self.schema[table]['name']
            attributes = self.schema[table]['attributes']
            sql_query = f"SELECT {','.join(attributes)} from {table_name}"
            self.msgstore_cursor.execute(sql_query).fetchone()  # this will fail if the table or the attributes do not
            # exist
