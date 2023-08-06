from plone.memoize import instance
from plone.app.layout.nextprevious import view
from plone.app.layout.nextprevious import interfaces 

from Acquisition import aq_inner, aq_parent

class Provider(object):
    """Retrieve the provider from the cookie if present"""

    @instance.memoize
    def _provider(self):
        if 'nextprev.collection' in self.context.REQUEST:
            container = self.context.restrictedTraverse(
                self.context.REQUEST['nextprev.collection'])
        else:
            container = aq_parent(aq_inner(self.context))
        return interfaces.INextPreviousProvider(container, None)

class NextPreviousView(Provider, view.NextPreviousView):
    pass

class NextPreviousViewlet(Provider, view.NextPreviousViewlet):
    pass

class NextPreviousLinksViewlet(Provider,
                               view.NextPreviousLinksViewlet):
    pass
