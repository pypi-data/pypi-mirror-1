
try:
    from Products.Five import BrowserView
    BrowserView
except ImportError:
    from zope.publisher.browser import BrowserView

from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

COOKIE_NAME = '__kss_devel'

class DevelView(BrowserView):

    def ison(self, REQUEST=None):
        '''Checks if running in development mode

        Two ways to induce development mode:

        - set the cookie on the request

        - switch portal_js tool into debug mode, this will
          select development mode without the cookie

        '''
        ison = COOKIE_NAME in self.request.cookies

        if not ison:
            # Check from javascript tool
            # XXX this should not be done from here, but I don't want to
            # modify other components yet.
            try:
                from Products.CMFCore.utils import getToolByName
                js_tool = getToolByName(self.context.aq_inner, 'portal_javascripts')
                ison = js_tool.getDebugMode()
            except:
                pass

        result = bool(ison)
        if REQUEST is not None:
            result = str(result)
        return result

    def isoff(self, REQUEST=None):
        'Check if running in production mode'
        result = not(self.ison())
        if REQUEST is not None:
            result = str(result)
        return result

    def set(self):
        'XXX'
        self.request.RESPONSE.setCookie(COOKIE_NAME, '1', path='/')

    def unset(self):
        'XXX'
        self.request.RESPONSE.expireCookie(COOKIE_NAME, path='/')

    _ui = ViewPageTemplateFile('develui.pt', content_type='text/html;charset=utf-8')

    def ui(self):
        'XXX'
        if 'devel' in self.request.form:
            self.set()
            self.request.cookies[COOKIE_NAME] = '1'
        if 'prod' in self.request.form:
            self.unset()
            if COOKIE_NAME in self.request.cookies:
                del self.request.cookies[COOKIE_NAME]
        return self._ui()

    def ui_js(self):
        'XXX'
        resource = self.context.restrictedTraverse('++resource++kss_devel_ui.js')
        cooked = resource.GET()
        return cooked

    def ui_css(self):
        'XXX'
        resource = self.context.restrictedTraverse('++resource++kss_devel_ui.css')
        cooked = resource.GET()
        return cooked

    def ui_kss(self):
        'XXX'
        resource = self.context.restrictedTraverse('++resource++kss_devel_ui.kss')
        cooked = resource.GET()
        return cooked
