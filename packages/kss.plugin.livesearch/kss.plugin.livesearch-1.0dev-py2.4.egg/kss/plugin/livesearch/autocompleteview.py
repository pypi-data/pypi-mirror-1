"""\
Support of keyword autocomplete widget for Plone / Archetypes
"""

from livesearchview import LiveSearchView
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.CMFCore.utils import getToolByName

class AutoCompleteView(LiveSearchView):

    # No need to send back a zero result set.
    emptyResult = False

    def update(self, q, limit=10):
        # Acqire additional parameters.
        fieldname = self.request.fieldname
        
        cat = getToolByName(self.context, 'portal_catalog')
        words = cat.uniqueValuesFor('Subject')
        # result is sorted already at this point.

        term = q.strip()

        self.results = results = []
        
        if not term:
            # Just do nothing if we just typed the comma.
            return

        for w in words:
            if w.startswith(term):
                if len(results) < limit:
                    results.append(w)
                else:
                    # we are over the limit already, we don't add that
                    # but we swith on the "more" link if there is one.
                    self.showMore = True
                    break

    renderHtml = ZopeTwoPageTemplateFile('autocompleteview.pt')
