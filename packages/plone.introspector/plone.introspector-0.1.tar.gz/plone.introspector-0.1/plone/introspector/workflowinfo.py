##############################################################################
#
# Copyright (c) 2007-2008 Zope Corporation and Contributors.
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
"""
from zope.interface import Interface
from plone.introspector.interfaces import IWorkflowInfo
from Products.CMFCore.utils import getToolByName
import grokcore.component as grok

class WorkflowInfo(grok.Adapter):
    """Determine views for contexts.
    """
    grok.implements(IWorkflowInfo)
    grok.context(Interface)
    grok.name('workflow')
    
    def getWorkflowHistory(self):
        """Get the current workflow state.
        
        Returns a string with the current workflow state.
        """
        try:
            return self.context.workflow_history
        except AttributeError:
            return None
            