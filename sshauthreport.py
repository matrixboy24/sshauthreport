#!/usr/bin/python
# coding: utf-8

import os
import time
import json
#Loading configuration...

config_file = open('config.json') #Opening the config file
config_json = json.load(config_file) #Load JSON in config_json
servername = config_json["%servername%"]
useTelegramBot = False
if config_json["telegram"]["useYourOwnBot"] == True:
    import telepot #Import the telegram bot api for python (telebot) if the user will use his personal Telegram bot
    bot = telebot.TeleBot(config_json["telegram"]["yourBotApiKey"]) #Loading the bot
    useTelegramBot = True

def checkTheLogs():
    sshLogin = False
    usersWhoAuthNeedAlert = []
    #here check the logs to find an ssh connexion
    if sshLogin == True:
        user = ""
        ip = ""
        print("new ssh connexion ! Sending alert !")
        if useTelegramBot == True:
            message = config_json["telegram"]["message"] #import the raw message from the config file
            message.replace("%ip%",ip) #loads vars in the message
            message.replace("%user%",user)
            message.replace("%servername%",servername)
            bot.sendMessage(config_json["telegram"]["yourTelegramId"], message) #Send the message to the Telegram user refered in the config file
        for urlObj in config_json["urls"]: #For each url refered in the config file
            url = urlObj["url"]
            message = urlObj["%message%"]
            url.replace("%message%",message) #put the message in the url
            urllib2.urlopen(url.encode('utf-8')) #then visit the url


    return False

while 1:
    checkTheLogs()
    time.sleep(1)
