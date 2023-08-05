from persistent import Persistent 
from OFS.SimpleItem import SimpleItem

from zope.interface import implements, Interface
from zope.component import adapts
from zope.formlib import form
from zope import schema
from zope.app.component.hooks import getSite

from zope.component.interfaces import IObjectEvent

from plone.contentrules.rule.interfaces import IExecutable, IRuleElementData

from plone.app.contentrules.browser.formhelper import AddForm, EditForm 

from Acquisition import aq_inner

from collective.keywordcondition import MessageFactory as _

class IKeywordCondition(Interface):
    """Interface for the configurable aspects of a keyword condition.
    
    This is also used to create add and edit forms, below.
    """
    
    keywords = schema.Tuple(title=_(u"Keywords"),
                              description=_(u"The keywords to check for."),
                              required=True,
                              value_type=schema.TextLine(title=_(u"Keyword")))
         
class KeywordCondition(SimpleItem):
    """The actual persistent implementation of the keyword condition element.
    
    Note that we must mix in SimpleItem to keep Zope 2 security happy.
    """
    implements(IKeywordCondition, IRuleElementData)
    
    keywords = []
    element = "collective.keywordcondition.Keyword"
    
    @property
    def summary(self):
        return _(u"Keywords contains: ${names}", mapping=dict(names=", ".join(self.keywords)))

class KeywordConditionExecutor(object):
    """The executor for this condition.
    
    This is registered as an adapter in configure.zcml
    """
    implements(IExecutable)
    adapts(Interface, IKeywordCondition, IObjectEvent)
         
    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        context = aq_inner(self.event.object)
        keywords = frozenset()
        try:
            keywords = frozenset(context.Subject())
        except (AttributeError, TypeError,):
            # The object doesn't have a Subject method
            return False
        return (len(keywords.intersection(self.element.keywords)) > 0)
        
class KeywordAddForm(AddForm):
    """An add form for portal type conditions.
    """
    form_fields = form.FormFields(IKeywordCondition)
    label = _(u"Add Keyword Condition")
    description = _(u"A keyword condition makes the rule apply only to content with certain keywords.")
    form_name = _(u"Configure element")
    
    def create(self, data):
        c = KeywordCondition()
        form.applyChanges(c, self.form_fields, data)
        return c

class KeywordEditForm(EditForm):
    """An edit form for portal type conditions
    """
    form_fields = form.FormFields(IKeywordCondition)
    label = _(u"Edit Keyword Condition")
    description = _(u"A keyword condition makes the rule apply only to content with certain keywords.")
    form_name = _(u"Configure element")
