from base import BaseGrabber, InvalidLogin
from lxml.html import fromstring
from pyquery import PyQuery as pq
import urllib2
import re


class MsnGrabber(BaseGrabber):
    LoginUrl = "https://mid.live.com/si/login.aspx"
    ExportUrl = "http://mpeople.live.com/default.aspx"
    
    
    def __init__(self, username, password):
        self.params = {'LoginTextBox' : username,'PasswordTextBox' : password,
                        'SavePasswordCheckBox': '0',
                        'PasswordSubmit': 'Sign in',
                        '__ET': '', "__EVENTTARGET":"", "__EVENTARGUMENT":""
        }
        super(MsnGrabber, self).__init__()
        
    def grab(self):
        doc = self.get_page(self.LoginUrl)
        doc = fromstring(doc, base_url = "https://mid.live.com/si/")
        doc.make_links_absolute()
        d = pq(doc)
        submit = d("#EmailPasswordForm").attr("action")
        
        
        self.get_page(submit, self.params)
        html = self.get_page(self.ExportUrl)
        self.contacts = []
        doc = parse(html) 
        doc.make_links_absolute()
        d = pq(doc)
        
        span_pages = d("#ctl00_MainContentPlaceHolder_ContactList_indexText").text()
        nbr_pages = int(re.match(r"\(Page 1 of (?P<pages>\d)+\)", span_pages).group('pages'))
        
        for i in range(2, m):
            html = self.get_page(self.ExportUrl +'?pg=' + str(i))
            contacts = self.get_contacts(html, contacts)
        return contacts

    def get_nbr_pages(self):
        pass
    
    def paginate(self):
        pass
    
    def get_contacts(self):
        pass