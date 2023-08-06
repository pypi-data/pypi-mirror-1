#-*- coding: utf-8 -*-
from gmail import GmailGrabber
from msn import MsnGrabber
from yahoo import YahooGrabber

def test_gmail():
    res = GmailGrabber(username="username", password="password").grab()
    assert len(res) > 0 

def test_hotmail():
    res = MsnGrabber(username="username@hotmail.com", password="password").grab()
    assert len(res) > 0 
    
def test_yahoo():
    res = YahooGrabber(username="username@yahoo.fr", password="password").grab()
    assert len(res) > 0 