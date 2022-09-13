# How to connect a telegram bot to a database, make it run on webhooks and deploy it on the server?

## 1. Intro

While creating this telegram bot, I saw plenty of videos about how to create telegram bots on python and how to create and handle different buttons and other features of the bot. However, there is lack of information about how to deploy the bot on the server, so it can run 24/7 and how to make it run on webhooks, so that the bot can operate much faster than they do if they are run using long-polling technique. In this tutorial I want to share my own experience in this topic and, using my own project, show how to run the Telegram bot with the Postress database on the Heroku server with the help of webhooks. 

## 2. General information about aiogram
Here is some information about the specific syntaxis of aiogram to get more understanding about the code in bot_anecbot.py and how aiogram works in general. 
  
1. [About creation bot in general](https://www.youtube.com/watch?v=I8K3iYcxPl0) (watch from 1:45 to 5:15)  
Author creates simple echo bot (bot replies with the same text as the one in the message sent by user) on aiogram and runs it locally (video is in Russian, but the author shows all the code and the outcome, so the part of the video can be quite clear even for non-Russian speakers)  
  
2. [Info about keyboard buttons appearance when using the bot](https://www.youtube.com/watch?v=I8K3iYcxPl0)  
The author of this video starts with the echo bot (almost the same code as the outcome at the 4:45 of the first video) and then adds the Keyboard buttons and write some simple algorithms in the handlers of the created buttons (video is in Russian as well, but the author shows all the code and the outcome, so the part of the video can also be quite clear even for non-Russian speakers)  
  
Now you have more understanding of how aiogram works. In the bot_anecbot.py the same syntaxis is used, but there are more buttons and algorithms than in the videos above and there is some work with psycopg2 as well (you can check Postgresser_telegram_bot.py file with the functions which deal with the database as well). Note, that you may find types.InlineKeyboardMarkup or types.InlineKeyboardButton and @dp.callback_query_handler(lambda call:True) unfamiliar, but the first couple represents the keyboard and the button under some message sent by the bot (I will attach the example of such buttons below, with buttons from 1 to 10 and "Добавить в "Сохранённые"" being under the message) and the second is the handler which handles all the buttons of such type.  
<img src="https://user-images.githubusercontent.com/92990826/189541909-bf5ce124-cc3b-4d57-91ad-d0fddc7e422d.png" width=65% height=65%>  
  
So you can inspect bot_anecbot.py and Postgreser_telegram_bot.py for more understanding of how aiogram works (there are some explanations provided there) and, of course, you can find some more advanced aiogram tutorials on the internet. Also it may be helpful to try out the bot itself, so here is the [link](https://t.me/bot_anecbot) to it. If the bot does not work/respond, it may be turned off. You can email me (v.s.averin26@gmail.com) if you want to try this bot out, and I will turn it back on (note, that the bot is in Russian). 

## 3. make the bot run on webhooks and deploy it on the server using Heroku
While I was creating this bot [this video](https://www.youtube.com/watch?v=TtvNVDilh60&t=590s) about deploying Telegram Bot on Heroku was really helpful to me (the author starts deploying the bot at 9:50 in the video). This video is in Russian and the author used long-polling method to deploy the bot, so I am going to show how to deploy the bot on webhooks using Heroku, using my project. However, with some minor changes, you can deploy simple echo bot as well (I will explain it later as well). Basically, there some minor differences compared to the algorithm in the video which was mentioned previously.

### a) How did I deploy my bot
#### i) Preparatory steps
1. Install git and github on your computer and create an account in Heroku. 
2. Creating Procfile, requirements.txt, config_Anecbot.py, runtime.txt. You can check what each file means in these files in the repository itself. 
#### ii) Running the bot on webhooks instead of long-polling
Here I list some changes which allow me to deploy the bot on webhooks instead of long-polling: 
1. Changes in bot_anecbot.py: you should import start_webhook function from aiogram.utils.executor (line 26 of bot_anecbot.py) and change if __name__ == '__main__' bit of code and the end of file (check the bottom of the bot_anecbot.py to see the differences. You can delete on_startup and on_shutdown arguments in your project if you don't want your bot to do anything when it's turned on/off)
2. Changes in config_AnecBot.py: just adding this chunk of code in the file (this chunk is exactly how it looks in my final project)
<img src = "https://user-images.githubusercontent.com/92990826/189881862-5c8d9098-7449-488e-b3f0-d7a7aa5be925.png">

### b) How to deploy simple echo bot

## Connect to the Postgress database to the bot and the Heroku server, using Heroku Postgresser
Just connect to database in psycopg2 and so on

## Sources, list all of the sources!!!

## Questions
Thanks! If you have questions write me
