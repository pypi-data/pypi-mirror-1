# -*- coding: utf-8 -*-
from my_base import BaseGrabber, InvalidLogin
from BeautifulSoup import BeautifulSoup
import re
import cStringIO
import Image
from pytesser import *
import urllib
            
pattern = re.compile(r"iui.ajaxLink\('(?P<profil_url>\S*)'\);",re.IGNORECASE)

class FacebookGrabber(BaseGrabber):
    LoginUrl = "https://login.facebook.com/login.php?iphone=1&next=http%253A%252F%252Ftouch.facebook.com%252F"
    ExportUrl = "http://touch.facebook.com/friends.php"
    BaseUrl = "http://touch.facebook.com"
    
    def __init__(self, username, password):
        self.params = {'email' : username,'pass' : password}
        super(FacebookGrabber, self).__init__()
        
    def grab(self):
        contacts = []
        self.get_page(self.LoginUrl, self.params)
        html = self.get_page(self.ExportUrl)
        soup = BeautifulSoup(unicode(''.join(html), errors='ignore'))
        friends = soup.findAll('div', attrs={'class' :"item"})
        for friend in friends:
            profil_url = re.match(pattern, friend.attrMap['onclick']).group('profil_url')
            html = self.get_page(self.BaseUrl + profil_url + "&v=info")
            src = re.search('.*<img src="(?P<src>\S*)" alt="" />.*', html).group("src")

            file = urllib.urlopen(self.BaseUrl + src)
            im = cStringIO.StringIO(file.read()) 
            email_img = Image.open(im)
            email = image_to_string(email_img)
            contacts.append(email)
        return contacts
        
        