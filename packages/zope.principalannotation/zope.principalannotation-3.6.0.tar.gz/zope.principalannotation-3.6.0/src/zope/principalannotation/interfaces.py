##############################################################################
#
# Copyright (c) 2009 Zope Corporation and Contributors.
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
"""Utility for storing `IAnnotations` for principals.

$Id: interfaces.py 97692 2009-03-09 14:09:35Z nadako $
"""
__docformat__ = 'restructuredtext'

from zope.interface import Interface


class IPrincipalAnnotationUtility(Interface):
    """Stores `IAnnotations` for `IPrinicipals`."""

    def getAnnotations(principal):
        """Return object implementing `IAnnotations` for the given
        `IPrinicipal`.

        If there is no `IAnnotations` it will be created and then returned.
        """

    def getAnnotationsById(principalId):
        """Return object implementing `IAnnotations` for the given
        `prinicipalId`.

        If there is no `IAnnotations` it will be created and then returned.
        """

    def hasAnnotations(principal):
        """Return boolean indicating if given `IPrincipal` has
        `IAnnotations`."""
