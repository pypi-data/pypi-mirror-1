"""
A simple pickleshare storage.

Entries are stored as dicts, using for keys the integers
as strings ("1", "2", "3", etc.) as default.
"""
from pickleshare import PickleShareDB

from atomstorage import shelvestorage


class EntryManager(shelvestorage.EntryManager):
    def __init__(self, location):
        self.db = PickleShareDB(location)
