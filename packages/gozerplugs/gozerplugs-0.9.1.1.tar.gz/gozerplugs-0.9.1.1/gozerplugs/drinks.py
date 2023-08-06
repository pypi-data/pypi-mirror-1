# plugs/drinks.py
#
#

from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.plughelp import plughelp
import os, string, random

plughelp.add('drinks', 'serve coffee/tea or beer')

coffee = ['booo', ]
tea = ['booo', ]
beer = ['booo', ]

def init():
    global coffee
    global tea
    global beer
    for i in  coffeetxt.split('\n'):
        if i:
            coffee.append(i.strip())
    for i in teatxt.split('\n'):
        if i:
            tea.append(i.strip())
    for i in beertxt.split('\n'):
        if i:
            beer.append(i.strip())
    return 1

def handle_coffee(bot, ievent):
    """ get a coffee """
    rand = random.randint(1,len(coffee))
    bot.action(ievent.channel,coffee[rand-1])    

def handle_tea(bot, ievent):
    """ get a tea """
    rand = random.randint(1,len(tea))
    bot.action(ievent.channel,tea[rand-1])
    
def handle_beer(bot, ievent):
    """ get a beer  """
    rand = random.randint(1,len(beer))
    bot.action(ievent.channel,beer[rand-1])

cmnds.add('coffee', handle_coffee, 'USER')
examples.add('coffee', 'get a coffee quote', 'coffee')

cmnds.add('tea', handle_tea, 'USER')
examples.add('tea', 'get an tea', 'tea')

cmnds.add('beer', handle_beer, 'USER')
examples.add('beer', 'get a beer', 'beer')

coffeetxt = """ pours a cup of coffee with two sweets..
pours a cup of espresso for you
gives you a glass of irish coffee
gives you a cappuccino
"""

teatxt = """ tea is for pussies!
"""

beertxt = """ gives you a warsteiner halfom. cheers!
gives a leffe blond. enjoy!
"""
