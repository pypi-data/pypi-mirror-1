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
""" Decorators
"""
import logging
import time
import datetime

def _formatter(total, function, args, kw):
    """default rendering"""
    def _fmt(element):
        if hasattr(element, 'func_name'):
            return element.func_name
        return element

    func_name = _fmt(function)
    args = tuple([_fmt(arg) for arg in args])

    now = datetime.datetime.now().isoformat()
    msg = 'function \'%s\', args: %s, kw: %s' % \
            (func_name, str(args), str(kw))
    return 'log_time::%s::%.3f::%s' % (now, total, msg)

def log_time(treshold=0, logger=logging.info, formatter=_formatter,
             debugger=None):
    """ timedtest decorator
    decorates the test method with a timer
    when the time spent by the test exceeds
    max_time in seconds, an Assertion error is thrown.
    """
    def _timedtest(function):
        def wrapper(*args, **kw):
            start = time.time()
            try:
                try:
                    return function(*args, **kw)
                except Exception, e:
                    if debugger is not None:
                        debugger(e)
                    raise e
            finally:
                total = time.time() - start

                if total > treshold:
                    logger(formatter(total, function, args, kw))

        return wrapper

    return _timedtest


