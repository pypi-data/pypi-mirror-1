# -*- coding: utf-8 -*-
"""
    pocoo.pkg.core.statustracking
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module implements some functions and classes used
    for tracking post/thread read/unread status information.

    :copyright: 2006 by Armin Ronacher.
    :license: GNU GPL, see LICENSE for more details.
"""
import marshal
import time


class StatusTracker(object):
    """
    Base class that is passes a binary status tracking information
    dump and is used to check or update tracking informations.
    """

    def __init__(self, data):
        pass
