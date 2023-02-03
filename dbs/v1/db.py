#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dbs.abstract_db import AbstractDatabase


class Database(AbstractDatabase):

    def __init__(self, msgstore, wa):
        schema = {
            'chat_view': {
                'name': 'chat_view',
                'attributes': [
                    '_id',
                    'raw_string_jid',
                    'sort_timestamp',
                    'last_message_row_id'
                ]
            },
            'message': {
                'name': 'message',
                'attributes': [
                    '_id',
                    'chat_row_id',
                    'key_id',
                    'from_me',
                    'timestamp',
                    'text_data',
                ]
            },
            'message_media': {
                'name': 'message_media',
                'attributes': [
                    'message_row_id',
                    'file_path',
                ]
            },
            'message_quoted': {
                'name': 'message_quoted',
                'attributes': [
                    'message_row_id',
                    'text_data',
                    'from_me',
                    'key_id'
                ]
            },
        }
        super(Database, self).__init__(msgstore, wa, schema=schema)

    def fetch_contact_chats(self):
        chat_view_table = self.schema['chat_view']['name']  # I will continue later
        sql_query = """
        select 
        chat_view._id, 
        jid.user,
        chat_view.raw_string_jid,
        message.text_data, 
        DATETIME(ROUND(chat_view.sort_timestamp / 1000), 'unixepoch') as timestamp

        from chat_view INNER JOIN jid ON chat_view.raw_string_jid=jid.raw_string 
        INNER JOIN message ON chat_view.last_message_row_id = message._id

        WHERE 

        chat_view.raw_string_jid not LIKE '%g.us'
        """
        return self.msgstore_cursor.execute(sql_query).fetchall()

    def fetch_group_chats(self):
        sql_query = """
                select 
                chat_view._id, 
                chat_view.subject as user,
                chat_view.raw_string_jid,
                message.text_data, 
                DATETIME(ROUND(chat_view.sort_timestamp / 1000), 'unixepoch') as timestamp

                from chat_view INNER JOIN jid ON chat_view.raw_string_jid=jid.raw_string 
                INNER JOIN message ON chat_view.last_message_row_id = message._id

                WHERE 

                chat_view.raw_string_jid LIKE '%g.us'
                """
        return self.msgstore_cursor.execute(sql_query).fetchall()

    def fetch_calls(self, how_many=None):
        sql_query = """
               select 
                call_log._id, call_log.from_me, 
                DATETIME(ROUND(call_log.timestamp / 1000), 'unixepoch') as timestamp, 
                call_log.video_call,
                Time(call_log.duration, 'unixepoch') as duration,
                jid.user, 
                jid.raw_string as raw_string_jid

                from call_log LEFT JOIN jid
                ON call_log.jid_row_id = jid._id
                """
        if how_many:
            return self.msgstore_cursor.execute(sql_query).fetchmany(how_many)
        else:
            return self.msgstore_cursor.execute(sql_query).fetchall()

    def fetch_chat(self, chat_id):
        sql_query = f"""
        select  message._id, message.key_id, message.from_me, DATETIME(ROUND(message.timestamp / 1000), 'unixepoch') as timestamp,  ifnull(message.text_data, '') as text_data,
        message_media.file_path,
        message_quoted.text_data  as message_quoted_text_data,
        message_quoted.from_me as message_quoted_from_me,
        message_quoted.key_id as message_quoted_key_id
        
        from  message LEFT JOIN message_media 
        ON message._id = message_media.message_row_id
        LEFT JOIN message_quoted 
        ON message._id = message_quoted.message_row_id
        
        WHERE message.chat_row_id={chat_id}
        """
        return self.msgstore_cursor.execute(sql_query).fetchall()
