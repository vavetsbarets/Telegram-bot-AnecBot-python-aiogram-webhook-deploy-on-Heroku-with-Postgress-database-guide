# How to connect a telegram bot to a database, make it run on webhooks and deploy it on the server?

While creating this telegram bot, I saw plenty of videos about how to create telegram bots on python and how to create and handle different buttons and other features of the bot. However, there is lack of information about how to deploy the bot on the server, so it can run 24/7 and how to make it run on webhooks, so that the bot can operate much faster than they do if they are run using long-polling technique. In this tutorial I want to share my own experience in this topic and, using my own project, show how to run the Telegram bot with the Postress database on the Heroku server with the help of webhooks. 

## General information about aiogram
Here is some information about the specific syntaxis of aiogram to get more understanding about the code in bot_anecbot.py and how aiogram works in general. 
  
1. [About creation bot in general](https://www.youtube.com/watch?v=I8K3iYcxPl0) (watch from 1:45 to 5:15)  
Author creates simple echo bot (bot replies with the same text as the one in the message sent by user) on aiogram and runs it locally (video is in Russian, but the author shows all the code and the outcome, so the part of the video can be quite clear even for non-Russian speakers)  
  
2. [Info about keyboard buttons appearance when using the bot](https://www.youtube.com/watch?v=I8K3iYcxPl0)  
The author of this video starts with the echo bot (almost the same code as the outcome at the 4:45 of the first video) and then adds the Keyboard buttons and write some simple algorithms in the handlers of the created buttons (video is in Russian as well, but the author shows all the code and the outcome, so the part of the video can also be quite clear even for non-Russian speakers)  
  
Now you have more understanding of how aiogram works. In the bot_anecbot.py the same syntaxis is used, but there are more buttons and algorithms than in the videos above and there is some work with psycopg2 as well (you can check Postgresser_telegram_bot.py file with the functions which deal with the database as well). Note, that you may find types.InlineKeyboardMarkup or types.InlineKeyboardButton and @dp.callback_query_handler(lambda call:True) unfamiliar, but the first couple represents the keyboard and the button under some message sent by the bot (I will attach the example of such buttons below, with buttons from 1 to 10 and "Добавить в "Сохранённые"" being under the message) and the second is the handler which handles all the buttons of such type. CHANGE SIZE OF PHOTO!!!
![image](https://user-images.githubusercontent.com/92990826/189541909-bf5ce124-cc3b-4d57-91ad-d0fddc7e422d.png | width = 100)


For more understanding: python files bot and postgresser (what I explain there) + try this bot in Telegram (may not run, if so, you can write me email or here and I will turn it on), other videos 

## make the bot run on webhooks and deploy it on the server using Heroku
Show Howdi video and say that I did similar, but there are some differences, due to webhook, also mention that git is used to publish basically

## Connect to the Postgress database to the bot and the Heroku server, using Heroku Postgresser
Just connect to database in psycopg2 and so on

## Sources, list all of the sources!!!

## Questions
Thanks! If you have questions write me
