import grokcore.view as grok

from zope import interface
from zope import component
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.traversing.interfaces import ITraversable
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.browser import applySkin
from zope.location.location import locate
from Products.Five import BrowserView
from zope.introspector.interfaces import IInfos

import Acquisition
from ZPublisher.BaseRequest import DefaultPublishTraverse, IPublishTraverse
from OFS.interfaces import IApplication

from plone.introspector.interfaces import ICodeIntrospector
from zope.introspector.code import Package


class IntrospectorLayer(IDefaultBrowserLayer):
    """A basic layer for all introspection stuff.
    """
    pass

class IntrospectorNamespace(object):
    interface.implements(ITraversable)
    component.adapts(interface.Interface, IBrowserRequest)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        applySkin(self.request, IntrospectorLayer)
        
    def traverse(self, name, ignore):
        # We currently don't have any names in this namespace.
        return self.context

class CodeIntrospector(Acquisition.Explicit):
    
    interface.implements(ICodeIntrospector)
    
    def __init__(self, id):
        self.id = id
    
class ApplicationTraverser(grok.MultiAdapter, DefaultPublishTraverse):
    grok.adapts(IApplication, IBrowserRequest)
    
    def publishTraverse(self, request, name):
        if name == '+code':
            return CodeIntrospector(name).__of__(self.context)
            
        return DefaultPublishTraverse.publishTraverse(self, request, name)

class Zope2Package(Acquisition.Explicit, Package):
    
    def __init__(self, id):
        Package.__init__(self, id)
        self.id = id

class BrowserTraverser(grok.MultiAdapter, DefaultPublishTraverse):
    grok.adapts(ICodeIntrospector, IBrowserRequest)
    
    def publishTraverse(self, request, name):
        if '.' in name:
            return None
        try:
            return Zope2Package(name).__of__(self.context)
        except ImportError:
            return None
                
    
class InfoView(BrowserView):
    
    def getInfos(self):
        return IInfos(Acquisition.aq_base(self.context)).infos()

