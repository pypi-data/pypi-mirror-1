from collective.singing.interfaces import IDispatch

from channel import BaseList
from email.MIMEText import MIMEText

def insert_before(s, char, string):
    return (string+char).join(s.split(char))

class Mailman(BaseList):
    protocol = u"Mailman"
    
    def subscribe(self, email):
        msg = MIMEText(u'subscribe')
        msg['Subject'] = u'subscribe'
        msg['From'] = email
        msg['To'] = insert_before(self.email, '@', '-request')
        IDispatch(msg)()
        
    def unsubscribe(self, email):
        msg = MIMEText(u'unsubscribe')
        msg['Subject'] = u'unsubscribe'
        msg['From'] = email
        msg['To'] = insert_before(self.email, '@', '-request')
        IDispatch(msg)()
