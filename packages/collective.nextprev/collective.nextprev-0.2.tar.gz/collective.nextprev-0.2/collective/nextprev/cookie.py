import Acquisition
from ZTUtils import Zope

class SetCookieView(object):

    def render(self):
        if self.context.getNextPreviousEnabled():
            self.request.response.setCookie(
                name='nextprev.collection',
                value='/'.join(self.context.getPhysicalPath()),
                path='/')
            if self.request.form:
                self.request.response.setCookie(
                    name='nextprev.form',
                    value=Zope.make_query(self.request.form),
                    path='/')
        return ''

class ExpireCookieView(object):

    type_names = ('Folder', 'Large Plone Folder', 'Topic')

    def isListing(self, name):
        for type_name in self.type_names:
            if name in getattr(
                self.context.portal_types.getTypeInfo(type_name),
                'view_methods', ()):
                return True

    def render(self):
        if 'nextprev.collection' in self.request:
            topic = self.context.restrictedTraverse(
                self.request['nextprev.collection'])
            if Acquisition.aq_base(
                self.context) is not Acquisition.aq_base(topic):
                name = self.__parent__.__name__
                if name == 'plone':
                    name = self.__parent__._data['template_id']
                if self.isListing(name):
                    self.request.response.expireCookie(
                        name='nextprev.collection', path='/')
                    self.request.response.expireCookie(
                        name='nextprev.form', path='/')
        return ''
