from zope.i18nmessageid import MessageFactory
MessageFactory = MessageFactory('collective.bouncing')

from monkey import wrap
import zope.publisher.http

@wrap(zope.publisher.http.HTTPCharsets.getPreferredCharsets,
      'a7476dbf32ccb3142de2d956647359e81bedf3ca',
      '1af5f3cdb9a124f5dc8a52ff6226907859207db9')
def zope2_request_fix(func, self):
    if not bool(self.request.get('HTTP_ACCEPT_CHARSET')):
        self.request = {'HTTP_ACCEPT_CHARSET': 'utf-8'}

    return func(self)

zope.publisher.http.HTTPCharsets.getPreferredCharsets = zope2_request_fix
