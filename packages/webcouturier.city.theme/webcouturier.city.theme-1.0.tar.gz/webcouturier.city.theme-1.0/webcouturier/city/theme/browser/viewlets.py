from plone.app.layout.viewlets import common

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class GlobalSectionsViewlet(common.GlobalSectionsViewlet):
    render = ViewPageTemplateFile('templates/webcouturier_sections.pt')
    
class SearchBoxViewlet(common.SearchBoxViewlet):
    render = ViewPageTemplateFile('templates/webcouturier_searchbox.pt')