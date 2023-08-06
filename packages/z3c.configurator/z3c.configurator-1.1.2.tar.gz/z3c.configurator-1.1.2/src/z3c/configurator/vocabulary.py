##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Vocabularies

$Id: vocabulary.py 72645 2007-02-16 09:45:11Z dobe $
"""
__docformat__ = "reStructuredText"
from zope import component
from zope.schema import vocabulary
import interfaces

def pluginNamesVocabulary(context):
    """a vocabulary that returns all names of registered configuration
    plugins"""
    terms = []
    plugins = dict(component.getAdapters(
        (context,), interfaces.IConfigurationPlugin))
    return vocabulary.SimpleVocabulary.fromValues(sorted(plugins.keys()))
