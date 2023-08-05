from warnings import warn

from zope.interface import implements
from zope.component import getMultiAdapter
from zope.app.container.interfaces import INameChooser

from Acquisition import aq_base, aq_inner
from OFS.SimpleItem import SimpleItem
from Products.Five import BrowserView

from plone.contentrules.engine.interfaces import IRuleStorage

from plone.app.contentrules.browser.interfaces import IRuleAdding
from plone.app.contentrules.browser.interfaces import IRuleElementAdding

class RuleAdding(SimpleItem, BrowserView):
    implements(IRuleAdding)

    def add(self, content):
        """Add the rule to the context
        """
        context = aq_inner(self.context)
        container = aq_base(context)
        
        storage = IRuleStorage(container)
        chooser = INameChooser(storage)
        storage[chooser.chooseName(None, content)] = content
        
    def nextURL(self):
        url = str(getMultiAdapter((self.context, self.request), name=u"absolute_url"))
        return url + "/@@manage-content-rules"

    def renderAddButton(self):
        warn("The renderAddButton method is deprecated, use nameAllowed",
            DeprecationWarning, 2)

    def namesAccepted(self):
        return False

    def nameAllowed(self):
        return False

class RuleElementAdding(SimpleItem, BrowserView):
    implements(IRuleElementAdding)
    
    def add(self, content):
        """Add the rule element to the context rule
        """
        rule = aq_base(aq_inner(self.context))
        rule.elements.append(content)
        
    def nextURL(self):
        url = str(getMultiAdapter((aq_parent(self.context), self.request), name=u"absolute_url"))
        return url + "/@@manage-content-rules"

    def renderAddButton(self):
        warn("The renderAddButton method is deprecated, use nameAllowed",
            DeprecationWarning, 2)

    def namesAccepted(self):
        return False

    def nameAllowed(self):
        return False