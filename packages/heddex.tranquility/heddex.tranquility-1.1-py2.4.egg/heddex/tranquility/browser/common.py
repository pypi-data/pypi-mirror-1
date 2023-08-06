from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import GlobalSectionsViewlet
from plone.app.layout.viewlets.common import PathBarViewlet

class themeGlobalSectionsViewlet(GlobalSectionsViewlet):
    index = ViewPageTemplateFile('sections.pt')

class themePathBarViewlet(PathBarViewlet):
    index = ViewPageTemplateFile('path_bar.pt')
