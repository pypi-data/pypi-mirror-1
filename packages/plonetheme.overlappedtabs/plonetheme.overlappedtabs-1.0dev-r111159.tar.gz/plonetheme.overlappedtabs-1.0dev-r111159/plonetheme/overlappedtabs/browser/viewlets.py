from AccessControl import ClassSecurityInfo, SecurityManagement
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from plone.app.layout.viewlets.common import GlobalSectionsViewlet as GlobalSectionsViewletBase

login_required = 'acl_users/credentials_cookie_auth/require_login'

class GlobalSectionsViewlet(GlobalSectionsViewletBase):
    index = ViewPageTemplateFile('templates/sections.pt')
    def selected_section(self):
        portal_url = self.context.portal_url()
        if self.context.id == 'disclaimer':
            return 'disclaimer'
        i = 0
        for j,tab in enumerate(self.portal_tabs):
            if tab['id'] == self.selected_portal_tab:
                i = j+1
        return i

class __GlobalSectionsLineViewlet(GlobalSectionsViewlet):
    index = ViewPageTemplateFile('templates/sections_line.pt')
    def show_logout(self):
        raise NotImplementedError

class GlobalSectionsLineViewletAbove(__GlobalSectionsLineViewlet):
    index = ViewPageTemplateFile('templates/sections_line.pt')
    name = 'above'
    def show_logout(self):
        user = SecurityManagement.getSecurityManager().getUser()
        return 'Authenticated' in user.getRoles()

class GlobalSectionsLineViewletBelow(__GlobalSectionsLineViewlet):
    index = ViewPageTemplateFile('templates/sections_line.pt')
    name = 'below'
    def show_logout(self):
        return False
