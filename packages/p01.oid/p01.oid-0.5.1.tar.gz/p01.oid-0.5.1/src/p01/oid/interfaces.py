##############################################################################
#
# Copyright (c) 2009 Projekt01 GmbH and Contributors.
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
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.schema


class IOIDAware(zope.interface.Interface):
    """OID aware object."""

    oid = zope.schema.Int(
        title=u"OID",
        description=u"The object id",
        default=None,
        readonly=False,
        required=False)


class IOIDManager(zope.interface.Interface):
    """Object id management adapter.
    
    This adapter can adapt any persistent object and offers access to the 
    objects located in the same database where the adapted object is stored.
    """

    def add(obj):
        """Add an object will activate the access to the object by apply an oid
        """

    def remove(obj):
        """Remove an object will deactivate the access to the object by remove
        an oid.
        """

    def validate(oid):
        """Returns True if an object is valid if not return False."""

    def getObject(oid):
        """Returns an object by the given object id.
        
        Raises a KeyError if no object can be found e.g. removed objects.
        """

    def queryObject(oid, default=None):
        """Return an object if availble if not return default."""

    def getOID(obj):
        """Returns an object id for the given object.
        
        Raises a KeyError if no object can be found e.g. non persistent objects.
        """

    def queryOID(obj, default=None):
        """Returns an oid if available or default if not."""



# events
class IOIDEvent(zope.interface.Interface):
    """Generic base interface for events"""

    object = zope.interface.Attribute("The object related to this event")


class IOIDRemovedEvent(IOIDEvent):
    """Before a oid will be removed from the object

    The event get notified BEFORE the oid is removed from the object.
    """


class IOIDAddedEvent(IOIDEvent):
    """After a unique oid get added to the object

    The event get notified AFTER an oid get added to the object.
    """
