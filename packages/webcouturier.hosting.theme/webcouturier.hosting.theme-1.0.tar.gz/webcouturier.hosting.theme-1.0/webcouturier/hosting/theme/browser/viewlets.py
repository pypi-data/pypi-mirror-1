from zope.component import getMultiAdapter

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets import common

class TopNavigationViewlet(common.ViewletBase):
    render = ViewPageTemplateFile('templates/webcouturier_topnavigation.pt')
    
    def update(self):
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.context_state = getMultiAdapter((self.context, self.request),
                                             name=u'plone_context_state')                                            

        self.top_navigation = self.context_state.actions().get('top_navigation', None)
        
        self.width = str(768/len(self.top_navigation)) + "px"
        
class WebcouturierPersonalBarViewlet(common.PersonalBarViewlet):
    render = ViewPageTemplateFile('templates/personal_bar.pt')
    
class WebcouturierSearchBoxViewlet(common.SearchBoxViewlet):
    render = ViewPageTemplateFile('templates/searchbox.pt')
    
class WebcouturierGlobalSectionsViewlet(common.GlobalSectionsViewlet):
    render = ViewPageTemplateFile('templates/sections.pt')
        
