from OFS.SimpleItem import SimpleItem
from persistent import Persistent 

from zope.interface import implements, Interface
from zope.component import adapts
from zope.formlib import form
from zope import schema

from plone.contentrules.rule.interfaces import IExecutable, IRuleActionData
from plone.contentrules.rule.rule import Node

from plone.app.contentrules.browser.formhelper import AddForm, EditForm 

import transaction
from Acquisition import aq_inner, aq_parent
from ZODB.POSException import ConflictError
from Products.CMFCore.utils import getToolByName

class ICopyAction(IRuleActionData):
    """Interface for the configurable aspects of a move action.
    
    This is also used to create add and edit forms, below.
    """
    
    # XXX: This is bad UI and not VHM-friendly
    target_folder = schema.TextLine(title=u"Target folder",
                                    description=u"As a path relative to the portal root",
                                    required=True)
         
class CopyAction(SimpleItem):
    """The actual persistent implementation of the action element.
    """
    implements(ICopyAction)
    
    target_folder = ''
    
class CopyActionExecutor(object):
    """The executor for this action.
    """
    implements(IExecutable)
    adapts(Interface, ICopyAction, Interface)
         
    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        portal_url = getToolByName(self.context, 'portal_url', None)
        if portal_url is None:
            return False
        
        obj = self.event.object
        parent = aq_parent(aq_inner(obj))
        
        path = self.element.target_folder
        if len(path) > 1 and path[0] == '/':
            path = path[1:]
        target = portal_url.getPortalObject().unrestrictedTraverse(str(path), None)
    
        if target is None:
            return False
        
        transaction.savepoint()
        
        try:
            cpy = parent.manage_copyObjects((obj.getId(),))
        except ConflictError, e:
            raise e
        except:
            return False
            
        transaction.savepoint()
        
        try:
            target.manage_pasteObjects(cpy)
        except ConflictError, e:
            raise e
        except:
            return False
        
        return True 
        
class CopyAddForm(AddForm):
    """An add form for move-to-folder actions.
    """
    form_fields = form.FormFields(ICopyAction)
    
    def create(self, data):
        a = CopyAction()
        a.target_folder = data.get('target_folder')
        return Node('plone.actions.Copy', a)

class CopyEditForm(EditForm):
    """An edit form for copy rule actions.
    
    Formlib does all the magic here.
    """
    form_fields = form.FormFields(ICopyAction)