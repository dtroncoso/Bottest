import sys, os
import logging
import subprocess
from flask import Flask, make_response
from slack import WebClient
from time import sleep
from slackeventsapi import SlackEventAdapter
from coinbot import CoinBot

#variables usadas para permitir o no DEPLOY
habilitadoDemo = True;
habilitadoTest = True;

# Initialize a Flask app to host te events adapter
app = Flask(__name__)
# Create an events adapter and register it to an endpoint in the slack app for event injestion.
slack_events_adapter = SlackEventAdapter(os.environ.get("SLACK_EVENTS_TOKEN"), "/slack/events", app)

# Initialize a Web API client
slack_web_client = WebClient(token=os.environ.get("SLACK_TOKEN"))

def flip_coin(channel):
    """ flip the coin and send the message to the channel
    """
    # Create a new CoinBot
    coin_bot = CoinBot(channel)

    # Get the onboarding message payload
    message = coin_bot.get_message_payload()

    # Post the onboarding message in Slack
    slack_web_client.chat_postMessage(**message)


# When a 'message' event is detected by the events adapter, forward that payload
# to this function.
@slack_events_adapter.on("app_mention")
def message(payload):
    """Parse the message event, and if the activation string is in the text.
    """
    global habilitadoTest
    global habilitadoDemo
    # Get the event data from the payload
    event = payload.get("event", {})
    #make_response('No-Retry', 200, {"X-Slack-No-Retry": 1})
    # Get the text from the event that came through
    text = event.get("text")
    # Check and see if the activation phrase was in the text of the message.
    # If so, execute the code to flip a coin.
    # Chequear por las palabras en el texto, en caso de coincidir ejecutar el codigo siguiente.
    if "tira una moneda" in text.lower():
        channel_id = event.get("channel")
        return flip_coin(channel_id)
    elif "deploy" in text:
        # Since the activation phrase was met, get the channel ID that the event
        # was executed on
        channel_id = event.get("channel")
        x = text.split('deploy',1)[1]
        y= x.split()
        if len(y) == 3:
            deploy(y)
        else:
            ayuda()
    elif "disable" in text:
        #deshabilita test y demo para DEPLOY
        channel_id = event.get("channel")
        x = text.split('disable',1)[1]
        y= x.split()
        print(" mirando ",y[0])
        if len(y) == 1:
            if y[0].upper()=='TEST':
                habilitadoTest = False
                print('des test')
            elif y[0].upper()=='DEMO':
                print('estaba en ',habilitadoDemo)
                habilitadoDemo = False
                print('des demo',habilitadoDemo)
    elif "enable" in text:
        #habilita test y demo para DEPLOY
        channel_id = event.get("channel")
        x = text.split('enable',1)[1]
        y= x.split()
        if len(y) == 1:
            if y[0].upper()=='TEST':
                habilitadoTest = True
                print('hab test',habilitadoTest)
            elif y[0].upper()=='DEMO':
                habilitadoDemo = True
                print('hab demo',habilitadoDemo)
    elif "status" in text:
        channel_id = event.get("channel")
        x = text.split('status',1)[1]
        y= x.split()
        if len(y) == 1:
            status(y)
        else:
            ayuda()
    elif "gracias" in text:
        channel_id = event.get("channel")
        frase()
    else:
       ayuda()

#ejecuta script de ayuda
def ayuda():
    subprocess.Popen(['bash', '/home/slackbot/presenta.sh'])
def frase():
        subprocess.Popen(['bash','frase.sh'])
        #subprocess.Popen(['bash','/home/slackbot/frase.sh'])
#ejecuta script de deploy
def deploy(y):
    global habilitadoTest
    global habilitadoDemo
    print('result', y[1],habilitadoDemo,habilitadoTest)
    if (y[1].upper()=='TEST' and habilitadoTest) or (y[1].upper()=='DEMO' and habilitadoDemo)or (y[1].upper()=='MOONITOREO'):
        subprocess.Popen(['sh', '/home/slackbot/corre.sh',y[0].upper(),y[1].upper(),y[2]])
    else:
        if (y[1].upper()=='TEST') or (y[1].upper()=='DEMO') or (y[1].upper()=='MOONITOREO'):
            subprocess.Popen(['sh', '/home/slackbot/mensajeBloqueado.sh',y[1].upper()])

#ejecuta script statusBranch
def status(y):
    subprocess.Popen(['sh', '/home/slackbot/statusBranch.sh',y[0].upper()])


if __name__ == "__main__":
    # Create the logging object
    logger = logging.getLogger()

    # Set the log level to DEBUG. This will increase verbosity of logging messages
    logger.setLevel(logging.DEBUG)

    # Add the StreamHandler as a logging handler
    logger.addHandler(logging.StreamHandler())

    # running it on localhost, which is traditional for development.
    app.run(host='0.0.0.0', port=PUERTO)
