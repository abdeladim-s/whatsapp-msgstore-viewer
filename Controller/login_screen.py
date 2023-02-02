import importlib
import os.path
import traceback
from typing import NoReturn

import multitasking

from Utility.Utils import check_path

multitasking.set_max_threads(10)

import View.LoginScreen.login_screen

# We have to manually reload the view module in order to apply the
# changes made to the code on a subsequent hot reload.
# If you no longer need a hot reload, you can delete this instruction.
importlib.reload(View.LoginScreen.login_screen)

from kivy.clock import mainthread


class LoginScreenController:

    def __init__(self, model):
        self.model = model  # Model.main_screen.MainScreenModel
        self.view = View.LoginScreen.login_screen.LoginScreenView(controller=self, model=self.model)
        self.decrypt = None

    def get_view(self) -> View.LoginScreen.login_screen:
        return self.view

    def check_files(self):
        if self.view.app.msgstore_file is None:
            self.view.show_dialog('No msgstore provided!!',
                                  title="Error",
                                  auto_dismiss=True)
            return False
        if not check_path(self.view.app.msgstore_file):
            self.view.show_dialog(f'Please recheck the provided msgstore path\n`{self.view.app.msgstore_file}`'
                                  f'\ndoes not exist',
                                  title="Error", auto_dismiss=True)
            return False

        if not check_path(self.view.app.wa_file):
            self.view.show_dialog(f'Please recheck the provided wa.db path\n`{self.view.app.wa_file}`'
                                  f'\ndoes not exist',
                                  title="Error", auto_dismiss=True)
            return False

        if not check_path(self.view.app.wp_dir):
            self.view.show_dialog(f'Please recheck the provided Whatsapp directory path\n`{self.view.app.wp_dir}`'
                                  f'\ndoes not exist',
                                  title="Error", auto_dismiss=True)
            return False

        return True

    @mainthread
    def login(self):
        try:
            self.view.app.load_db()
            self.view.screens_manager.get_screen('main screen').controller.on_enter()
            self.view.hide_dialog()
            self.view.app.screens_manager.current = "main screen"
        except Exception as e:
            print(traceback.format_exc())
            msg = f"""
{str(e)}

Try to choose another version from the `Database version` drop-down menu.

If no version works, probably the database is encrypted or you have an updated version of Whatsapp and your database schema is not supported yet.
Submit an issue on our Github page to help you add support to your database schema. 
                """
            self.view.show_dialog(msg=msg, title='Database schema is not supported!', auto_dismiss=True)

    @mainthread
    def show_decryption_error(self, error):
        err = """
Unfortunately, the decryption of the database was not successful.
Maybe you didn't provide the right key or the file is corrupted or the version is not supported.
This app is using the `WhatsApp-Crypt14-Crypt15-Decrypter` library under the hood. 
Visit their Github page for more information or to get some help:
<https://github.com/ElDavoo/WhatsApp-Crypt14-Crypt15-Decrypter>
        """
        print(traceback.format_exc())
        self.view.hide_dialog()
        self.view.show_dialog(f'{str(error)}\n\n{err} ', title='Decryption', auto_dismiss=True)

    def show_warning(self, warning):
        self.view.show_toast(f"{warning}")

    @mainthread
    def show_decryption_success(self, path):
        self.view.show_toast(f"Database decrypted successfully, the decrypted file is stored in {path}")

    @mainthread
    def update_dialog(self, msg):
        self.view.dialog.text = msg

    @multitasking.task
    def decrypt_dbs(self, key):
        # decrypting msgstore
        if self.view.app.wa_file is not None:
            try:
                self.update_dialog("Decrypting wa.db ...")
                enc_db = self.view.app.wa_file
                dec_db = enc_db + '-decrypted.db'
                self.decrypt_db(key, enc_db, dec_db)
                self.view.app.wa_file = dec_db
                self.show_decryption_success(dec_db)
            except Exception as e:
                self.show_decryption_error(e)
                os.remove(dec_db)
        try:
            self.update_dialog("Decrypting msgstore.db ...")
            enc_db = self.view.app.msgstore_file
            dec_db = enc_db + '-decrypted.db'
            self.decrypt_db(key, enc_db, dec_db)
            self.view.app.msgstore_file = dec_db
            self.show_decryption_success(dec_db)
            self.login()
        except Exception as e:
            self.show_decryption_error(e)
            os.remove(dec_db)

    def decrypt_db(self, key, enc_db, dec_db):
        from decryption.dbs.decrypt_db import decrypt_db
        decrypt_db(keyfile=key, encrypted=enc_db, decrypted=dec_db)
        if not check_path(dec_db):
            raise Exception('Decryption error\nNo decrypted database was found in path')
        self.show_decryption_success(dec_db)

    def on_tap_button_login(self) -> NoReturn:
        """Called when the `LOGIN` button is pressed."""
        self.view.show_dialog('Login ...', title='Please wait ...', auto_dismiss=False)
        self.view.app.msgstore_file = None if self.view.ids['msgstore_file_path'].text == '' else self.view.ids[
            'msgstore_file_path'].text
        self.view.app.wa_file = None if self.view.ids['wa_file_path'].text == '' else self.view.ids['wa_file_path'].text
        self.view.app.wp_dir = None if self.view.ids['wp_dir'].text == '' else self.view.ids['wp_dir'].text
        if not self.check_files():
            return

        if self.view.ids['enc_checkbox'].active:
            # decrypt first
            key = self.view.key_file_widget.text
            if key == '':
                self.view.show_dialog('Encrypted database is selected but no key has been provided!', title='Error',
                                      auto_dismiss=True)
                return
            elif not check_path(key):
                self.view.show_dialog(f'Please recheck the provided key path\n`{key}`'
                                      f'\ndoes not exist',
                                      title="Error", auto_dismiss=True)
                return
            else:
                # trying to decrypt
                self.view.show_dialog('Trying to decrypt ...', title='Please wait ...', auto_dismiss=False)
                self.decrypt_dbs(key)
        else:
            self.login()
