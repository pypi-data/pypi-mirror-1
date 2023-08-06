from plone.app.portlets.portlets.login import Renderer as BaseRenderer
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class Renderer(BaseRenderer):
    render = ViewPageTemplateFile('login.pt')

    @property
    def available(self):
	return True

    def show(self):
        if not self.portal_state.anonymous():
            return False
        if not self.pas_info.hasLoginPasswordExtractor():
            return False
        page = self.request.get('URL', '').split('/')[-1]
        return page not in ('login_form', 'join_form')

    def show_logout(self):
        page = self.request.get('URL', '').split('/')[-1]
        if page in ('login_form', 'join_form'):
            return False

	return not self.show()
