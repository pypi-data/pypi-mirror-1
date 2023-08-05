"""
A simple shelve storage.

This is the reference implementation for atomstorage. It's the
simplest thing that could work, and very easy to implement. The
only downside is that it's slow.

Entries are stored as dicts, using for keys the integers
as strings ("1", "2", "3", etc.) as default.
"""
import shelve
import datetime
import operator
import re


class EntryManager(object):
    def __init__(self, location):
        self.db = shelve.open(location)
    
    def create_entry(self, entry):
        """
        Create an entry in the entry manager::

            >>> entry = {}
            >>> entry['content'] = {'content': "<p>This is an entry.</p>"}
            >>> entry['author'] = {'name': "Roberto De Almeida",
            ...                    'email': "roberto@dealmeida.net"}
            >>> em.create_entry(entry)

        If empty, 'id', 'title' and 'updated' will be automatically set.
        """
        # Required atom feed elements.
        entry.setdefault('id', self._next_id())
        entry.setdefault('title', '')
        entry.setdefault('updated', datetime.datetime.utcnow())

        # Store entry.
        self.db[str(entry["id"])] = entry
        return entry

    def get_entry(self, key):
        """
        Retrive an entry by its id::
        
            >>> entry = em.get_entry("1")

        Will return a dict describing the entry.
        """
        entry = self.db[str(key)]
        return entry

    def get_entries(self, n=None):
        """
        Retrieve last n entries, sorted by the 'updated' attribute and in
        descending order::

            >>> entries = em.get_entries(10)

        If you omit the number, all entries will be retrieved.
        """
        entries = self.db.values()

        # Sort by time.
        entries.sort(key=operator.itemgetter('updated'), reverse=True)
        entries = entries[:n]
        return entries

    def delete_entry(self, key):
        """
        Delete an entry identified by its key::

            >>> em.delete_entry("1")
        """
        del self.db[str(key)]

    def update_entry(self, new_entry):
        """
        Update an entry.
        
            >>> entry = {'title': "This is an entry"}
            >>> entry = em.create_entry(entry)
            >>> print entry['id']
            0
            >>> entry['title'] = "A different title"
            >>> em.update_entry(entry)
        """
        # Retrieve old entry and update id.
        entry = self.db[str(new_entry["id"])]
        entry.update(new_entry)

        # Update 'updated'.
        entry['updated'] = datetime.datetime.utcnow()
        
        # Store it back.
        self.db[str(entry["id"])] = entry
        return entry

    def get_entries_by_date(self, year, month=None, day=None):
        """
        Retrieve all entries from a given date::

            >>> entries = em.get_entries_by_date(2006)
            >>> entries = em.get_entries_by_date(2006, 8)
            >>> entries = em.get_entries_by_date(2006, 8, 5)
        """
        entries = self.get_entries()
        entries = [e for e in entries if e['updated'].year == year]
        if month: entries = [e for e in entries if e['updated'].month == month]
        if day: entries = [e for e in entries if e['updated'].day == day]
        return entries

    def get_entries_by_category(self, category):
        """
        Retrieve all entries from a given category::

            >>> entries = em.get_entries_by_category("Python")
        """
        entries = self.get_entries()
        entries = [e for e in entries if category.lower() in 
            [c["term"].lower() for c in e.get('categories', [])]]
        return entries

    def search(self, regexp, flags=0):
        """
        Search all entries' content.

        This method searchs the entries' content for a given keyword
        (actually, a regular expression). Right now only the content
        is searched, it would be nice to extend the API to other
        attributes, perhaps? 

        A simple, case-sensitive search for the word "Python"::

            >>> entries = em.search("Python")

        For case-insensitive searching::

            >>> entries = em.search("Python", re.IGNORECASE)
        """
        entries = self.get_entries()
        entries = [e for e in entries if e.get('content') and re.search(regexp, e['content']['content'])]
        return entries

    def _next_id(self):
        # List keys.
        keys = self.db.keys()

        # Get a new key.
        if keys: key = int(max(keys)) + 1
        else: key = 0

        return str(key)

    def close(self):
        self.db.close()
