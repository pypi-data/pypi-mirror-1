from Acquisition import aq_inner
from OFS.SimpleItem import SimpleItem
from zope.component import adapts
from zope.component.interfaces import ComponentLookupError
from zope.interface import Interface, implements
from zope.formlib import form

from plone.app.contentrules.browser.formhelper import AddForm, EditForm 
from plone.contentrules.rule.interfaces import IRuleElementData, IExecutable

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode

from collective.contentrules.runscript.actions.interfaces import IRunScriptAction
from collective.contentrules.runscript import runscriptMessageFactory as _


class ScriptNotFound(Exception):
    def __init__(self, script, obj_url):
        self.script = script
        self.obj_url = obj_url
    
    def __str__(self):
        return 'Could not traverse from "%s" to "%s".' % (self.obj_url, self.script)


class RunScriptAction(SimpleItem):
    """
    The implementation of the action defined in IRunScriptAction
    """
    implements(IRunScriptAction, IRuleElementData)

    script = '' #unicode paths are not allowed
    fail_on_script_not_found = True
    
    element = 'plone.actions.RunScript' #what's this
    
    @property
    def summary(self):
        return _(u'Run script "${script}" on the object.', mapping=dict(script=self.script))


class RunScriptActionExecutor(object):
    """The executor for this action.
    """
    implements(IExecutable)
    adapts(Interface, IRunScriptAction, Interface)

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):

        obj = self.event.object
        event_title = safe_unicode(obj.Title())
        event_url = obj.absolute_url()
        
        try:
            script = obj.unrestrictedTraverse(str(self.element.script))
        except AttributeError:
            if self.element.fail_on_script_not_found:
                raise ScriptNotFound(self.element.script, event_url)
                return False
            else:
                return True
        
        script()
        return True

class RunScriptAddForm(AddForm):
    """
    An add form for the RunScript action
    """
    form_fields = form.FormFields(IRunScriptAction)
    label = _(u"Add RunScript Action")
    description = _(u"An action that can run a script on the object")
    form_name = _(u"Configure element")

    def create(self, data):
        a = RunScriptAction()
        form.applyChanges(a, self.form_fields, data)
        return a

class RunScriptEditForm(EditForm):
    """
    An edit form for the RunScript action
    """
    form_fields = form.FormFields(IRunScriptAction)
    label = _(u"Edit RunScript Action")
    description = _(u"An action that can run a script on the object")
    form_name = _(u"Configure element")
