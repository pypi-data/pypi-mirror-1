##############################################################################
#
# Copyright (c) 2006-2007 Zope Corporation and Contributors.
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
"""Grok directives.
"""

import grokcore.component

from grokcore.site.components import LocalUtility

from zope import interface
from zope.interface.interfaces import IInterface

import martian
from martian import util
from martian.error import GrokImportError

class local_utility(martian.Directive):
    scope = martian.CLASS
    store = martian.DICT

    def factory(self, factory, provides=None, name=u'',
                setup=None, public=False, name_in_container=None):
        if provides is not None and not IInterface.providedBy(provides):
            raise GrokImportError("You can only pass an interface to the "
                                  "provides argument of %s." % self.name)

        if provides is None:
            provides = grokcore.component.provides.bind().get(factory)

        if provides is None:
            if util.check_subclass(factory, LocalUtility):
                baseInterfaces = interface.implementedBy(LocalUtility)
                utilityInterfaces = interface.implementedBy(factory)
                provides = list(utilityInterfaces - baseInterfaces)

                if len(provides) == 0 and len(list(utilityInterfaces)) > 0:
                    raise GrokImportError(
                        "Cannot determine which interface to use "
                        "for utility registration of %r. "
                        "It implements an interface that is a specialization "
                        "of an interface implemented by grok.LocalUtility. "
                        "Specify the interface by either using grok.provides "
                        "on the utility or passing 'provides' to "
                        "grok.local_utility." % factory, factory)
            else:
                provides = list(interface.implementedBy(factory))

            util.check_implements_one_from_list(provides, factory)
            provides = provides[0]

        if (provides, name) in self.frame.f_locals.get(self.dotted_name(), {}):
            raise GrokImportError(
                "Conflicting local utility registration %r. "
                "Local utilities are registered multiple "
                "times for interface %r and name %r." %
                (factory, provides, name), factory)

        info = LocalUtilityInfo(factory, provides, name, setup, public,
                                name_in_container)
        return (provides, name), info


class LocalUtilityInfo(object):
    """The information about how to register a local utility.

    An instance of this class is created for each `grok.local_utility()`
    in a Grok application's code, to remember how the user wants their
    local utility registered.  Later, whenever the application creates
    new instances of the site or application for which the local utility
    directive was supplied, this block of information is used as the
    parameters to the creation of the local utility which is created
    along with the new site in the Zope database.

    """
    _order = 0

    def __init__(self, factory, provides, name=u'',
                 setup=None, public=False, name_in_container=None):
        self.factory = factory
        self.provides = provides
        self.name = name
        self.setup = setup
        self.public = public
        self.name_in_container = name_in_container

        self.order = LocalUtilityInfo._order
        LocalUtilityInfo._order += 1

    def __cmp__(self, other):
        # LocalUtilityInfos have an inherit sort order by which the
        # registrations take place.
        return cmp(self.order, other.order)
