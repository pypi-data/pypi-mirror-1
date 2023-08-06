# plugs/tinyurl.py
#
#

""" tinyurl.com feeder """

__author__ = "Wijnand 'tehmaze' Modderman - http://tehmaze.com"
__license__ = 'BSD'

from gozerbot.aliases import aliases
from gozerbot.callbacks import callbacks
from gozerbot.commands import cmnds
from gozerbot.generic import striphtml, useragent
from gozerbot.plughelp import plughelp
from gozerbot.examples import examples
import urllib
import urllib2
import urlparse
import re

plughelp.add('tinyurl', 'the tinyurl url provides a tiny url for the url \
provided as argument or the last url in the log')

re_url_match  = re.compile(u'((?:http|https)://\S+)')
urlcache = {}

def valid_url(url):
    """ check if url is valid """
    if not re_url_match.search(url):
        return False
    parts = urlparse.urlparse(url)
    cleanurl = '%s://%s' % (parts[0], parts[1])
    if parts[2]:
        cleanurl = '%s%s' % (cleanurl, parts[2])
    if parts[3]:
        cleanurl = '%s;%s' % (cleanurl, parts[3])
    if parts[4]:
        cleanurl = '%s?%s' % (cleanurl, parts[4])
    return cleanurl

def privmsgcb(bot, ievent):
    """ callback for urlcaching """
    test_url = re_url_match.search(ievent.txt)
    if test_url:
        url = test_url.group(1)
        if not urlcache.has_key(bot.name):
            urlcache[bot.name] = {}
        urlcache[bot.name][ievent.target] = url

callbacks.add('PRIVMSG', privmsgcb)

def get_tinyurl(url):
    """ grab a tinyurl """
    postarray = [
        ('submit', 'submit'),
        ('url', url),
        ]
    postdata = urllib.urlencode(postarray)
    req = urllib2.Request(url='http://tinyurl.com/create.php', data=postdata)
    req.add_header('User-agent', useragent())
    try:
        res = urllib2.urlopen(req).readlines()
    except urllib2.URLError, e:
        ievent.reply('URLError: %s' % str(ex))
        return
    except urllib2.HTTPError, e:
        ievent.reply('HTTP error: %s' % str(e))
        return
    urls = []
    for line in res:
        if line.startswith('<blockquote><b>'):
            urls.append(striphtml(line.strip()).split('[Open')[0])
    if len(urls) == 3:
        urls.pop(0)
    return urls

def handle_tinyurl(bot, ievent):
    """ get tinyurl from argument or last url in log """
    if not ievent.rest and (not urlcache.has_key(bot.name) or not \
urlcache[bot.name].has_key(ievent.target)):
        ievent.missing('<url>')
        return
    elif not ievent.rest:
        url = urlcache[bot.name][ievent.target]
    else:
        url = ievent.rest
    url = valid_url(url)
    if not url:
        ievent.reply('invalid or bad URL')
        return
    tinyurl = get_tinyurl(url)
    if tinyurl:
        ievent.reply(' .. '.join(tinyurl))
    else:
        ievent.reply('failed to create tinyurl')

cmnds.add('tinyurl', handle_tinyurl, 'USER')
examples.add('tinyurl', 'show a tinyurl', 'tinyurl http://gozerbot.org')
aliases.data['tu'] = 'tinyurl'
