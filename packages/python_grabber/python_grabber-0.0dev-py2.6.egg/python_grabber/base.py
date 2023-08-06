import urllib
import urllib2
import re
import cookielib

RE_EMAILS = re.compile(r"([a-zA-Z0-9+_\-\.]+@[0-9a-zA-Z][.-0-9a-zA-Z]*.[a-zA-Z]+)", re.IGNORECASE)

def iphone_request(url):
    """retourne un objet request avec le user-agent pour iphone """
    request = urllib2.Request(url)
    request.add_header("User-Agent", "Mozilla/5.0 (iPhone; U; CPU iPhone OS 3_0 like Mac OS X; en-us) AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7A341 Safari/528.16")
    return request

class InvalidLogin(Exception):
    pass

class BaseGrabber(object):
        
    def __init__(self):
        self.cookiejar = cookielib.CookieJar() 
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar), urllib2.HTTPRedirectHandler())
        
    def get_page(self, url, data=None):
        if data:
            data = urllib.urlencode(data)
        html = self.opener.open(url, data).read()
        return html
        
    def get_contacts(self, html, contacts=None):
        if contacts:
            emails = RE_EMAILS.findall(html)
            [contacts.add(email) for email in emails]
        else:
            emails = RE_EMAILS.findall(html)
            contacts = set([email for email in emails])
        return contacts

        