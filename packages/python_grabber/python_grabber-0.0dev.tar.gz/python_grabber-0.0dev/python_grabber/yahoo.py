from base import BaseGrabber, InvalidLogin

class YahooGrabber(BaseGrabber):
    LoginUrl = "https://login.yahoo.com/config/login?"
    ExportUrl = "http://address.yahoo.com/yab/us/Yahoo_ab.csv"
    
    def __init__(self, username, password):
        self.params = {'login' : username,'passwd' : password}
        super(YahooGrabber, self).__init__()
        
    def grab(self):
        self.get_page(self.LoginUrl, self.params)
        html = self.get_page(self.ExportUrl)
        contacts = self.get_contacts(html)
        if 'free2rhyme@yahoo.com' in contacts:
            raise InvalidLogin, "User or password incorrect"
        return contacts
        
  