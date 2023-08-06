from cubicweb.entities import AnyEntity, fetch_config
from cubicweb.interfaces import ICalendarable

class Book(AnyEntity):
    __regid__ = 'Book'
    __implements__ = AnyEntity.__implements__ + (ICalendarable,)

    fetch_attrs, fetch_order = fetch_config(['title', 'isbn13', 'isbn10', 'pages'])

    # ICalendarable
    @property
    def start(self):
        return self.publish_date
    stop = start

class Collection(AnyEntity):
    __regid__ = 'Collection'

    fetch_attrs, fetch_order = fetch_config(['name'])

class Editor(AnyEntity):
    __regid__ = 'Editor'

    fetch_attrs, fetch_order = fetch_config(['name'])

