# -*- coding: utf-8 -*-
from restkit import Resource
from simplejson import loads, dumps
import urllib2
import socket

def to_str(value):
    if isinstance(value, str):
        return value.decode('utf-8', 'ignore')
    return value.encode('utf-8', 'ignore')

def notify(title, message='', url='http://localhost:5222', path='/', recipients=[]):
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
        data = dict(title=title, message=message, recipients=recipients or None)
        page = res.post(path=path, payload=dumps(data), headers={'Content-Type': 'application/json'})
        return loads(page.body)
    except Exception, e:
        return dict(status=1, notify_error=str(e))


def quick_notify(title, message='', url='http://localhost:5222', path='/', recipients=[], timeout=0.5):
    """
    Same as :func:`notifier.notify` but with a timeout
    """
    opener = urllib2.build_opener()
    opener.addheaders = [('Content-Type', 'application/json')]
    data = dict(title=title, message=message, recipients=recipients or None)
    socket.setdefaulttimeout(timeout)
    try:
        data = opener.open('%s%s' % (url, path), dumps(data)).read()
    except Exception, e:
        data = dict(status=1, quick_notify_error=str(e))
    else:
        data = loads(data)
    socket.setdefaulttimeout(None)
    return data

def _main(args=[]):
    from optparse import OptionParser
    import logging as log
    import time
    import sys

    cook = dict(
            hard_eggs=(10, 0),
            boiled_eggs=(3, 15),
    )

    cook_str = ', '.join(['%s (%s)' % (k, '%sm%ss' % v) for k, v in sorted(cook.items())])

    parser = OptionParser()
    parser.usage = '%prog [options] message'
    parser.add_option("-u", "--url", dest="url",
                      default='http://localhost:5222',
                      help="HTTP Host")
    parser.add_option("-r", "--recipient", dest="recipients",
                      action="append", default=[],
                      help="Recipients. You can have more than one -r")
    parser.add_option("-q", "--quick", dest="quick",
                      action="store_true", default=False,
                      help="Use quick notifier")
    parser.add_option("-i", "--im", dest="im",
                      action="store_true", default=False,
                      help="Only send on IM")
    parser.add_option("-m", "--minutes", dest="minutes",
                      type="int", default="0",
                      help="Wait X minutes before sending")
    parser.add_option("-s", "--seconds", dest="seconds",
                      type="int", default="0",
                      help="Wait X seconds before sending")
    parser.add_option("-c", "--cook", dest="cook", metavar="INGREDIENT",
                      help="Send notification for cooking. Valid ingredients are: %s" % cook_str)
    parser.add_option("-v", "--verbose", dest="verbose",
                      action="count", default=0,
                      help="More output")
    if args:
        options, args = parser.parse_args(args)
    else:
        options, args = parser.parse_args()

    log.basicConfig(
            stream=sys.stdout,
            level=options.verbose and log.DEBUG or log.WARN,
            format='%(levelname)s %(message)s'
           )

    minutes = options.minutes
    seconds = options.seconds

    if options.cook:
        if minutes or seconds:
            parser.error("You can use minutes/seconds with the cook option")
        if options.cook in cook:
            minutes, seconds = cook.get(options.cook)
            args = ['Your %s are ready' % options.cook.replace('_', ' ')]
            options.im = True
        else:
            parser.error('%s is not in the cook list' % options.cook)

    if not args:
        parser.error('You must specify a message')

    if minutes or seconds:
        log.debug('Waiting %sm %ss before sending...', minutes, seconds)
        time.sleep((minutes * 60) + seconds)

    if options.quick:
        meth = quick_notify
    else:
        meth = notify

    log.debug('Sending notification...')
    results = meth(to_str(' '.join(args)),
                   url=options.url.strip('/'),
                   path=options.im and '/gtalk' or '/',
                   recipients=options.recipients,
                  )

    if results.get('status') == 0:
        results['recipients'] = ', '.join(results.get('recipients', []))
        log.warn('Request sent to %(recipients)s in %(time)ss', results)
    else:
        log.error('Request failure\n\t%r', results)

def main():
    try:
        _main()
    except KeyboardInterrupt:
        pass

