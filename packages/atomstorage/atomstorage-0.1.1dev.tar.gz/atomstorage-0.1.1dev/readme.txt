This is a simple API for storing and retrieving (Atom) entries. The
storage is based on an "entry manager", referencing the storage
system. For example, the reference backend uses the `shelve` Python
module. It is initialized in the following way::

    >>> from atomstorage import EntryManager
    >>> em = EntryManger('shelve:///path/to/file')

The `em` object defines methods to handle the stored entries. But
first we need to know how an entry looks like. An entry is a dict
representing an Atom feed in a JSON-like syntax::

    entry = { # Required elements.
              'id'         : 'http://example.com/1',
              'title'      : 'Man bites dog',
              'updated'    : <type 'datetime.datetime'>,

              # Recommended elements.
              'author'     : [person1, person2, ... ],
              'content'    : content,
              'link'       : link,
              'summary'    : 'Some text.',

              # Optional elements.
              'category'   : [category1, category2, ... ],
              'contributor': [person1, person2, ... ],
              'published'  : <type 'datetime.datetime'>,
              'source'     : feed,
              'rights'     : '(c) 2006 Jone Doe', }

Please note that some attributes ('updated' and 'published') are
stored as `datetime.datetime` objects.

A `person` is also a dict construct::

    person = { 'name' : 'John Doe',
               'uri'  : 'http://example.com',
               'email': 'jdoe@example.com', }

The 'name' attribute is required; 'uri' and 'email' are optional.

The `content` attribute is probably the most important one::

    content = { 'type'   : 'html',
                'src'    : 'http://example.com/1',
                'content': '<p>This is the post content.</p>', }

Usually, 'type' will be either 'text', 'html' or 'xhtml', and the
content will be stored in the 'content' attribute properly escaped
(http://www.atomenabled.org/developers/syndication/#text). If the
content is located elsewhere, 'src' should point to the URI where
the resource is located; in this case, 'type' should specify the
media type of the content.

Another construct is the `link`::

    link = { 'href'    : 'http://example.com/1',    
             'rel'     : 'self',
             'type'    : 'application/atom+xml',
             'hreflang': 'en',
             'title'   : 'This post',
             'length'  : 1024, }

Only 'href' is required; other attributes are otional.

For `category`, this is the structure::

    category = { 'term'  : 'technology',
                 'scheme': 'http://example.com/categories',
                 'label' : 'Tech and stuff', }

Only 'term' is required.

The 'source' attribute should point to a source `feed`, defined by
this contruct::
    
    feed = { 'id'         : 'http://example.com',
             'title'      : 'Example, Inc.',
             'updated'    : <type 'datetime.datetime'>,
             'author'     : [person],
             'link'       : link,
             'category'   : [category],
             'contributor': [person],
             'generator'  : generator,
             'icon'       : '/icon.jpg',
             'logo'       : '/logo.jpg',
             'rights'     : '(c) 2006 John Doe',
             'subtitle'   : 'Witty phrase', }

These should be copied from the source feed. Finally, the feed
itself contains a `generator` construct::

    generator = { 'uri'      : 'http://example.com/generator',
                  'version'  : '1.0',
                  'generator': 'Example generator', }

Now that you know how to create a entry, here's how you add it to
the entry manager::

    >>> entry = {'title': "A simple entry"}
    >>> entry = em.create_entry(entry)
    >>> print entry['id']
    0

Note that if the id is automatically created if not specified. To
delete this entry::

    >>> em.delete_entry(entry['id'])

To list all entries, ordered by update time, last to first::

    >>> entries = em.get_entries()

The last 10 entries, sorted::

    >>> entries = em.get_entries(10)

A specific entry::

    >>> entry = em.get_entry(id)

All entries by date::

    >>> entries = em.get_entries_by_date(2006)
    >>> entries = em.get_entries_by_date(2006, 8)
    >>> entries = em.get_entries_by_date(2006, 8, 15)

Or by category (case-insensitive)::

    >>> entries = em.get_entries_by_category("python")
    >>> entries = em.get_entries_by_category("PyThOn")

To search the entries' content::

    >>> entries = em.search("python")
    >>> entries = em.search("python", re.IGNORECASE)
    >>> entries = em.search("(python|javascript)")

Finally, to update an entry::

    >>> entry = em.get_entries(1)[0]
    >>> entry['title'] = "New Title"
    >>> em.update_entry(entry)
