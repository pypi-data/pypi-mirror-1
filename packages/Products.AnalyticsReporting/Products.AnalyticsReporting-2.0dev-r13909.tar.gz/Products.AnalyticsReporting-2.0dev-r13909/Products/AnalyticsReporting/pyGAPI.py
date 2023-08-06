import httplib
import urllib
import urllib2 
import re
import csv

# from csv import reader, DictReader
from cookielib import CookieJar
from string import ascii_letters, digits
from random import choice
from datetime import date

alphanums = list(ascii_letters + digits)
def _random_id(n):
    """
    create a random alphanumeric identifier of length n
    """
    ''.join(choice(alphanums) for i in range(n))

def _convert_to_float(s):
    """
    try to convert content to float, else return original content
    """
    try:
        return float(s)
    except:
        return s
    


class pyGAPI(object):
    """Google Analytics API that works through screen scraping"""
    def __init__(self, username, password, website_id=""):
        """
        provide login and password to be used to connect to Google Analytics
        all immutable system variables are also defined here
        website_id is the ID of the specific site on google analytics
        """        
        self.login_params = {
            'GA3T': _random_id(11),   # unique identifiers for session
            'GALX': _random_id(11),   # unique identifiers for session
            "continue": 'http://www.google.com/analytics/home/?et=reset&amp;hl=en-US',
            'nui': '1',
            'hl': 'en-US',
            'rmShown': '1',
            "PersistentCookie": "yes",
            "Email": username,
            "Passwd": password,
            'service': 'analytics' 
        }
        self.headers = [("Content-type", "application/x-www-form-urlencoded"),
                        ('User-Agent', 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'),
                        ("Accept", "text/plain")]
        self.url_ServiceLoginBoxAuth = 'https://www.google.com/accounts/ServiceLoginBoxAuth'
        self.url_Export = 'https://www.google.com/analytics/reporting/export'
        self._connect()

        # set the website_id, requires a connection because we may need to pull
        # the list of the user's sites
        try:
            if not website_id:
                # if no website ID, use the first one from the list
                self.website_id = self.list_sites()[0]['id']
            else:
                self.website_id = str(int(website_id))
        except:
            raise AttributeError, "website_id must be an integer"
        
    def _connect(self):
        """
        connect to Google Analytics
        """
        params = urllib.urlencode(self.login_params)
        self.cj = CookieJar()                            
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        self.opener.addheaders = self.headers
        resp = self.opener.open(self.url_ServiceLoginBoxAuth, params)
        
    def list_sites(self):
        """
        get list of sites and corresponding IDs by 
        screenscraping the analytics home page
        """
        sites_body = self.opener.open('https://www.google.com/analytics/home').read()
        site_list = [];
        # pull up to the first 20 sites
        #print sites_body
        for a in range(1,20):
            resitepuller = re.compile("ug_row.*?" + 'class="list_cell">' + str(a) +
                                        ".*?" + '<td class="list_cell">' + "(?P<site>.*?)" + 
                                        '</td>.*?/analytics/reporting/dashboard\?id=' + 
                                        "(?P<id>\d+)" + '&sci', re.DOTALL)
            m = resitepuller.search(sites_body)
            if not(m):
                break
            # create a dictionary of site results
            site_list.append({'site_name': m.group('site'), 'id': m.group('id')})
        return site_list
        
    def list_reports(self):
        """
        show which reports are currently configured
        """
        report_list = ('ReferringSourcesReport', 'SearchEnginesReport',
                       'AllSourcesReport', 'KeywordsReport', 'CampaignsReport',
                       'AdVersionsReport', 'TopContentReport',
                       'ContentByTitleReport', 'ContentDrilldownReport',
                       'EntrancesReport', 'ExitsReport', 'GeoMapReport', 
                       'LanguagesReport', 'HostnamesReport', 'SpeedsReport','VisitorsOverviewReport')
        return report_list
        
    def download_report(self, report_name, date_range, inputcmp='average', inputfmt='2', limit='10000'):
        """
        download a specific report
        report_name is limited to what can be called from list_Reports
        data_range should be a 2-tuple of Python dates like (date, date) 
        limit is the number of entries to pull down
        """
        # convert dates from a pair of dates to Google's input format
        # for instance: 
        # (date(2008,1,1), date(2008,1,31)) becomes 20080101-20080131
        if len(date_range) <> 2:
            return "daterange incorrect"
        inputpdr = date_range[0].strftime("%Y%m%d") + '-' + date_range[1].strftime("%Y%m%d")
        
        # TODO: convert to urllib2?
        params = urllib.urlencode({
            'id': self.website_id,
            'pdr': inputpdr,
            'cmp': inputcmp,
            'trows': limit,
            'rpt': report_name,
            'fmt': inputfmt,
        })
                                    
        self.raw_data = self.opener.open('https://www.google.com/analytics/reporting/export', params).read()
        
    def csv(self):
        """
        return just the CSV portion of the data
        """
        table_head = "# ----------------------------------------\n# Table\n# ----------------------------------------\n"
        table_end = "\n# --------------------------------------------------------------------------------"
        table_head_pos = self.raw_data.find(table_head)
        table_end_pos = self.raw_data.find(table_end)
        return self.raw_data[table_head_pos + len(table_head):table_end_pos]        
          
    def parse_csv_as_dicts(self, 
                           convert_numbers=False,
                           exclude_columnnames=('Keyword')):
        reader = csv.DictReader(self.csv().splitlines())
        results = list(reader)
        if convert_numbers:
            for d in results:
                for k, v in d.iteritems():
                    if k not in exclude_columnnames:
                        d[k] = _convert_to_float(v)
        return results  