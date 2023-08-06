##############################################################################
#
# Copyright (c) 2008 Projekt01 GmbH and Contributors.
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

import os

import zope.interface
import zope.configuration.fields
from zope.publisher.interfaces.browser import IBrowserPublication
from zope.publisher.interfaces.browser import IBrowserRequest


class IAcceleratorBrowserPublication(IBrowserPublication):
    """Accelerator browser publication."""


class IAcceleratorBrowserRequest(IBrowserRequest):
    """Request supporting direct file upload to file system."""

    def getTMPFileFactory():
        """Return a ITMPFile instance observed by a transaction."""
