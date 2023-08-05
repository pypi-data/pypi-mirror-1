from warnings import warn

from zope.interface import implements
from zope.component import getMultiAdapter, getUtility
from zope.app.container.interfaces import INameChooser

from Acquisition import aq_base, aq_inner, aq_parent, Implicit
from Products.Five import BrowserView

from plone.contentrules.engine.interfaces import IRuleStorage

from plone.app.contentrules.browser.interfaces import IRuleAdding
from plone.app.contentrules.browser.interfaces import IRuleConditionAdding
from plone.app.contentrules.browser.interfaces import IRuleActionAdding

class RuleAdding(Implicit, BrowserView):

    implements(IRuleAdding)

    context = None
    request = None
    contentName = None

    def __init__(self, context, request):
        super(RuleAdding, self).__init__(context, request)

    def add(self, content):
        """Add the rule to the context
        """
        storage = getUtility(IRuleStorage)
        chooser = INameChooser(storage)
        storage[chooser.chooseName(None, content)] = content

    def nextURL(self):
        url = str(getMultiAdapter((self.context, self.request), name=u"absolute_url"))
        return url + "/@@rules-controlpanel"

    def renderAddButton(self):
        warn("The renderAddButton method is deprecated, use nameAllowed",
            DeprecationWarning, 2)

    def namesAccepted(self):
        return False

    def nameAllowed(self):
        return False

    def isSingleMenuItem(self):
        return False

    def addingInfo(self):
        return []

    def hasCustomAddView(self):
        return None


class RuleElementAdding(Implicit, BrowserView):

    context = None
    request = None
    contentName = None

    def __init__(self, context, request):
        super(RuleElementAdding, self).__init__(context, request)

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

    def isSingleMenuItem(self):
        return False

    def addingInfo(self):
        return []

    def hasCustomAddView(self):
        return None


class RuleConditionAdding(RuleElementAdding):

    implements(IRuleConditionAdding)

    def add(self, content):
        """Add the rule element to the context rule
        """
        rule = aq_base(aq_inner(self.context))
        rule.conditions.append(content)


class RuleActionAdding(RuleElementAdding):

    implements(IRuleActionAdding)

    def add(self, content):
        """Add the rule element to the context rule
        """
        rule = aq_base(aq_inner(self.context))
        rule.actions.append(content)
