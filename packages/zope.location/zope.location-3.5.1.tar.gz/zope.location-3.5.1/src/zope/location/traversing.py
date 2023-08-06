##############################################################################
#
# Copyright (c) 2003-2009 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Classes to support implenting IContained

$Id: traversing.py 95961 2009-02-02 12:16:54Z nadako $
"""
__docformat__ = 'restructuredtext'

import zope.component
import zope.interface
from zope.location.interfaces import ILocationInfo
from zope.location.interfaces import IRoot, ITraverser
from zope.location.interfaces import ILocation, ISite
from zope.location.location import Location


class LocationPhysicallyLocatable(object):
    """Provide location information for location objects
    
    >>> from zope.interface.verify import verifyObject
    >>> info = LocationPhysicallyLocatable(Location())
    >>> verifyObject(ILocationInfo, info)
    True
    
    """

    zope.component.adapts(ILocation)
    zope.interface.implements(ILocationInfo)

    def __init__(self, context):
        self.context = context

    def getRoot(self):
        """Get the root location for a location.

        See ILocationInfo

        The root location is a location that contains the given
        location and that implements IContainmentRoot.

        >>> root = Location()
        >>> zope.interface.directlyProvides(root, IRoot)
        >>> LocationPhysicallyLocatable(root).getRoot() is root
        True

        >>> o1 = Location(); o1.__parent__ = root
        >>> LocationPhysicallyLocatable(o1).getRoot() is root
        True

        >>> o2 = Location(); o2.__parent__ = o1
        >>> LocationPhysicallyLocatable(o2).getRoot() is root
        True

        We'll get a TypeError if we try to get the location fo a
        rootless object:

        >>> o1.__parent__ = None
        >>> LocationPhysicallyLocatable(o1).getRoot()
        Traceback (most recent call last):
        ...
        TypeError: Not enough context to determine location root
        >>> LocationPhysicallyLocatable(o2).getRoot()
        Traceback (most recent call last):
        ...
        TypeError: Not enough context to determine location root

        If we screw up and create a location cycle, it will be caught:

        >>> o1.__parent__ = o2
        >>> LocationPhysicallyLocatable(o1).getRoot()
        Traceback (most recent call last):
        ...
        TypeError: Maximum location depth exceeded, """ \
                """probably due to a a location cycle.
        """
        context = self.context
        max = 9999
        while context is not None:
            if IRoot.providedBy(context):
                return context
            context = context.__parent__
            max -= 1
            if max < 1:
                raise TypeError("Maximum location depth exceeded, "
                                "probably due to a a location cycle.")

        raise TypeError("Not enough context to determine location root")

    def getPath(self):
        """Get the path of a location.

        See ILocationInfo

        This is an "absolute path", rooted at a root object.

        >>> root = Location()
        >>> zope.interface.directlyProvides(root, IRoot)
        >>> LocationPhysicallyLocatable(root).getPath()
        u'/'

        >>> o1 = Location(); o1.__parent__ = root; o1.__name__ = 'o1'
        >>> LocationPhysicallyLocatable(o1).getPath()
        u'/o1'

        >>> o2 = Location(); o2.__parent__ = o1; o2.__name__ = u'o2'
        >>> LocationPhysicallyLocatable(o2).getPath()
        u'/o1/o2'

        It is an error to get the path of a rootless location:

        >>> o1.__parent__ = None
        >>> LocationPhysicallyLocatable(o1).getPath()
        Traceback (most recent call last):
        ...
        TypeError: Not enough context to determine location root

        >>> LocationPhysicallyLocatable(o2).getPath()
        Traceback (most recent call last):
        ...
        TypeError: Not enough context to determine location root

        If we screw up and create a location cycle, it will be caught:

        >>> o1.__parent__ = o2
        >>> LocationPhysicallyLocatable(o1).getPath()
        Traceback (most recent call last):
        ...
        TypeError: Maximum location depth exceeded, """ \
                """probably due to a a location cycle.

        """

        path = []
        context = self.context
        max = 9999
        while context is not None:
            if IRoot.providedBy(context):
                if path:
                    path.append('')
                    path.reverse()
                    return u'/'.join(path)
                else:
                    return u'/'
            path.append(context.__name__)
            context = context.__parent__
            max -= 1
            if max < 1:
                raise TypeError("Maximum location depth exceeded, "
                                "probably due to a a location cycle.")

        raise TypeError("Not enough context to determine location root")

    def getParents(self):
        """Returns a list starting with the object's parent followed by
        each of its parents.

        Raises a TypeError if the object is not connected to a containment
        root.

        >>> root = Location()
        >>> zope.interface.directlyProvides(root, IRoot)
        >>> LocationPhysicallyLocatable(root).getParents()
        []

        >>> o1 = Location()
        >>> o2 = Location()
        >>> o1.__parent__ = root
        >>> o2.__parent__ = o1
        >>> LocationPhysicallyLocatable(o2).getParents() == [o1, root]
        True
        
        If the last parent is not an IRoot object, TypeError will be
        raised as statet before.
        
        >>> zope.interface.noLongerProvides(root, IRoot)
        >>> LocationPhysicallyLocatable(o2).getParents()
        Traceback (most recent call last):
        ...
        TypeError: Not enough context information to get all parents

        """
        # XXX Merge this implementation with getPath. This was refactored
        # from zope.traversing.
        if IRoot.providedBy(self.context):
            return []

        parents = []
        w = self.context
        while 1:
            w = w.__parent__
            if w is None:
                break
            parents.append(w)

        if parents and IRoot.providedBy(parents[-1]):
            return parents

        raise TypeError("Not enough context information to get all parents")

    def getName(self):
        """Get a location name

        See ILocationInfo

        >>> o1 = Location(); o1.__name__ = u'o1'
        >>> LocationPhysicallyLocatable(o1).getName()
        u'o1'

        >>> root = Location()
        >>> zope.interface.directlyProvides(root, IRoot)
        >>> LocationPhysicallyLocatable(root).getName()
        u''

        """
        if IRoot.providedBy(self.context):
            return u''
        return self.context.__name__

    def getNearestSite(self):
        """return the nearest site, see ILocationInfo

        >>> o1 = Location()
        >>> o1.__name__ = 'o1'
        >>> LocationPhysicallyLocatable(o1).getNearestSite()
        Traceback (most recent call last):
        ...
        TypeError: Not enough context information to get all parents

        >>> root = Location()
        >>> zope.interface.directlyProvides(root, IRoot)
        >>> o1 = Location()
        >>> o1.__name__ = 'o1'
        >>> o1.__parent__ = root
        >>> LocationPhysicallyLocatable(o1).getNearestSite() is root
        True
        
        >>> zope.interface.directlyProvides(o1, ISite)
        >>> LocationPhysicallyLocatable(o1).getNearestSite() is o1
        True
        
        >>> o2 = Location()
        >>> o2.__parent__ = o1
        >>> LocationPhysicallyLocatable(o2).getNearestSite() is o1
        True
        
        """
        if ISite.providedBy(self.context):
            return self.context
        for parent in self.getParents():
            if ISite.providedBy(parent):
                return parent
        return self.getRoot()
