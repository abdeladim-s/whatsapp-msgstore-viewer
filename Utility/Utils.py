#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Helper functions

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

import os
import emoji


def fix_emojis(text, font):
    def add_font(chars, data_dict):
        return f"[font={font}]{chars}[/font]"

    res = emoji.replace_emoji(text, replace=add_font)
    return res


def check_path(path=None):
    if path is None:
        return True
    else:
        return os.path.exists(path)


if __name__ == '__main__':
    pass
