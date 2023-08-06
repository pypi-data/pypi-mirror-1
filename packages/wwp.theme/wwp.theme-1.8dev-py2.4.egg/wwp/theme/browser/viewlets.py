from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from plone.app.layout.viewlets.common import PersonalBarViewlet,ViewletBase
from zope.component import getMultiAdapter
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

import datetime
import urllib
from Products.CMFCore.utils import getToolByName

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



class Wwpadsense(ViewletBase):
    """ Custom Personal bar """
    index = ViewPageTemplateFile('templates/wwp_adsense_top.pt')
    def getheader(self):
        header = urllib.urlopen("http://wwp.greenwichmeantime.com/cgi-bin/border-top-server.pl")
        header = header.read()
        return str(header)
    
    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()
    
    
class wwpfooter(ViewletBase):
    """ Custom Personal bar """
    index = ViewPageTemplateFile('footer.pt')
    def getfooter(self):
        
        #import unicodedata
        
        footer = ''
        extfile = urllib.urlopen("http://wwp.greenwichmeantime.com/cgi-bin/border-bottom-uk.pl")
        footer += '<p style="text-align: center" name="1">' + str(extfile.read()) + '</p>'
        extfile = urllib.urlopen("http://wwp.greenwichmeantime.com/cgi-bin/border-bottom-eu.pl")
        footer += '<p style="text-align: center" name="2">' + str(extfile.read()) + '</p>'
        extfile = urllib.urlopen("http://wwp.greenwichmeantime.com/cgi-bin/border-bottom-europe.pl")
        footer += '<p style="text-align: center" name="3">' + str(extfile.read()) + '</p>'
        extfile = urllib.urlopen("http://wwp.greenwichmeantime.com/cgi-bin/border-bottom-global.pl")
        footer += '<p style="text-align: left" name="4">' + str(extfile.read()) + '</p>'
        extfile = urllib.urlopen("http://wwp.greenwichmeantime.com/cgi-bin/border-bottom-server.pl")
        footer += '<p style="text-align: center" name="5">' + str(extfile.read()) + '</p>'
        extfile = urllib.urlopen("http://wwp.greenwichmeantime.com/cgi-bin/border-bottom-uk.pl")
        footer += '<p style="text-align: center" name="6">' + str(extfile.read()) + '</p>'


        footer = unicode(footer, errors='replace')
        #text = extfile.read()
        #footer_out = unicodedata.normalize('NFKD', text).encode('ascii','ignore')
        return footer





