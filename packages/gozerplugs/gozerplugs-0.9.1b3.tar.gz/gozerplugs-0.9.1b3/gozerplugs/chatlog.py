# gozerplugs/chatlog.py
#
# 

""" log irc channels to [hour:min] <nick> txt format """

__copyright__ = 'this file is in the public domain'
__author__ = 'Robert C Corsaro <rcorsaro@gmail.com>'

from gozerbot.commands import cmnds
from gozerbot.callbacks import callbacks, jcallbacks
from gozerbot.persist.persistconfig import PersistConfig
from gozerbot.generic import hourmin, rlog, lockdec
from gozerbot.irc.monitor import outmonitor
from gozerbot.xmpp.monitor import xmppmonitor
from gozerbot.plughelp import plughelp
from gozerbot.examples import examples
from gozerbot.irc.ircevent import Ircevent
from gozerbot.fleet import fleet
import time, os, thread
from os import path

plughelp.add('chatlog', 'log irc channels')

outlock = thread.allocate_lock()
outlocked = lockdec(outlock)

cfg = PersistConfig()
cfg.define('channels', [])
# format for logs. simple or supy are currently supported.
cfg.define('format', 'simple')
# basepath: the root of all logs.  None is $gozerbot-root/logs
cfg.define('basepath', None)
# msgs that should be logged start with this
cfg.define('nologprefix', '[nolog]')
# and are replaced with
cfg.define('nologmsg', '-= THIS MESSAGE NOT LOGGED =-')

logfiles = {}
stopped = False

 # Formats are defined here. simple also provides default values if values
 # are not supplied by the format, as well as format 'simple'. 
 # Parameters that should be supplied:
 #   * timestamp_format: format of timestamp in log files
 #     * all strftime vars supported.
 #   * filename: file name for log
 #     * var channel : full channel ie. #dunkbot
 #     * var channel_name : channel without '#' ie. dunkbot
 #   * event_filename: 
 #        if event_filename exists, then it will be used for
 #        logging events (seperate from chat)
 #     * var channel : full channel ie. #dunkbot
 #     * var channel_name : channel without '#' ie. dunkbot
 #   * separator: the separator between the timestamp and message
formats = {
    'simple': {
        'timestamp_format': '%Y-%m-%d %H:%M:%S',
        'basepath': None,
        'filename': 'logs/simple/%(channel)s.%Y%m%d.slog',
        'event_prefix': '',
        'event_filename': 'logs/simple/%(channel_name)s.%Y%m%d.slog',
        'separator': ' | ',
    },
    'supy': {
        'timestamp_format': '%Y-%m-%dT%H:%M:%S',
        'filename': 'logs/supy/%(channel)s/%(channel)s.%Y-%m-%d.log',
        'event_prefix': '*** ',
        'event_filename': None,
        'separator': '  ',
    }
}

# Get a format opt in the currently cfg'd format
def format_opt(name):
    simple_format = formats['simple']
    format = formats.get(cfg.get('format'), 'simple')
    opt = format.get(name, simple_format.get(name, None))
    return opt

def init():
    global stopped
    callbacks.add('ALL', chatlogcb, prechatlogcb)
    jcallbacks.add('ALL', jabberchatlogcb, jabberprechatlogcb)
    outmonitor.add('chatlog', chatlogcb, prechatlogcb)
    xmppmonitor.add('chatlog', jabberchatlogcb, jabberprechatlogcb)
    stopped = False
    return 1

def shutdown():
    global stopped
    stopped = True
    for file in logfiles.values():
        file.close()
    return 1

def timestr():
    return time.strftime(format_opt('timestamp_format'))

def write(channel, txt, event=False):
    if stopped:
        return
    f = time.strftime(format_opt('filename'))%({
        'channel': channel, 
        'channel_name': channel[1:]
    })
    # if this is an event, and there is an event_filename, use that
    # instead of filename
    if event:
        event_filename = format_opt('event_filename')
        if event_filename:
            f = time.strftime(event_filename)%({
                'channel': channel, 
                'channel_name': channel[1:]
            })

    # if there is a basepath specified, append it,
    # else it should go to a dir relative to the 
    # gozerbot dir.
    basepath = cfg.get('basepath')
    if basepath:
        f = path.join(basepath, f)

    # create dir if it doesn't exist
    dir = path.dirname(f)
    if not path.exists(dir):
        os.makedirs(dir)

    try:
        logfiles[f].write(txt)
        logfiles[f].flush()
    except KeyError:
        try:
            rlog(5, 'chatlog', 'opening %s for logging'%(f))
            logfiles[f] = open(f, 'a')
            logfiles[f].write(txt)
            logfiles[f].flush()
        except Exception, ex:
            rlog(10, 'chatlog', str(ex))
    except Exception, ex:
        rlog(10, 'chatlog', str(ex))

def log(bot, ievent):
    chan = ievent.channel
    prefix = "%s%s"%(timestr(), format_opt('separator'))
    event_prefix = "%s%s"%(prefix, format_opt('event_prefix'))
    if ievent.cmnd == 'PRIVMSG':
        if ievent.txt.startswith('\001ACTION'):
            txt = ievent.txt[7:-1].strip()
            write(chan, '%s* %s %s\n' % (prefix, ievent.nick, txt))
        else:
            write(chan, '%s<%s> %s\n' % (prefix, ievent.nick, ievent.origtxt)) 
    elif ievent.cmnd == 'NOTICE':
        write(ievent.arguments[0], '%s-%s- %s\n'%(
            prefix, ievent.nick, ievent.txt
        ))
    elif ievent.cmnd == 'TOPIC':
        write(chan, '%s%s changes topic to "%s"\n'%(
            event_prefix, ievent.nick, ievent.txt
        ), event=True)
    elif ievent.cmnd == 'MODE':
        write(chan, '%s%s sets mode: %s\n'%(
            event_prefix, ievent.nick, ' '.join(ievent.arguments[1:])
        ), event=True)
    elif ievent.cmnd == 'JOIN':
        write(chan, '%s%s (%s) has joined\n'%(
            event_prefix, ievent.nick, ievent.userhost
        ), event=True)
    elif ievent.cmnd == 'KICK':
        write(chan, '%s%s was kicked by %s (%s)\n'%(
            event_prefix, ievent.arguments[1], ievent.nick, ievent.txt
        ), event=True)
    elif ievent.cmnd == 'PART':
        write(chan, '%s%s (%s) has left\n'%(
            event_prefix, ievent.nick, ievent.userhost
        ), event=True)
    elif ievent.cmnd == 'NICK':
        if not bot.userchannels.has_key(ievent.nick.lower()):
            return
        for c in bot.userchannels[ievent.nick.lower()]:
            if [bot.name, c] in cfg.get('channels'):
                if c in bot.state['joinedchannels']:
                    write(c, '%s%s (%s) is now known as %s\n'%(
                        event_prefix, ievent.nick, ievent.userhost, ievent.txt
                    ), event=True)
    elif ievent.cmnd == 'QUIT':
        if not bot.userchannels.has_key(ievent.nick.lower()):
            return
        for c in bot.userchannels[ievent.nick.lower()]:
            if [bot.name, c] in cfg.get('channels'):
                if c in bot.state['joinedchannels']:
                    write(c, '%s%s (%s) has quit: %s\n'%(
                        event_prefix, ievent.nick, ievent.userhost, ievent.txt
                    ), event=True)

def jabberlog(bot, ievent):
    if ievent.botoutput:
        chan = ievent.to
    else:
        chan = ievent.channel
    if ievent.cmnd == 'Message':
            txt = ievent.txt.strip()
            write(chan, '%s | <%s> %s\n' % (timestr(), ievent.nick, txt))
    elif ievent.cmnd == 'Presence':
            if ievent.type == 'unavailable':
               txt = "%s left" % ievent.nick
            else:
               txt = "%s joined" % ievent.nick
            write(chan, '%s | %s\n' % (timestr(), txt))

def prechatlogcb(bot, ievent):
    """Check if event should be logged.  QUIT and NICK are not channel
    specific, so we will check each channel in log()."""
    if not ievent.msg and (bot.name, ievent.channel) in cfg.get('channels'):
        return 1
    if ievent.cmnd in ('QUIT', 'NICK'):
        return 1
    if ievent.cmnd == 'NOTICE':
        if [bot.name, ievent.arguments[0]] in cfg.get('channels'):
            return 1

def chatlogcb(bot, ievent):
    log(bot, ievent)

def jabberprechatlogcb(bot, ievent):
    if not ievent.groupchat:
        return 0
    if (bot.name, ievent.channel) in cfg.get('channels') or ievent.botoutput:
        return 1

def jabberchatlogcb(bot, ievent):
    jabberlog(bot, ievent)

def handle_chatlogon(bot, ievent):
    chan = ievent.channel
    if (bot.name, chan) not in cfg.get('channels'):
        cfg.get('channels').append((bot.name, chan))
        cfg.save()
        ievent.reply('chatlog enabled on (%s,%s)' % (bot.name, chan))
    else:
        ievent.reply('chatlog already enabled on (%s,%s)' % (bot.name, \
chan))
cmnds.add('chatlog-on', handle_chatlogon, 'OPER')
examples.add('chatlog-on', 'enable chatlog on <channel> or the channel \
the commands is given in', '1) chatlog-on 2) chatlog-on #dunkbots')

def handle_chatlogoff(bot, ievent):
    try:
        cfg.get('channels').remove((bot.name, ievent.channel))
        cfg.save()
    except ValueError:
        ievent.reply('chatlog is not enabled in (%s,%s)' % (bot.name, \
ievent.channel))
        return
    ievent.reply('chatlog disabled on (%s,%s)' % (bot.name, ievent.channel))

cmnds.add('chatlog-off', handle_chatlogoff, 'OPER')
examples.add('chatlog-off', 'disable chatlog on <channel> or the channel \
the commands is given in', '1) chatlog-off 2) chatlog-off #dunkbots')
