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
<img src = "https://user-images.githubusercontent.com/92990826/189881862-5c8d9098-7449-488e-b3f0-d7a7aa5be925.png" width=40% height=40%>  
  
3. Changes in the Procfile: just write 'web' instead of 'worker' (check Procfile in the repository)     
#### iii) Deploying the bot (on webhook) using heroku  
Once the previous steps are done, these are the final steps in order to deploy the bot on the Heroku servers (note, that I deployed the bot using the computer with Windows, but I think that the same steps can be successfully done on MacOS, Linux and other systems as well):  
1. Open the command line (shell, Powershell etc)  
2. Move to the path where your project is located using cd (i.e. type 'cd D:/Documents/Bot' in your command line if the project lies in the D:/Documents/Bot directory) (Note that here and further on when it says type 'something', you should type something without single quotation marks)  
3. Type and run 'heroku login' and then press any key other than q as it is asked in the shell  
4. Checked that it says 'logged in' by Heroku CLI in the opened browser  
5. Then type in the command line and run 'git init' then 'git add' and then 'git commit -m "***TYPE ANY MESSAGE ABOUT VERSION AS YOU WISH***"'  
6. Type 'heroku create ***AppName***' (AppName can be any which was not previously used in Heroku)
7. Type 'git remote -v' to check that you can push your project and then type 'git push heroku master' to actually deploy your project to Heroku (this process may take several minutes and there is one more step before the bot starts to work)
8. If there were no errors during the deploy, then go to your heroku account, you should see that there is an app there like in the photo below:   
<img src = "https://user-images.githubusercontent.com/92990826/189923736-7764dafb-9f13-40fc-a446-bf646d71e505.png" width=40% height=40%>  
Then click on your deployed app. Here you should see something like that: 
<img src = "https://user-images.githubusercontent.com/92990826/189924799-122930f4-84f6-4a89-bd8d-ce44931e1800.png" width=80% height=80%>  
Click on Configure Dynos and then you should see this:  
<img src = "https://user-images.githubusercontent.com/92990826/189925386-4cec6341-ef04-434c-a6eb-0682f6ee886f.png">
Click on the 'pen' (edit dyno formation) and then turn on the bot and press confirm like in the photo below (I have 7.00 dollars plan, but when you first do that, it should be free plan, then you can easily switch to any of non-free plans if you wish):  
<img src = "https://user-images.githubusercontent.com/92990826/189925725-0a0596f3-1d69-4b22-a314-24bb755ba1c3.png">
  
9. Basically your bot is deployed and turned on. After that I usually View logs to make sure there are no errors and I recommend you to do it as well. To do so click More and View logs like in the photo below:  
<img src = "https://user-images.githubusercontent.com/92990826/194127740-597421c0-1cad-4034-8c85-73d47c55b6e3.png">


### b) How to deploy simple echo bot
Well, all you need to do is to copy my repository and do some changes:  
1. You can delete these files: all markdown files, requirements.txt, Postgresser_telegram_bot.py, robot_saying_hi.webp 
2. Instead of my code in bot_anecbot.py you can put the one which can be found at 4:45 [here](https://www.youtube.com/watch?v=I8K3iYcxPl0)
3. Slight change to the point above: change if __name__ == '__main__': clause onto this one:
<img src = "https://user-images.githubusercontent.com/92990826/194242507-d240f8c0-e9a3-4163-aecf-4551a39830f3.png">  
But also delete on_startup and on_shutdown arguremnts, since you don't have them in the echo bot.  
4. In config_AnecBot.py delete all variables related to the database (USER, PASSWORD, HOST, PORT, DATABASE)
5. do all the steps in the section a) and your echo bot should be working on the Heroku server!


## Connect to the Postgress database to the bot and the Heroku server, using Heroku Postgres add-on
1. Just find Add-on Heroku Postgres on Heroku and choose plan that you want. Do that once you've created the app by deploying the Bot (so first deploy the bot and then install add-on to it). 
2. After installing this add-on you should see this add-on like on this photo (if you didn't install Papertail, you would not see this add-on on your account):
<img src = "https://user-images.githubusercontent.com/92990826/194247224-1eb17f42-26a8-4961-8fe7-f2f2f52b50ec.png">
3. Then click on this Heroku Postgres add-on and then go to the settings like in the photo below: 
<img src = "https://user-images.githubusercontent.com/92990826/194247665-01c9051a-88f2-4bb5-ab51-73e7a7e6ea1e.png">
4. Once you've clicked on settings you can see View Credentials button and once you've clicked there you will find all info which you can use in configs and so on, to access the database manually and automatically in your code, so now you have database which can be attached to your bot!  

## Sources
Here I want to thank all the resources, which helped me to create this bot: 
Youtube Channels: [Howdi Ho](https://www.youtube.com/c/HowdyhoNet), [Physics is simple](https://www.youtube.com/c/PhysicsisSimple)  
And all the creators of the packages used in my code which made the creation of the bot possible

## Questions
Thank you for reading this guide! Hope that it may be helpful! If you have any questions please write me on email: v.s.averin26@gmail.com or Telegram: @avs2607
