#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Decryption module

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.
This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
"""

from decryption.dbs.WhatsAppCrypt14Crypt15Decrypter.decrypt14_15 import *


def decrypt_db(keyfile: str, encrypted, decrypted, verbose=True, force=True,
               data_offset=DEFAULT_DATA_OFFSET, iv_offset=DEFAULT_IV_OFFSET, buffer_size=io.DEFAULT_BUFFER_SIZE,
               no_protobuf=False, no_guess=False, no_mem=False):
    with open(encrypted, 'rb') as encrypted:
        with open(decrypted, 'wb') as decrypted:
            logger = SimpleLog(verbose=verbose, force=force)
            if not (0 < data_offset < HEADER_SIZE - 128):
                logger.f("The data offset must be between 1 and {}".format(HEADER_SIZE - 129))
            if not (0 < iv_offset < HEADER_SIZE - 128):
                logger.f("The IV offset must be between 1 and {}".format(HEADER_SIZE - 129))
            if buffer_size is not None:
                if not 1 < buffer_size < maxsize:
                    logger.f("Invalid buffer size")
            # Get the decryption key from the key file or the hex encoded string.
            key = Key(logger, keyfile)
            logger.v(str(key))
            cipher = None
            file_hash = md5()
            # Now we have to get the IV and to guess where the data starts.
            # We have two approaches to do so.
            # First: try parsing the protobuf message.
            if not no_protobuf:
                # Check if the backup is crypt12 first.
                try:
                    cipher = check_crypt12(logger, file_hash, key, encrypted)
                except ValueError:
                    cipher = parse_protobuf(logger=logger, file_hash=file_hash, key=key, encrypted=encrypted)

            if cipher is None and not no_guess:
                # If parsing the protobuf message failed, we try guessing the offsets.
                cipher = guess_offsets(logger=logger, file_hash=file_hash, key=key.key, encrypted=encrypted,
                                       def_iv_offset=iv_offset, def_data_offset=data_offset)

            if buffer_size is not None:
                decrypt(logger, file_hash, cipher, encrypted, decrypted, buffer_size)
            elif no_mem:
                decrypt(logger, file_hash, cipher, encrypted, decrypted, io.DEFAULT_BUFFER_SIZE)
            else:
                decrypt(logger, file_hash, cipher, encrypted, decrypted)



            # LOL
            # if date.today().day == 1 and date.today().month == 4:
            #     logger.i("Done. Uploading messages to the developer's server...")
            #     sleep(0.5)
            #     logger.i("Uploaded. The developer will now read and publish your messages!")
            # else:
            #     logger.i("Done")


if __name__ == '__main__':
    pass
