# gozerplugs/test.py
#
#

from gozerbot.utils.exception import exceptionmsg
from gozerbot.tests import tests
from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.irc.ircevent import Ircevent
from gozerbot.users import users
from gozerbot.plughelp import plughelp

plughelp.add('test', 'plugin to do tests')

import time, random

donot = ['quit', 'reboot', 'shutdown', 'exit', 'delete', 'halt', 'upgrade', \
'install', 'reconnect', 'wiki', 'weather', 'sc', 'jump', 'disable', 'dict', \
'snarf', 'validate', 'popcon']

def dummy(a, b=None):
    return ""

import gozerbot.utils.url
import gozerbot.generic
oldgeturl = gozerbot.utils.url.geturl
oldgeturl2 = gozerbot.utils.url.geturl2 

def handle_testplugs(bot, msg):
    gozerbot.utils.url.geturl = dummy
    gozerbot.utils.url.geturl2 = dummy
    gozerbot.generic.geturl = dummy
    gozerbot.generic.geturl2 = dummy
    if msg.rest:
        match = msg.rest
    else:
        match = ""
    try:
        users.add('test', ['test@test',], ['USER', 'OPER'])
    except Exception, ex:
        pass
    bot.channels.setdefault('test', {})
    try:
        loop = int(msg.options['--loop'])
    except (KeyError, ValueError):
        loop = 1
    for i in range(loop):
        msg.reply('starting loop %s' % str(i))
        examplez = examples.getexamples()
        random.shuffle(examplez)
        for example in examplez:
            if match and match not in example:
                continue
            skip = False
            for dont in donot:
                if dont in example:
                    skip = True
            if skip:
                continue
            if bot.jabber:
                from gozerbot.jabber.jabbermsg import Jabbermsg
                newmessage = Jabbermsg(msg.orig)
                newmessage.copyin(msg)
                newmessage.txt = '!' + example
                msg.reply('command: ' + example)  
                bot.domsg(newmessage)
            else:
                newmessage = Ircevent(msg.orig)
                newmessage.copyin(msg)
                newmessage.txt = '!' + example
                msg.reply('command: ' + example)  
                bot.domsg(newmessage)
            try:
                time.sleep(int(msg.options['--sleep']))
            except (KeyError, ValueError):
                pass
    gozerbot.utils.url.geturl = oldgeturl
    gozerbot.utils.url.geturl2 = oldgeturl2
    gozerbot.generic.geturl = oldgeturl
    gozerbot.generic.geturl2 = oldgeturl2

cmnds.add('test-plugs', handle_testplugs, ['OPER', ], options={'--sleep': '1', '--loop': '1'}, threaded=True)
examples.add('test-plugs', 'run all the examples in the plugins', 'test-plugs')

def handle_testsrun(bot, ievent):
    errors = []
    teller = 0
    for i in range(len(tests.tests)):
       test = tests.tests[i]
       if ievent.rest and ievent.rest not in test.plugin:
           continue
       if test.expect:
           teller += 1
       try:
           result = test.run(bot, ievent)
           if not result:
               continue
           if not result.error:
               ievent.reply("OK %s ==> %s" % (test.execstring, test.response))
           else:
               errors.append(test)
               ievent.reply('ERROR %s (%s): %s ==> %s (%s)' % (test.error, test.where, test.execstring, test.response, test.expect))
       except Exception, ex:
           errors.append(test)
           test.error = exceptionmsg()
           ievent.reply(test.error)
    ievent.reply('%s tests run .. %s errors' % (teller, len(errors)))

cmnds.add('test-run', handle_testsrun, 'OPER', threaded=True)
examples.add('test-run', 'run the tests', 'test-run')
