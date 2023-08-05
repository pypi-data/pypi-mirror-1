from mechanoid.mechanoid import Browser
from HTMLParser import HTMLParseError
import re

class pyWebSMS(Browser):
    max_chars = 160
    
    def __init__(self, sms):
        Browser.__init__(self)
        self.sms = sms
        
    def start(self):
        try: int(self.sms.phone)
        except:
            return self.sms.error("The cellphone number should contain only numbers")
        if len(self.sms.phone) != 10:
            return self.sms.error("The cellphone number should have a length of 10")
        self.sms.run(self.home, self.login, self.enter, self.send, self.confirm)
        return 1
        
    def home(self):
        self.sms(0.01, 'Connecting to 190.it')
        self.open('http://www.190.it/190/trilogy/jsp/homePage.do?tabName=HOME+190&ty_skip_md=true')
        
    def login(self):
        self.sms(0.25, 'Logging in')
        self.select_form(name='loginForm')
        self['username'] = self.sms.username
        self['password'] = self.sms.password
        try: self.submit()
        except HTMLParseError: pass
        except: raise
        if re.search('registrazione.190.it', self.response.read()):
            raise UserWarning, 'Invalid username or password'
        
    def enter(self):
        self.sms(0.5, 'Entering sms zone')
        self.open('http://www.areaprivati.190.it/190/trilogy/jsp/programView.do?ty_nocache=true&pageTypeId=9604&channelId=-8663&programId=9361&ty_key=fsms_hp')
        try: self.follow_link(url='http://www.areaprivati.190.it/190/trilogy/jsp/dispatcher.do?ty_key=fsms_hp&ipage=next')
        except: return
        
    def send(self):
        self.sms(0.75, 'Sending sms')
        self.select_form('fsmsMessageForm')
        self['receiverNumber'] = self.sms.phone
        self['message'] = self.sms.text
        self.submit()
        
    def confirm(self):
        self.sms(0.99, 'Confirming sms')
        self.follow_link(url_regex=re.compile('send.do'))
