from plone.memoize import view

from Products.ATContentTypes.browser import nextprevious

def lazyIndex(seq, obj):
    rid = obj.portal_catalog.getrid('/'.join(obj.getPhysicalPath()))
    idx = 0
    for brain in seq:
        if brain.getRID() == rid:
            return idx
        idx += 1
    raise ValueError('%r not in %r' % (obj, seq))

class ResultsView(object):

    @view.memoize
    def __call__(self):
        """Return the collection results with saved form submission"""

        if 'nextprev.form' in self.request:
            # Make a fake request with the saved query string and use the
            # publisher code to reconstitute the values
            fake_req = self.request.__class__(
                stdin=None,
                environ={'QUERY_STRING':
                         self.context.REQUEST['nextprev.form'],
                         'SERVER_NAME': '', 'SERVER_PORT': ''},
                response=None)
            fake_req.processInputs()
            kw = fake_req.form
        else:
            kw = {}

        return self.context.queryCatalog(**kw)

class Provider(nextprevious.ATFolderNextPrevious):

    def getNextItem(self, obj):
        if 'nextprev.collection' in self.context.REQUEST:
            results = self.context.restrictedTraverse(
                self.context.REQUEST['nextprev.collection']
                + '/nextprev.results')()
            idx = lazyIndex(results, obj)
            try:
                next = results[idx+1]
            except IndexError:
                return
            return self.buildNextPreviousItem(next)
        return super(Provider, self).getNextItem(obj)
        
    def getPreviousItem(self, obj):
        if 'nextprev.collection' in self.context.REQUEST:
            results = self.context.restrictedTraverse(
                self.context.REQUEST['nextprev.collection']
                + '/nextprev.results')()
            idx = lazyIndex(results, obj)
            if idx == 0:
                return
            else:
                prev = results[idx-1]
            return self.buildNextPreviousItem(prev)
        return super(Provider, self).getPreviousItem(obj)
