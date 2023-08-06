from grokcore.view import View
from grokcore.component import context, name
from plone.introspector.interfaces import IWorkflowInfo

class Workflow(View):
    name('index.html')
    context(IWorkflowInfo)
    