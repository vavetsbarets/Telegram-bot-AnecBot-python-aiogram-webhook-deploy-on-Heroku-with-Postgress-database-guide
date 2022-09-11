# How to connect a telegram bot to a database, make it run on webhooks and deploy it on the server?

While creating this telegram bot, I saw plenty of videos about how to create telegram bots on python and how to create and handle different buttons and other features of the bot. However, there is lack of information about how to deploy the bot on the server, so it can run 24/7 and how to make it run on webhooks, so that the bot can operate much faster than they do if they are run using long-polling technique. In this tutorial I want to share my own experience in this topic and, using my own project, show how to run the Telegram bot with the Postress database on the Heroku server with the help of webhooks. 

## General information about aiogram

[About creation bot in general](https://www.youtube.com/watch?v=I8K3iYcxPl0) (watch from 1:45 to 5:15)
Author creates simple echo bot 

[Info about buttons](https://www.youtube.com/watch?v=I8K3iYcxPl0)
Starts from echo bot and adds some more  
features

## make the bot run on webhooks and deploy it on the server using Heroku

## Connect to the Postgress database to the bot and the Heroku server, using Heroku Postgresser
Just connect to database in psycopg2 and so on
