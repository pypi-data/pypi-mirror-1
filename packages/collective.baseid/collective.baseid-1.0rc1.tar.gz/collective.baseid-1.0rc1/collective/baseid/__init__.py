"""Base id utility

This is the base for utilities that assign ids to objects and 
supports lookups by object and by id.
"""

from persistent import Persistent
from zope.app.container.interfaces import IObjectRemovedEvent
from zope.app.container.interfaces import IObjectAddedEvent
from zope.app.container.contained import Contained
from zope.app.keyreference.interfaces import IKeyReference, NotYet
from zope.component import adapter, getAllUtilitiesRegisteredFor, adapts
from zope.event import notify
from zope.interface import implements
from zope.location.interfaces import ILocation
from zope.security.proxy import removeSecurityProxy
from collective.baseid.interfaces import IIds

class Ids(Persistent, Contained):
    """Utilities based on this class provide a two way mapping 
    between objects and ids.

    IKeyReferences to objects are stored in the indexes.
    """

    implements(IIds)

    def __init__(self):
        """This method must be overriden in the subclass.

        The subclass must provide:
            self.refs
            self.ids
        """

    def __len__(self):
        return len(self.ids)

    def items(self):
        return list(self.refs.items())

    def __iter__(self):
        return self.refs.iterkeys()

    def getObject(self, id):
        return self.refs[id]()

    def queryObject(self, id, default=None):
        r = self.refs.get(id)
        if r is not None:
            return r()
        return default

    def getId(self, ob):
        try:
            key = IKeyReference(ob)
        except (NotYet, TypeError):
            raise KeyError(ob)

        try:
            return self.ids[key]
        except KeyError:
            raise KeyError(ob)

    def queryId(self, ob, default=None):
        try:
            return self.getId(ob)
        except KeyError:
            return default

    def _generateId(self):
        """Generates a new id. Must be provided by subclass.
        """

    def register(self, ob):
        # Note that we'll still need to keep this proxy removal.
        ob = removeSecurityProxy(ob)
        key = IKeyReference(ob)

        if key in self.ids:
            return self.ids[key]
        uid = self._generateId()
        self.refs[uid] = key
        self.ids[key] = uid
        return uid

    def unregister(self, ob):
        # Note that we'll still need to keep this proxy removal.
        ob = removeSecurityProxy(ob)
        key = IKeyReference(ob, None)
        if key is None:
            return

        uid = self.ids[key]
        del self.refs[uid]
        del self.ids[key]

class RemoveIdSubscriber:
    adapts(ILocation, IObjectRemovedEvent)

    def __init__(self, ids_class, id_removed_event):
        self.ids_class = ids_class
        self.id_removed_event = id_removed_event

    def __call__(self, ob, event):
        """A subscriber to ObjectRemovedEvent

        Removes ids registered for the object in all the id utilities.
        """
        utilities = tuple(getAllUtilitiesRegisteredFor(self.ids_class))
        if utilities:
            key = IKeyReference(ob, None)
            # Register only objects that adapt to key reference
            if key is not None:
                # Notify the catalogs that this object is about to be removed.
                notify(self.id_removed_event(ob, event))
                for utility in utilities:
                    try:
                        utility.unregister(key)
                    except KeyError:
                        pass

class AddIdSubscriber:
    adapts(ILocation, IObjectAddedEvent)

    def __init__(self, ids_class, id_added_event):
        self.ids_class = ids_class
        self.id_added_event = id_added_event

    def __call__(self, ob, event):
        """A subscriber to ObjectAddedEvent

        Registers the object added in all id utilities and fires
        an event for the catalogs.
        """
        utilities = tuple(getAllUtilitiesRegisteredFor(self.ids_class))
        if utilities: # assert that there are any utilites
            key = IKeyReference(ob, None)
            # Register only objects that adapt to key reference
            if key is not None:
                for utility in utilities:
                    utility.register(key)
                # Notify the catalogs that this object was added.
                notify(self.id_added_event(ob, event))

