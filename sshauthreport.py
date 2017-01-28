#!/usr/bin/python
# coding: utf-8

#Importing default needed modules
import calendar
import datetime
import json
import os
import os.path
import re
import shutil
import time
import urllib2
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
    #here check the logs to find an ssh connexion
    if os.path.exists(authlogPath): #if the log file exist
        #make a copy of the log file to open it without conflict with the rsyslog servico
        shutil.copy2(authlogPath, "auth.log.temp")
        logFile = open("auth.log.temp", 'r') #open the copy of the file (in read only mode)
        #read the file, search for connexions
        logFile.seek(0) #make sure we are at the start of the file
        logsLines = logFile.readlines()
        logFile.close() #close the file after reading
        os.remove("auth.log.temp") #delete the copy of the file
        for line in logsLines:#for each line of the file
            authSearchRegex = re.search(r"^(?P<mounth>\w{3}) (?P<day>\d{2}) (?P<hour>\d{2}:\d{2}:\d{2}) (?P<serverprefix>.*) sshd\[(?P<session_id>\d+)\]: Accepted password for (?P<username>.*) from (?P<from_ip>.*) port (?P<from_port>\d+)",line)
            if authSearchRegex is not None: #if the line we reading specify an ssh sucessful connexion
                serverprefix = authSearchRegex.group("serverprefix")
                session_id = authSearchRegex.group("session_id")
                username = authSearchRegex.group("username")
                from_ip = authSearchRegex.group("from_ip")
                from_port = authSearchRegex.group("from_port")
                hour = authSearchRegex.group("hour")
                if session_id in alreadyAlertedConnexion:
                    break
                else:#and if the alert for this session was not already sended then
                    alreadyAlertedConnexion.append(session_id) #we add this session id to the list of already alerted connexion
                    message = config_json["message"] #import the raw message from the config file
                    #loads vars in the message
                    message = re.sub(r"%ip%", from_ip, message)
                    message = re.sub(r"%user%", username, message)
                    message = re.sub(r"%servername%", serverprefix, message)
                    print("New ssh connexion on " + str(serverprefix) + " id: " + str(session_id) + " user: " + str(username) + " from: " + str(from_ip) + ":" + str(from_port))
                    if useTelegramBot == True:
                        bot.sendMessage(config_json["telegram"]["yourTelegramId"], message) #Send the message to the Telegram user refered in the config file
                    for urlObj in config_json["urls"]: #For each url refered in the config file
                        url = urlObj["url"]
                        url = re.sub(r"%message%", message, url) #put the message in the url
                        urllib2.urlopen(url.encode('utf-8')) #then visit the url

while 1:
    checkTheLogs()
    time.sleep(10)#important to set a timer of 10 seconds here to prevent problem with the rsyslog service who write the auth log file
