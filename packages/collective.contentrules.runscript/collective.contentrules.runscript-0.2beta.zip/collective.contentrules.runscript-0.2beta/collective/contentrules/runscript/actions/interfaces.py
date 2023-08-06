from zope.interface import Interface
from zope import schema

from collective.contentrules.runscript import runscriptMessageFactory as _

class IRunScriptAction(Interface):
    """Definition of the configuration available for a runscript action"""
    
    script = schema.TextLine(
        title=_(u"Script"),
        description=_(u"The script"),
        required=True
    )
                              
    fail_on_script_not_found = schema.Bool(
        title=_("Fail on script not found"),
        description=_("Raise exception if script can't be traversed to from object."),
        required=False
    )
    
    restricted_traverse = schema.Bool(
        title=_("Perform permission verification on script"),
        description=_("If checked, tries to do a restricted traversal to the script."),
        required=False
    )