from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from plone.app.layout.viewlets import common as base

class PathBarViewlet(base.PathBarViewlet):
    """A custom version of the path bar class to change the dividers
    """
    def render(self):
        # defer to index method, because that's what gets overridden by the template ZCML attribute
        return self.index()
    index = ViewPageTemplateFile('greenearth_path_bar.pt')
    
class PersonalBarViewlet(base.PersonalBarViewlet):
    """A custom version of the personal bar class to move it to the bottom of the page; we shouldn't have to customize this, but we do because Plone 3.0 sucks.
    """
    def render(self):
        # defer to index method, because that's what gets overridden by the template ZCML attribute
        return self.index()    
    index = ViewPageTemplateFile('greenearth_personal_bar.pt')    