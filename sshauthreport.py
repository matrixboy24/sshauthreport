#!/usr/bin/python
# coding: utf-8

#Importing default needed modules
import json
import os
import os.path
import re
import time
#Loading configuration...

config_file = open('config.json') #Opening the config file
config_json = json.load(config_file) #Load JSON in config_json
authlogPath = config_json["authlogPath"]
usersWhoAuthNeedAlert = []
alreadyAlertedConnexion = [] #Contain the connexion session id wich are already been alerted
useTelegramBot = False
if config_json["telegram"]["useYourOwnBot"] == True:
    import telepot #Import the telegram bot api for python (telebot) if the user will use his personal Telegram bot
    bot = telebot.TeleBot(config_json["telegram"]["yourBotApiKey"]) #Loading the bot
    useTelegramBot = True

def checkTheLogs():
    sshLogin = False

    #here check the logs to find an ssh connexion
    if os.path.exists(authlogPath): #if the log file exist
        logFile = open(authlogPath, 'r') #open it (in read only mode)
        #read the file, search for connexions
        # Make sure we're at the start of the file
        logFile.seek(0)
        logsLines = logFile.readlines()
        logFile.close() #close the file after reading
        for line in logsLines:
            print(line)
            # example line sshd[session_id]: Accepted password for username from 77.15... port 56.. ssh2
            #looking for line who specify an ssh sucessful connexion
            authSearchRegex = re.search(r"^(?P<mounth>\w{3}) (?P<day>\d{2}) (?P<hour>\d{2}:\d{2}:\d{2}) (?P<serverprefix>.*) sshd\[(?P<session_id>\d+)\]: Accepted password for (?P<username>.*) from (?P<from_ip>.*) port (?P<from_port>\d+)",line)
            if authSearchRegex is not None:
                serverprefix = authSearchRegex.group("serverprefix")
                session_id = authSearchRegex.group("session_id")
                username = authSearchRegex.group("username")
                from_ip = authSearchRegex.group("from_ip")
                from_port = authSearchRegex.group("from_port")
                if session_id in alreadyAlertedConnexion == False:#If the alert for this session was not already sended then
                    message = config_json["telegram"]["message"] #import the raw message from the config file
                    message.replace("%ip%",from_ip) #loads vars in the message
                    message.replace("%user%",username)
                    message.replace("%servername%",serverprefix)
                    print("New ssh connexion on " + str(serverprefix) + " id: " + str(session_id) + " user: " + str(username) + " from: " + str(from_ip) + ":" + str(from_port))
                    if useTelegramBot == True:
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
