from zope.interface import Interface, Attribute, implements

class IIdsQuery(Interface):

    def getObject(uuid):
        """Return an object by its id.
        """

    def getId(ob):
        """Get an id of an object.
        """

    def queryObject(uuid, default=None):
        """Return an object by its id.

        Return the default if the id isn't registered.
        """

    def queryId(ob, default=None):
        """Get an id of an object.

        Return the default if the object isn't registered.
        """

    def __iter__():
        """Return an iteration on the ids.
        """

class IIdsSet(Interface):

    def register(ob):
        """Register an object and returns an id generated for it.

        The object *must* be adaptable to IKeyReference.

        If the object is already registered, its id is returned anyway.
        """

    def unregister(ob):
        """Remove the object from the indexes.

        KeyError is raised if o is not registered previously.
        """

class IIdsManage(Interface):

    def __len__():
        """Return the number of objects indexed.
        """

    def items():
        """Return a list of (id, object) pairs.
        """

class IIds(IIdsSet, IIdsQuery, IIdsManage):
    """A utility that assigns ids to objects.

    Supports  querying object by id and id by object.
    """

class IIdRemovedEvent(Interface):
    """An id will be removed.

    The event is published before the id is removed from the utility so that
    the indexing objects can unindex the object.
    """

    object = Attribute("The object being removed")

    original_event = Attribute("The IObjectRemovedEvent related to this event")

class IdRemovedEvent:
    """The event which is published before the id is removed from
    the utility so that the catalogs can unindex the object.
    """

    implements(IIdRemovedEvent)

    def __init__(self, object, event):
        self.object = object
        self.original_event = event

class IIdAddedEvent(Interface):
    """An id has been added.

    The event gets sent when an object is registered in an id utility.
    """

    object =  Attribute("The object being added")

    original_event = Attribute("The ObjectAddedEvent related to this event")

class IdAddedEvent:
    """The event which gets sent when an object is registered in an id
    utility."""

    implements(IIdAddedEvent)

    def __init__(self, object, event):
        self.object = object
        self.original_event = event

class IId(Interface):
    """"An interface for adapting an object to get its id.
    """

    def id():
        """This object's id.
        """