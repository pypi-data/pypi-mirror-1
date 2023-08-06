from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from plone.app.layout.viewlets.common import PersonalBarViewlet,ViewletBase
from zope.component import getMultiAdapter
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
import datetime


class WWPLogoViewlet(ViewletBase):
    #this renders the page template
    render = ViewPageTemplateFile('templates/logo.pt')

    #this is the viewlet its self
    def update(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
	#parameter 'sitehome' is made accessible from within template using tal:attributes="href view/sitehome"
        self.sitehome = portal_state.navigation_root_url()



class WwpDate(ViewletBase):
    """ Custom Personal bar """
    index = ViewPageTemplateFile('templates/WwpDate.pt')
    def update(self):
        super(WwpDate, self).update()
        #added by us
        self.dateTimeNow = datetime.date.today()








