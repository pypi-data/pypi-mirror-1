##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Interfaces for Code Interpreters

$Id: interfaces.py 26892 2004-08-04 05:10:21Z pruggera $
"""
__docformat__ = 'restructuredtext'

from zope.interface import Interface

class IInterpreter(Interface):

    def evaluate(code, globals):
        """Evaluate the code given the global variables."""

    def evaluateRawCode(code, globals):
        """Evaluate the code given the global variables.

        However, this method does a little bit more. Sometimes (or in our case
        often) code might come from an uncontrolled environment, like a page
        template and is not properly formatted, i.e. indentation, so that some
        cleanup is necessary. This method does the cleanup before evaluating
        the code.
        """
