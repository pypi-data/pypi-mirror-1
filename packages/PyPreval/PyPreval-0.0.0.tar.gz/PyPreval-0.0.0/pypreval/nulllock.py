#!/usr/bin/env python2.4
#
# (c) 2008 Andreas Kostyrka
#
"""
NullLock class that implements null operations, meaning
that the Store class will not serialize transactions.
Which means that serializing is the responsibility of the user.
"""

class NullLock(object):
    "ignore acquire/release"
    def acquire(self):
        "acquire a lock to protect a critical region"

    def release(self):
        "acquire a lock to protect a critical region"

    
