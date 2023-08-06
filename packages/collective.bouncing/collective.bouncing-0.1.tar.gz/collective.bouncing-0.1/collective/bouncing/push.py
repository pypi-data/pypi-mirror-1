from zope import interface
from zope import component

import zope.sendmail.interfaces
import Products.CMFPlone.interfaces

import smtplib

class SMTPMailer(object):
    interface.implements(zope.sendmail.interfaces.ISMTPMailer)

    SMTP = smtplib.SMTP

    def _fetch_settings(self):
        root = component.getUtility(Products.CMFPlone.interfaces.IPloneSiteRoot)
        m = root.MailHost
        return dict(hostname=m.smtp_host or 'localhost',
                    port=m.smtp_port,
                    username=m.smtp_userid or m.smtp_uid or None,
                    password=m.smtp_pass or m.smtp_pwd or None,)

    def send(self, fromaddr, toaddrs, message):
        cfg = self._fetch_settings()

        connection = self.SMTP(cfg['hostname'], str(cfg['port']))
        if cfg['username'] is not None and cfg['password'] is not None:
            connection.login(cfg['username'], cfg['password'])
        connection.sendmail(fromaddr, toaddrs, message)
        connection.quit()
