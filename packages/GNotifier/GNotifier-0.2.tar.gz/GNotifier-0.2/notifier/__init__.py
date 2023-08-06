# -*- coding: utf-8 -*-
from restkit import Resource
from simplejson import loads, dumps
import urllib2
import socket

def to_str(value):
    if isinstance(value, str):
        return value.decode('utf-8', 'ignore')
    return value.encode('utf-8', 'ignore')

def notify(title, message='', url='http://localhost:5222', path='/'):
    """
    - **title**: message title (required).

    - **url**: the url of the GNotifier server.

    - **path**: allowed paths are:

        * ``/`` send message on gtalk and gmail

        * ``/gmail`` send message on gmail

        * ``/gtalk`` send message on gtalk

    """
    try:
        res = Resource(url)
        data = dict(title=title, message=message)
        page = res.post(path=path, payload=dumps(data), headers={'Content-Type': 'application/json'})
        return loads(page.body)
    except Exception, e:
        return dict(status=1, notify_error=str(e))


def quick_notify(title, message='', url='http://localhost:5222', path='/', timeout=0.5):
    """
    Same as :func:`notifier.notify` but with a timeout
    """
    opener = urllib2.build_opener()
    opener.addheaders = [('Content-Type', 'application/json')]
    data = dict(title=title, message=message)
    socket.setdefaulttimeout(timeout)
    try:
        data = opener.open('%s%s' % (url, path), dumps(data)).read()
    except Exception, e:
        data = dict(status=1, quick_notify_error=str(e))
    else:
        data = loads(data)
    socket.setdefaulttimeout(None)
    return data

def main():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-u", "--url", dest="url",
                      default='http://localhost:5222',
                      help="http host")
    parser.add_option("-q", "--quick", dest="quick",
                      action="store_true", default=False,
                      help="http host")
    options, args = parser.parse_args()
    if options.quick:
        meth = quick_notify
    else:
        meth = notify
    print meth(to_str(' '.join(args)), url=options.url.strip('/'))


