from transitions import Machine
from transitions.extensions import GraphMachine
import random
from linebot import LineBotApi, WebhookParser, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage

class Cat(object):

    states = ['asleep', 'hungry', 'dirty', 'walking', 'savingcat']
    def __init__(self, name):
        self.name = name
        self.cat_rescued = 0
        self.distance = 0
        self.machine = GraphMachine(model=self, states=Cat.states, initial='asleep')
        self.machine.add_transition(trigger='wakeup', source='asleep', dest='walking')
        self.machine.add_transition(trigger='run', source='walking', dest='hungry', after='updatedis')
        self.machine.add_transition(trigger='eat', source='hungry', dest='walking')
        self.machine.add_transition(trigger='savecat', source='*', dest='savingcat', conditions='farenough')
        self.machine.add_transition(trigger='done', source='savingcat', dest='dirty', after='updatecat')
        self.machine.add_transition(trigger='clean', source='dirty', dest='asleep', conditions=['is_tired'])
        self.machine.add_transition(trigger='clean', source='dirty', dest='walking')
        self.machine.add_transition(trigger='nap', source='*', dest='asleep')
    def farenough(self):
        return self.distance >= 100
    def updatedis(self):
        self.distance += random.randint(25, 35)
        if self.distance >= 100:
            self.distance = 100

    def updatecat(self):
        print('one more')
        self.cat_rescued += 1
        self.distance = 0

    def is_tired(self):
        return random.random() < 0.5

    def advance(self, bot, event, text):
        helper = 'Now is: {0}\nDistance: {1}\nCat rescued: {2}\ntype \'cmd\' for action list'.format(self.state, self.distance, self.cat_rescued)
        cmd_list = 'wakeup\nrun\neat\nsavecat\ndone\nclean\nnap'
        if text == 'help':
            bot.reply_message(event.reply_token, TextSendMessage(text=helper))
        elif text == 'cmd':
            bot.reply_message(event.reply_token, TextSendMessage(text=cmd_list))
        else:
            try:
                self.trigger(text)
                display = 'Caster is now %s'%self.state
                if text == 'wakeup':
                    bot.reply_message(event.reply_token, TextSendMessage(text=display))
                elif text == 'run':
                    bot.reply_message(event.reply_token, TextSendMessage(text='Distance now: {0}, and Caster is now {1}'.format(self.distance,self.state)))
                elif text == 'eat':
                    bot.reply_message(event.reply_token, TextSendMessage(text=display))
                elif text == 'savecat':
                    if self.distance < 100:
                        bot.reply_message(event.reply_token, TextSendMessage(text='Keep running, distance not enough'))
                    else:
                        bot.reply_message(event.reply_token, TextSendMessage(text=display))
                elif text == 'done':
                    # bot.reply_message(event.reply_token, TextMessage(text=helper))
                    rep = ImageSendMessage(original_content_url='https://i.imgflip.com/70jhcb.jpg', preview_image_url='https://i.imgflip.com/70jhcb.jpg')
                    bot.reply_message(event.reply_token, rep)
                elif text == 'clean':
                    bot.reply_message(event.reply_token, TextSendMessage(text=display))
                elif text == 'nap':
                    bot.reply_message(event.reply_token, TextSendMessage(text=display))
            except:
                if self.state == 'hungry':
                    bot.reply_message(event.reply_token, TextSendMessage(text='Must eat!'))
                else:  
                    bot.reply_message(event.reply_token, TextSendMessage(text='can\'t trigger'))