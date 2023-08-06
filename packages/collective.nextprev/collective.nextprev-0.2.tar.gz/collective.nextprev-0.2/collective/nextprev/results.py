from plone.memoize import view

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

    @view.memoize
    def index(self, path):
        """Return the of the item within the results."""
        rid = self.context.portal_catalog.getrid(path)
        idx = 0
        for brain in self():
            if brain.getRID() == rid:
                return idx
            idx += 1
