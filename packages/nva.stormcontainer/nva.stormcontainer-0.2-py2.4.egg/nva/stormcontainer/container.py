from string import split

import transaction

from zope import interface
from zope.component import getUtility
from zope.configuration.name import resolve
from zope.interface import directlyProvides, directlyProvidedBy

from zope.location.interfaces import ILocation
from zope.exceptions.interfaces import UserError
from zope.security.proxy import removeSecurityProxy
from zope.proxy import ProxyBase, sameProxiedObjects

from zope.app.container.contained import Contained
from zope.app.container.contained import NameChooser
from zope.app.container.interfaces import IContained
from zope.app.container.contained import ContainedProxy

from storm.zope.interfaces import IZStorm
from storm.info import get_obj_info

from interfaces import IStormContainer
from nva.stormcontainer.utils import *

def contained(obj, parent=None, name=None):
    """An implementation of zope.app.container.contained.contained
    that doesn't generate events, for internal use.

    Borrowed from SQLOS.
    """
    if (parent is None):
        raise TypeError, 'Must provide a parent'

    if not IContained.providedBy(obj):
        if ILocation.providedBy(obj):
            directlyProvides(obj, IContained, directlyProvidedBy(obj))
        else:
            obj = ContainedProxy(obj)

    oldparent = obj.__parent__
    oldname = obj.__name__

    if (oldparent is None) or not (oldparent is parent
                                   or sameProxiedObjects(oldparent, parent)):
        obj.__parent__ = parent

    if oldname != name and name is not None:
        obj.__name__ = name

    return obj


#class StormNameChooser(NameChooser):
#
#    def checkName(self, name, content):
#        if isinstance(name, str):
#            name = unicode(name)
#        elif not isinstance(name, unicode):
#            raise TypeError("Invalid name type", type(name))
#
#        unproxied = removeSecurityProxy(self.context)
#        if not name.startswith(unproxied._class.__name__+'-'):
#            raise UserError("Invalid name for Storm object")
#        return True
#
#    def chooseName(self, name, obj):
#        # flush the object to make sure it contains an id
#        session = z3c.zalchemy.getSession()
#        session.save(obj)
#        session.flush()
#        return self.context._toStringIdentifier(obj)

class StormContainer(object):
    """ Make a Storm Container for Zope"""
    interface.implements(IStormContainer)

    def __init__(self):
        super(StormContainer,self).__init__()

        _className = ''
        _class = None
        _storeUtilityName = ''

    def setStoreUtilityName(self, name):
        self._storeUtilityName = name

    def getStoreUtilityName(self):
        return self._storeUtilityName

    storeUtilityName = property(getStoreUtilityName, setStoreUtilityName) 

    def setClassName(self, name):
        self._className = name
        self._class=resolve(name)

    def getClassName(self):
        return self._className

    className = property(getClassName, setClassName)

    def keys(self):
        for name, obj in self.items():
            yield name

    def values(self):
        for name, obj in self.items():
            yield obj

    def __iter__(self):
        return iter(self.keys())

    def items(self):
        store = getUtility(IZStorm).get(self.getStoreUtilityName())
        for obj in store.find(self._class):
            name = self._toStringIdentifier(obj)
            yield (name, contained(obj, self, name) )

    def __getitem__(self, name):
        if not isinstance(name, basestring):
            raise KeyError, "%s is not a string" % name
        obj = self._fromStringIdentifier(name)
        if obj is None:
            raise KeyError(name)
        return contained(obj, self, name)

    def get(self, name, default=None):
        try:
            return self[name]
        except KeyError:
            return default
    
    def __contains__(self, name):
        return self.get(name) is not None

    def __len__(self):
        try:
            store = getUtility(IZStorm).get(self.getStoreUtilityName())
	    query = store.find(self._class)
            return query.count()
        except:
            # we don't want an exception in case of database problems
            return 0

    def __delitem__(self, name):
        obj = self._fromStringIdentifier(name) 
        #TODO: better delete objects using a delete adapter
        #      for dependency handling.
        store = getUtility(IZStorm).get(self.getStoreUtilityName())
        store.remove(obj)
        transaction.commit()
        #store.flush()
	    #store.commit()

    def __setitem__(self, name, item):
        store = getUtility(IZStorm).get(self.getStoreUtilityName())
        store.add(item)
        transaction.commit()
        #store.flush()
	    #store.commit()

    def _toStringIdentifier(self, obj):
        store = getUtility(IZStorm).get(self.getStoreUtilityName())
        ident = self._getInstanceKey(obj)
        prefix = "%s-" %self._class.__name__
        return "%s%s" %(prefix, ident)

    def _fromStringIdentifier(self, name):
        prefix = "%s-" %self._class.__name__
        if not str(name).startswith(prefix):
            return None
        store = getUtility(IZStorm).get(self.getStoreUtilityName())
        id = name[ len(str(self._class.__name__)) + 1: ]
        key = decodePKString(id)
        return store.get(self._class, key)

    def _getInstanceKey(self, obj):
        """ Get an unique id form obj """
        obj_info = get_obj_info(obj)
        ids = tuple(obj_info.variables[column].get() for column in obj_info.cls_info.primary_key)
	return encodePKString(ids)
