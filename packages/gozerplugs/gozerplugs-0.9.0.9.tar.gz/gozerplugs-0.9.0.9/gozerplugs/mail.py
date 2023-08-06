# plugs/mail.py
#
#

__copyright__ = 'this file is in the public domain'
__depend__ = ['log', ]
__gendocfirst__ = ['mail-set', ]

from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.generic import waitforqueue, rlog, hourmin, strtotime
from gozerbot.users import users
from gozerbot.config import config
from gozerbot.plugins import plugins
from gozerbot.plughelp import plughelp
from gozerplugs.log import logs
import smtplib, random, time, types

plughelp.add('mail', 'mail related commands')

rendezvous = {}

class Mailservernotset(Exception):

    """ exception to raise if mail server is not set """

    def __str__(self):
        return "config['mailserver'] is not set"

def domail(mailto, txt, fromm=None, mailserver=None, subject=None):
    """ sent the mail """
    if not txt:
        rlog(10, 'mail', 'no text to send')
        return
    if fromm:
        fromaddr = fromm
    else:
        fromaddr = config['mailfrom']
        if not fromaddr:
            fromaddr = 'gozerbot@gozerbot.org'
    if not mailserver:
        mailserver = config['mailserver']
    if not mailserver:
        raise Mailservernotset
    if type(txt) != types.ListType:
        txt = [txt, ]
    msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % \
(fromaddr, mailto, subject))
    for i in txt:
        msg += "%s\r\n" % i 
    server = smtplib.SMTP(mailserver)
    server.sendmail(fromaddr, mailto, msg)

def handle_mailset(bot, ievent):
    """ set email by sending a email with confirmation code """
    try:
        addr = ievent.args[0]
    except IndexError:
        ievent.missing('<emailadres>')
        return
    username = users.getname(ievent.userhost)
    rendezvous[username] = (str(random.randint(0, 10000)), addr)
    try:
        domail(addr, 'the code is %s' % str(rendezvous[username][0]), \
subject='gozerbot mail verification')
    except Exception, ex:
        ievent.reply("can't send test email: %s" % str(ex))
        return
    ievent.reply('test email is sent .. what is de code ? .. use the \
mail-code command')
    time.sleep(120)
    try:
        del rendezvous[username]
    except KeyError:
        pass

cmnds.add('mail-set', handle_mailset, ['MAIL', 'OPER'])
examples.add('mail-set', 'set email of user giving the command .. send \
confirm mail', 'mail-set bart@gozerbot.org')

def handle_mailcode(bot, ievent):
    """ confirm code """
    try:
        nr = ievent.args[0]
    except IndexError:
        ievent.missing('<nr>')
        return
    username = users.getname(ievent.userhost)
    try:
        code = rendezvous[username][0]
    except KeyError:
        ievent.reply('the code is not longer valid .. try the mail-set \
command again')
        return
    if nr == rendezvous[username][0]:
        if users.setemail(username, rendezvous[username][1]):
            ievent.reply('email set')
            try:
                del rendezvous[username]
            except KeyError:
                pass
        else:
            ievent.reply('failed to set email')
    else:
        ievent.reply('reply is not ok .. try again')

cmnds.add('mail-code', handle_mailcode, ['MAIL', 'OPER'])
examples.add('mail-code', 'check mail confirmation code', 'mail-code 333')

def handle_mail(bot, ievent):
    """ mail result from pipeline to the user giving the command """
    if not ievent.inqueue:
        ievent.reply('use mail in a pipeline')
        return
    result = waitforqueue(ievent.inqueue, 60)
    if not result:
        ievent.reply('no data to mail')
        return
    username = users.getname(ievent.userhost)
    email = users.getemail(username)
    if email:
        try:
            sub = "output of %s" % ievent.origtxt
            domail(email, result, subject=sub)
        except Exception, ex:
            ievent.reply("can't send email: %s" % str(ex))
            return
        ievent.reply('%s lines sent' % len(result))
    else:
        ievent.reply("can't get email of %s" % username)
 
cmnds.add('mail', handle_mail, ['MAIL', 'OPER'])
examples.add('mail', 'mail pipelined data to user giving the command', \
'todo | mail')

def handle_re(bot, ievent):
    """ mail log since last spoken """
    if not logs:
        ievent.reply('log plugin is not enabled')
        return
    if ievent.channel not in logs.loglist:
        ievent.reply('logging is not enabled in %s' % ievent.channel)
        return
    lastlist = logs.lastspokelist(ievent.channel, ievent.userhost, 100)
    lasttime = time.time()
    gotcha = None
    for i in lastlist[::-1]:
        delta = lasttime - i
        if delta > 600:
            gotcha = i
            break
        else:
            lasttime = i
    if gotcha:
        result = logs.fromtimewithbot(ievent.channel, gotcha)
        if result:
            username = users.getname(ievent.userhost)
            email = users.getemail(username)
            if email:
                try:
                    res = []
                    for i in result:
                        if i[2] == 'bot':
                            txt = i[4]
                        else:
                            nr = i[4].find(' ')
                            txt = i[4][nr:].strip()
                        res.append("[%s] <%s> %s" % \
(hourmin(float(i[1])), i[2], txt))
                    domail(email, res, subject="log of %s" % ievent.channel)
                except Exception, ex:
                    ievent.reply("can't send email: %s" % str(ex))
                    return
                ievent.reply('%s lines sent' % len(result))
                return
            else:
                ievent.reply("can't get email of %s" % username)
                return
    ievent.reply('no data found')
    
cmnds.add('re', handle_re, ['MAIL', 'OPER'])
examples.add('re', 'mail the log since last spoken word', 're')

def handle_mailtime(bot, ievent):
    """ mail log since a given time """
    if not logs:
        ievent.reply('log plugin is not enabled')
        return
    if ievent.channel not in logs.loglist:
        ievent.reply('logging is not enabled in %s' % ievent.channel)
        return
    fromtime = strtotime(ievent.rest)
    if not fromtime:
        ievent.reply("can't detect time")
        return
    result = logs.fromtimewithbot(ievent.channel, fromtime)
    if result:
        username = users.getname(ievent.userhost)
        email = users.getemail(username)
        if email:
            try:
                res = []
                for i in result:
                    if i[2] == 'bot':
                        txt = i[4]
                    else:
                        nr = i[4].find(' ')
                        txt = i[4][nr:].strip()
                    res.append("[%s] <%s> %s" % (hourmin(float(i[1])), i[2], \
txt))
                domail(email, res, subject="log of %s" % ievent.channel)
            except Exception, ex:
                ievent.reply("can't send email: %s" % str(ex))
                return
            ievent.reply('%s lines sent' % len(result))
            return
        else:
            ievent.reply("can't get email of %s" % username)
            return
    ievent.reply('no data found')
    
cmnds.add('mail-time', handle_mailtime, ['MAIL', 'OPER'])
examples.add('mail-time', 'mail the log since given time', 'mail-time 12:00')
