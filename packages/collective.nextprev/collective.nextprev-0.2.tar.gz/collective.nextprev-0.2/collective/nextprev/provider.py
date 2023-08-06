from zope import component

from Products.ATContentTypes import interface
from Products.ATContentTypes.browser import nextprevious

class Provider(nextprevious.ATFolderNextPrevious):
    component.adapts(interface.IATTopic)

    def getNextItem(self, obj):
        view = self.context.restrictedTraverse('nextprev.results')
        results = view()
        idx = view.index('/'.join(obj.getPhysicalPath()))
        if idx is None:
            # If this item isn't in the set then don't render
            # links
            return

        try:
            next = results[idx+1]
        except IndexError:
            # Don't render a next link if there's no next item
            return
        return self.buildNextPreviousItem(next)
        
    def getPreviousItem(self, obj):
        view = self.context.restrictedTraverse('nextprev.results')
        results = view()
        idx = view.index('/'.join(obj.getPhysicalPath()))
        if idx is None:
            # If this item isn't in the set then don't render
            # links
            return
        
        if idx == 0:
            # Don't render a prev link if there's no prev item
            return
        else:
            prev = results[idx-1]
        return self.buildNextPreviousItem(prev)
