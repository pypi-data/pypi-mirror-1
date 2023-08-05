# -*- coding: utf-8 -*-
# Copyright (C)2007 Ingeniweb

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
""" Base filters
"""
from Levenshtein import ratio

def search_similarities(code_mapping, treshold=0.7):
    similar = []
    items = code_mapping.items()
    done = []
    for key, value in items:
        done.append(key)
        code = str(value.code)
        for key2, value2 in items:
            if key2 == key or key2 in done:
                continue
            code2 = str(value2.code)
            res = ratio(code, code2)
            if res > treshold:
                yield (res, value.key, value2.key)

