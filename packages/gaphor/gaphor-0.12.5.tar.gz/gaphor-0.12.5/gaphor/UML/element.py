#!/usr/bin/env python
# vim:sw=4:et
"""
Base class for UML model elements.
"""

__all__ = [ 'Element' ]

import types, mutex
from zope import component
from event import ElementDeleteEvent
from gaphor.misc import uniqueid
from properties import umlproperty, association

class Element(object):
    """
    Base class for UML data classes.
    """

    def __init__(self, id=None, factory=None):
        self._id = id or uniqueid.generate_id()
        # The factory this element belongs to.
        self._factory = factory
        self._observers = dict()
        self.__in_unlink = mutex.mutex()

    id = property(lambda self: self._id, doc='Id')

    factory = property(lambda self: self._factory,
                       doc="The factory that created this element")

    def umlproperties(self):
        """
        Iterate over all UML properties 
        """
        umlprop = umlproperty
        class_ = type(self)
        for propname in dir(class_):
            if not propname.startswith('_'):
                prop = getattr(class_, propname)
                if isinstance(prop, umlprop):
                    yield prop

    # TODO: move save/load code to adapters
    def save(self, save_func):
        """
        Save the state by calling save_func(name, value).
        """
        for prop in self.umlproperties():
            prop.save(self, save_func)

    def load(self, name, value):
        """
        Loads value in name. Make sure that for every load postload()
        should be called.
        """
        try:
            prop = getattr(type(self), name)
        except AttributeError, e:
            raise AttributeError, "'%s' has no property '%s'" % \
                                        (type(self).__name__, name)
        else:
            prop.load(self, value)

    def postload(self):
        """
        Fix up the odds and ends.
        """
        for prop in self.umlproperties():
            prop.postload(self)

    def unlink(self):
        """
        Unlink the element. All the elements references are destroyed.
        """
        # Uses a mutex to make sure it is not called recursively
        if self.__in_unlink.testandset():
            component.handle(ElementDeleteEvent(self._factory, self))
            try:
                for prop in self.umlproperties():
                    prop.unlink(self)
                self.notify('__unlink__')
            finally:
                self.__in_unlink.unlock()

    def connect(self, names, callback, *data):
        """
        Attach 'callback' to a list of names. Names may also be a string.
        A name is the name of a property of the object or '__unlink__'.

        Obsolete. Connect to the appropriate change event (see event.py)
        """
        #log.debug('Element.connect(%s, %s, %s)' % (names, callback, data))
        if type(names) is types.StringType:
            names = (names,)
        cb = (callback,) + data
        for name in names:
            self._observers.setdefault(name, []).append(cb)

    def disconnect(self, callback, *data):
        """
        Detach a callback identified by it's data.

        Obsolete. Connect to the appropriate change event (see event.py)
        """
        cb = (callback,) + data
        for values in self._observers.values():
            # Remove all occurences of 'cb' from values
            # (if none is found ValueError is raised).
            try:
                while True:
                    values.remove(cb)
            except ValueError:
                pass

    def notify(self, name, pspec=None):
        """
        Send notification to attached callbacks that a property
        has changed.

        Obsolete. Connect to the appropriate change event (see event.py)
        """
        cb_list = self._observers.get(name, ())
        #log.debug('Element.notify: %s' % cb_list)
        if not pspec:
            try:
                pspec = getattr(type(self), name)
            except AttributeError:
                pspec = name
        
        # Use a copy of the list to ensure all items are notified
        for cb_data in list(cb_list):
            try:
                apply(cb_data[0], (self, pspec) + cb_data[1:])
            except Exception, e:
                log.error('failed notification for %s' % cb_data[0], e)

    # OCL methods: (from SMW by Ivan Porres (http://www.abo.fi/~iporres/smw))

    def isKindOf(self, class_):
        """
        Returns true if the object is an instance of class_.
        """
        return isinstance(self, class_)

    def isTypeOf(self, other):
        """
        Returns true if the object is of the same type as other.
        """
        return type(self) == type(other)


try:
    import psyco
except ImportError:
    pass
else:
    psyco.bind(Element)

