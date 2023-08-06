from zope.introspector.interfaces import IInfo
from zope.interface import Interface

class IWorkflowInfo(IInfo):
    """The representation of an object that has workflow information attached to it.
    """
    def getWorkflowHistory():
        """Get the current workflow state.
        
        Returns a string with the current workflow state.
        """

class ICodeIntrospector(Interface):
    """An introspector for packages, classes and other code.
    """