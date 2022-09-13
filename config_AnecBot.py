import os

# When you create your bot in Bot_father, it gives you the token, enter this token here
# Note, that *** should not be actually left anywhere in this code, here it should be 
    # just token in the quotation marks, for example
TOKEN = '***ENTER YOUR TELEGRAM BOT TOKEN HERE***'

# This is not needed in general in the bot's creation and deploy. 
    # I personally needed my telegram ID and the one of my telegram channel
    # for the bot to send some messages specifically to me or my channel
    # To find your IDs you can use one of numerous bots which are specified in doing so (I personally used @username_to_id_bot)
id_of_channel = ***ENTER THE TELEGRAM ID OF YOUR TELEGRAM CHANNEL (OPTIONAL)***
my_id = ***ENTER YOUR TELEGRAM ID (OPTIONAL)***


# Postgress server database info
# Once you obtained the heroku-postrgress database, in the settings you can find its credentials,
    # add these credentials here
USER = '***ENTER THE USERNAME OF YOUR DATABASE CONNECTION***'
PASSWORD = '***ENTER THE PASSWORD OF YOUR DATABASE CONNECTION***'
HOST = '***ENTER THE HOST OF YOUR DATABASE CONNECTION***'
PORT = '***ENTER THE PORT OF YOUR DATABASE CONNECTION***'
DATABASE = '***ENTER THE DATABASE ID OF YOUR DATABASE***'


# The name of your app on heroku is needed for webhook!!!!
HEROKU_APP_NAME = '***ENTER YOU HEROKU APP NAME***'


# webhook settings, leave it as it is here!
WEBHOOK_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
WEBHOOK_PATH = f'/webhook/{TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

# webserver settings, leave it as it is here!
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = int(os.getenv('PORT', 0))
