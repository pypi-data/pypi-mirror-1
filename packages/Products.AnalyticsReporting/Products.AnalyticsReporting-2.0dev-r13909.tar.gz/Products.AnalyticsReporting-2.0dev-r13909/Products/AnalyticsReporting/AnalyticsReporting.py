from OFS import SimpleItem
from Globals import DTMLFile, MessageDialog
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from Products.CMFCore import permissions
from OFS.PropertyManager import PropertyManager

class AnalyticsReporting(SimpleItem.SimpleItem, PropertyManager):
    """ the class for AnalyticsReporting objects """

    meta_type = 'AnalyticsReporting'
    security = ClassSecurityInfo()

    manage_options=(
          {'label':'Properties', 'action':'manage_propertiesForm'},
          {'label': 'View', 'action': 'analytics_view'},
         ) + SimpleItem.SimpleItem.manage_options

    def __init__(self, id, title, content):
        """ Initialize a new instance of AnalyticsReporting objects """

        self.id = id
        self.title = title
        self.content = content
        
        self.manage_addProperty(id='analytics_login', type='string', value='email@example.com')
        self.manage_addProperty(id='analytics_password', type='string', value='secret')
        self.manage_addProperty(id='analytics_siteid', type='string', value='1234567')
        
    #security.declarePublic('getReport')
    security.declareProtected(permissions.ModifyPortalContent, 'getReport')
    def getReport(self, daterange, type='TopContentReport', format=0, limit=500):
        """ show analytics - TODO: Make this a separate product"""
        import pyGAPI
        import datetime

        #connector = pyGAPI.pyGAPI('googletest@jessnorwood.co.uk', '12345abc', website_id='6350605')
        connector = pyGAPI.pyGAPI(self.analytics_login, self.analytics_password, website_id=self.analytics_siteid)
        
        types = connector.list_reports()
        if type not in types:
            return "Type must be one of: " + ", ".join(types)
        
        if daterange=='week':
            delta = datetime.timedelta(days=7)
            startdate = datetime.date.today() - delta
        elif daterange=='month':
            delta = datetime.timedelta(days=31)
            startdate = datetime.date.today() - delta
        elif daterange=='year':
            delta = datetime.timedelta(days=365)
            startdate = datetime.date.today() - delta
        elif daterange=='all':
            startdate = datetime.date(2000, 1, 1)
        else:
            return "Date range must be 'week', 'month', 'year' or 'all'"
        
        connector.download_report(type, (startdate, datetime.date.today()), inputfmt=format, limit=limit)
        
        setHeader = self.REQUEST.RESPONSE.setHeader
        
        if str(format)=='0':
            setHeader('Content-Type','application/pdf')
            setHeader('Content-disposition','attachment; filename=' + type + '.pdf')
            
        elif str(format)=='2':
            setHeader('Content-Type','application/vnd.ms-excel')
            setHeader('Content-disposition','attachment; filename=' + type + '.csv')        
        
        return connector.raw_data
    
    
    analytics_view = PageTemplateFile('zpt/analytics_view.pt', globals())
    analytics_macro = PageTemplateFile('zpt/analytics_macro.pt', globals())
    manage_editAnalyticsReporting = PageTemplateFile('zpt/editForm.pt', globals())

# Constructors
manage_addAnalyticsReportingForm = PageTemplateFile('zpt/addForm.pt', globals())
def manage_addAnalyticsReporting(self, id, title, content, REQUEST=None):
    """ Add an AnalyticsReporting instance """
    newObj= AnalyticsReporting(id, title, content)
    self._setObject(id, newObj)

    if REQUEST:
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/' + id + '/manage_propertiesForm')
