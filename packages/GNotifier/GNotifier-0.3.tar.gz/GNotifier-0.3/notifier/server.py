# -*- coding: utf-8 -*-
from webob import Request, Response, exc
from simplejson import loads, dumps
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
import traceback
import smtplib
import mimetypes
import time
import sys
import os

from notifier import to_str

try:
    import xmpp
except:
    sys.path.append(os.path.dirname(__file__))
    import xmpp

def status(func):
    def wrapper(*args, **kwargs):
        try:
            results = func(*args, **kwargs)
        except Exception, e:
            error = traceback.format_exc()
            return dict(status=1, error=str(e), **{'%s_error' % func.func_name: error})
        else:
            if isinstance(results, dict):
                results.update(status=0)
                return results
            else:
                return dict(status=0)
    return wrapper

class Notifier(object):

    def __init__(self, gid='', passwd='', recipients='', debug=False):
        self.gid = gid
        self.jid=xmpp.protocol.JID(gid)
        self.passwd = passwd
        self.recipients = recipients.split()
        if not debug:
            self.gtalk('Notifier started')

    @status
    def gtalk(self, title, message, recipients):
        cl=xmpp.Client(self.jid.getDomain(),debug=[])
        cl.connect(('talk.google.com', 5222))
        cl.auth(self.jid.getNode(), self.passwd)
        if message:
            body = '%s\n\n%s' % (to_str(title), to_str(message))
        else:
            body = title
        for recipient in recipients:
            cl.send(xmpp.Message(recipient, body))
        cl.disconnect()

    @status
    def gmail(self, title, message, recipients):
        msg = MIMEMultipart()
        msg['From'] = self.gid
        msg['To'] = ','.join(self.recipients)
        msg['Subject'] = title
        msg.attach(MIMEText(message))
        msg = msg.as_string()

        cl = smtplib.SMTP('smtp.gmail.com', 587)
        cl.ehlo()
        cl.starttls()
        cl.ehlo()
        cl.login(self.gid, self.passwd)
        for recipient in recipients:
            cl.sendmail(self.gid, recipient, msg)
        cl.close()

    @status
    def send(self, title, message='', recipients=None):
        results = self.gtalk(title, message, recipients)
        results.update(self.gmail(title, message, recipients))
        return results

    def __call__(self, environ, start_response):
        t = time.time()
        req = Request(environ)
        resp = Response()
        path_info = req.path_info
        results = dict(status=1)
        if req.method == 'POST':
            try:
                data = loads(req.body)
            except Exception, e:
                results['error'] = str(e)
            else:
                if 'title' in data:
                    title = to_str(data.get('title', ''))
                    message = to_str(data.get('message', ''))
                    recipients = data.get('recipients', self.recipients)
                    if not isinstance(recipients, list):
                        recipients = self.recipients
                    recipients = set(recipients)
                    if path_info == '/':
                        data = self.send(title, message, recipients)
                    elif path_info == '/gtalk':
                        data = self.gtalk(title, message, recipients)
                    elif path_info == '/gmail':
                        data = self.gmail(title, message, recipients)
                    else:
                        data = {}
                    results.update(data, recipients=list(recipients))
            results['time'] = time.time() - t
            resp.content_type='application/json'
            resp.body = dumps(results)
        else:
            resp.body = '<html><body><h1>Welcome to GNotifier<h1></body></html>'
        return resp(environ, start_response)

def main(global_config, **local_config):
    return Notifier(**local_config)

