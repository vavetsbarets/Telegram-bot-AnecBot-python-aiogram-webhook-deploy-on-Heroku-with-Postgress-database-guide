# -*- coding: utf-8 -*-
# line above is to make all russian symbols work fine!


# WHAT IS COMMENTED (DESCRIBED PRECISELY) IN THIS FILE? (OTHER THINGS ARE WITH COMMENTS AS WELL, BUT NOT THAT PRECISE)!!!
    # 1. Beginning of this file: imports, loadings, connections to databases and so on
    # 2. Handler of the button 'анек' (check: @dp.message_handler(lambda message: message.text.lower() == 'анек'))
    # 3. Handler of the callback (inline keyboard) buttons with number from 1 to 10, below the message (check: @dp.callback_query_handler(lambda call:True), if clause only: if call.data[:4] == 'mark':)
    # 4. Aioscheduler: making automated tasks to be done at the certain time. (check: async def scheduler():)
    
# LOOKING AT THE FUNCTIONS AT THESE FOUR FILES (AND LOOKING AT OTHER FILES IN THIS REPOSITORY) SHOULD BE ENOUGH TO BE ABLE TO CREATE YOUR OWN AIOGTAM TELEGRAM BOT WITH DATABASE AND LAUNCH IT IN HEROKU! OTHER STUFF IN THIS FILE IS SIMILAR IN TERMS OF METHODS AND PACKAGES USED! IT'S JUST BOT-SPECIFIC, SO TO SAY.



import logging

# importing info from configs
from config_AnecBot import TOKEN, id_of_channel, my_id, USER, PASSWORD, HOST, PORT, DATABASE 
from config_AnecBot import HEROKU_APP_NAME, WEBHOOK_URL, WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT

# line below for more logging
#from aiogram.contrib.middlewares.logging import LoggingMiddleware

# main library for telegram bot: aiogram
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_webhook
from aiogram import Bot, Dispatcher, executor, types

# importing libraries needed in the code below
import numpy as np
import spacy
import random
import schedule
import time
import os
from threading import Thread
import aioschedule
import asyncio
from datetime import timedelta
from dateutil import tz
from datetime import datetime
import pytz 
from tzlocal import get_localzone

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# TO UPGRADE DATABASE TO MORE THAN 10 MILLION ROWS USE https://devcenter.heroku.com/articles/upgrading-heroku-postgres-databases AND ALL INFO ABOUT DATABASE IS CHANGED OR MAYBE partially delete users_history, since it is not used fully, think where it is used!!!!!! CHANGE IT ALL IN CONFIG FILE!!!!!
# IF DATABASE DOES NOT WORK IT MAY BE THE SWITCH OF CREDENTIALS!!!! 

# import class with python funcions to deal with postgress
from Postgresser_telegram_bot import Postgresser_general


# WHAT TO DO IF MOVE FROM PUBLIC WORK TO PRIVATE DEBUGGING AND VICE VERSA: !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# YOU CAN FIX IT WITHOUT FIRST TURNING OFF THE APP ON HEROKU!!!!!!!!!
# As for me, I change some variables in the code and move to the test bot (changing token) + 
    # + sometimes switching to polling from webhooks if I wanted to run my bot locally
# You can create your own more efficient way of debugging!

# make levels of log
logging.basicConfig(level = logging.INFO)

# to REDEPLOY (not first deploy)!!!!! Need to open command line and: !!!!!!!!!!!!!!!!!!!!!!
# 1. go to the path where your folder with the project is
# 2. heroku login
# 3. git add .
# 4. git commit -m "any message"
# 5. git push heroku master

# to remove the circle for users when they press certain collback button, while using bot
# await call.answer(cache_time = 0)

# initializing of the bot
bot = Bot(token = TOKEN)
dp = Dispatcher(bot)
# this line is if you want to have more logs
#dp.middleware.setup(LoggingMiddleware())

# nlp, changed from large to middle since no memory in heroku!!!
# I needed it specifically for my bot
nlp = spacy.load('ru_core_news_md')
    
# realisation of the POSTGRES class from postrgress python file, setting info to connect to database
general_base1 = Postgresser_general(USER, PASSWORD, HOST, PORT, DATABASE)   
    

# Activation of get 1 anec (anecdote/funny story) command, so this happens when users press button 'Aнек' in the bot
# I WILL COMMENT THIS FUNCTION AND FOR OTHER BUTTONS (NOT CALLBACK (OR INLINE KEYBOARD) ONES) THE DIFFERENCE WILL BE IN THE ALGORITHM 
    # ITSELF, SO I WILL NOT COMMENT OTHER BUTTONS AS DETAILED AS THIS BUTTON. NOTE, THAT I COMMENTED IN DETAIL PART OF THE 
    # CALLBACK BUTTONS AS WELL! (CHECK @dp.callback_query_handler(lambda call:True))
# In general, if you see the line like one below (starting with @dp.messaeg_handler), then this is 
    # function with is run when certain button in the bot is pressed
@dp.message_handler(lambda message: message.text.lower() == 'анек')
async def get_anec(message: types.Message):
    #checking that person is not novice (just started the bot), by connecting to database
    with general_base1.connection:
        # execution of the sql code in the database
        general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (message.chat.id,))
        # extracting output from sql code
        isn = general_base1.cursor.fetchall()[0][0]
    # code if user is novice
    if isn == 1:
        # connection to the base and extracting certain example anecdote
        with general_base1.connection:
            general_base1.cursor.execute("SELECT anec_text, source, date, id_entry FROM anecdotes_general_table WHERE id_entry = 145150 LIMIT 1")
            data = general_base1.cursor.fetchall()
        # saving info about this anecdote
        anec = data[0][0]
        source = data[0][1]
        date = data[0][2]
        id_entry = data[0][3]
        # text of the message sent to the user
        fin_mes = 'ID: {}-{}\n***anecbot***\n\n{}\n\nИстoчник: {}\nДата oпубликования в источнике: {}'.format(614, id_entry, anec, source, date)
        # Markup: buttons which appears under the message sent to the user
        markup = types.InlineKeyboardMarkup(row_width = 10)
        # collback buttons, basically user gives a mark to an anecdote from 1 to 10
        item_1 = types.InlineKeyboardButton(1, callback_data = "mark 1")
        item_2 = types.InlineKeyboardButton(2, callback_data = "mark 2")
        item_3 = types.InlineKeyboardButton(3, callback_data = "mark 3")
        item_4 = types.InlineKeyboardButton(4, callback_data = "mark 4")
        item_5 = types.InlineKeyboardButton(5, callback_data = "mark 5")
        item_6 = types.InlineKeyboardButton(6, callback_data = "mark 6")
        item_7 = types.InlineKeyboardButton(7, callback_data = "mark 7")
        item_8 = types.InlineKeyboardButton(8, callback_data = "mark 8")
        item_9 = types.InlineKeyboardButton(9, callback_data = "mark 9")
        item_10 = types.InlineKeyboardButton(10, callback_data = "mark 10")
        # adding buttons to the markup
        markup.add(item_1, item_2, item_3, item_4, item_5)
        markup.add(item_6, item_7, item_8, item_9, item_10)
        # changed upper O onto latin one!!!!!
        final = '{}\n\nOцените анекдот:'.format(fin_mes)
        # sending messages to the user
        await message.answer(final, reply_markup = markup)
        await message.answer('Сообщением выше я прислал Вам сообщение с анекдотом. На нём Вы можете увидеть номер анекдота, текст самого анекдота, источник, откуда был взят анекдот и дату опубликования этого анекдота в источнике.\n\nПод сообщением c анекдотом Вы можете оценить анекдот по шкале от 1 до 10, нажав на одну из кнопок с соответсвующим числом. Очень важно оценивать каждый присланный мною анекдот, так как исходя из этих оценок я буду рекомендовать Вам тот или иной анекдот.\n\nОцените анекдот, нажав на одну из кнопок с числом!')
     
    # if person is not a novice!!
    elif isn == 0:
        # checking that stopped anecs in a row, it's just another feature of the bot
        with general_base1.connection:
            general_base1.cursor.execute("SELECT in_a_row_started FROM anecs_in_a_row WHERE user_id = %s LIMIT 1", (message.chat.id,))
            status = general_base1.cursor.fetchall()[0][0]
        if status == 1:
            await message.answer('Чтобы получить 1 анекдот, сначала нажмите на кнопку "СТОП анеки подряд" и затем нажмите на "Анек" заново!')
            
        # if no restrictions, so that the command can be realised
        elif status == 0:
            with general_base1.connection:
                # selecting sources (groups) to which the person is subscribed
                general_base1.cursor.execute('SELECT * FROM users_sources WHERE user_id = %s LIMIT 1', (message.chat.id,))
                li_user_sources = list(general_base1.cursor.fetchall()[0][2:])
            
            # if the user is not subscribed to any sources
            if max(li_user_sources) == 0:
                await message.answer('Вы отписались от всех источников! Чтобы получить анекдот, выберите хотя бы один источник в разделе "выбор_источников"!')
            # if user is subscribed to some source, so that some anecdote can be taken
            else:
                # each cluster has anecdotes from a single source, so depending on sources on which the user subscribed, 
                    # only certain clusters can be considered, which are from the sources chosen by the user 
                li_clusters = [111, 112, 113, 114, 115, 116, 121, 122, 123, 124, 125, 131, 132, 133, 134, 211, 212, 213, 214, 221, 222, 223, 311, 312, 411, 511, 512, 513, 514, 612, 613, 614, 615, 711, 712, 713, 811, 812, 813, 911, 1011]
                #making list of suitable clusters
                fil_li_clu = li_clusters
                for i in range(len(li_user_sources)):
                    if li_user_sources[i] == 1:
                        pass
                    else:
                        fil_li_clu = [j for j in fil_li_clu if j // 100 != i+1]

                # some handmade algorithm which assign the probability of each cluster (from the list above) to be chosen
                #split the case p = 0.75 of sending recommended anec and p = 0.25 of sending random one! Choosing cluster
                nus = np.random.random()
                if nus > 0.25 and nus < 1.01:
                    with general_base1.connection:
                        general_base1.cursor.execute("SELECT * FROM users_clusters WHERE user_id = %s AND source_activated = True", (message.chat.id,))
                        
                        dan = general_base1.cursor.fetchall()

                        general_base1.cursor.execute("SELECT COUNT(*) FROM users_history WHERE user_id = %s", (message['chat']['id'],))
                        cou = general_base1.cursor.fetchall()[0][0]

                    liu = []
                    dictis = {}
                    for i in range(len(dan)):
                        liu.append(dan[i][4])

                    for i in range(len(dan)):
                        if min(liu) == max(liu):
                            dictis[dan[i][2]] = float(max(np.log(max(cou, 1))/np.log(6)-1, 0)) + 1
                        else:
                            dictis[dan[i][2]] = float(dan[i][4]-min(liu)) / float(max(liu)-min(liu)) * float(max(np.log(max(cou, 1))/np.log(6)-1, 0)) + 1

                    lui = []

                    for i in fil_li_clu:
                        if i in dictis.keys():
                            lui.append(dictis[i])
                        else:
                            lui.append(max(7, max(np.log(max(cou, 1))/np.log(6)-1, 0)))

                    louis = np.cumsum(np.array(lui) / sum(lui))

                    n = np.random.random()
                    for i in range(len(fil_li_clu)):
                        if louis[i] > n:
                            chosen_cluster = fil_li_clu[i]
                            break  
                elif nus <= 0.25 and nus > -0.01:
                    chosen_cluster = int(np.random.choice(fil_li_clu))
                else:
                    await message.answer('error in nus')

                # choosing random anec from the chosen cluster:
                with general_base1.connection:
                    general_base1.cursor.execute('SELECT COUNT(*) FROM anecdotes_general_table WHERE cluster_num = %s', (chosen_cluster,))
                    # number of anecdotes in the cluster
                    num_of_anec_cluster = general_base1.cursor.fetchall()[0][0]
                # random index taken
                k = np.random.randint(num_of_anec_cluster)

                # don't forget to include id of the anecdote and change the callback!!!!!
                with general_base1.connection:
                    general_base1.cursor.execute("SELECT anec_text, source, date, id_entry FROM anecdotes_general_table WHERE cluster_num = %s LIMIT 1 OFFSET %s", (chosen_cluster, k))
                    # random anecdote from the chosen cluster
                    data = general_base1.cursor.fetchall()
                anec = data[0][0]
                source = data[0][1]
                date = data[0][2]
                id_entry = data[0][3]
                fin_mes = 'ID: {}-{}\n***anecbot***\n\n{}\n\nИстoчник: {}\nДата oпубликования в источнике: {}'.format(chosen_cluster, id_entry, anec, source, date)
                # Markup: buttons which appears under the message sent to the user
                markup = types.InlineKeyboardMarkup(row_width = 10)
                # collback buttons, basically user gives a mark to an anecdote from 1 to 10 and also has option to save the anecdote!
                item_1 = types.InlineKeyboardButton(1, callback_data = "mark 1")
                item_2 = types.InlineKeyboardButton(2, callback_data = "mark 2")
                item_3 = types.InlineKeyboardButton(3, callback_data = "mark 3")
                item_4 = types.InlineKeyboardButton(4, callback_data = "mark 4")
                item_5 = types.InlineKeyboardButton(5, callback_data = "mark 5")
                item_6 = types.InlineKeyboardButton(6, callback_data = "mark 6")
                item_7 = types.InlineKeyboardButton(7, callback_data = "mark 7")
                item_8 = types.InlineKeyboardButton(8, callback_data = "mark 8")
                item_9 = types.InlineKeyboardButton(9, callback_data = "mark 9")
                item_10 = types.InlineKeyboardButton(10, callback_data = "mark 10")
                item_11 = types.InlineKeyboardButton('Добавить в "Сохранённые"', callback_data = "add_to_save")
                markup.add(item_1, item_2, item_3, item_4, item_5)
                markup.add(item_6, item_7, item_8, item_9, item_10)
                markup.add(item_11)                                     

                # changed upper O onto latin one!!!!!
                final = '{}\n\nOцените анекдот:'.format(fin_mes)

                # avoiding limit of max 4096 characters: check how it works, but separately selecting anecs with > 4096 characters!!!!
                # if anecdote is more than 4096 symbols, then several messages are sent!!!
                if len(final) <= 4096:
                    await message.answer(final, reply_markup = markup)  
                else:
                    for x in range(0, len(final) - 4096, 4096):
                        await message.answer(final[x : x + 4096])
                    k = len(final)//4096
                    await message.answer('ID: {}-{}\n***anecbot***\n\n'.format(chosen_cluster, id_entry) + final[k * 4096 : k * 4096 + 4096], reply_markup = markup)
        else:
            await message.answer('error in status')
            
    else:
        await message.answer('error in isn')
            

            
# Activation of get 10 anecs command
@dp.message_handler(lambda message: message.text.lower() == '10 анеков')
async def get_10anecs(message: types.Message):
    with general_base1.connection:
        general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (message.chat.id,))
        isn = general_base1.cursor.fetchall()[0][0]
    if isn == 1:
        await message.answer('На данный момент эта команда недоступна так как Вы находитесь в разделе "Начальная инструкция".\n\nЭта команда будет доступна, как только Вы завершите или пропустите начальную инструкцию')
    elif isn == 0:
        # checking that stopped anecs in a row
        with general_base1.connection:
            general_base1.cursor.execute("SELECT in_a_row_started FROM anecs_in_a_row WHERE user_id = %s LIMIT 1", (message.chat.id,))
            status = general_base1.cursor.fetchall()[0][0]
        if status == 1:
            await message.answer('Чтобы получить 10 анекдотов, сначала нажмите на кнопку "СТОП анеки подряд" и затем нажмите на "10 Анеков" заново!')
        elif status == 0:
            with general_base1.connection:
                general_base1.cursor.execute('SELECT * FROM users_sources WHERE user_id = %s LIMIT 1', (message.chat.id,))
                li_user_sources = list(general_base1.cursor.fetchall()[0][2:])


            if max(li_user_sources) == 0:
                await message.answer('Вы отписались от всех источников! Чтобы получить анекдот, выберите хотя бы один источник в разделе "выбор_источников".')

            else:
                markup = types.InlineKeyboardMarkup(row_width = 10)
                item_1 = types.InlineKeyboardButton(1, callback_data = "mark 1")
                item_2 = types.InlineKeyboardButton(2, callback_data = "mark 2")
                item_3 = types.InlineKeyboardButton(3, callback_data = "mark 3")
                item_4 = types.InlineKeyboardButton(4, callback_data = "mark 4")
                item_5 = types.InlineKeyboardButton(5, callback_data = "mark 5")
                item_6 = types.InlineKeyboardButton(6, callback_data = "mark 6")
                item_7 = types.InlineKeyboardButton(7, callback_data = "mark 7")
                item_8 = types.InlineKeyboardButton(8, callback_data = "mark 8")
                item_9 = types.InlineKeyboardButton(9, callback_data = "mark 9")
                item_10 = types.InlineKeyboardButton(10, callback_data = "mark 10")
                item_11 = types.InlineKeyboardButton('Добавить в "Сохранённые"', callback_data = "add_to_save")
                markup.add(item_1, item_2, item_3, item_4, item_5)
                markup.add(item_6, item_7, item_8, item_9, item_10)
                markup.add(item_11)

                li_clusters = [111, 112, 113, 114, 115, 116, 121, 122, 123, 124, 125, 131, 132, 133, 134, 211, 212, 213, 214, 221, 222, 223, 311, 312, 411, 511, 512, 513, 514, 612, 613, 614, 615, 711, 712, 713, 811, 812, 813, 911, 1011]

                #making list of suitable clusters
                fil_li_clu = li_clusters
                for i in range(len(li_user_sources)):
                    if li_user_sources[i] == 1:
                        pass
                    else:
                        fil_li_clu = [j for j in fil_li_clu if j // 100 != i+1]

                # recomendation list
                with general_base1.connection:
                    general_base1.cursor.execute("SELECT * FROM users_clusters WHERE user_id = %s AND source_activated = True", (message.chat.id,))
                    dan = general_base1.cursor.fetchall()

                    general_base1.cursor.execute("SELECT COUNT(*) FROM users_history WHERE user_id = %s", (message['chat']['id'],))
                    cou = general_base1.cursor.fetchall()[0][0]

                liu = []
                dictis = {}
                for i in range(len(dan)):
                    liu.append(dan[i][4])

                for i in range(len(dan)):
                    if min(liu) == max(liu):
                        dictis[dan[i][2]] = float(max(np.log(max(cou, 1))/np.log(6)-1, 0)) + 1
                    else:
                        dictis[dan[i][2]] = float(dan[i][4]-min(liu)) / float(max(liu)-min(liu)) * float(max(np.log(max(cou, 1))/np.log(6)-1, 0)) + 1


                lui = []

                for i in fil_li_clu:
                    if i in dictis.keys():
                        lui.append(dictis[i])
                    else:
                        lui.append(max(7, max(np.log(max(cou, 1))/np.log(6)-1, 0)))

                louis = np.cumsum(np.array(lui) / sum(lui))

                #split the case p = 0.75 when recomend and p = 0.25 when random, start cycling 10! Choosing cluster
                for j in range(10):
                    nus = np.random.random()
                    if nus > 0.25 and nus < 1.01:
                        n = np.random.random()
                        for i in range(len(fil_li_clu)):
                            if louis[i] > n:
                                chosen_cluster = fil_li_clu[i]
                                break  
                    elif nus <= 0.25 and nus > -0.01:
                        chosen_cluster = int(np.random.choice(fil_li_clu))
                    else:
                        await message.answer('error in nus')

                    # choosing random anec from the chosen cluster:
                    with general_base1.connection:
                        general_base1.cursor.execute('SELECT COUNT(*) FROM anecdotes_general_table WHERE cluster_num = %s', (chosen_cluster,))
                        num_of_anec_cluster = general_base1.cursor.fetchall()[0][0]

                    k = np.random.randint(num_of_anec_cluster)

                    with general_base1.connection:
                        general_base1.cursor.execute("SELECT anec_text, source, date, id_entry FROM anecdotes_general_table WHERE cluster_num = %s LIMIT 1 OFFSET %s", (chosen_cluster, k))
                        data = general_base1.cursor.fetchall()
                    anec = data[0][0]
                    source = data[0][1]
                    date = data[0][2]
                    id_entry = data[0][3]
                    fin_mes = '{}) ID: {}-{}\n***anecbot***\n\n{}\n\nИстoчник: {}\nДата oпубликования в источнике: {}'.format(j + 1, chosen_cluster, id_entry, anec, source, date)

                    # changed upper O onto latin one!!!!!
                    final = '{}\n\nOцените анекдот:'.format(fin_mes)

                    # avoiding limit of max 4096 characters: check how it works, but separately selecting anecs with > 4096 characters!!!!
                    if len(final) <= 4096:
                        await message.answer(final, reply_markup = markup)  
                    else:
                        for x in range(0, len(final) - 4096, 4096):
                            await message.answer(final[x : x + 4096])
                        k = len(final)//4096
                        await message.answer('{}) ID: {}-{}\n***anecbot***\n\n'.format(j + 1, chosen_cluster, id_entry) + final[k * 4096 : k * 4096 + 4096], reply_markup = markup)
        else:
            await message.answer('error in status')
    else:
        await message.answer('error in isn')

            
# Activation of get many anecs command
@dp.message_handler(lambda message: message.text.lower() == 'много анеков')
async def get_many_anecs(message: types.Message):
    with general_base1.connection:
        general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (message.chat.id,))
        isn = general_base1.cursor.fetchall()[0][0]
    if isn == 1:
        await message.answer('На данный момент эта команда недоступна так как Вы находитесь в разделе "Начальная инструкция".\n\nЭта команда будет доступна, как только Вы завершите или пропустите начальную инструкцию')
    elif isn == 0:    
        # checking that stopped anecs in a row
        with general_base1.connection:
            general_base1.cursor.execute("SELECT in_a_row_started FROM anecs_in_a_row WHERE user_id = %s LIMIT 1", (message.chat.id,))
            status = general_base1.cursor.fetchall()[0][0]
        if status == 1:
            await message.answer('Чтобы получить много анекдотов, сначала нажмите на кнопку "СТОП анеки подряд" и затем нажмите на "Много анеков" заново!')
        elif status == 0:
            markup = types.InlineKeyboardMarkup(row_width = 10)
            item_1 = types.InlineKeyboardButton(1, callback_data = "anecs1")
            item_2 = types.InlineKeyboardButton(2, callback_data = "anecs2")
            item_3 = types.InlineKeyboardButton(3, callback_data = "anecs3")
            item_4 = types.InlineKeyboardButton(4, callback_data = "anecs4")
            item_5 = types.InlineKeyboardButton(5, callback_data = "anecs5")
            item_6 = types.InlineKeyboardButton(6, callback_data = "anecs6")
            item_7 = types.InlineKeyboardButton(7, callback_data = "anecs7")
            item_8 = types.InlineKeyboardButton(8, callback_data = "anecs8")
            item_9 = types.InlineKeyboardButton(9, callback_data = "anecs9")
            item_10 = types.InlineKeyboardButton(10, callback_data = "anecs10")
            item_11 = types.InlineKeyboardButton(11, callback_data = "anecs11")
            item_12 = types.InlineKeyboardButton(12, callback_data = "anecs12")
            item_13 = types.InlineKeyboardButton(13, callback_data = "anecs13")
            item_14 = types.InlineKeyboardButton(14, callback_data = "anecs14")
            item_15 = types.InlineKeyboardButton(15, callback_data = "anecs15")
            item_16 = types.InlineKeyboardButton(16, callback_data = "anecs16")
            item_17 = types.InlineKeyboardButton(17, callback_data = "anecs17")
            item_18 = types.InlineKeyboardButton(18, callback_data = "anecs18")
            item_19 = types.InlineKeyboardButton(19, callback_data = "anecs19")
            item_20 = types.InlineKeyboardButton(20, callback_data = "anecs20")
            item_21 = types.InlineKeyboardButton(21, callback_data = "anecs21")
            item_22 = types.InlineKeyboardButton(22, callback_data = "anecs22")
            item_23 = types.InlineKeyboardButton(23, callback_data = "anecs23")
            item_24 = types.InlineKeyboardButton(24, callback_data = "anecs24")
            item_25 = types.InlineKeyboardButton(25, callback_data = "anecs25")
            item_26 = types.InlineKeyboardButton('Отмена', callback_data = "exit2")

            markup.add(item_1, item_2, item_3, item_4, item_5)
            markup.add(item_6, item_7, item_8, item_9, item_10)
            markup.add(item_11, item_12, item_13, item_14, item_15)
            markup.add(item_16, item_17, item_18, item_19, item_20)
            markup.add(item_21, item_22, item_23, item_24, item_25)
            markup.add(item_26)
            await message.answer('Выберите количество анекдотов, которые Вы хотите получить:', reply_markup = markup)
        else:
            await message.answer('error in status')
    else:
        await message.answer('error in isn')

                             
                             
# Activation of get anecs in a row command
@dp.message_handler(lambda message: message.text.lower() == 'старт анеки подряд')        
async def start_anecs_in_a_row(message: types.Message):
    with general_base1.connection:
        general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (message.chat.id,))
        isn = general_base1.cursor.fetchall()[0][0]
    if isn == 1:
        await message.answer('На данный момент эта команда недоступна так как Вы находитесь в разделе "Начальная инструкция".\n\nЭта команда будет доступна, как только Вы завершите или пропустите начальную инструкцию')
    elif isn == 0:
        general_base1.update_anecs_in_a_row_status(message.chat.id, 1)

        with general_base1.connection:
            general_base1.cursor.execute("SELECT subscribed FROM users_sub_best_anec_day WHERE user_id = %s LIMIT 1", (message.chat.id,))
            ku = general_base1.cursor.fetchall()[0][0]
            general_base1.cursor.execute("SELECT subscribed FROM users_sub_random_anec WHERE user_id = %s LIMIT 1", (message.chat.id,))
            kz = general_base1.cursor.fetchall()[0][0]
            
        #keyboard
        markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
        item1 = types.KeyboardButton("Анек")
        item2 = types.KeyboardButton("10 Анеков")
        item3 = types.KeyboardButton("Много Анеков")
        item4 = types.KeyboardButton("СТОП Анеки подряд")
        item10 = types.KeyboardButton("Сохранённые Анеки")
        item5 = types.KeyboardButton("Выбор источников")
        item6 = types.KeyboardButton("Поиск Анека по слову: инструкция")
        item7 = types.KeyboardButton("Список источников")
        item8 = types.KeyboardButton("help")
        if ku == 0:
            item9 = types.KeyboardButton("Анек дня: подписаться")
        elif ku == 1:
            item9 = types.KeyboardButton("Анек дня: отписаться")
        else:
            await message.answer('error in ku') 
        if kz == 0:
            item12 = types.KeyboardButton("Рандомный Анек: подписаться")
        elif kz == 1:
            item12 = types.KeyboardButton("Рандомный Анек: отписаться")
        else:
            await message.answer('error in kz') 
        item11 = types.KeyboardButton('Последние 5 удалённых сохранёнок')
        markup.add(item1, item2) 
        markup.add(item3, item4)
        markup.add(item10, item5)
        markup.add(item6)
        markup.add(item7, item8)
        markup.add(item9)
        markup.add(item12)
        markup.add(item11)
        await message.answer('После оценки анекдота Вы автоматически получите следующий Анек!\nЧтобы потом прератить автоматическую подачу анекдотов, нажмите кнопку "СТОП анеки подряд" на клавиатуре!', reply_markup = markup)
        # the rest is the same like in get 1 anec
        with general_base1.connection:
            general_base1.cursor.execute('SELECT * FROM users_sources WHERE user_id = %s LIMIT 1', (message.chat.id,))
            li_user_sources = list(general_base1.cursor.fetchall()[0][2:])

        if max(li_user_sources) == 0:
            await message.answer('Вы отписались от всех источников! Чтобы получить анекдот, выберите хотя бы один источник в разделе "выбор_источников".')

        else:
            li_clusters = [111, 112, 113, 114, 115, 116, 121, 122, 123, 124, 125, 131, 132, 133, 134, 211, 212, 213, 
                           214, 221, 222, 223, 311, 312, 411, 511, 512, 513, 514, 612, 613, 614, 615, 711, 712, 713, 
                           811, 812, 813, 911, 1011]

            #making list of suitable clusters
            fil_li_clu = li_clusters
            for i in range(len(li_user_sources)):
                if li_user_sources[i] == 1:
                    pass
                else:
                    fil_li_clu = [j for j in fil_li_clu if j // 100 != i+1]

            #split the case p = 0.75 when recomend and p = 0.25 when random! Choosing cluster
            nus = np.random.random()
            if nus > 0.25 and nus < 1.01:
                with general_base1.connection:
                    general_base1.cursor.execute("SELECT * FROM users_clusters WHERE user_id = %s AND source_activated = True", (message.chat.id,))
                    dan = general_base1.cursor.fetchall()

                    general_base1.cursor.execute("SELECT COUNT(*) FROM users_history WHERE user_id = %s", (message['chat']['id'],))
                    cou = general_base1.cursor.fetchall()[0][0]

                liu = []
                dictis = {}
                for i in range(len(dan)):
                    liu.append(dan[i][4])

                for i in range(len(dan)):
                    if min(liu) == max(liu):
                        dictis[dan[i][2]] = float(max(np.log(max(cou, 1))/np.log(6)-1, 0)) + 1
                    else:
                        dictis[dan[i][2]] = float(dan[i][4]-min(liu)) / float(max(liu)-min(liu)) * float(max(np.log(max(cou, 1))/np.log(6)-1, 0)) + 1


                lui = []

                for i in fil_li_clu:
                    if i in dictis.keys():
                        lui.append(dictis[i])
                    else:
                        lui.append(max(7, max(np.log(max(cou, 1))/np.log(6)-1, 0)))

                louis = np.cumsum(np.array(lui) / sum(lui))

                n = np.random.random()
                for i in range(len(fil_li_clu)):
                    if louis[i] > n:
                        chosen_cluster = fil_li_clu[i]
                        break  
            elif nus <= 0.25 and nus > -0.01:
                chosen_cluster = int(np.random.choice(fil_li_clu))
            else:
                await message.answer('error in nus')

            # choosing random anec from the chosen cluster:
            with general_base1.connection:
                general_base1.cursor.execute('SELECT COUNT(*) FROM anecdotes_general_table WHERE cluster_num = %s', (chosen_cluster,))
                num_of_anec_cluster = general_base1.cursor.fetchall()[0][0]

            k = np.random.randint(num_of_anec_cluster)

            # don't forget to include id of the anecdote and change the callback!!!!!
            with general_base1.connection:            
                general_base1.cursor.execute("SELECT anec_text, source, date, id_entry FROM anecdotes_general_table WHERE cluster_num = %s LIMIT 1 OFFSET %s", (chosen_cluster, k))
                data = general_base1.cursor.fetchall()
            anec = data[0][0]
            source = data[0][1]
            date = data[0][2]
            id_entry = data[0][3]
            fin_mes = 'ID: {}-{}\n***anecbot***\n\n{}\n\nИстoчник: {}\nДата oпубликования в источнике: {}'.format(chosen_cluster, id_entry, anec, source, date)

            markup = types.InlineKeyboardMarkup(row_width = 10)
            item_1 = types.InlineKeyboardButton(1, callback_data = "mark 1")
            item_2 = types.InlineKeyboardButton(2, callback_data = "mark 2")
            item_3 = types.InlineKeyboardButton(3, callback_data = "mark 3")
            item_4 = types.InlineKeyboardButton(4, callback_data = "mark 4")
            item_5 = types.InlineKeyboardButton(5, callback_data = "mark 5")
            item_6 = types.InlineKeyboardButton(6, callback_data = "mark 6")
            item_7 = types.InlineKeyboardButton(7, callback_data = "mark 7")
            item_8 = types.InlineKeyboardButton(8, callback_data = "mark 8")
            item_9 = types.InlineKeyboardButton(9, callback_data = "mark 9")
            item_10 = types.InlineKeyboardButton(10, callback_data = "mark 10")
            item_11 = types.InlineKeyboardButton('Добавить в "Сохранённые"', callback_data = "add_to_save")
            markup.add(item_1, item_2, item_3, item_4, item_5)
            markup.add(item_6, item_7, item_8, item_9, item_10)
            markup.add(item_11)

            # changed upper O onto latin one!!!!!
            final = '{}\n\nOцените анекдот:'.format(fin_mes)

            # avoiding limit of max 4096 characters: check how it works, but separately selecting anecs with > 4096 characters!!!!
            if len(final) <= 4096:
                await message.answer(final, reply_markup = markup)  
            else:
                for x in range(0, len(final) - 4096, 4096):
                    await message.answer(final[x : x + 4096])
                k = len(final)//4096
                await message.answer('ID: {}-{}\n***anecbot***\n\n'.format(chosen_cluster, id_entry) + final[k * 4096 : k * 4096 + 4096], reply_markup = markup)
    
    else:
        await message.answer('error in isn')
            

# Activation of stop getting anecs in a row command
@dp.message_handler(lambda message: message.text.lower() == 'стоп анеки подряд')        
async def stop_anecs_in_a_row(message: types.Message):
    with general_base1.connection:
        general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (message.chat.id,))
        isn = general_base1.cursor.fetchall()[0][0]
    if isn == 1:
        await message.answer('На данный момент эта команда недоступна так как Вы находитесь в разделе "Начальная инструкция".\n\nЭта команда будет доступна, как только Вы завершите или пропустите начальную инструкцию')
    elif isn == 0:
        general_base1.update_anecs_in_a_row_status(message.chat.id, 0)
        
        with general_base1.connection:
            general_base1.cursor.execute("SELECT subscribed FROM users_sub_best_anec_day WHERE user_id = %s LIMIT 1", (message.chat.id,))
            ku = general_base1.cursor.fetchall()[0][0]
            general_base1.cursor.execute("SELECT subscribed FROM users_sub_random_anec WHERE user_id = %s LIMIT 1", (message.chat.id,))
            kz = general_base1.cursor.fetchall()[0][0]
            
        #keyboard
        markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
        item1 = types.KeyboardButton("Анек")
        item2 = types.KeyboardButton("10 Анеков")
        item3 = types.KeyboardButton("Много Анеков")
        item4 = types.KeyboardButton("СТАРТ Анеки подряд")
        item10 = types.KeyboardButton("Сохранённые Анеки")
        item5 = types.KeyboardButton("Выбор источников")
        item6 = types.KeyboardButton("Поиск Анека по слову: инструкция")
        item7 = types.KeyboardButton("Список источников")
        item8 = types.KeyboardButton("help")
        if ku == 0:
            item9 = types.KeyboardButton("Анек дня: подписаться")
        elif ku == 1:
            item9 = types.KeyboardButton("Анек дня: отписаться")
        else:
            await message.answer('error in ku') 
        if kz == 0:
            item12 = types.KeyboardButton("Рандомный Анек: подписаться")
        elif kz == 1:
            item12 = types.KeyboardButton("Рандомный Анек: отписаться")
        else:
            await message.answer('error in kz') 
        item11 = types.KeyboardButton('Последние 5 удалённых сохранёнок')
        markup.add(item1, item2) 
        markup.add(item3, item4)
        markup.add(item10, item5)
        markup.add(item6)
        markup.add(item7, item8)
        markup.add(item9)
        markup.add(item12)
        markup.add(item11)
        await message.answer('Вы остановили высылку анекдотов подряд, после оценки анекдота, следующий анекдот не будет присылаться автоматически!', reply_markup = markup)
    else:
        await message.answer('error in isn')
        
        
        
        
# putting mark into the database and all other callbacks in the whole bot!!!
@dp.callback_query_handler(lambda call:True)
async def callback_inline(call):
    try:
        if call.message:
            # basically this is handler if the user pressed one of buttons (marks) from 1 to 10 below the message with anecdote
            # call.data is the callback_data arguments in the lines like: item_1 = types.InlineKeyboardButton(1, callback_data = "mark 1")
            if call.data[:4] == 'mark':
                for i in range(1, 11):
                    # catching the exact mark, left by the user
                    # id of the user, who pressed the button is caught by call.message.chat.id
                    if call.data == 'mark {}'.format(i):
                        # BE CAREFULL HERE, SOME letters in split are IN LATIN, check get_anec for that!!!
                        x, y = call.message['text'].split('\n***anecbot***\n\n')
                        if x[0] == 'А':
                            x = x.split('\n')[1]
                        # collecting info about the message sent to user
                        cluster_num = x.split('-')[0].split('ID: ')[1]
                        source_id = cluster_num[:-2]
                        id_anec = x.split('-')[1]
                        anec, b = y.split('\n\nИстoчник: ')
                        source, c = b.split('\nДата oпубликования в источнике: ')
                        date, d = c.split('\n\nOцените анекдот:')
                        # check whether 0 or 1 feedback in the users_history (whether user already marked the same anecdote 
                            # which was sent before)
                        with general_base1.connection:
                            general_base1.cursor.execute('SELECT COUNT(*) from users_history where user_id = %s and id_entry_from_general_base = %s', (call.message['chat']['id'], id_anec))
                            is_present = general_base1.cursor.fetchone()[0]
                         
                        # checking that no duplicates of user-anecdote pair in the database
                        if is_present in [0, 1]:
                            # remove or edit inline buttons and edit initial message
                            await call.message.edit_text(text = call.message['text'][:-18] + '\n\nВаша оценка: {}'.format(i))
                            # getting the list of rows of callback buttons
                            leso = call.message.reply_markup.inline_keyboard
                            # if 3 rows, then 2 rows are 10 buttons of marks from 1 to 10 and third row has button to save anec(dote)
                                # so after user chose the number, we chose should leave only save anec callback button
                            if len(leso) == 3:
                                await call.message.edit_reply_markup(reply_markup = {"inline_keyboard": [call.message.reply_markup.inline_keyboard[-1]]})
                            # if not 3 rows initially, then user saved anec before, so only 2 rows with marks from 1 to 10 should be left,
                                # so if not 2 rows, then it's error!
                            # if 2 rows initially, then after user presses the mark, no inline (callback) buttons must be left under 
                                # the message
                            elif len(leso) != 2:
                                await call.message.answer('error in leso')
                            # adding or updating user's feedback for the certain anecdote
                            # this is the function which is defined in the Posgresser_telegram_bot.py
                            general_base1.add_feedback(call.message['chat']['id'], call.message['date'].strftime('%Y-%m-%d'), i, id_anec, is_present)

                            with general_base1.connection:
                                # for all users I save what is their average mark per each cluster
                                general_base1.cursor.execute("SELECT * FROM users_clusters WHERE user_id = %s AND cluster_num = %s LIMIT 1", (call.message['chat']['id'], cluster_num))
                                ac = general_base1.cursor.fetchall()
                            
                            # if user marked first anec from the cluster, I need to add the line to the table
                            if ac == []:
                                # to add the line to the table I need to know whether the user is subscribed to the source, 
                                    # from which the anec was received
                                if int(source_id) == 1:
                                    with general_base1.connection:
                                        general_base1.cursor.execute("SELECT source_1_chosen FROM users_sources WHERE user_id = %s LIMIT 1", (call.message['chat']['id'],))
                                        geed = general_base1.cursor.fetchall()[0][0]
                                elif int(source_id) == 2:
                                    with general_base1.connection:
                                        general_base1.cursor.execute("SELECT source_2_chosen FROM users_sources WHERE user_id = %s LIMIT 1", (call.message['chat']['id'],))
                                        geed = general_base1.cursor.fetchall()[0][0]
                                elif int(source_id) == 3:
                                    with general_base1.connection:
                                        general_base1.cursor.execute("SELECT source_3_chosen FROM users_sources WHERE user_id = %s LIMIT 1", (call.message['chat']['id'],))
                                        geed = general_base1.cursor.fetchall()[0][0]
                                elif int(source_id) == 4:
                                    with general_base1.connection:
                                        general_base1.cursor.execute("SELECT source_4_chosen FROM users_sources WHERE user_id = %s LIMIT 1", (call.message['chat']['id'],))
                                        geed = general_base1.cursor.fetchall()[0][0]
                                elif int(source_id) == 5:
                                    with general_base1.connection:
                                        general_base1.cursor.execute("SELECT source_5_chosen FROM users_sources WHERE user_id = %s LIMIT 1", (call.message['chat']['id'],))
                                        geed = general_base1.cursor.fetchall()[0][0]
                                elif int(source_id) == 6:
                                    with general_base1.connection:
                                        general_base1.cursor.execute("SELECT source_6_chosen FROM users_sources WHERE user_id = %s LIMIT 1", (call.message['chat']['id'],))
                                        geed = general_base1.cursor.fetchall()[0][0]
                                elif int(source_id) == 7:
                                    with general_base1.connection:
                                        general_base1.cursor.execute("SELECT source_7_chosen FROM users_sources WHERE user_id = %s LIMIT 1", (call.message['chat']['id'],))
                                        geed = general_base1.cursor.fetchall()[0][0]
                                elif int(source_id) == 8:
                                    with general_base1.connection:
                                        general_base1.cursor.execute("SELECT source_8_chosen FROM users_sources WHERE user_id = %s LIMIT 1", (call.message['chat']['id'],))
                                        geed = general_base1.cursor.fetchall()[0][0]
                                elif int(source_id) == 9:
                                    with general_base1.connection:
                                        general_base1.cursor.execute("SELECT source_9_chosen FROM users_sources WHERE user_id = %s LIMIT 1", (call.message['chat']['id'],))
                                        geed = general_base1.cursor.fetchall()[0][0]
                                elif int(source_id) == 10:
                                    with general_base1.connection:
                                        general_base1.cursor.execute("SELECT source_10_chosen FROM users_sources WHERE user_id = %s LIMIT 1", (call.message['chat']['id'],))
                                        geed = general_base1.cursor.fetchall()[0][0]
                                # if subscribed to the source from which anec was received, last parameter is 1, otherwise it's 0        
                                if geed == True:
                                    # the definition of this function can be seen in Postgresser_telegram_bot.py
                                    general_base1.add_user_cluster_combination_to_users_clusters(call.message['chat']['id'], cluster_num, 1, i, source_id, 1)
                                elif geed == False:
                                    general_base1.add_user_cluster_combination_to_users_clusters(call.message['chat']['id'], cluster_num, 1, i, source_id, 0)
                                else:
                                    call.message.answer('error in geed')
                            # if there is already user-cluster pair in the table, then the line needs to be updated
                            else:
                                id_entry = ac[0][0]
                                new_anecs_read = ac[0][3] + 1
                                new_average_rating = (ac[0][3] * ac[0][4] + i) / new_anecs_read
                                general_base1.update_user_cluster_combination_in_users_clusters(id_entry, new_anecs_read, new_average_rating)

                            #checking that person is not novice, then it's part of the instruction
                            with general_base1.connection:
                                general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (call.message.chat.id,))
                                isn = general_base1.cursor.fetchall()[0][0]
                            if isn == 1:
                                await call.answer('Ваша оценка сохранена!')
                                #keyboard
                                markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
                                item1 = types.KeyboardButton("Анек")
                                item2 = types.KeyboardButton("Выбор источников")
                                item3 = types.KeyboardButton("Пропустить начальную инструкцию")
                                markup.add(item1)
                                markup.add(item2)
                                markup.add(item3)
                                await call.message.answer('Отлично, Вы оценили свой первый анекдот!\n\nЧем больше анекдотов Вы оцените, тем больше шансов, что я пришлю Вам анекдот, который Вам понравится!\n\nТеперь, давайте попробуем опцию, где Вы можете лично отсеить анекдоты, которые Вам точно не понравятся, отписавшись от некоторых источников. Нажмите на "Выбор источников", чтобы попробовать эту опцию!', reply_markup = markup)
                            
                            # if not novice!
                            elif isn == 0:
                                # Split: either anecs in a row case (option to automatically send the next anec after marking from 1 to 10 
                                    # the current anecdote or classic one (nothing is sent after marking)!
                                with general_base1.connection:
                                    general_base1.cursor.execute("SELECT in_a_row_started FROM anecs_in_a_row WHERE user_id = %s LIMIT 1", (call.message.chat.id,))
                                    status = general_base1.cursor.fetchall()[0][0]
                                #classic case
                                if status == 0:                            
                                    # info to user that the feedback is considered: not message, but temporary notification
                                    await call.answer('Ваша оценка сохранена!')
                                #in a row case
                                elif status == 1:
                                    # info to user that the feedback is considered and next anec is going to be sent
                                    await call.answer('Ваша оценка сохранена! Высылаю следующий Анек:')
                                    # then there is similar algorithm as if anec button is pressed!!! No comments below in this function!
                                    with general_base1.connection:
                                        general_base1.cursor.execute('SELECT * FROM users_sources WHERE user_id = %s LIMIT 1', (call.message.chat.id,))
                                        li_user_sources = list(general_base1.cursor.fetchall()[0][2:])

                                    if max(li_user_sources) == 0:
                                        await call.message.answer('Вы отписались от всех источников! Чтобы получить анекдот, выберите хотя бы один источник в разделе "выбор_источников".')

                                    else:
                                        li_clusters = [111, 112, 113, 114, 115, 116, 121, 122, 123, 124, 125, 131, 132, 133, 134, 211, 212, 213, 214, 221, 222, 223, 311, 312, 411, 511, 512, 513, 514, 612, 613, 614, 615, 711, 712, 713, 811, 812, 813, 911, 1011]

                                        #making list of suitable clusters
                                        fil_li_clu = li_clusters
                                        for i in range(len(li_user_sources)):
                                            if li_user_sources[i] == 1:
                                                pass
                                            else:
                                                fil_li_clu = [j for j in fil_li_clu if j // 100 != i+1]

                                        #split the case p = 0.75 when recomend and p = 0.25 when random! Choosing cluster
                                        nus = np.random.random()
                                        if nus > 0.25 and nus < 1.01:
                                            with general_base1.connection:
                                                general_base1.cursor.execute("SELECT * FROM users_clusters WHERE user_id = %s AND source_activated = True", (call.message.chat.id,))
                                                dan = general_base1.cursor.fetchall()

                                                general_base1.cursor.execute("SELECT COUNT(*) FROM users_history WHERE user_id = %s", (call.message['chat']['id'],))
                                                cou = general_base1.cursor.fetchall()[0][0]

                                            liu = []
                                            dictis = {}
                                            for i in range(len(dan)):
                                                liu.append(dan[i][4])

                                            for i in range(len(dan)):
                                                if min(liu) == max(liu):
                                                    dictis[dan[i][2]] = float(max(np.log(max(cou, 1))/np.log(6)-1, 0)) + 1
                                                else:
                                                    dictis[dan[i][2]] = float(dan[i][4]-min(liu)) / float(max(liu)-min(liu)) * float(max(np.log(max(cou, 1))/np.log(6)-1, 0)) + 1


                                            lui = []

                                            for i in fil_li_clu:
                                                if i in dictis.keys():
                                                    lui.append(dictis[i])
                                                else:
                                                    lui.append(max(7, max(np.log(max(cou, 1))/np.log(6)-1, 0)))

                                            louis = np.cumsum(np.array(lui) / sum(lui))

                                            n = np.random.random()
                                            for i in range(len(fil_li_clu)):
                                                if louis[i] > n:
                                                    chosen_cluster = fil_li_clu[i]
                                                    break  
                                        elif nus <= 0.25 and nus > -0.01:
                                            chosen_cluster = int(np.random.choice(fil_li_clu))
                                        else:
                                            await call.message.answer('error in nus')

                                        # choosing random anec from the chosen cluster:
                                        with general_base1.connection:
                                            general_base1.cursor.execute('SELECT COUNT(*) FROM anecdotes_general_table WHERE cluster_num = %s', (chosen_cluster,))
                                            num_of_anec_cluster = general_base1.cursor.fetchall()[0][0]

                                        k = np.random.randint(num_of_anec_cluster)

                                        with general_base1.connection:
                                            general_base1.cursor.execute("SELECT anec_text, source, date, id_entry FROM anecdotes_general_table WHERE cluster_num = %s LIMIT 1 OFFSET %s", (chosen_cluster, k))
                                            data = general_base1.cursor.fetchall()
                                        anec = data[0][0]
                                        source = data[0][1]
                                        date = data[0][2]
                                        id_entry = data[0][3]
                                        fin_mes = 'ID: {}-{}\n***anecbot***\n\n{}\n\nИстoчник: {}\nДата oпубликования в источнике: {}'.format(chosen_cluster, id_entry, anec, source, date)

                                        markup = types.InlineKeyboardMarkup(row_width = 10)
                                        item_1 = types.InlineKeyboardButton(1, callback_data = "mark 1")
                                        item_2 = types.InlineKeyboardButton(2, callback_data = "mark 2")
                                        item_3 = types.InlineKeyboardButton(3, callback_data = "mark 3")
                                        item_4 = types.InlineKeyboardButton(4, callback_data = "mark 4")
                                        item_5 = types.InlineKeyboardButton(5, callback_data = "mark 5")
                                        item_6 = types.InlineKeyboardButton(6, callback_data = "mark 6")
                                        item_7 = types.InlineKeyboardButton(7, callback_data = "mark 7")
                                        item_8 = types.InlineKeyboardButton(8, callback_data = "mark 8")
                                        item_9 = types.InlineKeyboardButton(9, callback_data = "mark 9")
                                        item_10 = types.InlineKeyboardButton(10, callback_data = "mark 10")
                                        item_11 = types.InlineKeyboardButton('Добавить в "Сохранённые"', callback_data = "add_to_save")
                                        markup.add(item_1, item_2, item_3, item_4, item_5)
                                        markup.add(item_6, item_7, item_8, item_9, item_10)
                                        markup.add(item_11)

                                        # changed upper O onto latin one!!!!!
                                        final = '{}\n\nOцените анекдот:'.format(fin_mes)

                                        # avoiding limit of max 4096 characters: check how it works, but separately selecting anecs with > 4096 characters!!!!
                                        if len(final) <= 4096:
                                            await call.message.answer(final, reply_markup = markup)  
                                        else:
                                            for x in range(0, len(final) - 4096, 4096):
                                                await call.message.answer(final[x : x + 4096])
                                            k = len(final)//4096
                                            await call.message.answer('ID: {}-{}\n***anecbot***\n\n'.format(chosen_cluster, id_entry) + final[k * 4096 : k * 4096 + 4096], reply_markup = markup)
                                #case when status is neither 0 nor 1
                                else:
                                    await call.message.answer('error in status')
                            else:
                                await call.message.answer('error in isn')
                        else:
                            await call.message.answer('error in is_present')
                            
                                     
            # next is just handler for other callback buttons, so different algorithms, but same packages and methods are used!
            # Not commenting other callback button handlers!!!
            elif call.data[:5] == 'anecs':
                with general_base1.connection:
                    general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (call.message.chat.id,))
                    isn = general_base1.cursor.fetchall()[0][0]
                if isn == 1:
                    await call.message.answer('На данный момент эта команда недоступна так как Вы находитесь в разделе "Начальная инструкция".\n\nЭта команда будет доступна, как только Вы завершите или пропустите начальную инструкцию')
                elif isn == 0:
                    with general_base1.connection:
                        general_base1.cursor.execute("SELECT in_a_row_started FROM anecs_in_a_row WHERE user_id = %s LIMIT 1", (call.message.chat.id,))
                        status = general_base1.cursor.fetchall()[0][0]
                    if status == 1:
                        await call.message.answer('Чтобы получить много анекдотов, сначала нажмите на кнопку "СТОП анеки подряд" на клавиатуре и затем нажмите на число под сообщением заново!')
                    elif status == 0:
                        nu = int(call.data[5:])
                        # remove inline buttons and edit initial message
                        await call.message.edit_reply_markup(reply_markup = None)
                        if nu in [1, 21]:
                            await call.message.edit_text('Вы выбрали получить {} анекдот'.format(nu))
                            await call.answer('Высылаю Вам {} анекдот'.format(nu))
                        elif nu in [2, 3, 4, 22, 23, 24]:
                            await call.message.edit_text('Вы выбрали получить {} анекдота'.format(nu))
                            await call.answer('Высылаю Вам {} анекдота'.format(nu))
                        else:
                            await call.message.edit_text('Вы выбрали получить {} анекдотов'.format(nu))
                            await call.answer('Высылаю Вам {} анекдотов'.format(nu))
                        # the rest is the same like in get 10 anecs, but changed 10 onto nu in for loop and adding call to messages!!!
                        with general_base1.connection:
                            general_base1.cursor.execute('SELECT * FROM users_sources WHERE user_id = %s LIMIT 1', (call.message.chat.id,))
                            li_user_sources = list(general_base1.cursor.fetchall()[0][2:])

                        if max(li_user_sources) == 0:
                            await call.message.answer('Вы отписались от всех источников! Чтобы получить анекдот, выберите хотя бы один источник в разделе "выбор_источников".')

                        else:
                            markup = types.InlineKeyboardMarkup(row_width = 10)
                            item_1 = types.InlineKeyboardButton(1, callback_data = "mark 1")
                            item_2 = types.InlineKeyboardButton(2, callback_data = "mark 2")
                            item_3 = types.InlineKeyboardButton(3, callback_data = "mark 3")
                            item_4 = types.InlineKeyboardButton(4, callback_data = "mark 4")
                            item_5 = types.InlineKeyboardButton(5, callback_data = "mark 5")
                            item_6 = types.InlineKeyboardButton(6, callback_data = "mark 6")
                            item_7 = types.InlineKeyboardButton(7, callback_data = "mark 7")
                            item_8 = types.InlineKeyboardButton(8, callback_data = "mark 8")
                            item_9 = types.InlineKeyboardButton(9, callback_data = "mark 9")
                            item_10 = types.InlineKeyboardButton(10, callback_data = "mark 10")
                            item_11 = types.InlineKeyboardButton('Добавить в "Сохранённые"', callback_data = "add_to_save")
                            markup.add(item_1, item_2, item_3, item_4, item_5)
                            markup.add(item_6, item_7, item_8, item_9, item_10)
                            markup.add(item_11)

                            li_clusters = [111, 112, 113, 114, 115, 116, 121, 122, 123, 124, 125, 131, 132, 133, 134, 211, 212, 213, 214, 221, 222, 223, 311, 312, 411, 511, 512, 513, 514, 612, 613, 614, 615, 711, 712, 713, 811, 812, 813, 911, 1011]

                            #making list of suitable clusters
                            fil_li_clu = li_clusters
                            for i in range(len(li_user_sources)):
                                if li_user_sources[i] == 1:
                                    pass
                                else:
                                    fil_li_clu = [j for j in fil_li_clu if j // 100 != i+1]

                            #preparing recomendation list
                            with general_base1.connection:
                                general_base1.cursor.execute("SELECT * FROM users_clusters WHERE user_id = %s AND source_activated = True", (call.message.chat.id,))
                                dan = general_base1.cursor.fetchall()

                                general_base1.cursor.execute("SELECT COUNT(*) FROM users_history WHERE user_id = %s", (call.message['chat']['id'],))
                                cou = general_base1.cursor.fetchall()[0][0]

                            liu = []
                            dictis = {}
                            for i in range(len(dan)):
                                liu.append(dan[i][4])

                            for i in range(len(dan)):
                                if min(liu) == max(liu):
                                    dictis[dan[i][2]] = float(max(np.log(max(cou, 1))/np.log(6)-1, 0)) + 1
                                else:
                                    dictis[dan[i][2]] = float(dan[i][4]-min(liu)) / float(max(liu)-min(liu)) * float(max(np.log(max(cou, 1))/np.log(6)-1, 0)) + 1

                            lui = []

                            for i in fil_li_clu:
                                if i in dictis.keys():
                                    lui.append(dictis[i])
                                else:
                                    lui.append(max(7, max(np.log(max(cou, 1))/np.log(6)-1, 0)))

                            louis = np.cumsum(np.array(lui) / sum(lui))

                            #start cycling here and remove general things above!
                            for j in range(nu):
                                nus = np.random.random()
                                if nus > 0.25 and nus < 1.01:
                                    n = np.random.random()
                                    for i in range(len(fil_li_clu)):
                                        if louis[i] > n:
                                            chosen_cluster = fil_li_clu[i]
                                            break  
                                elif nus <= 0.25 and nus > -0.01:
                                    chosen_cluster = int(np.random.choice(fil_li_clu))
                                else:
                                    await call.message.answer('error in nus')

                                with general_base1.connection:
                                    general_base1.cursor.execute('SELECT COUNT(*) FROM anecdotes_general_table WHERE cluster_num = %s', (chosen_cluster,))
                                    num_of_anec_cluster = general_base1.cursor.fetchall()[0][0]

                                k = np.random.randint(num_of_anec_cluster)

                                with general_base1.connection:
                                    general_base1.cursor.execute("SELECT anec_text, source, date, id_entry FROM anecdotes_general_table WHERE cluster_num = %s LIMIT 1 OFFSET %s", (chosen_cluster, k))
                                    data = general_base1.cursor.fetchall()
                                anec = data[0][0]
                                source = data[0][1]
                                date = data[0][2]
                                id_entry = data[0][3]
                                fin_mes = '{}) ID: {}-{}\n***anecbot***\n\n{}\n\nИстoчник: {}\nДата oпубликования в источнике: {}'.format(j + 1, chosen_cluster, id_entry, anec, source, date)

                                # changed upper O onto latin one!!!!!
                                final = '{}\n\nOцените анекдот:'.format(fin_mes)

                                # avoiding limit of max 4096 characters: check how it works, but separately selecting anecs with > 4096 characters!!!!
                                if len(final) <= 4096:
                                    await call.message.answer(final, reply_markup = markup)  
                                else:
                                    for x in range(0, len(final) - 4096, 4096):
                                        await call.message.answer(final[x : x + 4096])
                                    k = len(final)//4096
                                    await call.message.answer('{}) ID: {}-{}\n***anecbot***\n\n'.format(j + 1,  chosen_cluster, id_entry) + final[k * 4096 : k * 4096 + 4096], reply_markup = markup)
                    else:
                        await call.message.answer('error in status')
                else:
                    await call.message.answer('error in isn')

                          
            elif call.data == 'unsubscribe':
                
                # remove inline buttons
                await call.message.edit_reply_markup(reply_markup = None)
                
                # making dictionary!!!!
                dicta = {
                    'ВК паблик "Анекдоты (megaotriv)"': 0,
                    'ВК паблик "анекдотов.net"': 1,
                    'ВК паблик "Смешные анекдоты"': 2,
                    'Телеграмм канал "Анекдоты (AnekdotiRu)"': 3,
                    'ВК паблик "Анекдоты категории Б"': 4,
                    'ВК паблик "Анекдоты категории Б+"': 5,
                    'ВК паблик "Мои любимые юморески"': 6,
                    'Телеграмм канал "Мои любимые юморески"': 7,
                    'Телеграмм канал "Лига Плохих Шуток"': 8,
                    'ВК паблик "Лига плохих шуток"': 9                     
                }
                
                k = dicta[call.message['text'].split('\n')[0]]
                
                if k == 0:
                    with general_base1.connection:
                        general_base1.cursor.execute("UPDATE users_sources SET source_1_chosen = False WHERE user_id = %s", (call.message['chat']['id'],))
                elif k == 1:
                    with general_base1.connection:
                        general_base1.cursor.execute("UPDATE users_sources SET source_2_chosen = False WHERE user_id = %s", (call.message['chat']['id'],))
                elif k == 2:
                    with general_base1.connection:
                        general_base1.cursor.execute("UPDATE users_sources SET source_3_chosen = False WHERE user_id = %s", (call.message['chat']['id'],))
                elif k == 3:
                    with general_base1.connection:
                        general_base1.cursor.execute("UPDATE users_sources SET source_4_chosen = False WHERE user_id = %s", (call.message['chat']['id'],))
                elif k == 4:
                    with general_base1.connection:
                        general_base1.cursor.execute("UPDATE users_sources SET source_5_chosen = False WHERE user_id = %s", (call.message['chat']['id'],))
                elif k == 5:
                    with general_base1.connection:
                        general_base1.cursor.execute("UPDATE users_sources SET source_6_chosen = False WHERE user_id = %s", (call.message['chat']['id'],))
                elif k == 6:
                    with general_base1.connection:
                        general_base1.cursor.execute("UPDATE users_sources SET source_7_chosen = False WHERE user_id = %s", (call.message['chat']['id'],))
                elif k == 7:
                    with general_base1.connection:
                        general_base1.cursor.execute("UPDATE users_sources SET source_8_chosen = False WHERE user_id = %s", (call.message['chat']['id'],))
                elif k == 8:
                    with general_base1.connection:
                        general_base1.cursor.execute("UPDATE users_sources SET source_9_chosen = False WHERE user_id = %s", (call.message['chat']['id'],))
                elif k == 9:
                    with general_base1.connection:
                        general_base1.cursor.execute("UPDATE users_sources SET source_10_chosen = False WHERE user_id = %s", (call.message['chat']['id'],))
                        
                general_base1.update_source_subscription_in_users_clusters(0, call.message['chat']['id'], k+1)
                
                #checking that person is not novice
                with general_base1.connection:
                    general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (call.message.chat.id,))
                    isn = general_base1.cursor.fetchall()[0][0]
                if isn == 1:
                    await call.message.edit_text(text = 'Вы ОТПИСАЛИСЬ от источника:\n{}'.format(call.message['text'].split('\n')[0]))  
                    await call.message.answer('Супер, Вы отписались от источника! Теперь нажмите ту же кнопку с числом, которую Вы нажимали до этого, чтобы попробовать подписаться на этот источник обратно!')
                elif isn == 0:
                    await call.message.edit_text(text = 'Вы ОТПИСАЛИСЬ от источника:\n{}\n\nНажмите кнопку "Выйти", чтобы выйти в главное меню или выберите номер ещё одного источника, чтобы отписаться/подписаться. Номер источника можно найти нажав на кнопку "help источники"'.format(call.message['text'].split('\n')[0]))
                else: 
                    await call.message.answer('error in isn')
                                    
            
            elif call.data == 'subscribe':
                
                # remove inline buttons
                await call.message.edit_reply_markup(reply_markup = None)
                
                # make dictionary!!!!!!!
                dicta = {
                    'ВК паблик "Анекдоты (megaotriv)"': 0,
                    'ВК паблик "анекдотов.net"': 1,
                    'ВК паблик "Смешные анекдоты"': 2,
                    'Телеграмм канал "Анекдоты (AnekdotiRu)"': 3,
                    'ВК паблик "Анекдоты категории Б"': 4,
                    'ВК паблик "Анекдоты категории Б+"': 5,
                    'ВК паблик "Мои любимые юморески"': 6,
                    'Телеграмм канал "Мои любимые юморески"': 7,
                    'Телеграмм канал "Лига Плохих Шуток"': 8,
                    'ВК паблик "Лига плохих шуток"': 9    
                }
                
                k = dicta[call.message['text'].split('\n')[0]]

                if k == 0:
                    with general_base1.connection:
                        general_base1.cursor.execute("UPDATE users_sources SET source_1_chosen = True WHERE user_id = %s", (call.message['chat']['id'],))
                elif k == 1:
                    with general_base1.connection:
                        general_base1.cursor.execute("UPDATE users_sources SET source_2_chosen = True WHERE user_id = %s", (call.message['chat']['id'],))
                elif k == 2:
                    with general_base1.connection:
                        general_base1.cursor.execute("UPDATE users_sources SET source_3_chosen = True WHERE user_id = %s", (call.message['chat']['id'],))
                elif k == 3:
                    with general_base1.connection:
                        general_base1.cursor.execute("UPDATE users_sources SET source_4_chosen = True WHERE user_id = %s", (call.message['chat']['id'],))
                elif k == 4:
                    with general_base1.connection:
                        general_base1.cursor.execute("UPDATE users_sources SET source_5_chosen = True WHERE user_id = %s", (call.message['chat']['id'],))
                elif k == 5:
                    with general_base1.connection:
                        general_base1.cursor.execute("UPDATE users_sources SET source_6_chosen = True WHERE user_id = %s", (call.message['chat']['id'],))
                elif k == 6:
                    with general_base1.connection:
                        general_base1.cursor.execute("UPDATE users_sources SET source_7_chosen = True WHERE user_id = %s", (call.message['chat']['id'],))
                elif k == 7:
                    with general_base1.connection:
                        general_base1.cursor.execute("UPDATE users_sources SET source_8_chosen = True WHERE user_id = %s", (call.message['chat']['id'],))
                elif k == 8:
                    with general_base1.connection:
                        general_base1.cursor.execute("UPDATE users_sources SET source_9_chosen = True WHERE user_id = %s", (call.message['chat']['id'],))
                elif k == 9:
                    with general_base1.connection:
                        general_base1.cursor.execute("UPDATE users_sources SET source_10_chosen = True WHERE user_id = %s", (call.message['chat']['id'],))
                        
                general_base1.update_source_subscription_in_users_clusters(1, call.message['chat']['id'], k+1)
                
                #checking that person is not novice
                with general_base1.connection:
                    general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (call.message.chat.id,))
                    isn = general_base1.cursor.fetchall()[0][0]
                if isn == 1:
                    #keyboard
                    markup = types.ReplyKeyboardMarkup(row_width = 5)
                    item1 = types.KeyboardButton('Выйти')
                    item2 = types.KeyboardButton('Подписки и отписки')
                    item3 = types.KeyboardButton(1)
                    item4 = types.KeyboardButton(2)
                    item5 = types.KeyboardButton(3)
                    item6 = types.KeyboardButton(4)
                    item7 = types.KeyboardButton(5)
                    item8 = types.KeyboardButton(6)
                    item9 = types.KeyboardButton(7)
                    item10 = types.KeyboardButton(8)
                    item11 = types.KeyboardButton(9)
                    item12 = types.KeyboardButton(10)
                    item13 = types.KeyboardButton('Пропустить начальную инструкцию')

                    markup.add(item1)
                    markup.add(item2)
                    markup.add(item3, item4, item5, item6, item7)
                    markup.add(item8, item9, item10, item11, item12)
                    markup.add(item13)
                    await call.message.edit_text(text = 'Вы ПОДПИСАЛИСЬ на источник:\n{}'.format(call.message['text'].split('\n')[0]))  
                    await call.message.answer('Класс, теперь Вы знаете, как отписаться и подписаться обратно на тот или иной источник!\n\nТеперь, если Вы сразу знаете, что Вам точно не подходят те или иные источники, Вы можете от них отписаться.\nЕсли ещё не знакомы с этими источниками, то Вы можете познакомиться с ними, перейдя по ссылкам в сообщении внизу ИЛИ получая всё больше и больше анекдотов от меня.\n\nЕсли Вы на данный момент не хотите отписываться или подписываться на источнки, Вы всегда сможете это сделать потом, поэтому сейчас нажмите кнопку "Выйти", чтобы закончить начальную инструкцию!\n\nСсылки на источники:\n1. ВК паблик "Анекдоты (megaotriv)"\n(vk.com/megaotriv)\n2. ВК паблик "анекдотов.net"\n(vk.com/anekdot)\n3. ВК паблик "Смешные анедкоты"\n(vk.com/smeshnye__anekdoty)\n4. Телеграмм канал "Анекдоты (AnekdotiRu)"\n(t.me/AnekdotiRu)\n5. ВК паблик "Анекдоты категории Б"\n(vk.com/baneks)\n6. ВК паблик "Анекдоты категории Б+"\n(vk.com/anekdotikategoriib)\n7. ВК паблик "Мои любимые юморески"\n(vk.com/jumoreski)\n8. Телеграм канал "Мои любимые юморески"\n(t.me/myfavoritejumoreski)\n9. Телеграмм канал "Лига Плохих Шуток"\n(t.me/ligapsh)\n10. ВК паблик "Лига плохих шуток"\n(vk.com/badjokesleague)', reply_markup = markup, disable_web_page_preview = True)
                elif isn == 0:
                    await call.message.edit_text(text = 'Вы ПОДПИСАЛИСЬ на источник:\n{}\n\nНажмите кнопку "Выйти", чтобы выйти в главное меню или выберите номер ещё одного источника, чтобы отписаться/подписаться. Номер источника можно найти нажав на кнопку "help источники"'.format(call.message['text'].split('\n')[0]))
                else:
                    await call.message.answer('error in isn')
                
            
            elif call.data == 'exit':
                #checking that person is not novice
                with general_base1.connection:
                    general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (call.message.chat.id,))
                    isn = general_base1.cursor.fetchall()[0][0]
                if isn == 1:
                    await call.message.edit_reply_markup(reply_markup = None)
                    await call.message.edit_text(text = 'Вы нажали кнопку "отмена"')
                    await call.message.answer('Вы нажали кнопку "отмена"\n\nЕсли Вы не видите кнопку "Выйти" на своей клавиатуре, значит Вам нужно нажать на кнопку с числом на клавиатуре, которое соответствует источнику, НА КОТОРЫЙ ВЫ ПОДПИСАНЫ и затем попробовать отписаться и затем подписаться заново на этот источник, чтобы продолжить проходить начальную инструкцию.\n\nЕсли Вы видите кнопку "Выйти" и больше не хотите отписываться/подписываться на данный момент, то нажмите на "Выйти", чтобы продолжить проходить начальную инструкцию')
                elif isn == 0:
                    # remove inline buttons
                    await call.message.edit_reply_markup(reply_markup = None)
                    await call.message.edit_text(text = 'Вы нажали кнопку "отмена"\n\nНажмите кнопку "Выйти", чтобы выйти в главное меню или выберите номер источника, чтобы отписаться/подписаться. Номер источника можно найти нажав на кнопку "help источники"')
                    await call.answer('Вы остались при своих')
                else:
                    await call.message.answer('error in isn')
                
            elif call.data == 'exit1':
                # remove inline buttons
                await call.message.edit_reply_markup(reply_markup = None)
                
            elif call.data == 'exit_by_word':
                await call.message.edit_reply_markup(reply_markup = None)
                # some letters are probably latin in split!!!!
                await call.message.edit_text(text = call.message.text.split(':\nНайти анекдoт')[0] + ':\n\nВы нажали кнопку "отмена", поэтому я не буду присылать Вам анекдоты с этим словом.\n\nИспользуйте команды "Найти" или "Найти мои источники", чтобы найти анекдот по выбранному Вами слову!')
                
            elif call.data == 'exit_unsub_anec_day':
                await call.message.edit_reply_markup(reply_markup = None)
                await call.message.edit_text(text = 'Вы нажали на кнопку "отмена" и НЕ отписались от "Анека дня"\n\nЧтобы отписаться от "Анека дня", нажмите кнопку "Анек дня: отписаться" на клавиатуре заново!')
                
            elif call.data == 'exit_unsub_random_anec':
                await call.message.edit_reply_markup(reply_markup = None)
                await call.message.edit_text(text = 'Вы нажали на кнопку "отмена" и НЕ отписались от "Рандомного Анека"\n\nЧтобы отписаться от "Рандомного Анека", нажмите кнопку "Рандомный Анек: отписаться" на клавиатуре заново!')
                
            elif call.data == 'exit_sub_anec_day':
                await call.message.edit_reply_markup(reply_markup = None)
                await call.message.edit_text(text = 'Вы нажали на кнопку "отмена" и НЕ подписались на "Анек дня"\n\nЧтобы подписаться на "Анек дня", нажмите кнопку "Анек дня: подписаться" на клавиатуре заново!')
                
            elif call.data == 'exit_sub_random_anec':
                await call.message.edit_reply_markup(reply_markup = None)
                await call.message.edit_text(text = 'Вы нажали на кнопку "отмена" и НЕ подписались на "Рандомный Анек"\n\nЧтобы подписаться на "Рандомный Анек", нажмите кнопку "Рандомный Анек: подписаться" на клавиатуре заново!')
                
            elif call.data == 'exit2':
                await call.message.edit_reply_markup(reply_markup = None)
                await call.message.edit_text(text = 'Вы не выбрали количество анекдотов. Нажмите на кнопку "Получить много анеков" ещё раз или нажмите на одну из других кнопок, чтобы получить анекдот(-ы)!')
                
            elif call.data == 'exit3':
                await call.message.edit_reply_markup(reply_markup = None)
                await call.message.edit_text(text = 'Вы не выбрали количество первых сохранёнок. Нажмите на кнопку "Первые Сохры" ещё раз, чтобы получить первые добавленные Вами в сохранённые анекдоты!')
                
            elif call.data == 'exit4':
                await call.message.edit_reply_markup(reply_markup = None)
                await call.message.edit_text(text = 'Вы не выбрали количество последних сохранёнок. Нажмите на кнопку "Последние Сохры" ещё раз, чтобы получить последние добавленные Вами в сохранённые анекдоты!')
                
                
                
            elif call.data == 'get_anec_by_word':
                with general_base1.connection:
                    general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (call.message.chat.id,))
                    isn = general_base1.cursor.fetchall()[0][0]
                if isn == 1:
                    await call.message.answer('На данный момент эта команда недоступна так как Вы находитесь в разделе "Начальная инструкция".\n\nЭта команда будет доступна, как только Вы завершите или пропустите начальную инструкцию')
                elif isn == 0:
                    with general_base1.connection:
                        general_base1.cursor.execute("SELECT in_a_row_started FROM anecs_in_a_row WHERE user_id = %s LIMIT 1", (call.message.chat.id,))
                        status = general_base1.cursor.fetchall()[0][0]
                    if status == 1:
                        await call.message.answer('Чтобы я смог найти анекдоты по слову(-ам), сначала нажмите на кнопку "СТОП анеки подряд" на клавиатуре и затем нажмите на "Да" под сообщением заново!')
                    elif status == 0:
                        # latin o in anecdot!!!!!!
                        await call.message.edit_text(text = 'Cлово(-а): {}\nПроцесс поиска может занять некоторое время, подождите...'.format(call.message.text.split(':\nНайти анекдoт с этим словом(-ами)?')[0]))
                        word_raw = call.message.text.split(':\nНайти анекдoт')[0]
                        word_raw_nlp = nlp(word_raw)
                        lemmas = [token.lemma_ for token in word_raw_nlp]
                        a_lemmas = [lemma for lemma in lemmas if lemma.isalpha() or lemma == '-PRON-']
                        word_clean = ' '.join(a_lemmas)
                        with general_base1.connection:
                            coe = general_base1.cursor.execute("SELECT COUNT(*) FROM anecdotes_general_table WHERE anec_cl LIKE %(word)s", {'word': '%{}%'.format(word_clean)})
                            coe = general_base1.cursor.fetchall()[0][0]
                        if coe == 0:
                            await call.message.answer('Не удалось найти анекдот с этим словом(-ами). Выберите другое слово или уменьшите количество слов в фразе, чтобы найти анекдоты!')
                        else:
                            if coe % 10 in [0, 5, 6, 7, 8, 9] or coe % 100 - coe % 10 == 1:
                                await call.message.answer('Найдено {} анекдотов со словом {}'.format(coe, word_raw))
                            elif coe % 10 in [2, 3, 4]:
                                await call.message.answer('Найдено {} анекдота со словом {}'.format(coe, word_raw))
                            else:
                                await call.message.answer('Найден {} анекдот со словом {}'.format(coe, word_raw))
                            with general_base1.connection:
                                general_base1.cursor.execute("SELECT id_entry FROM anecdotes_general_table WHERE anec_cl LIKE %(word)s", {'word': '%{}%'.format(word_clean)})
                                anush = general_base1.cursor.fetchall()
                            if len(anush) >= 15:
                                kus = random.sample(anush, 15)
                            else:
                                kus = anush
                            kusi = []
                            for i in kus:
                                kusi.append(i[0])
                            ne = np.random.randint(len(kusi))
                            with general_base1.connection:
                                general_base1.cursor.execute("SELECT anec_text, source, date, id_entry, cluster_num FROM anecdotes_general_table WHERE id_entry = %s LIMIT 1", (kusi[ne],))
                                data = general_base1.cursor.fetchall()
                            kusi.remove(kusi[ne])

                            # anec style like in get anec with rating
                            anec = data[0][0]
                            source = data[0][1]
                            date = data[0][2]
                            id_entry = data[0][3]
                            cluster_num = data[0][4]
                            fin_mes = 'ID: {}-{}\n***anecbot***\n\n{}\n\nИстoчник: {}\nДата oпубликования в источнике: {}'.format(cluster_num, id_entry, anec, source, date)

                            markup = types.InlineKeyboardMarkup(row_width = 10)
                            item_1 = types.InlineKeyboardButton(1, callback_data = "mark 1")
                            item_2 = types.InlineKeyboardButton(2, callback_data = "mark 2")
                            item_3 = types.InlineKeyboardButton(3, callback_data = "mark 3")
                            item_4 = types.InlineKeyboardButton(4, callback_data = "mark 4")
                            item_5 = types.InlineKeyboardButton(5, callback_data = "mark 5")
                            item_6 = types.InlineKeyboardButton(6, callback_data = "mark 6")
                            item_7 = types.InlineKeyboardButton(7, callback_data = "mark 7")
                            item_8 = types.InlineKeyboardButton(8, callback_data = "mark 8")
                            item_9 = types.InlineKeyboardButton(9, callback_data = "mark 9")
                            item_10 = types.InlineKeyboardButton(10, callback_data = "mark 10")
                            item_11 = types.InlineKeyboardButton('Добавить в "Сохранённые"', callback_data = "add_to_save")
                            markup.add(item_1, item_2, item_3, item_4, item_5)
                            markup.add(item_6, item_7, item_8, item_9, item_10)
                            markup.add(item_11)

                            # changed upper O onto latin one!!!!!
                            final = '{}\n\nOцените анекдот:'.format(fin_mes)

                            # avoiding limit of max 4096 characters: check how it works, but separately selecting anecs with > 4096 characters!!!!
                            if len(final) <= 4096:
                                await call.message.answer(final, reply_markup = markup)  
                            else:
                                for x in range(0, len(final) - 4096, 4096):
                                    await call.message.answer(final[x : x + 4096])
                                k = len(final)//4096
                                await call.message.answer('ID: {}-{}\n***anecbot***\n\n'.format(cluster_num, id_entry) + final[k * 4096 : k * 4096 + 4096], reply_markup = markup)

                            # inline keyboard button with yes another word
                            markup1 = types.InlineKeyboardMarkup(row_width = 10)
                            item1 = types.InlineKeyboardButton('Да', callback_data = 'another_anec_with_word')
                            item2 = types.InlineKeyboardButton('Другое слово', callback_data = 'another_word')
                            markup1.add(item1)
                            markup1.add(item2)
                            await call.message.answer('Анекдот находится сообщением выше\n{}\n(не обращайте внимания на эти числа)\n\nХотите ещё один анекдот с этим же словом?'.format([coe,kusi]), reply_markup = markup1)
                    else:
                        await call.message.answer('error in status')
                else:
                    await call.message.answer('error in isn')

                    
            
            elif call.data == 'get_anec_by_word_group':
                with general_base1.connection:
                    general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (call.message.chat.id,))
                    isn = general_base1.cursor.fetchall()[0][0]
                if isn == 1:
                    await call.message.answer('На данный момент эта команда недоступна так как Вы находитесь в разделе "Начальная инструкция".\n\nЭта команда будет доступна, как только Вы завершите или пропустите начальную инструкцию')
                elif isn == 0:
                    with general_base1.connection:
                        general_base1.cursor.execute("SELECT in_a_row_started FROM anecs_in_a_row WHERE user_id = %s LIMIT 1", (call.message.chat.id,))
                        status = general_base1.cursor.fetchall()[0][0]
                    if status == 1:
                        await call.message.answer('Чтобы я смог найти анекдоты по слову(-ам) из Ваших любимых источников, сначала нажмите на кнопку "СТОП анеки подряд" на клавиатуре и затем нажмите на "Да" под сообщением заново!')
                    elif status == 0:
                        # search for groups, prefered by user
                        with general_base1.connection:
                            general_base1.cursor.execute("SELECT * FROM users_sources WHERE user_id = %s LIMIT 1", (call.message['chat']['id'],))
                            ka = list(general_base1.cursor.fetchall()[0])[2:]
                        lefrut = []
                        for i in range(len(ka)):
                            if ka[i] == 1:
                                lefrut.append(i + 1)
                            elif ka[i] == 0:
                                lefrut.append(0)
                            else:
                                print('error in ka[i]')

                        if max(lefrut) == 0:
                            await call.message.answer('Вы отписались от всех источников! Чтобы получить анекдот, выберите хотя бы один источник в разделе "выбор_источников".')
                        else:
                            # the rest is the almost same as in 'get_anec_by_word'!!!!!! 
                            # latin o in anecdot!!!!!!
                            await call.message.edit_text(text = 'Cлово(-а): {}\nПроцесс поиска может занять некоторое время, подождите...'.format(call.message.text.split(':\nНайти анекдoт из Ваших любимых источников с этим словом(-ами)?')[0]))
                            word_raw = call.message.text.split(':\nНайти анекдoт')[0]
                            word_raw_nlp = nlp(word_raw)
                            lemmas = [token.lemma_ for token in word_raw_nlp]
                            a_lemmas = [lemma for lemma in lemmas if lemma.isalpha() or lemma == '-PRON-']
                            word_clean = ' '.join(a_lemmas)
                            with general_base1.connection:
                                general_base1.cursor.execute("SELECT COUNT(*) FROM anecdotes_general_table WHERE anec_cl LIKE %(word)s AND source_id in (%(one)s, %(two)s, %(three)s, %(four)s, %(five)s, %(six)s, %(seven)s, %(eight)s, %(nine)s, %(ten)s)", {'word': '%{}%'.format(word_clean), 'one': lefrut[0], 'two': lefrut[1], 'three': lefrut[2], 'four': lefrut[3], 'five': lefrut[4], 'six': lefrut[5], 'seven': lefrut[6], 'eight': lefrut[7], 'nine': lefrut[8], 'ten': lefrut[9]})
                                coe = general_base1.cursor.fetchall()[0][0]
                            if coe == 0:
                                await call.message.answer('Не удалось найти анекдот из Ваших любимых источников с этим словом(-ами). Выберите другое слово, уменьшите количество слов в фразе или напишите это же слово, но после команды "Найти", чтобы найти анекдоты!')
                            else:
                                if coe % 10 in [0, 5, 6, 7, 8, 9] or coe % 100 - coe % 10 == 1:
                                    await call.message.answer('Найдено {} анекдотов из Ваших любимых источников со словом(-ами) {}'.format(coe, word_raw))
                                elif coe % 10 in [2, 3, 4]:
                                    await call.message.answer('Найдено {} анекдота из Ваших любимых источников со словом(-ами) {}'.format(coe, word_raw))
                                else:
                                    await call.message.answer('Найден {} анекдот из Ваших любимых источников со словом(-ами) {}'.format(coe, word_raw))

                                with general_base1.connection:
                                    general_base1.cursor.execute("SELECT id_entry FROM anecdotes_general_table WHERE anec_cl LIKE %(word)s AND source_id in (%(one)s, %(two)s, %(three)s, %(four)s, %(five)s, %(six)s, %(seven)s, %(eight)s, %(nine)s, %(ten)s)", {'word': '%{}%'.format(word_clean), 'one': lefrut[0], 'two': lefrut[1], 'three': lefrut[2], 'four': lefrut[3], 'five': lefrut[4], 'six': lefrut[5], 'seven': lefrut[6], 'eight': lefrut[7], 'nine': lefrut[8], 'ten': lefrut[9]})
                                    anush = general_base1.cursor.fetchall()
                                if len(anush) >= 15:
                                    kus = random.sample(anush, 15)
                                else:
                                    kus = anush
                                kusi = []
                                for i in kus:
                                    kusi.append(i[0])
                                ne = np.random.randint(len(kusi))
                                with general_base1.connection:
                                    general_base1.cursor.execute("SELECT anec_text, source, date, id_entry, cluster_num FROM anecdotes_general_table WHERE id_entry = %s LIMIT 1", (kusi[ne],))
                                    data = general_base1.cursor.fetchall()
                                kusi.remove(kusi[ne])

                                # anec style like in get anec with rating
                                anec = data[0][0]
                                source = data[0][1]
                                date = data[0][2]
                                id_entry = data[0][3]
                                cluster_num = data[0][4]
                                fin_mes = 'ID: {}-{}\n***anecbot***\n\n{}\n\nИстoчник: {}\nДата oпубликования в источнике: {}'.format(cluster_num, id_entry, anec, source, date)

                                markup = types.InlineKeyboardMarkup(row_width = 10)
                                item_1 = types.InlineKeyboardButton(1, callback_data = "mark 1")
                                item_2 = types.InlineKeyboardButton(2, callback_data = "mark 2")
                                item_3 = types.InlineKeyboardButton(3, callback_data = "mark 3")
                                item_4 = types.InlineKeyboardButton(4, callback_data = "mark 4")
                                item_5 = types.InlineKeyboardButton(5, callback_data = "mark 5")
                                item_6 = types.InlineKeyboardButton(6, callback_data = "mark 6")
                                item_7 = types.InlineKeyboardButton(7, callback_data = "mark 7")
                                item_8 = types.InlineKeyboardButton(8, callback_data = "mark 8")
                                item_9 = types.InlineKeyboardButton(9, callback_data = "mark 9")
                                item_10 = types.InlineKeyboardButton(10, callback_data = "mark 10")
                                item_11 = types.InlineKeyboardButton('Добавить в "Сохранённые"', callback_data = "add_to_save")
                                markup.add(item_1, item_2, item_3, item_4, item_5)
                                markup.add(item_6, item_7, item_8, item_9, item_10)
                                markup.add(item_11)

                                # changed upper O onto latin one!!!!!
                                final = '{}\n\nOцените анекдот:'.format(fin_mes)

                                # avoiding limit of max 4096 characters: check how it works, but separately selecting anecs with > 4096 characters!!!!
                                if len(final) <= 4096:
                                    await call.message.answer(final, reply_markup = markup)  
                                else:
                                    for x in range(0, len(final) - 4096, 4096):
                                        await call.message.answer(final[x : x + 4096])
                                    k = len(final)//4096
                                    await call.message.answer('ID: {}-{}\n***anecbot***\n\n'.format(chosen_cluster, id_entry) + final[k * 4096 : k * 4096 + 4096], reply_markup = markup)

                                # inline keyboard button with yes another word
                                markup1 = types.InlineKeyboardMarkup(row_width = 10)
                                item1 = types.InlineKeyboardButton('Да', callback_data = 'another_anec_with_word')
                                item2 = types.InlineKeyboardButton('Другое слово', callback_data = 'another_word')
                                markup1.add(item1)
                                markup1.add(item2)
                                await call.message.answer('Анекдот находится сообщением выше\n{}\n(не обращайте внимания на эти числа)\n\nХотите ещё один анекдот с этим же словом?'.format([coe,kusi]), reply_markup = markup1)
                    else:
                        await call.message.answer('error in status')
                else:
                    await call.message.answer('error in isn')

                    
            
            elif call.data == 'another_anec_with_word':
                with general_base1.connection:
                    general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (call.message.chat.id,))
                    isn = general_base1.cursor.fetchall()[0][0]
                if isn == 1:
                    await call.message.answer('На данный момент эта команда недоступна так как Вы находитесь в разделе "Начальная инструкция".\n\nЭта команда будет доступна, как только Вы завершите или пропустите начальную инструкцию')
                elif isn == 0:
                    with general_base1.connection:
                        general_base1.cursor.execute("SELECT in_a_row_started FROM anecs_in_a_row WHERE user_id = %s LIMIT 1", (call.message.chat.id,))
                        status = general_base1.cursor.fetchall()[0][0]
                    if status == 1:
                        await call.message.answer('Чтобы я смог отослать ещё анекдотов с конкретным(-и) словом(-ами), сначала нажмите на кнопку "СТОП анеки подряд" на клавиатуре и затем нажмите на "Да" под сообщением заново!')
                    elif status == 0:
                        # remove inline buttons
                        await call.message.edit_reply_markup(reply_markup = None)
                        await call.message.edit_text(text = 'Высылаю ещё один анекдот с этим же словом')

                        li = call.message.text.split('\n(не обр')[0].split('ением выше\n')[1]
                        lus = []
                        les = []
                        for i in li.replace(' ', ''):
                            try:
                                type(int(i))
                                lus.append(i)
                            except:
                                if lus != []:
                                    les.append(''.join(lus))
                                    lus = []
                        lon = [int(x) for x in les]

                        if len(lon) <= 1:
                            if lon[0] > 15:
                                await call.message.edit_text(text = 'За один запрос выдаётся 15 анекдотов. Если хотите ещё анекдотов с этим словом, пропишите команду\n"Найти" (или "Найти мои источники") и это слово через пробел заново')
                            else:
                                await call.message.edit_text(text = 'В базе больше нет анекдотов с этим словом. Чтобы найти анекдоты, содержащие другое слово, пропишите команду\n"Найти" (или "Найти мои источники") и нужное Вам слово через пробел ещё раз')

                        else:
                            ke = np.random.randint(1, len(lon))
                            lusung = lon[ke]
                            with general_base1.connection:
                                general_base1.cursor.execute("SELECT anec_text, source, date, id_entry, cluster_num FROM anecdotes_general_table WHERE id_entry = %s LIMIT 1", (lon[ke],))
                                data = general_base1.cursor.fetchall()
                            lon.remove(lon[ke])
                            # anec style like in get anec with rating
                            anec = data[0][0]
                            source = data[0][1]
                            date = data[0][2]
                            id_entry = data[0][3]
                            cluster_num = data[0][4]
                            fin_mes = 'ID: {}-{}\n***anecbot***\n\n{}\n\nИстoчник: {}\nДата oпубликования в источнике: {}'.format(cluster_num, id_entry, anec, source, date)

                            markup = types.InlineKeyboardMarkup(row_width = 10)
                            item_1 = types.InlineKeyboardButton(1, callback_data = "mark 1")
                            item_2 = types.InlineKeyboardButton(2, callback_data = "mark 2")
                            item_3 = types.InlineKeyboardButton(3, callback_data = "mark 3")
                            item_4 = types.InlineKeyboardButton(4, callback_data = "mark 4")
                            item_5 = types.InlineKeyboardButton(5, callback_data = "mark 5")
                            item_6 = types.InlineKeyboardButton(6, callback_data = "mark 6")
                            item_7 = types.InlineKeyboardButton(7, callback_data = "mark 7")
                            item_8 = types.InlineKeyboardButton(8, callback_data = "mark 8")
                            item_9 = types.InlineKeyboardButton(9, callback_data = "mark 9")
                            item_10 = types.InlineKeyboardButton(10, callback_data = "mark 10")
                            item_11 = types.InlineKeyboardButton('Добавить в "Сохранённые"', callback_data = "add_to_save")
                            markup.add(item_1, item_2, item_3, item_4, item_5)
                            markup.add(item_6, item_7, item_8, item_9, item_10)
                            markup.add(item_11)

                            # changed upper O onto latin one!!!!!
                            final = '{}\n\nOцените анекдот:'.format(fin_mes)

                            # avoiding limit of max 4096 characters: check how it works, but separately selecting anecs with > 4096 characters!!!!
                            if len(final) <= 4096:
                                await call.message.answer(final, reply_markup = markup)  
                            else:
                                for x in range(0, len(final) - 4096, 4096):
                                    await call.message.answer(final[x : x + 4096])
                                k = len(final)//4096
                                await call.message.answer('ID: {}-{}\n***anecbot***\n\n'.format(chosen_cluster, id_entry) + final[k * 4096 : k * 4096 + 4096], reply_markup = markup)

                            # inline keyboard button with yes another word
                            markup1 = types.InlineKeyboardMarkup(row_width = 10)
                            item1 = types.InlineKeyboardButton('Да', callback_data = 'another_anec_with_word')
                            item2 = types.InlineKeyboardButton('Другое слово', callback_data = 'another_word')
                            markup1.add(item1)
                            markup1.add(item2)
                            await call.message.answer('Новый анекдот находится сообщением выше\n{}\n(не обращайте внимания на эти числа)\n\nХотите ещё один анекдот с этим же словом?'.format(lon), reply_markup = markup1)
                    else:
                        await call.message.answer('error in status')
                else:
                    await call.message.answer('error in isn')
                
                
                
            elif call.data == 'another_word':
                # remove inline buttons
                await call.message.edit_reply_markup(reply_markup = None)
                await call.message.edit_text(text = 'Выбери другое слово и напиши его после команды\n "Найти" или "Найти мои источники" через пробел')
                
                
            elif call.data == 'subscribe_to_anec_of_the_day':
                with general_base1.connection:
                    general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (call.message.chat.id,))
                    isn = general_base1.cursor.fetchall()[0][0]
                if isn == 1:
                    await call.message.answer('На данный момент эта команда недоступна так как Вы находитесь в разделе "Начальная инструкция".\n\nЭта команда будет доступна, как только Вы завершите или пропустите начальную инструкцию')
                elif isn == 0:
                    # remove inline buttons
                    await call.message.edit_reply_markup(reply_markup = None)
                    #keyboard
                    with general_base1.connection:
                        general_base1.cursor.execute("SELECT in_a_row_started FROM anecs_in_a_row WHERE user_id = %s LIMIT 1", (call.message.chat.id,))
                        status = general_base1.cursor.fetchall()[0][0]
                        general_base1.cursor.execute("SELECT subscribed FROM users_sub_random_anec WHERE user_id = %s LIMIT 1", (call.message.chat.id,))
                        kz = general_base1.cursor.fetchall()[0][0]
                    markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
                    item1 = types.KeyboardButton("Анек")
                    item2 = types.KeyboardButton("10 Анеков")
                    item3 = types.KeyboardButton("Много Анеков")
                    if status == 0:   
                        item4 = types.KeyboardButton("СТАРТ Анеки подряд")
                    elif status == 1:
                        item4 = types.KeyboardButton("СТОП Анеки подряд")
                    else:
                        item4 = types.KeyboardButton("error in status")
                    item10 = types.KeyboardButton("Сохранённые Анеки")
                    item5 = types.KeyboardButton("Выбор источников")
                    item6 = types.KeyboardButton("Поиск Анека по слову: инструкция")
                    item7 = types.KeyboardButton("Список источников")
                    item8 = types.KeyboardButton("help")
                    item9 = types.KeyboardButton("Анек дня: отписаться")
                    if kz == 0:
                        item12 = types.KeyboardButton("Рандомный Анек: подписаться")
                    elif kz == 1:
                        item12 = types.KeyboardButton("Рандомный Анек: отписаться")
                    else:
                        await call.message.answer('error in kz') 
                    item11 = types.KeyboardButton('Последние 5 удалённых сохранёнок')
                    markup.add(item1, item2) 
                    markup.add(item3, item4)
                    markup.add(item10, item5)
                    markup.add(item6)
                    markup.add(item7, item8)
                    markup.add(item9)
                    markup.add(item12)
                    markup.add(item11)
                    general_base1.update_subscription_to_best_anec_day(call.message.chat.id, 1)
                    await call.message.edit_text(text = 'Вы подписались на "Анек дня". Каждый день Вы будете получать лучший анекдот дня из базы этого бота по мнению пользователей этого бота, а также канала AnecBot channel\n(t.me/anecbot_channel)') 
                    await call.message.answer('Подписывайтесь на канал, чтобы тоже участвовать в голосовании за \"Анек дня\"!', reply_markup = markup)
                else:
                    await call.message.answer('error in isn')

 

            elif call.data == 'unsubscribe_from_anec_of_the_day':
                with general_base1.connection:
                    general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (call.message.chat.id,))
                    isn = general_base1.cursor.fetchall()[0][0]
                if isn == 1:
                    await call.message.answer('На данный момент эта команда недоступна так как Вы находитесь в разделе "Начальная инструкция".\n\nЭта команда будет доступна, как только Вы завершите или пропустите начальную инструкцию')
                elif isn == 0:
                    # remove inline buttons
                    await call.message.edit_reply_markup(reply_markup = None)
                    #keyboard
                    with general_base1.connection:
                        general_base1.cursor.execute("SELECT in_a_row_started FROM anecs_in_a_row WHERE user_id = %s LIMIT 1", (call.message.chat.id,))
                        status = general_base1.cursor.fetchall()[0][0]
                        general_base1.cursor.execute("SELECT subscribed FROM users_sub_random_anec WHERE user_id = %s LIMIT 1", (call.message.chat.id,))
                        kz = general_base1.cursor.fetchall()[0][0]
                    markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
                    item1 = types.KeyboardButton("Анек")
                    item2 = types.KeyboardButton("10 Анеков")
                    item3 = types.KeyboardButton("Много Анеков")
                    if status == 0:   
                        item4 = types.KeyboardButton("СТАРТ Анеки подряд")
                    elif status == 1:
                        item4 = types.KeyboardButton("СТОП Анеки подряд")
                    else:
                        item4 = types.KeyboardButton("error in status")
                    item10 = types.KeyboardButton("Сохранённые Анеки")
                    item5 = types.KeyboardButton("Выбор источников")
                    item6 = types.KeyboardButton("Поиск Анека по слову: инструкция")
                    item7 = types.KeyboardButton("Список источников")
                    item8 = types.KeyboardButton("help")
                    item9 = types.KeyboardButton("Анек дня: подписаться")
                    if kz == 0:
                        item12 = types.KeyboardButton("Рандомный Анек: подписаться")
                    elif kz == 1:
                        item12 = types.KeyboardButton("Рандомный Анек: отписаться")
                    else:
                        await call.message.answer('error in kz') 
                    item11 = types.KeyboardButton('Последние 5 удалённых сохранёнок')
                    markup.add(item1, item2) 
                    markup.add(item3, item4)
                    markup.add(item10, item5)
                    markup.add(item6)
                    markup.add(item7, item8)
                    markup.add(item9)
                    markup.add(item12)
                    markup.add(item11)
                    general_base1.update_subscription_to_best_anec_day(call.message.chat.id, 0)
                    await call.message.edit_text(text = 'Вы отписались от \"Анека дня\"')
                    await call.message.answer('Чтобы подписаться обратно, нажмите кнопку "Анек дня: подписаться"!', reply_markup = markup)
                else:
                    await call.message.answer('error in isn')
            
            
            
            elif call.data == 'subscribe_to_random_anec':
                with general_base1.connection:
                    general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (call.message.chat.id,))
                    isn = general_base1.cursor.fetchall()[0][0]
                if isn == 1:
                    await call.message.answer('На данный момент эта команда недоступна так как Вы находитесь в разделе "Начальная инструкция".\n\nЭта команда будет доступна, как только Вы завершите или пропустите начальную инструкцию')
                elif isn == 0:
                    # remove inline buttons
                    await call.message.edit_reply_markup(reply_markup = None)
                    #keyboard
                    with general_base1.connection:
                        general_base1.cursor.execute("SELECT in_a_row_started FROM anecs_in_a_row WHERE user_id = %s LIMIT 1", (call.message.chat.id,))
                        status = general_base1.cursor.fetchall()[0][0]
                        general_base1.cursor.execute("SELECT subscribed FROM users_sub_best_anec_day WHERE user_id = %s LIMIT 1", (call.message.chat.id,))
                        ku = general_base1.cursor.fetchall()[0][0]
                    markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
                    item1 = types.KeyboardButton("Анек")
                    item2 = types.KeyboardButton("10 Анеков")
                    item3 = types.KeyboardButton("Много Анеков")
                    if status == 0:   
                        item4 = types.KeyboardButton("СТАРТ Анеки подряд")
                    elif status == 1:
                        item4 = types.KeyboardButton("СТОП Анеки подряд")
                    else:
                        item4 = types.KeyboardButton("error in status")
                    item10 = types.KeyboardButton("Сохранённые Анеки")
                    item5 = types.KeyboardButton("Выбор источников")
                    item6 = types.KeyboardButton("Поиск Анека по слову: инструкция")
                    item7 = types.KeyboardButton("Список источников")
                    item8 = types.KeyboardButton("help")
                    if ku == 0:
                        item9 = types.KeyboardButton("Анек дня: подписаться")
                    elif ku == 1:
                        item9 = types.KeyboardButton("Анек дня: отписаться")
                    else:
                        await call.message.answer('error in ku')
                    item12 = types.KeyboardButton("Рандомный Анек: отписаться") 
                    item11 = types.KeyboardButton('Последние 5 удалённых сохранёнок')
                    markup.add(item1, item2) 
                    markup.add(item3, item4)
                    markup.add(item10, item5)
                    markup.add(item6)
                    markup.add(item7, item8)
                    markup.add(item9)
                    markup.add(item12)
                    markup.add(item11)
                    general_base1.update_subscription_to_random_anec(call.message.chat.id, 1)
                    await call.message.edit_text(text = 'Вы подписались на Рандомный анек!') 
                    await call.message.answer('Теперь Вы будете получать случайный анекдот из моей базы 2 раза в день!', reply_markup = markup) 
                else:
                    await call.message.answer('error in isn')

 

            elif call.data == 'unsubscribe_from_random_anec':
                with general_base1.connection:
                    general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (call.message.chat.id,))
                    isn = general_base1.cursor.fetchall()[0][0]
                if isn == 1:
                    await call.message.answer('На данный момент эта команда недоступна так как Вы находитесь в разделе "Начальная инструкция".\n\nЭта команда будет доступна, как только Вы завершите или пропустите начальную инструкцию')
                elif isn == 0:
                    # remove inline buttons
                    await call.message.edit_reply_markup(reply_markup = None)
                    #keyboard
                    with general_base1.connection:
                        general_base1.cursor.execute("SELECT in_a_row_started FROM anecs_in_a_row WHERE user_id = %s LIMIT 1", (call.message.chat.id,))
                        status = general_base1.cursor.fetchall()[0][0]
                        general_base1.cursor.execute("SELECT subscribed FROM users_sub_best_anec_day WHERE user_id = %s LIMIT 1", (call.message.chat.id,))
                        ku = general_base1.cursor.fetchall()[0][0]
                    markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
                    item1 = types.KeyboardButton("Анек")
                    item2 = types.KeyboardButton("10 Анеков")
                    item3 = types.KeyboardButton("Много Анеков")
                    if status == 0:   
                        item4 = types.KeyboardButton("СТАРТ Анеки подряд")
                    elif status == 1:
                        item4 = types.KeyboardButton("СТОП Анеки подряд")
                    else:
                        item4 = types.KeyboardButton("error in status")
                    item10 = types.KeyboardButton("Сохранённые Анеки")
                    item5 = types.KeyboardButton("Выбор источников")
                    item6 = types.KeyboardButton("Поиск Анека по слову: инструкция")
                    item7 = types.KeyboardButton("Список источников")
                    item8 = types.KeyboardButton("help")
                    if ku == 0:
                        item9 = types.KeyboardButton("Анек дня: подписаться")
                    elif ku == 1:
                        item9 = types.KeyboardButton("Анек дня: отписаться")
                    else:
                        await call.message.answer('error in ku')
                    item12 = types.KeyboardButton("Рандомный Анек: подписаться") 
                    item11 = types.KeyboardButton('Последние 5 удалённых сохранёнок')
                    markup.add(item1, item2) 
                    markup.add(item3, item4)
                    markup.add(item10, item5)
                    markup.add(item6)
                    markup.add(item7, item8)
                    markup.add(item9)
                    markup.add(item12)
                    markup.add(item11)
                    general_base1.update_subscription_to_random_anec(call.message.chat.id, 0)
                    await call.message.edit_text(text = 'Вы отписались от Рандомного Анека')
                    await call.message.answer('Чтобы подписаться обратно, нажмите кнопку "Рандомный Анек: подписаться"!', reply_markup = markup)
                else:
                    await call.message.answer('error in isn')
            

                
            elif call.data == 'add_to_save':
                with general_base1.connection:
                    general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (call.message.chat.id,))
                    isn = general_base1.cursor.fetchall()[0][0]
                if isn == 1:
                    await call.message.answer('На данный момент эта команда недоступна так как Вы находитесь в разделе "Начальная инструкция".\n\nЭта команда будет доступна, как только Вы завершите или пропустите начальную инструкцию')
                elif isn == 0:
                    await call.message.edit_reply_markup(reply_markup = {"inline_keyboard": call.message.reply_markup.inline_keyboard[:-1]})
                    x = call.message['text'].split('\n***anecbot***\n\n')[0]
                    if x[0] == 'A':
                        x = x.split('\n')[1]
                    id_anec = x.split('-')[1]
                    with general_base1.connection:
                        general_base1.cursor.execute("SELECT * FROM saved_anecs_by_user WHERE user_id = %s AND id_anec = %s AND not_deleted = True LIMIT 1", (call.message.chat.id, id_anec))
                        lon = general_base1.cursor.fetchall()

                        general_base1.cursor.execute('SELECT * FROM saved_anecs_by_user WHERE user_id = %s AND id_anec = %s', (call.message.chat.id, id_anec))
                        kan = general_base1.cursor.fetchall()

                    if kan == []:
                        general_base1.add_anec_to_saved_anecs_by_user(call.message.chat.id, id_anec, round(time.time()))
                        with general_base1.connection:
                            general_base1.cursor.execute("SELECT COUNT(*) FROM saved_anecs_by_user WHERE user_id = %s AND not_deleted = True", (call.message.chat.id,))
                            ken = general_base1.cursor.fetchall()[0][0]                        
                        if ken == 20:
                            await call.message.answer('ВНИМАНИЕ! Вы сохранили 20 Анеков. При сохранении 20 Анеков и больше, при нажатии на кнопку "Сохранённые Анеки", будет открываться отдельная клавиатура с новыми кнопками. Попробуйте новый функционал кнопки "Сохранённые Анеки"!')
                        await call.answer('Анекдот добавлен в "Сохранённые Анеки"')
                    elif lon == []:
                        general_base1.update_status_of_saved_anec_and_add_or_remove_from_deleted_saved_table( call.message.chat.id, id_anec, 1)
                        with general_base1.connection:
                            general_base1.cursor.execute("SELECT COUNT(*) FROM saved_anecs_by_user WHERE user_id = %s AND not_deleted = True", (call.message.chat.id,))
                            ken = general_base1.cursor.fetchall()[0][0]
                        if ken == 20:
                            await call.message.answer('ВНИМАНИЕ! Вы сохранили 20 Анеков. При сохранении 20 Анеков и больше, при нажатии на кнопку "Сохранённые Анеки", будет открываться отдельная клавиатура с новыми кнопками. Попробуйте новый функционал кнопки "Сохранённые Анеки"!')
                        await call.answer('Анекдот добавлен в "Сохранённые Анеки"')
                    else:
                        await call.answer('Этот анекдот уже был добавлен в "Сохранённые Анеки"')
                else:
                    await call.message.answer('error in isn')
  

                    
            elif call.data == 'delete_saved':
                with general_base1.connection:
                    general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (call.message.chat.id,))
                    isn = general_base1.cursor.fetchall()[0][0]
                if isn == 1:
                    await call.message.answer('На данный момент эта команда недоступна так как Вы находитесь в разделе "Начальная инструкция".\n\nЭта команда будет доступна, как только Вы завершите или пропустите начальную инструкцию')
                elif isn == 0:
                    x = call.message['text'].split('\n***anecbot***\n\n')[0]
                    id_anec = x.split('-')[1]
                    with general_base1.connection:
                        general_base1.cursor.execute('SELECT * FROM saved_anecs_by_user WHERE user_id = %s AND id_anec = %s AND not_deleted = False', (call.message.chat.id, id_anec))
                        kan = general_base1.cursor.fetchall()
                    if kan == []:
                        markup = types.InlineKeyboardMarkup(row_width = 2)
                        item1 = types.InlineKeyboardButton('Да', callback_data = 'yes_delete_saved')
                        item2 = types.InlineKeyboardButton("Нет", callback_data = 'no_delete_saved')
                        markup.add(item1, item2)
                        await call.message.edit_text(text = call.message.text + '\n\nВы действительно хотите удалить этот анекдот из "Сохранённых"?')
                        await call.message.edit_reply_markup(reply_markup = markup)
                    else:
                        await call.message.edit_text(text = id_anec + '\nВы уже до этого удалили этот анекдот из сохранённых.\nЧтобы обратно добавить в "Сохранённые" удалённый анекдот, намжите на кнопку "Последние 5 удалённых сохранёнок"!') 
                        await call.answer('Анекдот уже удалён из сохранённых')
                else:
                    await call.message.answer('error in isn')

                        
                        
            elif call.data == 'yes_delete_saved':
                with general_base1.connection:
                    general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (call.message.chat.id,))
                    isn = general_base1.cursor.fetchall()[0][0]
                if isn == 1:
                    await call.message.answer('На данный момент эта команда недоступна так как Вы находитесь в разделе "Начальная инструкция".\n\nЭта команда будет доступна, как только Вы завершите или пропустите начальную инструкцию')
                elif isn == 0:
                    x = call.message['text'].split('\n***anecbot***\n\n')[0]
                    id_anec = x.split('-')[1]
                    with general_base1.connection:
                        general_base1.cursor.execute('SELECT * FROM saved_anecs_by_user WHERE user_id = %s AND id_anec = %s AND not_deleted = False', (call.message.chat.id, id_anec))
                        kan = general_base1.cursor.fetchall()
                    if kan == []:
                        general_base1.update_status_of_saved_anec_and_add_or_remove_from_deleted_saved_table( call.message.chat.id, id_anec, 0)
                        with general_base1.connection:
                            general_base1.cursor.execute("SELECT COUNT(*) FROM saved_anecs_by_user WHERE user_id = %s AND not_deleted = True", (call.message.chat.id,))
                            ken = general_base1.cursor.fetchall()[0][0]
                        if ken == 19:
                            with general_base1.connection:
                                general_base1.cursor.execute("SELECT subscribed FROM users_sub_best_anec_day WHERE user_id = %s LIMIT 1", (call.message.chat.id,))
                                ku = general_base1.cursor.fetchall()[0][0]
                                general_base1.cursor.execute("SELECT subscribed FROM users_sub_random_anec WHERE user_id = %s LIMIT 1", (message.chat.id,))
                                kz = general_base1.cursor.fetchall()[0][0]
                                general_base1.cursor.execute("SELECT in_a_row_started FROM anecs_in_a_row WHERE user_id = %s LIMIT 1", (call.message.chat.id,))
                                status = general_base1.cursor.fetchall()[0][0]
                            #keyboard
                            markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
                            item1 = types.KeyboardButton("Анек")
                            item2 = types.KeyboardButton("10 Анеков")
                            item3 = types.KeyboardButton("Много Анеков")
                            if status == 0:   
                                item4 = types.KeyboardButton("СТАРТ Анеки подряд")
                            elif status == 1:
                                item4 = types.KeyboardButton("СТОП Анеки подряд")
                            else:
                                item4 = types.KeyboardButton("error")
                            item10 = types.KeyboardButton("Сохранённые Анеки")
                            item5 = types.KeyboardButton("Выбор источников")
                            item6 = types.KeyboardButton("Поиск Анека по слову: инструкция")
                            item7 = types.KeyboardButton("Список источников")
                            item8 = types.KeyboardButton("help")
                            if ku == 0:
                                item9 = types.KeyboardButton("Анек дня: подписаться")
                            elif ku == 1:
                                item9 = types.KeyboardButton("Анек дня: отписаться")
                            else:
                                await call.message.answer('error in ku')
                            if kz == 0:
                                item12 = types.KeyboardButton("Рандомный Анек: подписаться")
                            elif kz == 1:
                                item12 = types.KeyboardButton("Рандомный Анек: отписаться")
                            else:
                                await message.answer('error in kz') 
                            item11 = types.KeyboardButton('Последние 5 удалённых сохранёнок')
                            markup.add(item1, item2) 
                            markup.add(item3, item4)
                            markup.add(item10, item5)
                            markup.add(item6)
                            markup.add(item7, item8)
                            markup.add(item9)
                            markup.add(item11)
                            await call.message.answer('Сейчас у Вас снова меньше 20 сохранённых анекдотов. Теперь Вы сможете получить все сохранённые анекдоты, нажав на кнопку "Сохранённые Анеки"!', reply_markup = markup)
                        await call.message.edit_text(text = id_anec + '\nВы удалили этот анекдот из сохранённых!\nЧтобы обратно добавить в "Сохранённые" удалённый анекдот, намжите на кнопку "Последние 5 удалённых сохранёнок"!') 
                        await call.answer('Анекдот удалён из сохранённых')

                    else:
                        await call.message.edit_text(text = id_anec + '\nВы уже до этого удалили этот анекдот из сохранённых.\nЧтобы обратно добавить в "Сохранённые" удалённый анекдот, намжите на кнопку "Последние 5 удалённых сохранёнок"!') 
                        await call.answer('Анекдот уже удалён из сохранённых')
                else:
                    await call.message.answer('error in isn')
 


            elif call.data == 'no_delete_saved':
                with general_base1.connection:
                    general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (call.message.chat.id,))
                    isn = general_base1.cursor.fetchall()[0][0]
                if isn == 1:
                    await call.message.answer('На данный момент эта команда недоступна так как Вы находитесь в разделе "Начальная инструкция".\n\nЭта команда будет доступна, как только Вы завершите или пропустите начальную инструкцию')
                elif isn == 0:
                    x = call.message['text'].split('\n***anecbot***\n\n')[0]
                    id_anec = x.split('-')[1]
                    with general_base1.connection:
                        general_base1.cursor.execute('SELECT * FROM saved_anecs_by_user WHERE user_id = %s AND id_anec = %s AND not_deleted = False', (call.message.chat.id, id_anec))
                        kan = general_base1.cursor.fetchall()
                    if kan == []:
                        await call.message.edit_text(text = call.message.text[:-62] + 'Вы НЕ удалили этот анекдот из сохранённых!') 
                        await call.answer('Анекдот НЕ удалён из сохранённых')
                    else:
                        await call.message.edit_text(text = id_anec + '\nВы уже до этого удалили этот анекдот из сохранённых.\nЧтобы обратно добавить в "Сохранённые" удалённый анекдот, намжите на кнопку "Последние 5 удалённых сохранёнок"!') 
                        await call.answer('Вы уже до этого удалили анекдот из сохранёнок')
                else:
                    await call.message.answer('error in isn')

                    
            
            elif call.data == 'recover_saved':
                with general_base1.connection:
                    general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (call.message.chat.id,))
                    isn = general_base1.cursor.fetchall()[0][0]
                if isn == 1:
                    await call.message.answer('На данный момент эта команда недоступна так как Вы находитесь в разделе "Начальная инструкция".\n\nЭта команда будет доступна, как только Вы завершите или пропустите начальную инструкцию')
                elif isn == 0:
                    x = call.message['text'].split('\n***anecbot***\n\n')[0]
                    id_anec = x.split('-')[1]
                    with general_base1.connection:
                        general_base1.cursor.execute('SELECT * FROM saved_anecs_by_user WHERE user_id = %s AND id_anec = %s AND not_deleted = True', (call.message.chat.id, id_anec))
                        kan = general_base1.cursor.fetchall()
                    if kan == []:
                        markup = types.InlineKeyboardMarkup(row_width = 2)
                        item1 = types.InlineKeyboardButton('Да', callback_data = 'yes_recover')
                        item2 = types.InlineKeyboardButton("Нет", callback_data = 'no_recover')
                        markup.add(item1, item2)
                        await call.message.edit_text(text = call.message.text + '\n\nВы действительно хотите добавить этот анекдот в "Сохранённые" обратно?')
                        await call.message.edit_reply_markup(reply_markup = markup)
                    else:
                        await call.message.edit_text(text = id_anec + '\nАнекдот уже находится у Вас в сохранённых!') 
                        await call.answer('Анекдот уже в сохранёнках')
                else:
                    await call.message.answer('error in isn')
                    
                    
                    
            elif call.data == 'yes_recover':
                with general_base1.connection:
                    general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (call.message.chat.id,))
                    isn = general_base1.cursor.fetchall()[0][0]
                if isn == 1:
                    await call.message.answer('На данный момент эта команда недоступна так как Вы находитесь в разделе "Начальная инструкция".\n\nЭта команда будет доступна, как только Вы завершите или пропустите начальную инструкцию')
                elif isn == 0:
                    x = call.message['text'].split('\n***anecbot***\n\n')[0]
                    if x[0] == 'A':
                        x = x.split('\n')[1]
                    id_anec = x.split('-')[1]
                    with general_base1.connection:
                        general_base1.cursor.execute("SELECT * FROM saved_anecs_by_user WHERE user_id = %s AND id_anec = %s AND not_deleted = True LIMIT 1", (call.message.chat.id, id_anec))
                        lon = general_base1.cursor.fetchall()
                    if lon == []:
                        general_base1.update_status_of_saved_anec_and_add_or_remove_from_deleted_saved_table(call.message.chat.id, id_anec, 1)
                        with general_base1.connection:
                            general_base1.cursor.execute("SELECT COUNT(*) FROM saved_anecs_by_user WHERE user_id = %s AND not_deleted = True", (call.message.chat.id,))
                            ken = general_base1.cursor.fetchall()[0][0]
                        if ken == 20:
                            await call.message.answer('ВНИМАНИЕ! Вы сохранили 20 Анеков. При сохранении 20 Анеков и больше, при нажатии на кнопку "Сохранённые Анеки", будет открываться отдельная клавиатура с новыми кнопками. Попробуйте новый функционал кнопки "Сохранённые Анеки"!')
                        await call.message.edit_text(text = id_anec + '\nВы добавили этот анекдот обратно в "Сохранённые Анеки"!') 
                        await call.answer('Анекдот добавлен обратно в сохранёнки')
                    else:
                        await call.message.edit_text(text = id_anec + '\nЭтот анекдот уже находится у Вас в "Сохранённых Анеках"!') 
                        await call.answer('Этот анекдот уже был добавлен обратно в сохранёнки')
                else:
                    await call.message.answer('error in isn')
                        
                    
                    
            elif call.data == 'no_recover':
                with general_base1.connection:
                    general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (call.message.chat.id,))
                    isn = general_base1.cursor.fetchall()[0][0]
                if isn == 1:
                    await call.message.answer('На данный момент эта команда недоступна так как Вы находитесь в разделе "Начальная инструкция".\n\nЭта команда будет доступна, как только Вы завершите или пропустите начальную инструкцию')
                elif isn == 0:
                    x = call.message['text'].split('\n***anecbot***\n\n')[0]
                    id_anec = x.split('-')[1]
                    with general_base1.connection:
                        general_base1.cursor.execute('SELECT * FROM saved_anecs_by_user WHERE user_id = %s AND id_anec = %s AND not_deleted = True', (call.message.chat.id, id_anec))
                        kan = general_base1.cursor.fetchall()
                    if kan == []:
                        await call.message.edit_text(text = call.message.text[:-70] + 'Вы НЕ добавлили этот анекдот обратно в сохранённые!') 
                        await call.answer('Анекдот НЕ добавлен обратно в сохранёнки')
                    else:
                        await call.message.edit_text(text = id_anec + '\nАнекдот уже находится у Вас в сохранённых!') 
                        await call.answer('Вы уже до этого добавили анекдот в сохранёнки')
                else:
                    await call.message.answer('error in isn')
             
            
            
            elif call.data[:10] == 'savedfirst':
                with general_base1.connection:
                    general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (call.message.chat.id,))
                    isn = general_base1.cursor.fetchall()[0][0]
                if isn == 1:
                    await call.message.answer('На данный момент эта команда недоступна так как Вы находитесь в разделе "Начальная инструкция".\n\nЭта команда будет доступна, как только Вы завершите или пропустите начальную инструкцию')
                elif isn == 0:
                    with general_base1.connection:
                        general_base1.cursor.execute("SELECT COUNT(*) FROM saved_anecs_by_user WHERE user_id = %s AND not_deleted = True", (call.message.chat.id,))
                        ken = general_base1.cursor.fetchall()[0][0]
                    if ken < 20:
                        with general_base1.connection:
                            general_base1.cursor.execute("SELECT subscribed FROM users_sub_best_anec_day WHERE user_id = %s LIMIT 1", (call.message.chat.id,))
                            ku = general_base1.cursor.fetchall()[0][0]
                            general_base1.cursor.execute("SELECT in_a_row_started FROM anecs_in_a_row WHERE user_id = %s LIMIT 1", (call.message.chat.id,))
                            status = general_base1.cursor.fetchall()[0][0]
                            general_base1.cursor.execute("SELECT subscribed FROM users_sub_random_anec WHERE user_id = %s LIMIT 1", (call.message.chat.id,))
                            kz = general_base1.cursor.fetchall()[0][0]

                        #keyboard
                        markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
                        await main_markup(markup, ku, status, kz)
                        await call.message.answer('Вы cохранили меньше 20 анекдотов. Поэтому, при нажатии на кнопку "Сохранённые Анеки", Вам автоматически будут присылаться все сохранённые Вами анекдоты!', reply_markup = markup)
                    else:
                        nu = int(call.data[10:])
                        # remove inline buttons and edit initial message
                        await call.message.edit_reply_markup(reply_markup = None)
                        if nu == 1:
                            await call.message.edit_text('Вы выбрали получить самый первый сохранённый анекдот'.format(nu))
                            await call.answer('Высылаю Вам {} анекдот'.format(nu))
                        elif nu in [2, 3, 4]:
                            await call.message.edit_text('Вы выбрали получить {} первых сохранённых анекдота'.format(nu))
                            await call.answer('Высылаю Вам {} анекдота'.format(nu))
                        else:
                            await call.message.edit_text('Вы выбрали получить {} первых сохранённых анекдотов'.format(nu))
                            await call.answer('Высылаю Вам {} анекдотов'.format(nu))

                        with general_base1.connection:
                            duta = general_base1.cursor.execute("SELECT cluster_num, id_entry, anec_text, source, epoch_time_added FROM saved_anecs_by_user AS sabu INNER JOIN anecdotes_general_table AS agt ON sabu.id_anec = agt.id_entry WHERE user_id = %s AND not_deleted = True ORDER BY epoch_time_added LIMIT %s", (call.message.chat.id, nu))
                            duta = general_base1.cursor.fetchall()

                        markup = types.InlineKeyboardMarkup(row_width = 2)
                        item_1 = types.InlineKeyboardButton("Удалить Анек из \"Сохранённых\"", callback_data = 'delete_saved')
                        markup.add(item_1)

                        for i in range(nu):
                            final = '{}) ID: {}-{}\n***anecbot***\n\n{}\n\nИстoчник: {}\nДата сохранения Анека: {}'.format(i + 1, duta[i][0], duta[i][1], duta[i][2], duta[i][3], datetime.fromtimestamp(duta[i][4]).strftime('%Y-%m-%d')) 
                            if len(final) <= 4096:
                                await call.message.answer(final, reply_markup = markup)  
                            else:
                                for x in range(0, len(final) - 4096, 4096):
                                    await call.message.answer(final[x : x + 4096])
                                k = len(final)//4096
                                await call.message.answer('{}) ID: {}-{}\n***anecbot***\n\n'.format(i + 1, duta[i][0], duta[i][1]) + final[k * 4096 : k * 4096 + 4096], reply_markup = markup) 
                else:
                    await call.message.answer('error in isn')
                
 

            elif call.data[:9] == 'savedlast':
                with general_base1.connection:
                    general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (call.message.chat.id,))
                    isn = general_base1.cursor.fetchall()[0][0]
                if isn == 1:
                    await call.message.answer('На данный момент эта команда недоступна так как Вы находитесь в разделе "Начальная инструкция".\n\nЭта команда будет доступна, как только Вы завершите или пропустите начальную инструкцию')
                elif isn == 0:
                    with general_base1.connection:
                        general_base1.cursor.execute("SELECT COUNT(*) FROM saved_anecs_by_user WHERE user_id = %s AND not_deleted = True", (call.message.chat.id,))
                        ken = general_base1.cursor.fetchall()[0][0]
                    if ken < 20:
                        with general_base1.connection:
                            general_base1.cursor.execute("SELECT subscribed FROM users_sub_best_anec_day WHERE user_id = %s LIMIT 1", (call.message.chat.id,))
                            ku = general_base1.cursor.fetchall()[0][0]
                            general_base1.cursor.execute("SELECT in_a_row_started FROM anecs_in_a_row WHERE user_id = %s LIMIT 1", (call.message.chat.id,))
                            status = general_base1.cursor.fetchall()[0][0]
                            general_base1.cursor.execute("SELECT subscribed FROM users_sub_random_anec WHERE user_id = %s LIMIT 1", (call.message.chat.id,))
                            kz = general_base1.cursor.fetchall()[0][0]

                        #keyboard
                        markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
                        await main_markup(markup, ku, status, kz)
                        await call.message.answer('Вы cохранили меньше 20 анекдотов. Поэтому, при нажатии на кнопку "Сохранённые Анеки", Вам автоматически будут присылаться все сохранённые Вами анекдоты!', reply_markup = markup)
                    else:
                        nu = int(call.data[9:])
                        # remove inline buttons and edit initial message
                        await call.message.edit_reply_markup(reply_markup = None)
                        if nu == 1:
                            await call.message.edit_text('Вы выбрали получить самый последний анекдот'.format(nu))
                            await call.answer('Высылаю Вам {} анекдот'.format(nu))
                        elif nu in [2, 3, 4]:
                            await call.message.edit_text('Вы выбрали получить {} самых последних сохранённых анекдота'.format(nu))
                            await call.answer('Высылаю Вам {} анекдота'.format(nu))
                        else:
                            await call.message.edit_text('Вы выбрали получить {} самых последних сохранённых анекдотов'.format(nu))
                            await call.answer('Высылаю Вам {} анекдотов'.format(nu))

                        with general_base1.connection:
                            general_base1.cursor.execute("SELECT cluster_num, id_entry, anec_text, source, epoch_time_added FROM saved_anecs_by_user AS sabu INNER JOIN anecdotes_general_table AS agt ON sabu.id_anec = agt.id_entry WHERE user_id = %s AND not_deleted = True ORDER BY epoch_time_added DESC LIMIT %s", (call.message.chat.id, nu))
                            duta = general_base1.cursor.fetchall()

                        markup = types.InlineKeyboardMarkup(row_width = 2)
                        item_1 = types.InlineKeyboardButton("Удалить Анек из \"Сохранённых\"", callback_data = 'delete_saved')
                        markup.add(item_1)

                        for i in range(nu):
                            final = '{}) ID: {}-{}\n***anecbot***\n\n{}\n\nИстoчник: {}\nДата сохранения Анека: {}'.format(i + 1, duta[i][0], duta[i][1], duta[i][2], duta[i][3], datetime.fromtimestamp(duta[i][4]).strftime('%Y-%m-%d')) 
                            if len(final) <= 4096:
                                await call.message.answer(final, reply_markup = markup)  
                            else:
                                for x in range(0, len(final) - 4096, 4096):
                                    await call.message.answer(final[x : x + 4096])
                                k = len(final)//4096
                                await call.message.answer('{}) ID: {}-{}\n***anecbot***\n\n'.format(i + 1, duta[i][0], duta[i][1]) + final[k * 4096 : k * 4096 + 4096], reply_markup = markup) 
                else:
                    await call.message.answer('error in isn')
                
                   
                
            elif call.data[:7] == 'button_':
                if call.data == 'button_intro_instruction':
                    if call.message.chat.id < 0:
                        await call.message.answer('РАЗДЕЛ "Начальная инструкция (текстовая)"\n(Если Вы новый пользователь, то для интерактивной начальной инструкции нажмите сюда -> @bot_anecbot и нажмите на "ЗАПУСТИТЬ" ("START"). Вам сразу же откроется интерактивная начальная инструкция! Если Вы не новый пользователь, зайдите в чат со мной (@bot_anecbot), нажмите на "help" и затем нажмите на "Начальная инструкция" под появившимся сообщением)\n\nДля начала, я на всякий случай хочу заметить, что я часто использую слово "Анек". Если это слово вводит Вас в ступор, то не волнуйтесь: "Анек" это сокращение слова "Анекдот". Поэтому, чтобы получить анекдот, нажмите на кнопку "Анек" на клавиатуре (самая верхняя кнопка слева). После нажатия Вам придёт сообщение, в котором Вы увидите анекдот, его источник и дату опубликования.\n\nЗатем Вам будет предложено оценить анекдот оценкой от 1 до 10. Оценивать анекдоты очень важно, так как, именно исходя из Ваших оценок, я буду стараться подбирать Вам следующие анекдоты, чтобы они Вам точно понравились.\n\nТакже очень важно понимать, что разные источники содержат разные анекдоты. Поэтому я советую Вам на начальном этапе понять, какие источники Вам нравятся, а какие нет, переходя по ссылкам на источники (для этого нажмите на кнопку "Список источников" на 5ом ряду клавиатуры слева) или постепенно читая анекдоты здесь с помощью кнопки "Анек"\n\nИзначально Вы получаете анекдоты изо всех источников. Однако, вы можете отписаться от некоторых источников, то есть не получать анекдоты оттуда, с помощью кнопки "Выбор источников". Нажав на эту кнопку, Вам откроется клавиатура с новыми кнопками, с помощью которых Вы легко сможете отписаться или подписаться на те или иные источники. Нажмите на кнопку "Выбор источников" для более подробной информации о процедуре подписки и отписки от источников.\n\nЕсли Вы прошли все эти шаги, то Вы уже можете считаться профессиональным пользователем. С большой вероятностью Вам уже будут попадаться анекдоты, которые Вам понравятся! После этих шагов Вы можете постепенно изучать функционал других кнопок, чтобы получить ещё более качественный сервис от меня!\n\nНе забывайте, что меню с инструкцией по всем кнопкам всегда можно вызвать в любой момент нажав на кнопку "help" на клавиатуре!')
                        await call.answer('Отослал раздел "Начальная инструкция"')
                    else:
                        with general_base1.connection:
                            general_base1.cursor.execute("SELECT in_a_row_started FROM anecs_in_a_row WHERE user_id = %s LIMIT 1", (call.message.chat.id,))
                            status = general_base1.cursor.fetchall()[0][0]
                        if status == 1:
                            await call.message.answer('Чтобы Вы смогли зайти в раздел "Начальная инструкция", сначала нажмите на кнопку "СТОП анеки подряд" на клавиатуре и затем нажмите на "Начальная инструкция" под сообщением заново!')
                        elif status == 0:
                            general_base1.update_is_novice(call.message.chat.id, 1)
                            await call.message.edit_text('Вы находитесь в разделе "Начальная инструкция"!')
                            #keyboard
                            markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
                            item1 = types.KeyboardButton("Анек")
                            item2 = types.KeyboardButton("Пропустить начальную инструкцию")
                            markup.add(item1)
                            markup.add(item2)
                            await call.message.answer('Привет, это AnecBot!\nЯ подбираю анекдоты специально для Вас из базы, содержащей более чем 170000 анекдотов!\n\nДля начала найдите две кнопки на Вашей клавиатуре: "Анек" и "Пропустить начальную инструкцию". Если Вы не видите этих кнопок, то накжмите на квадратик с 4-мя кружочками внутри рядом в верхнем углу клавиатуры справа рядом со значком микрофона.\n\nТеперь нажмите на кнопку "Анек", чтобы получить анекдот!\n\n(Вы можете выйти в главное меню, нажав на кнопку "Пропустить начальную инструкцию", НО я не рекомендую Вам этого делать, если Вы до этого не проходили до конца эту инструкцию)', reply_markup = markup)
                        else:
                            await call.message.answer('error in status')
                    
                    
                    
                elif call.data == 'button_anec':
                    await call.message.answer('ИНСТРУКЦИЯ ПО КНОПКЕ "Анек"\n(верхняя кнопка слева на клавиатуре)\n\nНажав на эту кнопку, я пришлю Вам сообщение с анекдотом, источником и датой опубликования. под сообщением Вы увидите кнопки с числами от 1 до 10, а также кнопку с надписью "Добавить в "Сохранённые"".\n\nЧисла означают оценки за анекдот по шкале от 1 до 10. Оценивать анекдоты очень важно, так как, именно исходя из Ваших оценок, я буду стараться подбирать Вам следующие анекдоты, чтобы они Вам точно понравились. После нажатия на одну из цифр, Вы получите уведомление, что ваша оценка сохранена и в конце сообщения Вы увидите Вашу оценку. Также после нажатия на одну из цифр, все кнопки с цифрами под сообщением исчезнут.\n\nПосле нажатия на кнопку "Добавить в "Сохранённые"", эта кнопка исчезнет, и Вы получите уведомление, что анекдот добавлен в сохранённые. Вы сможете найти сохранённый анекдот, нажав на кнопку "Сохранённые Анеки" (3ий ряд клавиатуры слева).\n\nЭта кнопка лишь один из способов получения анекдотов. Советую прочитать отличия кнопок "10 Анеков", "Много Анеков", "СТАРТ/СТОП Анеки подряд" (1ый и 2ой ряд клавиатуры) от кнопки "Анек". Эти кнопки могут сделать для Вас процесс получения анекдотов более удобным!\n\nНе забывайте, что меню с инструкцией по всем кнопкам всегда можно вызвать в любой момент нажав на кнопку "help" на клавиатуре!')
                    await call.answer('Отослал инструкцию по кнопке "Анек"')
                    
                elif call.data == 'button_ten_anecs':
                    await call.message.answer('ИНСТРУКЦИЯ ПО КНОПКЕ "10 Анеков"\n(верхняя кнопка справа на клавиатуре)\nЭта кнопка выполняет практитечки ту же функцию, что и кнопка "Анек". Единственное отличие заключается в том, что я пришлю Вам сразу 10 анекдотов.\n\nНе забывайте, что меню с инструкцией по всем кнопкам всегда можно вызвать в любой момент нажав на кнопку "help" на клавиатуре!')
                    await call.answer('Отослал инструкцию по кнопке "10 Анеков"')
                    
                elif call.data == 'button_many_anecs':
                    await call.message.answer('ИНСТРУКЦИЯ ПО КНОПКЕ "Много Анеков"\n(левая кнопка на 2ом ряду клавиатуры)\n\nЭта кнопка выполняет схожую функцию, что и кнопка "Анек". Отличие заключается в том, что перед получением анекдотов Вы должны выбрать количество анекдотов от 1 до 25. Нажав на число, я пришлю Вам соответственное количество анекдотов.\n\nНе забывайте, что меню с инструкцией по всем кнопкам всегда можно вызвать в любой момент нажав на кнопку "help" на клавиатуре!')
                    await call.answer('Отослал инструкцию по кнопке "Много Анеков"')
                elif call.data == 'button_anecs_in_a_row':
                    await call.message.answer('ИНСТРУКЦИЯ ПО КНОПКЕ "СТАРТ/СТОП Анеки подряд"\n(правая кнопка на 2ом ряду клавиатуры)\n\nЕсли на этой кнопке написано "СТАРТ Анеки подряд", то после нажатия на неё текст на кнопке станет "СТОП Анеки подряд" и наоборот!\n\nЭта кнопка выполняет схожую функцию, что и кнопка "Анек". Отличие заключается в том, что как только Вы нажали на "СТАРТ Анеки подряд" и не нажали на "СТОП Анеки подряд", после оценки каждого анекдота (нажатие числа от 1 до 10), Вам автоматически будет присылаться следующий анекдот.\n\nТакже стоит отметить, что если Вы нажали на "СТАРТ Анеки подряд", но не нажали на "СТОП Анеки подряд", кнопки "Анек", "10 Анеков" и "Много Анеков" не будут работать должным образом!\n\nНе забывайте, что меню с инструкцией по всем кнопкам всегда можно вызвать в любой момент нажав на кнопку "help" на клавиатуре!')
                    await call.answer('Отослал инструкцию по кнопке "СТАРТ/СТОП Анеки подряд"')
                elif call.data == 'button_saved_anecs':
                    await call.message.answer('ИНСТРУКЦИЯ ПО КНОПКЕ "Сохранённые Анеки"\n(левая кнопка на 3ем ряду клавиатуры)\n\nЗдесь находятся все анекдоты, которые Вы до это добавили в сохранённые. Если Вы сохранили меньше 20 анекдотов, то при нажатии на кнопку "Сохранённые Анеки" я пришлю Вам все Ваши сохранённые анекдоты. Если Вы сохранили 20 анекдотов и больше, то при нажатии на эту кнопку, Вам откроется клавиатура с новыми кнопки, где с помощью встроенной мини-инструкции, Вы с лёгкостью сможете найти и получить те или иные анекдоты. Не парьтесь по поводу этого, если у Вы сохранили меньше 20 анекдотов.\n\nБолее того, каждый раз, когда я буду присылать Вам сохранённый анекдот, у Вас будет возможность удалить этот анекдот, нажав на кнопку "Удалить Анек из "Сохранённых"", и затем подтвердив удаление, нажав на кнопку "Да", котороая должна появиться после нажатия на "Удалить Анек из "Сохранённых"". Если Вы случайно удалили какой-то из сохранённых анекдотов, его можно будет восстановить (добавить в сохранённые обратно), нажав на кнопку "Последние 5 удалённых сохранёнок".\n\nНе забывайте, что меню с инструкцией по всем кнопкам всегда можно вызвать в любой момент нажав на кнопку "help" на клавиатуре!')
                    await call.answer('Отослал инструкцию по кнопке "Сохранённые Анеки"')
                elif call.data == 'button_choose_sources':
                    await call.message.answer('ИНСТРУКЦИЯ ПО КНОПКЕ "Выбор источников"\n(правая кнопка на 3ем ряду клавиатуры)\n\nС помощью этой кнопки Вы сможете отписаться или подписаться на те или иные источники. После нажатия на эту кнопку, Вам откроется клавиатура с новыми кнопками, с помощью которых Вы сможете узнать, как отписаться или подписаться на источник, на какие источники Вы подписаны или не подписаны в данный момент и, конечно же, вы сможете подписаться или отписаться.\n\nНе забывайте, что меню с инструкцией по всем кнопкам всегда можно вызвать в любой момент нажав на кнопку "help" на клавиатуре!')
                    await call.answer('Отослал инструкцию по кнопке "Выбор источников"')
                elif call.data == 'button_search_by_word':
                    await call.message.answer('ИНСТРУКЦИЯ ПО КНОПКЕ "Поиск Анека по слову: инструкция"\n(кнопка на 4ом ряду клавиатуры)\n\nНажав на эту кнопку Вы получите мини-инструкцию, как искать анекдот с конкретным словом или фразой и целой базы с анекдотами. Эту мини-инструкцию я также продублирую в этом сообщении ниже\n\nМини-инструкция:\nЧтобы найти анекдот по выбранному Вами слову, напишите мне слово "Найти" (без кавычек!) и затем через пробел слово или несколько слов, по которым Вы хотите найти анекдоты. Функции остальных кнопок, во время поиска анекдотов по слову, остаются теми же.\n\nВНИМАНИЕ!!! через команду "Найти" могут попасться анекдоты из любых источников. Чтобы находить анекдот по слову СТРОГО из источников, на которые Вы подписаны, вместо команды "Найти" напишите фразу "Найти мои источники" (опять же без кавычек!) и потом, опять же через пробел, введите слово, по которому нужно найти анекдот!\n\nНе забывайте, что меню с инструкцией по всем кнопкам всегда можно вызвать в любой момент нажав на кнопку "help" на клавиатуре!')
                    await call.answer('Отослал инструкцию по кнопке "Поиск Анека по слову: инструкция"')
                elif call.data == 'button_list_sources':
                    await call.message.answer('ИНСТРУКЦИЯ ПО КНОПКЕ "Список источников"\n(левая кнопка на 5ом ряду клавиатуры)\n\nС помощью этой кнопки Вы всегда можете получить ссылки на все источники, из которых брались анекдоты. Продублирую этот список здесь:\n1. ВК паблик "Анекдоты (megaotriv)"\n(vk.com/megaotriv)\n2. ВК паблик "анекдотов.net"\n(vk.com/anekdot)\n3. ВК паблик "Смешные анедкоты"\n(vk.com/smeshnye__anekdoty)\n4. Телеграмм канал "Анекдоты (AnekdotiRu)"\n(t.me/AnekdotiRu)\n5. ВК паблик "Анекдоты категории Б"\n(vk.com/baneks)\n6. ВК паблик "Анекдоты категории Б+"\n(vk.com/anekdotikategoriib)\n7. ВК паблик "Мои любимые юморески"\n(vk.com/jumoreski)\n8. Телеграм канал "Мои любимые юморески"\n(t.me/myfavoritejumoreski)\n9. Телеграмм канал "Лига Плохих Шуток"\n(t.me/ligapsh)\n10. ВК паблик "Лига плохих шуток"\n(vk.com/badjokesleague)\n\nНе забывайте, что меню с инструкцией по всем кнопкам всегда можно вызвать в любой момент нажав на кнопку "help" на клавиатуре!', disable_web_page_preview = True)
                    await call.answer('Отослал инструкцию по кнопке "Список источников"')
                elif call.data == 'button_sub_or_unsub_anec_day':
                    await call.message.answer('ИНСТРУКЦИЯ ПО КНОПКЕ "Анек дня: отписаться/подписаться"\n(кнопка на 6ом ряду клавиатуры)\n\nПри нажатии на кнопку "Анек дня: отписаться", текст на кнопке станет "Анек дня: подписаться" и наоборот.\nЧто такое "Анек дня"? Каждый день я буду выбирать ТОП 5 анекдотов, исходя из оценок всех пользователей. Затем в телеграмм-канале AnecBot channel (t.me/anecbot_channel), все пользователи могут выбрать лучший из этих пяти анекдотов, и именно этот анекдот будет автоматически присылаться тем, кто подписан на "Анек дня". Так что подписывайтесь на канал!\n\nИзначально, каждый подписан на "Анек дня". Чтобы отписаться или обратно подписаться на "Анек дня", Вы можете нажать на кнопку "Анек дня: отписаться/подписаться" и затем я пришлю Вам сообщение, где Вы должны подтвердить отписку/подписку, нажав на кнопку "Да" под сообщением.\n\nНе забывайте, что меню с инструкцией по всем кнопкам всегда можно вызвать в любой момент нажав на кнопку "help" на клавиатуре!')
                    await call.answer('Отослал инструкцию по кнопке "Анек дня: отписаться/подписаться"')
                elif call.data == 'button_sub_or_unsub_random_anec':
                    await call.message.answer('ИНСТРУКЦИЯ ПО КНОПКЕ "Рандомный Анек: отписаться/подписаться"\n(кнопка на 7ом ряду клавиатуры)\n\nПри нажатии на кнопку "Рандомный Анек: отписаться", текст на кнопке станет "Рандомный Анек: подписаться" и наоборот.\nЕсли Вы подписаны на "Рандомный Анек", то каждый день в 13:00 и в 18:00 по московскому времени я буду высылать Вам случайный анекдот из моей базы.\n\nИзначально, каждый подписан на "Рандомный Анек". Чтобы отписаться или обратно подписаться на "Рандомный Анек", Вы можете нажать на кнопку "Рандомный Анек: отписаться/подписаться" и затем я пришлю Вам сообщение, где Вы должны подтвердить отписку/подписку, нажав на кнопку "Да" под сообщением.\n\nНе забывайте, что меню с инструкцией по всем кнопкам всегда можно вызвать в любой момент нажав на кнопку "help" на клавиатуре!')
                    await call.answer('Отослал инструкцию по кнопке "Рандомный Анек: отписаться/подписаться"')
                elif call.data == 'button_last_five_saved': 
                    await call.message.answer('ИНСТРУКЦИЯ ПО КНОПКЕ "Последние 5 удалённых сохранёнок"\n(кнопка на 8ом ряду клавиатуры)\n\nЭта кнопка предназначена для того, чтобы возвращать обратно в сохранённые случайно удалённые оттуда анекдоты.\n\nНажав на эту кнопку Вы получите 5 последних удалённых Вами сохранённых анекдотов. Чтобы добавить анекдот обратно в сохранённые, нажмите на соответствующую кнопку под сообщением и подтвердите выбор, нажав на кнопку "Да".\n\nНе забывайте, что меню с инструкцией по всем кнопкам всегда можно вызвать в любой момент нажав на кнопку "help" на клавиатуре!')
                    await call.answer('Отослал инструкцию по кнопке "Последние 5 удалённых сохранёнок"')
                elif call.data == 'button_potential_problems':
                    await call.message.answer('Раздел "Возможные проблемы"\n\nЭтот раздел будет пополняться по мере обнаружения возможных неточностей в моей работе. Если у Вас возникла проблема, которая не описана здесь, опишите её в чате Anecbot chat (t.me/anecbot_chat), где админ или другие пользователи бота помогут Вам решить эту проблему!\n\nВозможные проблемы:\n1. Если вдруг в какой-то момент Вы обнаружили, что нет кнопок на клавиатуре, напишите мне "/start" или "Выйти" без кавычек!\n\nНе забывайте, что меню с инструкцией по всем кнопкам всегда можно вызвать в любой момент нажав на кнопку "help" на клавиатуре!')
                    await call.answer('Отослал раздел "Возможные проблемы"')
                elif call.data == 'button_full_instr':
                    final = 'ПОЛНАЯ ИНСТРУКЦИЯ\n\nЗдесь Вы найдете все предыдущие разделы инструкции и инструкции по каждой кнопке.\n\n\n1. РАЗДЕЛ "Начальная инструкция" (текст)\n\nДля начала, я на всякий случай хочу заметить, что я часто использую слово "Анек". Если это слово вводит Вас в ступор, то не волнуйтесь: "Анек" это сокращение слова "Анекдот". Поэтому, чтобы получить анекдот, нажмите на кнопку "Анек" на клавиатуре (самая верхняя кнопка слева). После нажатия Вам придёт сообщение, в котором Вы увидите анекдот, его источник и дату опубликования.\n\nЗатем Вам будет предложено оценить анекдот оценкой от 1 до 10. Оценивать анекдоты очень важно, так как, именно исходя из Ваших оценок, я буду стараться подбирать Вам следующие анекдоты, чтобы они Вам точно понравились.\n\nТакже очень важно понимать, что разные источники содержат разные анекдоты. Поэтому я советую Вам на начальном этапе понять, какие источники Вам нравятся, а какие нет, переходя по ссылкам на источники (для этого нажмите на кнопку "Список источников" на 5ом ряду клавиатуры слева) или постепенно читая анекдоты здесь с помощью кнопки "Анек"\n\nИзначально Вы получаете анекдоты изо всех источников. Однако, вы можете отписаться от некоторых источников, то есть не получать анекдоты оттуда, с помощью кнопки "Выбор источников". Нажав на эту кнопку, Вам откроется клавиатура с новыми кнопками, с помощью которых Вы легко сможете отписаться или подписаться на те или иные источники. Нажмите на кнопку "Выбор источников" для более подробной информации о процедуре подписки и отписки от источников.\n\nЕсли Вы прошли все эти шаги, то Вы уже можете считаться профессиональным пользователем. С большой вероятностью Вам уже будут попадаться анекдоты, которые Вам понравятся! После этих шагов Вы можете постепенно изучать функционал других кнопок, чтобы получить ещё более качественный сервис от меня!\n\nНе забывайте, что меню с инструкцией по всем кнопкам всегда можно вызвать в любой момент нажав на кнопку "help" на клавиатуре!\n\n\n2. ИНСТРУКЦИЯ ПО КНОПКЕ "Анек"\n(верхняя кнопка слева на клавиатуре)\n\nНажав на эту кнопку, я пришлю Вам сообщение с анекдотом, источником и датой опубликования. под сообщением Вы увидите кнопки с числами от 1 до 10, а также кнопку с надписью "Добавить в "Сохранённые"".\n\nЧисла означают оценки за анекдот по шкале от 1 до 10. Оценивать анекдоты очень важно, так как, именно исходя из Ваших оценок, я буду стараться подбирать Вам следующие анекдоты, чтобы они Вам точно понравились. После нажатия на одну из цифр, Вы получите уведомление, что ваша оценка сохранена и в конце сообщения Вы увидите Вашу оценку. Также после нажатия на одну из цифр, все кнопки с цифрами под сообщением исчезнут.\n\nПосле нажатия на кнопку "Добавить в "Сохранённые"", эта кнопка исчезнет, и Вы получите уведомление, что анекдот добавлен в сохранённые. Вы сможете найти сохранённый анекдот, нажав на кнопку "Сохранённые Анеки" (3ий ряд клавиатуры слева).\n\nЭта кнопка лишь один из способов получения анекдотов. Советую прочитать отличия кнопок "10 Анеков", "Много Анеков", "СТАРТ/СТОП Анеки подряд" (1ый и 2ой ряд клавиатуры) от кнопки "Анек". Эти кнопки могут сделать для Вас процесс получения анекдотов более удобным!\n\nНе забывайте, что меню с инструкцией по всем кнопкам всегда можно вызвать в любой момент нажав на кнопку "help" на клавиатуре!\n\n\n3. ИНСТРУКЦИЯ ПО КНОПКЕ "10 Анеков"\n(верхняя кнопка справа на клавиатуре)\nЭта кнопка выполняет практитечки ту же функцию, что и кнопка "Анек". Единственное отличие заключается в том, что я пришлю Вам сразу 10 анекдотов.\n\nНе забывайте, что меню с инструкцией по всем кнопкам всегда можно вызвать в любой момент нажав на кнопку "help" на клавиатуре!\n\n\n4. ИНСТРУКЦИЯ ПО КНОПКЕ "Много Анеков"\n(левая кнопка на 2ом ряду клавиатуры)\n\nЭта кнопка выполняет схожую функцию, что и кнопка "Анек". Отличие заключается в том, что перед получением анекдотов Вы должны выбрать количество анекдотов от 1 до 25. Нажав на число, я пришлю Вам соответственное количество анекдотов.\n\nНе забывайте, что меню с инструкцией по всем кнопкам всегда можно вызвать в любой момент нажав на кнопку "help" на клавиатуре!\n\n\n5. ИНСТРУКЦИЯ ПО КНОПКЕ "СТАРТ/СТОП Анеки подряд"\n(правая кнопка на 2ом ряду клавиатуры)\n\nЕсли на этой кнопке написано "СТАРТ Анеки подряд", то после нажатия на неё текст на кнопке станет "СТОП Анеки подряд" и наоборот!\n\nЭта кнопка выполняет схожую функцию, что и кнопка "Анек". Отличие заключается в том, что как только Вы нажали на "СТАРТ Анеки подряд" и не нажали на "СТОП Анеки подряд", после оценки каждого анекдота (нажатие числа от 1 до 10), Вам автоматически будет присылаться следующий анекдот.\n\nТакже стоит отметить, что если Вы нажали на "СТАРТ Анеки подряд", но не нажали на "СТОП Анеки подряд", кнопки "Анек", "10 Анеков" и "Много Анеков" не будут работать должным образом!\n\nНе забывайте, что меню с инструкцией по всем кнопкам всегда можно вызвать в любой момент нажав на кнопку "help" на клавиатуре!\n\n\n6. ИНСТРУКЦИЯ ПО КНОПКЕ "Сохранённые Анеки"\n(левая кнопка на 3ем ряду клавиатуры)\n\nЗдесь находятся все анекдоты, которые Вы до это добавили в сохранённые. Если Вы сохранили меньше 20 анекдотов, то при нажатии на кнопку "Сохранённые Анеки" я пришлю Вам все Ваши сохранённые анекдоты. Если Вы сохранили 20 анекдотов и больше, то при нажатии на эту кнопку, Вам откроется клавиатура с новыми кнопки, где с помощью встроенной мини-инструкции, Вы с лёгкостью сможете найти и получить те или иные анекдоты. Не парьтесь по поводу этого, если у Вы сохранили меньше 20 анекдотов.\n\nБолее того, каждый раз, когда я буду присылать Вам сохранённый анекдот, у Вас будет возможность удалить этот анекдот, нажав на кнопку "Удалить Анек из "Сохранённых"", и затем подтвердив удаление, нажав на кнопку "Да", котороая должна появиться после нажатия на "Удалить Анек из "Сохранённых"". Если Вы случайно удалили какой-то из сохранённых анекдотов, его можно будет восстановить (добавить в сохранённые обратно), нажав на кнопку "Последние 5 удалённых сохранёнок".\n\nНе забывайте, что меню с инструкцией по всем кнопкам всегда можно вызвать в любой момент нажав на кнопку "help" на клавиатуре!\n\n\n7. ИНСТРУКЦИЯ ПО КНОПКЕ "Выбор источников"\n(правая кнопка на 3ем ряду клавиатуры)\n\nС помощью этой кнопки Вы сможете отписаться или подписаться на те или иные источники. После нажатия на эту кнопку, Вам откроется клавиатура с новыми кнопками, с помощью которых Вы сможете узнать, как отписаться или подписаться на источник, на какие источники Вы подписаны или не подписаны в данный момент и, конечно же, вы сможете подписаться или отписаться.\n\nНе забывайте, что меню с инструкцией по всем кнопкам всегда можно вызвать в любой момент нажав на кнопку "help" на клавиатуре!\n\n\n8. ИНСТРУКЦИЯ ПО КНОПКЕ "Поиск Анека по слову: инструкция"\n(кнопка на 4ом ряду клавиатуры)\n\nНажав на эту кнопку Вы получите мини-инструкцию, как искать анекдот с конкретным словом или фразой и целой базы с анекдотами. Эту мини-инструкцию я также продублирую в этом сообщении ниже\n\nМини-инструкция:\nЧтобы найти анекдот по выбранному Вами слову, напишите мне слово "Найти" (без кавычек!) и затем через пробел слово или несколько слов, по которым Вы хотите найти анекдоты. Функции остальных кнопок, во время поиска анекдотов по слову, остаются теми же.\n\nВНИМАНИЕ!!! через команду "Найти" могут попасться анекдоты из любых источников. Чтобы находить анекдот по слову СТРОГО из источников, на которые Вы подписаны, вместо команды "Найти" напишите фразу "Найти мои источники" (опять же без кавычек!) и потом, опять же через пробел, введите слово, по которому нужно найти анекдот!\n\nНе забывайте, что меню с инструкцией по всем кнопкам всегда можно вызвать в любой момент нажав на кнопку "help" на клавиатуре!\n\n\n9. ИНСТРУКЦИЯ ПО КНОПКЕ "Список источников"\n(левая кнопка на 5ом ряду клавиатуры)\n\nС помощью этой кнопки Вы всегда можете получить ссылки на все источники, из которых брались анекдоты. Продублирую этот список здесь:\n1) ВК паблик "Анекдоты (megaotriv)"\n(vk.com/megaotriv)\n2) ВК паблик "анекдотов.net"\n(vk.com/anekdot)\n3) ВК паблик "Смешные анедкоты"\n(vk.com/smeshnye__anekdoty)\n4) Телеграмм канал "Анекдоты (AnekdotiRu)"\n(t.me/AnekdotiRu)\n5) ВК паблик "Анекдоты категории Б"\n(vk.com/baneks)\n6) ВК паблик "Анекдоты категории Б+"\n(vk.com/anekdotikategoriib)\n7) ВК паблик "Мои любимые юморески"\n(vk.com/jumoreski)\n8) Телеграм канал "Мои любимые юморески"\n(t.me/myfavoritejumoreski)\n9) Телеграмм канал "Лига Плохих Шуток"\n(t.me/ligapsh)\n10) ВК паблик "Лига плохих шуток"\n(vk.com/badjokesleague)\n\nНе забывайте, что меню с инструкцией по всем кнопкам всегда можно вызвать в любой момент нажав на кнопку "help" на клавиатуре!\n\n\n10. ИНСТРУКЦИЯ ПО КНОПКЕ "Анек дня: отписаться/подписаться"\n(кнопка на 6ом ряду клавиатуры)\n\nПри нажатии на кнопку "Анек дня: отписаться", текст на кнопке станет "Анек дня: подписаться" и наоборот.\nЧто такое "Анек дня"? Каждый день я буду выбирать ТОП 5 анекдотов, исходя из оценок всех пользователей. Затем в телеграмм-канале AnecBot channel (t.me/anecbot_channel), все пользователи могут выбрать лучший из этих пяти анекдотов, и именно этот анекдот будет автоматически присылаться тем, кто подписан на "Анек дня". Так что подписывайтесь на канал!\n\nИзначально, каждый подписан на "Анек дня". Чтобы отписаться или обратно подписаться на "Анек дня", Вы можете нажать на кнопку "Анек дня: отписаться/подписаться" и затем я пришлю Вам сообщение, где Вы должны подтвердить отписку/подписку, нажав на кнопку "Да" под сообщением.\n\nНе забывайте, что меню с инструкцией по всем кнопкам всегда можно вызвать в любой момент нажав на кнопку "help" на клавиатуре!\n\n\n11. ИНСТРУКЦИЯ ПО КНОПКЕ "Рандомный Анек: отписаться/подписаться"\n(кнопка на 7ом ряду клавиатуры)\n\nПри нажатии на кнопку "Рандомный Анек: отписаться", текст на кнопке станет "Рандомный Анек: подписаться" и наоборот.\nЕсли Вы подписаны на "Рандомный Анек", то каждый день в 13:00 и в 18:00 по московскому времени я буду высылать Вам случайный анекдот из моей базы.\n\nИзначально, каждый подписан на "Рандомный Анек". Чтобы отписаться или обратно подписаться на "Рандомный Анек", Вы можете нажать на кнопку "Рандомный Анек: отписаться/подписаться" и затем я пришлю Вам сообщение, где Вы должны подтвердить отписку/подписку, нажав на кнопку "Да" под сообщением.\n\nНе забывайте, что меню с инструкцией по всем кнопкам всегда можно вызвать в любой момент нажав на кнопку "help" на клавиатуре!\n\n\n12. ИНСТРУКЦИЯ ПО КНОПКЕ "Последние 5 удалённых сохранёнок"\n(кнопка на 8ом ряду клавиатуры)\n\nЭта кнопка предназначена для того, чтобы возвращать обратно в сохранённые случайно удалённые оттуда анекдоты.\n\nНажав на эту кнопку Вы получите 5 последних удалённых Вами сохранённых анекдотов. Чтобы добавить анекдот обратно в сохранённые, нажмите на соответствующую кнопку под сообщением и подтвердите выбор, нажав на кнопку "Да".\n\nНе забывайте, что меню с инструкцией по всем кнопкам всегда можно вызвать в любой момент нажав на кнопку "help" на клавиатуре!\n\n\n13. Раздел "Возможные проблемы"\n\nЭтот раздел будет пополняться по мере обнаружения возможных неточностей в моей работе. Если у Вас возникла проблема, которая не описана здесь, опишите её в чате Anecbot chat (t.me/anecbot_chat), где админ или другие пользователи бота помогут Вам решить эту проблему!\n\nВозможные проблемы:\n1) Если вдруг в какой-то момент Вы обнаружили, что нет кнопок на клавиатуре, напишите мне "/start" или "Выйти" без кавычек!\n\nНе забывайте, что меню с инструкцией по всем кнопкам всегда можно вызвать в любой момент нажав на кнопку "help" на клавиатуре!'
                    await call.message.answer(final[: 4067], disable_web_page_preview = True)
                    await call.message.answer(final[4067: 7632], disable_web_page_preview = True)
                    await call.message.answer(final[7632: ], disable_web_page_preview = True)
                    await call.answer('Отослал полную инструкцию')
                else:
                    await call.message.answer('error in instruction button call data')
            
            
            elif call.data == 'finish_start_instruction':
                await call.message.edit_text('Вы закончили начальную инструкцию!')
                general_base1.update_is_novice(call.message.chat.id, 0)
                general_base1.add_user_to_users_sub_best_anec_day(call.message.chat.id)
                general_base1.add_user_to_users_sub_random_anec(call.message.chat.id)
                #keyboard data prep
                with general_base1.connection:
                    general_base1.cursor.execute("SELECT subscribed FROM users_sub_best_anec_day WHERE user_id = %s LIMIT 1", (call.message.chat.id,))
                    ku = general_base1.cursor.fetchall()[0][0]
                    general_base1.cursor.execute("SELECT in_a_row_started FROM anecs_in_a_row WHERE user_id = %s LIMIT 1", (call.message.chat.id,))
                    status = general_base1.cursor.fetchall()[0][0]
                    general_base1.cursor.execute("SELECT subscribed FROM users_sub_random_anec WHERE user_id = %s LIMIT 1", (call.message.chat.id,))
                    kz = general_base1.cursor.fetchall()[0][0]
                #keyboard
                markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
                await main_markup(markup, ku, status, kz)
                await call.message.answer('Теперь, Вы уже можете считаться профессиональным пользователем. С большой вероятностью Вам уже будут попадаться анекдоты, которые Вам понравятся! После этих шагов Вы можете постепенно изучать функционал других кнопок, чтобы получить ещё более качественный сервис от меня!\n\nЧтобы узнать, как работает та или иная кнопка, нажмите на кнопку "help" (это кнопка на пятом ряду клавиатуры справа) и я скажу Вам, как узнать функционал определённой кнопки!\n\nТакже подписывайтесь на канал AnecBot channel\n(t.me/anecbot_channel), чтобы голосовать за лучший анекдот дня и узнавать релевантную информацию о боте!\n\nПомимо этого, Вы всегда можете добавить бота в свои чаты и получать анекдоты там (если после добавления бота в чат у Вас не появится клавиатуры с кнопками бота, то просто напишите в чат "/start" (без кавычек)).\n\nПРЕДУПРЕЖДЕНИЕ: некоторые анекдоты могут содержать мат и прочую нецензурную лексику!\n\nЖелаю Вам смешных анекдотов!', reply_markup = markup)
                await call.message.answer('Чтобы пройти начальную инструкцию ещё раз, нажмите на "help" на клавиатуре. После этого я пришлю Вам сообщение и под ним Вам нужно будет нажать кнопку "начальная инструкция", чтобы открыть её')
                
                
            elif call.data == 'repeat_start_instruction':
                with general_base1.connection:
                    general_base1.cursor.execute("SELECT in_a_row_started FROM anecs_in_a_row WHERE user_id = %s LIMIT 1", (call.message.chat.id,))
                    status = general_base1.cursor.fetchall()[0][0]
                if status == 1:
                    await call.message.answer('Чтобы Вы смогли пройти начальную инструкцию заново, сначала нажмите на кнопку "СТОП анеки подряд" на клавиатуре и затем нажмите на "Пройти начальную инструкцию заново" под сообщением заново!')
                elif status == 0:
                    general_base1.update_is_novice(call.message.chat.id, 1)
                    await call.message.edit_text('Вы решили пройти начальную инструкцию заново\n\nЕсли Вы не хотите проходить её полностью, то Вы в любой момент можете её пропустить и выйти в основное главное меню, нажав на кнопку "Пропустить начальную инструкцию"!')
                    #keyboard
                    markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
                    item1 = types.KeyboardButton("Анек")
                    item2 = types.KeyboardButton("Пропустить начальную инструкцию")
                    markup.add(item1)
                    markup.add(item2)
                    await call.message.answer('Привет, это AnecBot!\nЯ подбираю анекдоты специально для Вас из базы, содержащей более чем 170000 анекдотов!\n\nДля начала найдите две кнопки на Вашей клавиатуре: "Анек" и "Пропустить начальную инструкцию". Если Вы не видите этих кнопок, то накжмите на квадратик с 4-мя кружочками внутри рядом в верхнем углу клавиатуры справа рядом со значком микрофона.\n\nТеперь нажмите на кнопку "Анек", чтобы получить анекдот!\n\n(Вы можете выйти в главное меню, нажав на кнопку "Пропустить начальную инструкцию", НО я не рекомендую Вам этого делать, если Вы до этого не проходили до конца эту инструкцию)', reply_markup = markup)
                else:
                    await call.message.answer('error in status')
            
            
            
            elif call.data == 'skip_intro':
                with general_base1.connection:
                    general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (call.message.chat.id,))
                    isn = general_base1.cursor.fetchall()[0][0]
                if isn == 1:
                    await call.message.edit_text('Вы пропустили начальную инструкцию!\n\nЧтобы пройти начальную инструкцию ещё раз, нажмите на "help" (это кнопка на пятом ряду клавиатуры справа). После этого я пришлю Вам сообщение и под ним Вам нужно будет нажать кнопку "начальная инструкция", чтобы открыть её')
                    general_base1.update_is_novice(call.message.chat.id, 0)
                    general_base1.add_user_to_users_sub_best_anec_day(call.message.chat.id)
                    general_base1.add_user_to_users_sub_random_anec(call.message.chat.id)
                    #keyboard data prep
                    with general_base1.connection:
                        general_base1.cursor.execute("SELECT subscribed FROM users_sub_best_anec_day WHERE user_id = %s LIMIT 1", (call.message.chat.id,))
                        ku = general_base1.cursor.fetchall()[0][0]
                        general_base1.cursor.execute("SELECT in_a_row_started FROM anecs_in_a_row WHERE user_id = %s LIMIT 1", (call.message.chat.id,))
                        status = general_base1.cursor.fetchall()[0][0]
                        general_base1.cursor.execute("SELECT subscribed FROM users_sub_random_anec WHERE user_id = %s LIMIT 1", (call.message.chat.id,))
                        kz = general_base1.cursor.fetchall()[0][0]
                    #keyboard
                    markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
                    await main_markup(markup, ku, status, kz)
                    await call.message.answer('Теперь, Вы находитесь в основном главном меню, где Вы можете увидеть намного больше кнопок: с некоторыми Вы уже знакомы, а некоторые Вы можете видеть впервые. Вы вполне можете пользоваться только теми кнопками, о которых Вы узнали в начальной инструкции, но пользуясь другими кнопками Вы сможете получить от меня намного больше!\n\nЧтобы узнать, как работает та или иная кнопка, нажмите на кнопку "help" (это кнопка на пятом ряду клавиатуры справа) и я скажу Вам, как узнать функционал определённой кнопки!\n\nТакже подписывайтесь на канал AnecBot channel\n(t.me/anecbot_channel), чтобы голосовать за лучший анекдот дня и узнавать релевантную информацию о боте!\n\nПомимо этого, Вы всегда можете добавить бота в свои чаты и получать анекдоты там (если после добавления бота в чат у Вас не появится клавиатуры с кнопками бота, то просто напишите в чат "/start" (без кавычек)).\n\nПРЕДУПРЕЖДЕНИЕ: некоторые анекдоты могут содержать мат и прочую нецензурную лексику!\n\nЖелаю Вам смешных анекдотов!', reply_markup = markup)
                elif isn == 0:
                    await call.message.answer('Вы и так уже не в начальной инструкции!\nВы завершили прохождение начальной инструкции до этого') 
                else:
                    await call.message.answer('error in isn')
                
 
            elif call.data == 'not_skip_intro':
                with general_base1.connection:
                    general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (call.message.chat.id,))
                    isn = general_base1.cursor.fetchall()[0][0]
                if isn == 1:
                    await call.message.edit_text('Вы нажали кнопку "отмена" и остались в начальной инструкции')
                elif isn == 0:
                    await call.message.answer('Вы уже не в начальной инструкции!\nВы завершили прохождение начальной инструкции до этого')
                else:
                    await call.message.answer('error in isn')

                
            elif call.data == 'test':
                await call.message.answer(call.message.reply_markup)
                await call.message.edit_reply_markup(reply_markup = {"inline_keyboard": call.message.reply_markup.inline_keyboard[:-1]})
                
            else:
                await call.message.answer(call.data)
                await call.message.answer('error in call_data, call_data is not found')
                                           
    except Exception as e:
        print(repr(e))
        

        
#Initializing bot when /start is pressed:
@dp.message_handler(commands = ['start'])
async def welcome(message: types.message):
    if message.chat.id < 0:
        general_base1.add_user_to_user_novice_or_not(message.chat.id)
        general_base1.add_user_to_anecs_in_a_row_table(message.chat.id)
        general_base1.add_user_to_users_sources(message.chat.id)
        general_base1.add_user_to_users_sub_best_anec_day(message.chat.id)
        general_base1.add_user_to_users_sub_random_anec(message.chat.id)
        general_base1.update_is_novice(message.chat.id, 0)
        with general_base1.connection:
            general_base1.cursor.execute("SELECT subscribed FROM users_sub_best_anec_day WHERE user_id = %s LIMIT 1", (message.chat.id,))
            ku = general_base1.cursor.fetchall()[0][0]
            general_base1.cursor.execute("SELECT in_a_row_started FROM anecs_in_a_row WHERE user_id = %s LIMIT 1", (message.chat.id,))
            status = general_base1.cursor.fetchall()[0][0]
            general_base1.cursor.execute("SELECT subscribed FROM users_sub_random_anec WHERE user_id = %s LIMIT 1", (message.chat.id,))
            kz = general_base1.cursor.fetchall()[0][0]

        #keyboard
        markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
        await main_markup(markup, ku, status, kz)
        await message.answer('Привет, это AnecBot!\nЯ подбираю анекдоты специально для Вас из базы, содержащей более чем 170000 анекдотов!\n\nЕсли Вы опытный пользователь, то Вам не составит труда пользоваться моими командами в групповых чатах, так как мой функционал такой же, как если бы Вы пользовались моими командами здесь: @bot_anecbot\n\nЕсли Вы новый пользователь, то я рекомендую Вам пройти начальную инструкцию, чтобы узнать мой базовый функционал. Чтобы получить начальную инструкцию в текстовом виде, нажмите на кнопку "help" (5ый ряд клавиатуры справа) и затем Вы получите от меня сообщение, под которым Вам нужно будет нажать на кнопку "Начальная инструкция". Если Вы не видите кнопку "help", то нажмите на квадратик с 4-мя кружочками внутри рядом в верхнем углу клавиатуры справа рядом со значком микрофона.\n\nБолее того, вместо прочтения текстовой инструкции Вы можете пройти начальную инструкцию в интерактивном режиме. Если Вы новый пользователь, то переходите по этой ссылке\n-> @bot_anecbot и нажимайте на "ЗАПУСТИТЬ" ("START"), чтобы начать проходить интерактивную начальную инструкцию.\n\nЖелаю Вам смешных анекдотов!', reply_markup = markup) 
        
    else:    
        general_base1.add_user_to_user_novice_or_not(message.chat.id)
        with general_base1.connection:
            general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (message.chat.id,))
            isn = general_base1.cursor.fetchall()[0][0]

        if isn == 1:
            general_base1.add_user_to_anecs_in_a_row_table(message.chat.id)
            general_base1.add_user_to_users_sources(message.chat.id)

            sti = open('robot_saying_hi.webp', 'rb')
            await bot.send_sticker(message.chat.id, sti)

            #keyboard
            markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
            item1 = types.KeyboardButton("Анек")
            item2 = types.KeyboardButton("Пропустить начальную инструкцию")
            markup.add(item1)
            markup.add(item2)
            await message.answer('Привет, это AnecBot!\nЯ подбираю анекдоты специально для Вас из базы, содержащей более чем 170000 анекдотов!\n\nДля начала найдите две кнопки на Вашей клавиатуре: "Анек" и "Пропустить начальную инструкцию". Если Вы не видите этих кнопок, то накжмите на квадратик с 4-мя кружочками внутри рядом в верхнем углу клавиатуры справа рядом со значком микрофона.\n\nТеперь нажмите на кнопку "Анек", чтобы получить анекдот!(я на всякий случай хочу заметить, что я часто буду использовать слово "Анек". Если это слово вводит Вас в ступор, то не волнуйтесь: "Анек" это сокращение от слова "Анекдот")\n\n(Вы можете выйти в главное меню, нажав на кнопку "Пропустить начальную инструкцию", НО я не рекомендую Вам этого делать, если Вы до этого не проходили до конца эту инструкцию)', reply_markup = markup)

        elif isn == 0:    
            general_base1.add_user_to_users_sub_best_anec_day(message.chat.id)
            general_base1.add_user_to_users_sub_random_anec(message.chat.id)

            with general_base1.connection:
                general_base1.cursor.execute("SELECT subscribed FROM users_sub_best_anec_day WHERE user_id = %s LIMIT 1", (message.chat.id,))
                ku = general_base1.cursor.fetchall()[0][0]
                general_base1.cursor.execute("SELECT in_a_row_started FROM anecs_in_a_row WHERE user_id = %s LIMIT 1", (message.chat.id,))
                status = general_base1.cursor.fetchall()[0][0]
                general_base1.cursor.execute("SELECT subscribed FROM users_sub_random_anec WHERE user_id = %s LIMIT 1", (message.chat.id,))
                kz = general_base1.cursor.fetchall()[0][0]
                
            #keyboard
            markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
            await main_markup(markup, ku, status, kz)

            await message.answer('Вы находитесь в главном меню!', reply_markup = markup, disable_notification = True)
            await message.answer('Нажмите на кнопку "help" на клавиатуре, чтобы узнать функционал той или иной кнопки', disable_web_page_preview = True, disable_notification = True)

        else:
            await message.answer('error in isn')
    
 

 # Button to choose sources:
@dp.message_handler(lambda message: message.text.lower() == 'выбор источников')
async def choose_sources(message: types.Message):
    #checking that person is not novice
    with general_base1.connection:
        general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (message.chat.id,))
        isn = general_base1.cursor.fetchall()[0][0]
    if isn == 1:
        markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
        item1 = types.KeyboardButton('Подписки и отписки')
        item2 = types.KeyboardButton('Пропустить начальную инструкцию')
        markup.add(item1)
        markup.add(item2)
        await message.answer('Вы находитесь в разделе "Выбор источников"!\n\nВ моей базе находятся анекдоты из 10 источников. Чтобы посмотреть на источники и на то, подписаны Вы на этот источник или нет, нажмите на кнопку "Подписки и отписки"', reply_markup = markup)
    elif isn == 0:
        #keyboard
        markup = types.ReplyKeyboardMarkup(row_width = 10)
        item1 = types.KeyboardButton("Выйти")
        item2 = types.KeyboardButton('Подписки и отписки')
        item3 = types.KeyboardButton('help источники')
        item4 = types.KeyboardButton(1)
        item5 = types.KeyboardButton(2)
        item6 = types.KeyboardButton(3)
        item7 = types.KeyboardButton(4)
        item8 = types.KeyboardButton(5)
        item9 = types.KeyboardButton(6)
        item10 = types.KeyboardButton(7)
        item11 = types.KeyboardButton(8)
        item12 = types.KeyboardButton(9)
        item13 = types.KeyboardButton(10)

        markup.add(item1)
        markup.add(item2, item3)
        markup.add(item4, item5, item6, item7, item8)
        markup.add(item9, item10, item11, item12, item13)
        await message.answer('Вы находитесь в разделе "Выбор источников"!\n\nВ первую очередь хочу сказать, что Вы всегда можете получить эту мини-инструкцию, нажав на кнопку "help источники"\n\nЗдесь Вы можете выбрать источник чтобы подписаться или отписаться от него. Чтобы отписаться или подписаться на определённый источник, нажми на кнопку с определённым числом на клавиатуре (и затем подтвердите Ваше решение, нажав на кнопку "Да" под сообщением). Соответствие чисел и источников Вы можете увидеть в списке внизу.\n\nСписок:\n1. ВК паблик "Анекдоты (megaotriv)"\n2. ВК паблик "анекдотов.net"\n3. ВК паблик "Смешные анекдоты"\n4. Телеграмм канал "Анекдоты (AnekdotiRu)"\n5. ВК паблик "Анекдоты категории Б"\n6. ВК паблик "Анекдоты категории Б+"\n7. ВК паблик "Мои любимые юморески"\n8. Телеграм канал "Мои любимые юморески"\n9. Телеграмм канал "Лига Плохих Шуток"\n10. ВК паблик "Лига плохих шуток"\n\nБолее того, номер также соответсвует первой цифре в ID любого анекдота (или первым двум цифрам, если число в ID перед тире - четырёхзначное), который присылается Вам ботом, так что Вы можете, глядя на ID и источник, просто написать в чат эту цифру и отписаться от этого источника!\n\nТакже Вы можете увидеть, на какие источники Вы подписаны, а на какие не подписаны, нажав на кнопку "Подписки и отписки"!\n\nЧтобы выйти в главное меню с клавиатурой с изначальными кнопками, нажмите кнопку "Выйти"', reply_markup = markup)
    else:
        await message.answer('error in isn')


# activation of /help_источник button or command in choose_source area:
@dp.message_handler(lambda message: message.text.lower() == 'help источники')
async def help_sources(message: types.Message):
    await message.answer('В этом разделе Вы можете выбрать источник чтобы подписаться или отписаться от него. Чтобы отписаться или подписаться на определённый источник, нажми на кнопку с определённым числом на клавиатуре (и затем подтвердите Ваше решение, нажав на кнопку "Да" под сообщением). Соответствие чисел и источников Вы можете увидеть в списке внизу.\n\nСписок:\n1. ВК паблик "Анекдоты (megaotriv)"\n2. ВК паблик "анекдотов.net"\n3. ВК паблик "Смешные анекдоты"\n4. Телеграмм канал "Анекдоты (AnekdotiRu)"\n5. ВК паблик "Анекдоты категории Б"\n6. ВК паблик "Анекдоты категории Б+"\n7. ВК паблик "Мои любимые юморески"\n8. Телеграм канал "Мои любимые юморески"\n9. Телеграмм канал "Лига Плохих Шуток"\n10. ВК паблик "Лига плохих шуток"\n\nБолее того, номер также соответсвует первой цифре в ID любого анекдота (или первым двум цифрам, если число в ID перед тире - четырёхзначное), который присылается Вам ботом, так что Вы можете, глядя на ID и источник, просто написать в чат эту цифру и отписаться от этого источника!\n\nТакже Вы можете увидеть, на какие источники Вы подписаны, а на какие не подписаны, нажав на кнопку "Подписки и отписки"!\n\nЧтобы выйти в главное меню с клавиатурой с изначальными кнопками, нажмите кнопку "Выйти"')
    
    
# activation of /subscribe_unsubscribe button or command in choose_source area:
@dp.message_handler(lambda message: message.text.lower() == 'подписки и отписки')
async def sub_unsub_all_sources(message: types.Message):
    #checking that person is not novice
    with general_base1.connection:
        general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (message.chat.id,))
        isn = general_base1.cursor.fetchall()[0][0]
        
    if isn == 0 or isn == 1:    
        with general_base1.connection:
            general_base1.cursor.execute('SELECT * FROM users_sources WHERE user_id = %s LIMIT 1', (message.chat.id,))
            li_user_sources = list(general_base1.cursor.fetchall()[0][2:])

        li_sub = []

        for i in range(len(li_user_sources)):
            if li_user_sources[i] == 1:
                li_sub.append('ПОДПИСАНЫ')
            elif li_user_sources[i] == 0:
                li_sub.append('НЕ ПОДПИСАНЫ')

        await message.answer('1. ВК паблик "Анекдоты (megaotriv)":\n{}\n2. ВК паблик "анекдотов.net":\n{}\n3.ВК паблик "Смешные анекдоты":\n{}\n4.Телеграмм канал "Анекдоты (AnekdotiRu)":\n{}\n5. ВК паблик "Анекдоты категории Б":\n{}\n6. ВК паблик "Анекдоты категории Б+":\n{}\n7. ВК паблик "Мои любимые юморески":\n{}\n8. Телеграм канал "Мои любимые юморески":\n{}\n9. Телеграмм канал "Лига Плохих Шуток":\n{}\n10. ВК паблик "Лига плохих шуток:\n{}"'.format(li_sub[0], li_sub[1], li_sub[2], li_sub[3], li_sub[4], li_sub[5], li_sub[6], li_sub[7], li_sub[8], li_sub[9]))
        if isn == 1:
            #keyboard
            markup = types.ReplyKeyboardMarkup(row_width = 5)
            item1 = types.KeyboardButton('Подписки и отписки')
            item2 = types.KeyboardButton(1)
            item3 = types.KeyboardButton(2)
            item4 = types.KeyboardButton(3)
            item5 = types.KeyboardButton(4)
            item6 = types.KeyboardButton(5)
            item7 = types.KeyboardButton(6)
            item8 = types.KeyboardButton(7)
            item9 = types.KeyboardButton(8)
            item10 = types.KeyboardButton(9)
            item11 = types.KeyboardButton(10)
            item12 = types.KeyboardButton('Пропустить начальную инструкцию')

            markup.add(item1)
            markup.add(item2, item3, item4, item5, item6)
            markup.add(item7, item8, item9, item10, item11)
            markup.add(item12)
            await message.answer('Отлично!\nВ сообщении выше Вы видите все источники, откуда брались анекдоты, а также подписаны Вы на эти источники или нет (если Вы новый пользователь, то Вы изначально автоматически подписаны на все источники).\n\nТакже теперь Вы можете увидеть числа на клавиатуре от 1 до 10. Каждое число соответсвует номеру источника в списке в сообщении выше. Выберите любой источник, НА КОТОРЫЙ ВЫ ПОДПИСАНЫ, и нажмите на соответсвующее число на клавиатуре, чтобы отписаться от этого источника!', reply_markup = markup)
    else:
        await message.answer('error in isn')
    
    
#Button to exit choose sources:
@dp.message_handler(lambda message: message.text.lower() == 'выйти')
async def exit_to_main_keyboard(message: types.Message):
    with general_base1.connection:
        general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (message.chat.id,))
        isn = general_base1.cursor.fetchall()[0][0]
    if isn == 1:
        #keyboards
        markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
        item1 = types.KeyboardButton('Анек')
        item2 = types.KeyboardButton('Выбор источников')
        markup.add(item1)
        markup.add(item2)
        markup1 = types.InlineKeyboardMarkup(row_width = 2)
        item_1 = types.InlineKeyboardButton("Закончить начальную инструкцию", callback_data = 'finish_start_instruction')
        item_2 = types.InlineKeyboardButton("Пройти начальную инструкцию заново", callback_data = 'repeat_start_instruction')
        markup1.add(item_1)
        markup1.add(item_2)
        await message.answer('Нажав на кнопку "Выйти", Вы вышли в меню с кнопками, которые были изначально!', reply_markup = markup)
        await message.answer('Поздравляем!!!\nТеперь Вы знаете мой основной функционал!\n\nЕсли Вы хотите пройти начальную инструкцию ещё раз, то нажмите на "Пройти начальную инструкцию заново" под этим сообщением.\nЕсли не хотите, то нажмите на "Закончить начальную инструкцию", чтобы перейти в основное меню, где Вы увидите мой полный функционал!', reply_markup = markup1)
    elif isn == 0:
        with general_base1.connection:
            general_base1.cursor.execute("SELECT subscribed FROM users_sub_best_anec_day WHERE user_id = %s LIMIT 1", (message.chat.id,))
            ku = general_base1.cursor.fetchall()[0][0]
            general_base1.cursor.execute("SELECT in_a_row_started FROM anecs_in_a_row WHERE user_id = %s LIMIT 1", (message.chat.id,))
            status = general_base1.cursor.fetchall()[0][0]
            general_base1.cursor.execute("SELECT subscribed FROM users_sub_random_anec WHERE user_id = %s LIMIT 1", (message.chat.id,))
            kz = general_base1.cursor.fetchall()[0][0]

        #keyboard
        markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
        await main_markup(markup, ku, status, kz)
        await message.answer('Вы вышли в главное меню!', reply_markup = markup)
    else:
        await message.answer('error in isn')
    
#Button for each source:
@dp.message_handler(lambda message: message.text in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'])
async def sub_unsub_certain_source(message: types.Message):
    
    lis = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    k = lis.index(int(message['text']))
    dicta = {
        0: 'ВК паблик "Анекдоты (megaotriv)"',
        1: 'ВК паблик "анекдотов.net"',
        2: 'ВК паблик "Смешные анекдоты"',
        3: 'Телеграмм канал "Анекдоты (AnekdotiRu)"',
        4: 'ВК паблик "Анекдоты категории Б"',
        5: 'ВК паблик "Анекдоты категории Б+"',
        6: 'ВК паблик "Мои любимые юморески"',
        7: 'Телеграмм канал "Мои любимые юморески"',
        8: 'Телеграмм канал "Лига Плохих Шуток"',
        9: 'ВК паблик "Лига плохих шуток"'
    }
    
    if k == 0:
        with general_base1.connection:
            general_base1.cursor.execute("SELECT source_1_chosen FROM users_sources WHERE user_id = %s LIMIT 1", (message['chat']['id'],))
            nu = general_base1.cursor.fetchall()[0][0]
    elif k == 1:
        with general_base1.connection:
            general_base1.cursor.execute("SELECT source_2_chosen FROM users_sources WHERE user_id = %s LIMIT 1", (message['chat']['id'],))
            nu = general_base1.cursor.fetchall()[0][0]
    elif k == 2:
        with general_base1.connection:
            general_base1.cursor.execute("SELECT source_3_chosen FROM users_sources WHERE user_id = %s LIMIT 1", (message['chat']['id'],))
            nu = general_base1.cursor.fetchall()[0][0]
    elif k == 3:
        with general_base1.connection:
            general_base1.cursor.execute("SELECT source_4_chosen FROM users_sources WHERE user_id = %s LIMIT 1", (message['chat']['id'],))
            nu = general_base1.cursor.fetchall()[0][0]
    elif k == 4:
        with general_base1.connection:
            general_base1.cursor.execute("SELECT source_5_chosen FROM users_sources WHERE user_id = %s LIMIT 1", (message['chat']['id'],))
            nu = general_base1.cursor.fetchall()[0][0]
    elif k == 5:
        with general_base1.connection:
            general_base1.cursor.execute("SELECT source_6_chosen FROM users_sources WHERE user_id = %s LIMIT 1", (message['chat']['id'],))
            nu = general_base1.cursor.fetchall()[0][0]
    elif k == 6:
        with general_base1.connection:
            general_base1.cursor.execute("SELECT source_7_chosen FROM users_sources WHERE user_id = %s LIMIT 1", (message['chat']['id'],))
            nu = general_base1.cursor.fetchall()[0][0]
    elif k == 7:
        with general_base1.connection:
            general_base1.cursor.execute("SELECT source_8_chosen FROM users_sources WHERE user_id = %s LIMIT 1", (message['chat']['id'],))
            nu = general_base1.cursor.fetchall()[0][0]
    elif k == 8:
        with general_base1.connection:
            general_base1.cursor.execute("SELECT source_9_chosen FROM users_sources WHERE user_id = %s LIMIT 1", (message['chat']['id'],))
            nu = general_base1.cursor.fetchall()[0][0]
    elif k == 9:
        with general_base1.connection:
            general_base1.cursor.execute("SELECT source_10_chosen FROM users_sources WHERE user_id = %s LIMIT 1", (message['chat']['id'],))
            nu = general_base1.cursor.fetchall()[0][0]
    else:
        await message.answer('error in k')
    
    if nu == 0:
        #checking that person is not novice
        with general_base1.connection:
            general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (message.chat.id,))
            isn = general_base1.cursor.fetchall()[0][0]
        
        if isn == 0 or isn == 1:    
            fin_mes = '{}\n\nНа данный момент вы НЕ ПОЛУЧАЕТЕ анекдоты от этого источника. Хотите ПОДПИСАТЬСЯ на этот источник?'.format(dicta[k])
            markup = types.InlineKeyboardMarkup(row_width = 2)
            item_1 = types.InlineKeyboardButton("Да", callback_data = 'subscribe')
            item_2 = types.InlineKeyboardButton("Отмена", callback_data = 'exit')
            markup.add(item_1, item_2)
            await message.answer(fin_mes, reply_markup = markup)
            if isn == 1:
                await message.answer('Нажмите кнопку "Да" под сообщением выше, чтобы Подписаться на соответствующий источник обратно')
        else:
            await message.answer('error in isn')
    
    elif nu == 1:
        #checking that person is not novice
        with general_base1.connection:
            general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (message.chat.id,))
            isn = general_base1.cursor.fetchall()[0][0]
        
        if isn == 0 or isn == 1:
            fin_mes = '{}\n\nНа данный момент вы ПОЛУЧАЕТЕ анекдоты от этого источника. Хотите ОТПИСАТЬСЯ от этого источника?'.format(dicta[k])
            markup = types.InlineKeyboardMarkup(row_width = 2)
            item_1 = types.InlineKeyboardButton("Да", callback_data = 'unsubscribe')
            item_2 = types.InlineKeyboardButton("Отмена", callback_data = 'exit')
            markup.add(item_1, item_2)
            await message.answer(fin_mes, reply_markup = markup)
            if isn == 1:
                await message.answer('Нажмите кнопку "Да" под сообщением выше, чтобы отписаться от соответствующего источника')
        else:
            await message.answer('error in isn')    
    else:
        await message.answer('error in nu')
        

#Initializing the list of sources:
@dp.message_handler(lambda message: message.text.lower() == 'список источников')
async def list_sources(message: types.Message):
    await message.answer('Все источники (с ссылками), из которых брались анекдоты:\n\n1. ВК паблик "Анекдоты (megaotriv)"\n(vk.com/megaotriv)\n2. ВК паблик "анекдотов.net"\n(vk.com/anekdot)\n3. ВК паблик "Смешные анедкоты"\n(vk.com/smeshnye__anekdoty)\n4. Телеграмм канал "Анекдоты (AnekdotiRu)"\n(t.me/AnekdotiRu)\n5. ВК паблик "Анекдоты категории Б"\n(vk.com/baneks)\n6. ВК паблик "Анекдоты категории Б+"\n(vk.com/anekdotikategoriib)\n7. ВК паблик "Мои любимые юморески"\n(vk.com/jumoreski)\n8. Телеграм канал "Мои любимые юморески"\n(t.me/myfavoritejumoreski)\n9. Телеграмм канал "Лига Плохих Шуток"\n(t.me/ligapsh)\n10. ВК паблик "Лига плохих шуток"\n(vk.com/badjokesleague)\n\nНравится источник?\nПодписывайтесь на него, переходя по соответсвующей ссылке!', disable_web_page_preview = True)
    

#Initializing instruction of search of anec by word:
@dp.message_handler(lambda message: message.text.lower() == 'поиск анека по слову: инструкция')
async def find_anec_word_instruction(message: types.Message):
    with general_base1.connection:
        general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (message.chat.id,))
        isn = general_base1.cursor.fetchall()[0][0]
    if isn == 1:
        await message.answer('На данный момент эта команда недоступна так как Вы находитесь в разделе "Начальная инструкция".\n\nЭта команда будет доступна, как только Вы завершите или пропустите начальную инструкцию')
    elif isn == 0:
        with general_base1.connection:
            general_base1.cursor.execute("SELECT in_a_row_started FROM anecs_in_a_row WHERE user_id = %s LIMIT 1", (message.chat.id,))
            status = general_base1.cursor.fetchall()[0][0]
        if status == 1:
            await message.answer('Чтобы я смог найти анекдоты по слову(-ам), сначала нажмите на кнопку "СТОП анеки подряд" на клавиатуре и затем нажмите на "Поиск Анека по слову: инструкция" на клавиатуре заново!')
        elif status == 0:
            await message.answer('Прочитали смешной анекдот, но помните из него всего лишь пару слов? Здесь Вы узнаете, как найти целые анекдоты по слову(-ам)!\n\nЧтобы найти анекдот по выбранному Вами слову(-ам), напишите мне слово "Найти" (без кавычек!) и затем через пробел слово или несколько слов, по которым Вы хотите найти анекдоты. Функции остальных кнопок, во время поиска анекдотов по слову, остаются теми же.\n\nВНИМАНИЕ!!! через команду "Найти" могут попасться анекдоты из любых источников. Чтобы находить анекдот по слову СТРОГО из источников, на которые Вы подписаны, вместо команды "Найти" напишите фразу "Найти мои источники" (опять же без кавычек!) и потом, опять же через пробел, введите слово, по которому нужно найти анекдот!')
        else:
            await message.answer('error in status')
    else:
        await message.answer('error in isn')

    
    
#Initializing search of anec by word:
@dp.message_handler(lambda message: message.text[:5].lower() == 'найти' and message.text[5:19].lower() != ' мои источники' and message.text.lower()[:11] != 'найти сохра' and message.text.lower() != 'найти сохру по слову: инструкция')
async def find_anec_word_all(message: types.Message):
    with general_base1.connection:
        general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (message.chat.id,))
        isn = general_base1.cursor.fetchall()[0][0]
    if isn == 1:
        await message.answer('На данный момент эта команда недоступна так как Вы находитесь в разделе "Начальная инструкция".\n\nЭта команда будет доступна, как только Вы завершите или пропустите начальную инструкцию')
    elif isn == 0:
        with general_base1.connection:
            general_base1.cursor.execute("SELECT in_a_row_started FROM anecs_in_a_row WHERE user_id = %s LIMIT 1", (message.chat.id,))
            status = general_base1.cursor.fetchall()[0][0]
        if status == 1:
            await message.answer('Чтобы я смог найти анекдоты по слову(-ам), сначала нажмите на кнопку "СТОП анеки подряд" на клавиатуре и затем напишите мне слово после команды "Найти" заново!')
        elif status == 0:
            y = message['text'][5:].strip()
            if len(y) > 250:
                await message.answer('Вы ввели слишком много слов для поиска анекдота!\n\nСократите количество слов, чтобы я начал искать анекдоты, содержащие эту последовательность из слов!')   
            elif y == '':
                await message.answer('Вы не написали слово. Напишите слово после команды "Найти", чтобы выбрать слово.')    
            else:
                markup = types.InlineKeyboardMarkup(row_width = 2)
                item_1 = types.InlineKeyboardButton("Да", callback_data = 'get_anec_by_word')
                item_2 = types.InlineKeyboardButton("Выбрать другое слово", callback_data = 'another_word')
                item_3 = types.InlineKeyboardButton("Отмена", callback_data = 'exit_by_word')
                markup.add(item_1)
                markup.add(item_2)
                markup.add(item_3)

                await message.answer('{}:\nНайти анекдoт с этим словом(-ами)?'.format(y), reply_markup = markup)   
        else:
            await message.answer('error in status')
    else:
        await message.answer('error in isn')
            
            
    
#Initializing search of anec by word:
@dp.message_handler(lambda message: message.text[:19].lower() == 'найти мои источники')
async def find_anec_word_favourite_sources(message: types.Message):
    with general_base1.connection:
        general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (message.chat.id,))
        isn = general_base1.cursor.fetchall()[0][0]
    if isn == 1:
        await message.answer('На данный момент эта команда недоступна так как Вы находитесь в разделе "Начальная инструкция".\n\nЭта команда будет доступна, как только Вы завершите или пропустите начальную инструкцию')
    elif isn == 0:
        with general_base1.connection:
            general_base1.cursor.execute("SELECT in_a_row_started FROM anecs_in_a_row WHERE user_id = %s LIMIT 1", (message.chat.id,))
            status = general_base1.cursor.fetchall()[0][0]
        if status == 1:
            await message.answer('Чтобы я смог найти анекдоты по слову(-ам) из Ваших любимых источников, сначала нажмите на кнопку "СТОП анеки подряд" на клавиатуре и затем напишите слово после команды "Найти мои источники" заново!')
        elif status == 0:
            y = message['text'][19:].strip()
            if len(y) > 250:
                await message.answer('Вы ввели слишком много слов для поиска анекдота!\n\nСократите количество слов, чтобы я начал искать анекдоты, содержащие эту последовательность из слов!')   
            elif y == '':
                await message.answer('Вы не написали слово. Напишите слово после команды "Найти мои источники", чтобы выбрать слово.')

            else:
                markup = types.InlineKeyboardMarkup(row_width = 2)
                item_1 = types.InlineKeyboardButton("Да", callback_data = 'get_anec_by_word_group')
                item_2 = types.InlineKeyboardButton("Выбрать другое слово", callback_data = 'another_word')
                item_3 = types.InlineKeyboardButton("Отмена", callback_data = 'exit_by_word')
                markup.add(item_1)
                markup.add(item_2)
                markup.add(item_3)

                await message.answer('{}:\nНайти анекдoт из Ваших любимых источников с этим словом(-ами)?'.format(y), reply_markup = markup) 
        else:
            await message.answer('error in status')
    else:
        await message.answer('error in isn')

        
    
# activation of /help button or command:
@dp.message_handler(lambda message: message.text.lower() == 'help')
async def help_main(message: types.message):
    markup = types.InlineKeyboardMarkup(row_width = 2)
    item_1 = types.InlineKeyboardButton("Начальная инструкция", callback_data = 'button_intro_instruction')
    item_2 = types.InlineKeyboardButton("Анек", callback_data = 'button_anec')
    item_3 = types.InlineKeyboardButton("10 Анеков", callback_data = 'button_ten_anecs')
    item_4 = types.InlineKeyboardButton("Много Анеков", callback_data = 'button_many_anecs')
    item_5 = types.InlineKeyboardButton("СТАРТ/СТОП Анеки подряд", callback_data = 'button_anecs_in_a_row')
    item_6 = types.InlineKeyboardButton("Сохранённые Анеки", callback_data = 'button_saved_anecs')
    item_7 = types.InlineKeyboardButton("Выбор источников", callback_data = 'button_choose_sources')
    item_8 = types.InlineKeyboardButton("Поиск Анека по слову: инструкция", callback_data = 'button_search_by_word')
    item_9 = types.InlineKeyboardButton("Список источников", callback_data = 'button_list_sources')
    item_10 = types.InlineKeyboardButton("Анек дня: отписаться/подписаться", callback_data = 'button_sub_or_unsub_anec_day')
    item_14 = types.InlineKeyboardButton("Рандомный Анек: отписаться/подписаться", callback_data = 'button_sub_or_unsub_random_anec')
    item_11 = types.InlineKeyboardButton("Последние 5 удалённых сохранённок", callback_data = 'button_last_five_saved')
    item_12 = types.InlineKeyboardButton("Возможные проблемы", callback_data = 'button_potential_problems')
    item_13 = types.InlineKeyboardButton("Полная инструкция", callback_data = 'button_full_instr')
    markup.add(item_1)
    markup.add(item_2)
    markup.add(item_3)
    markup.add(item_4)
    markup.add(item_5)
    markup.add(item_6)
    markup.add(item_7)
    markup.add(item_8)
    markup.add(item_9)
    markup.add(item_10)
    markup.add(item_14)
    markup.add(item_11)
    markup.add(item_12)
    markup.add(item_13)                                     
    await message.answer('В этой инструкции Вы можете узнать, какие функции выполняет каждая моя кнопка на клавиатуре, нажав на соответствующее название под сообщением. Ещё Вы можете нажать на "Полная инструкция", чтобы получить полную инструкцию по всем кнопкам соответственно.\n\nВажно добавить, что, вместо нажатия кнопки на клавиатуре, вы можете написать мне обычное сообщение с текстом на кнопке, чтобы вызвать ту или иную команду (например, вместо нажатия на кнопку "help", Вы можете просто написать и отправить мне слово help), причём не важно, делаете Вы это заглавными или прописными буквами.\n\nТакже Вы можете нажать на "Начальная инструкция" под сообщением, чтобы вспомнить, как пользоваться основными командами.\n\nТакже если возникли какие-то проблемы или баги, Вы можете посмотреть раздел "Возможные проблемы". Если не помогло, то Вы можете обратиться с возникшей проблемой в общий чат AnecBot chat (t.me/anecbot_chat)\n\nПомимо этого, Вы всегда можете добавить бота в свои чаты и получать анекдоты там (если после добавления бота в чат у Вас не появится клавиатуры с кнопками бота, то просто напишите в чат "/start" (без кавычек). Также в чатах начальная инструкция не будет интерактивной (вместо этого, будет текстовая инструкция)).\n\nПРЕДУПРЕЖДЕНИЕ: некоторые анекдоты могут содержать мат и прочую нецензурную лексику!\n\nЧтобы потом посмотреть другой раздел инструкции, вы можете вернуться к этому сообщению или нажать на клавиатуре кнопку "help" заново.\n\nВыберите раздел инструкции:', reply_markup = markup)
    

# activation of subscription to the anec of the day:
@dp.message_handler(lambda message: message.text.lower() == 'анек дня: подписаться')
async def sub_anec_day(message: types.message):
    with general_base1.connection:
        general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (message.chat.id,))
        isn = general_base1.cursor.fetchall()[0][0]
    if isn == 1:
        await message.answer('На данный момент эта команда недоступна так как Вы находитесь в разделе "Начальная инструкция".\n\nЭта команда будет доступна, как только Вы завершите или пропустите начальную инструкцию')
    elif isn == 0:
        markup = types.InlineKeyboardMarkup(row_width = 2)
        item_1 = types.InlineKeyboardButton("Да", callback_data = 'subscribe_to_anec_of_the_day')
        item_2 = types.InlineKeyboardButton("Отмена", callback_data = 'exit_sub_anec_day')
        markup.add(item_1, item_2)
        await message.answer('Вам каждый день автоматически будет присылаться лучший анекдот дня по версии пользователей бота.\nПодписаться на анекдот дня?', reply_markup = markup) 
    else:
        await message.answer('error in isn')

    
# activation of unsubscription to the anec of the day:
@dp.message_handler(lambda message: message.text.lower() == 'анек дня: отписаться')
async def unsub_anec_day(message: types.message):
    with general_base1.connection:
        general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (message.chat.id,))
        isn = general_base1.cursor.fetchall()[0][0]
    if isn == 1:
        await message.answer('На данный момент эта команда недоступна так как Вы находитесь в разделе "Начальная инструкция".\n\nЭта команда будет доступна, как только Вы завершите или пропустите начальную инструкцию')
    elif isn == 0:
        markup = types.InlineKeyboardMarkup(row_width = 2)
        item_1 = types.InlineKeyboardButton("Да", callback_data = 'unsubscribe_from_anec_of_the_day')
        item_2 = types.InlineKeyboardButton("Отмена", callback_data = 'exit_unsub_anec_day')
        markup.add(item_1, item_2)
        await message.answer('Вам больше не будет присылаться лучший анекдот дня по версии пользователей бота.\nОтписаться от анекдота дня?', reply_markup = markup)
    else:
        await message.answer('error in isn')
        
        
        
# activation of subscription to the anec of the day:
@dp.message_handler(lambda message: message.text.lower() == 'рандомный анек: подписаться')
async def sub_random_anec(message: types.message):
    with general_base1.connection:
        general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (message.chat.id,))
        isn = general_base1.cursor.fetchall()[0][0]
    if isn == 1:
        await message.answer('На данный момент эта команда недоступна так как Вы находитесь в разделе "Начальная инструкция".\n\nЭта команда будет доступна, как только Вы завершите или пропустите начальную инструкцию')
    elif isn == 0:
        markup = types.InlineKeyboardMarkup(row_width = 2)
        item_1 = types.InlineKeyboardButton("Да", callback_data = 'subscribe_to_random_anec')
        item_2 = types.InlineKeyboardButton("Отмена", callback_data = 'exit_sub_random_anec')
        markup.add(item_1, item_2)
        await message.answer('Вам 2 раза в день автоматически будет присылаться случайный анекдот из моей базы.\nПодписаться на рандомный Анек?', reply_markup = markup) 
    else:
        await message.answer('error in isn')

    
# activation of unsubscription to the anec of the day:
@dp.message_handler(lambda message: message.text.lower() == 'рандомный анек: отписаться')
async def unsub_random_anec(message: types.message):
    with general_base1.connection:
        general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (message.chat.id,))
        isn = general_base1.cursor.fetchall()[0][0]
    if isn == 1:
        await message.answer('На данный момент эта команда недоступна так как Вы находитесь в разделе "Начальная инструкция".\n\nЭта команда будет доступна, как только Вы завершите или пропустите начальную инструкцию')
    elif isn == 0:
        markup = types.InlineKeyboardMarkup(row_width = 2)
        item_1 = types.InlineKeyboardButton("Да", callback_data = 'unsubscribe_from_random_anec')
        item_2 = types.InlineKeyboardButton("Отмена", callback_data = 'exit_unsub_random_anec')
        markup.add(item_1, item_2)
        await message.answer('Вам больше не будет присылаться случайный анекдот два раза в день.\nОтписаться от рандомного Анека?', reply_markup = markup)
    else:
        await message.answer('error in isn')
    
   
    
# activation of saved anecs button:
@dp.message_handler(lambda message: message.text.lower() == 'сохранённые анеки')
async def saved_anecs(message: types.message):
    with general_base1.connection:
        general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (message.chat.id,))
        isn = general_base1.cursor.fetchall()[0][0]
    if isn == 1:
        await message.answer('На данный момент эта команда недоступна так как Вы находитесь в разделе "Начальная инструкция".\n\nЭта команда будет доступна, как только Вы завершите или пропустите начальную инструкцию')
    elif isn == 0:
        with general_base1.connection:
            general_base1.cursor.execute("SELECT COUNT(*) FROM saved_anecs_by_user WHERE user_id = %s AND not_deleted = True", (message.chat.id,))
            ken = general_base1.cursor.fetchall()[0][0]
        if ken == 0:
            await message.answer('На данный момент Вы не сохранили ни один анекдот. Нажимайте на кнопку "Добавить в "Сохранённые"" под анекдотом, чтобы сохранить анекдот')
        # when less than 20 anecs
        elif ken > 0 and ken < 20:
            if ken == 1:
                await message.answer('На данный момент Вы сохранили 1 анекдот. Высылаю Вам этот анекдот!')
            elif ken in [2, 3, 4]:
                await message.answer('На данный момент Вы сохранили {} анекдота. Высылаю Вам все эти анекдоты, отсортированные по дате сохранения!'.format(ken))
            elif ken > 4:
                await message.answer('На данный момент Вы сохранили {} анекдотов. Высылаю Вам все эти анекдоты, отсортированные по дате сохранения!'.format(ken))
            else: 
                await message.answer('error in ken')

            with general_base1.connection:
                general_base1.cursor.execute("SELECT cluster_num, id_entry, anec_text, source, epoch_time_added FROM saved_anecs_by_user AS sabu INNER JOIN anecdotes_general_table AS agt ON sabu.id_anec = agt.id_entry WHERE user_id = %s AND not_deleted = True ORDER BY epoch_time_added", (message.chat.id,))
                duta = general_base1.cursor.fetchall()

            await asyncio.sleep(1)

            markup = types.InlineKeyboardMarkup(row_width = 2)
            item_1 = types.InlineKeyboardButton("Удалить Анек из \"Сохранённых\"", callback_data = 'delete_saved')
            markup.add(item_1)

            for i in range(ken):
                final = '{}) ID: {}-{}\n***anecbot***\n\n{}\n\nИстoчник: {}\nДата сохранения Анека: {}'.format(i + 1, duta[i][0], duta[i][1], duta[i][2], duta[i][3], datetime.fromtimestamp(duta[i][4]).strftime('%Y-%m-%d')) 
                if len(final) <= 4096:
                    await message.answer(final, reply_markup = markup)  
                else:
                    for x in range(0, len(final) - 4096, 4096):
                        await message.answer(final[x : x + 4096])
                    k = len(final)//4096
                    await message.answer('ID: {}-{}\n***anecbot***\n\n'.format(duta[i][0], duta[i][1]) + final[k * 4096 : k * 4096 + 4096], reply_markup = markup)   

        #when more than 20 saved anecs!!!
        elif ken >= 20:       
            #keyboard
            markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
            item1 = types.KeyboardButton("Выйти")
            item2 = types.KeyboardButton("help Сохры")
            item3 = types.KeyboardButton("Рандомная Сохра")         
            item4 = types.KeyboardButton("5 рандомных Сохр")
            item5 = types.KeyboardButton("Первые Сохры")
            item6 = types.KeyboardButton("Последние Сохры")
            item7 = types.KeyboardButton("Сохра Лаг: инструкция")
            item8 = types.KeyboardButton("Найти Сохру по слову: инструкция")
            item9 = types.KeyboardButton("Количество Сохр")
            item10 = types.KeyboardButton('Последние 5 удалённых Сохр')

            markup.add(item1, item2) 
            markup.add(item3, item4)
            markup.add(item5, item6)
            markup.add(item7)
            markup.add(item8)
            markup.add(item9)
            markup.add(item10)

            await message.answer('Так как у Вас больше 20 сохранённых анекдотов (Ваше количество сохранённых анекдотов: {}), при нажатии на кнопку "Сохранённые анекдоты", будет открываться клавиатура с новыми кнопками.\n\nТакже теперь сохранённые анекдоты коротко называются "Сохрами" (одна "Сохра", много "Сохр"). Чтобы выйти в главное меню с клавиатурой с изначальными кнопками, Вы можете просто нажать кнопку "Выйти".\n\nК сожалению, теперь нельзя будет нажатием одной кнопки выслать все сохранённые анекдоты: это может перегрузить меня, а также это засоряет Ваш чат со мной. Однако, это не означает того, что Вы не сможете найти Сохру, которую хотите найти. С помощью кнопок на клавиатуре, это будет не так уж и сложно.\n\nТакже как и в случае, когда у Вас было меньше, чем 20 сохранённых анекдотов, Вы всегда сможете удалить анекдот из сохранённых, нажав на соответствующую кнопку под сообщением.\n\nНамжите кнопку "help Сохры", чтобы узнать функционал каждой из кнопок на этой клавиатуре!'.format(ken), reply_markup = markup)

        else:
            await message.answer('error in ken')
    else:
        await message.answer('error in isn')
            
        
        
# activation of random saved anec button:
@dp.message_handler(lambda message: message.text.lower() == 'help сохры')
async def help_saved_anecs(message: types.message):
    with general_base1.connection:
        general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (message.chat.id,))
        isn = general_base1.cursor.fetchall()[0][0]
    if isn == 1:
        await message.answer('На данный момент эта команда недоступна так как Вы находитесь в разделе "Начальная инструкция".\n\nЭта команда будет доступна, как только Вы завершите или пропустите начальную инструкцию')
    elif isn == 0:
        with general_base1.connection:
            general_base1.cursor.execute("SELECT COUNT(*) FROM saved_anecs_by_user WHERE user_id = %s AND not_deleted = True", (message.chat.id,))
            ken = general_base1.cursor.fetchall()[0][0]
        if ken < 20:
            with general_base1.connection:
                general_base1.cursor.execute("SELECT subscribed FROM users_sub_best_anec_day WHERE user_id = %s LIMIT 1", (message.chat.id,))
                ku = general_base1.cursor.fetchall()[0][0]
                general_base1.cursor.execute("SELECT in_a_row_started FROM anecs_in_a_row WHERE user_id = %s LIMIT 1", (message.chat.id,))
                status = general_base1.cursor.fetchall()[0][0]
                general_base1.cursor.execute("SELECT subscribed FROM users_sub_random_anec WHERE user_id = %s LIMIT 1", (message.chat.id,))
                kz = general_base1.cursor.fetchall()[0][0]

            #keyboard
            markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
            await main_markup(markup, ku, status, kz)
            await message.answer('Вы cохранили меньше 20 анекдотов. Поэтому, при нажатии на кнопку "Сохранённые Анеки", Вам автоматически будут присылаться все сохранённые Вами анекдоты!', reply_markup = markup)
        else:
            await message.answer('В этой инструкции я буду объяснять функцию каждой новой кнопки(кроме кнопки "help Сохры", на которую Вы нажали), которая появилась после Вашего нажатия на кнопку "Сохранённые Анеки".\n\n\n1. ИНСТРУКЦИЯ ПО КНОПКЕ "Выйти"\n\nНажав на эту кнопку Вы просто выйдете в главное меню с клавиатурой с изначальными кнопками.\n\n\n2. ИНСТРУКЦИЯ ПО КНОПКЕ "Рандомная Сохра"\n\nНажав на эту кнопку, Вы получите один из Ваших сохранённых анекдотов, выбранного мною случайным образом.\n\n\n3. ИНСТРУКЦИЯ ПО КНОПКЕ "5 рандомных Сохр"\n\nЭта кнопка аналогична предыдущей, только я выбираю 5 Ваших сохранённых анекдотов случайным образом.\n\n\n4. ИНСТРУКЦИЯ ПО КНОПКЕ "Первые Сохры"\n\nС помощью этой кнопки Вы можете получить самые ранние (по дате и времени добавления их в сохранённые) сохранённые анекдоты.\n\nСначала Вам будет предложено выбрать количество самых ранних анекдотов. После нажатия на цифру я пришлю соответствующее количество самых первых сохранённых анекдотов.\n\n\n5. ИНСТРУКЦИЯ ПО КНОПКЕ "Последние Сохры"\n\nЭта кнопка аналогична предыдущей, только теперь я буду присылать самые поздние (по дате и времени добавления их в сохранённые) сохранённые анекдоты.\n\nЛАЙФХАК: если у Вас от 20 до 40 сохранённых анекдотов, то вы легко можете получить все сохранённые анекдоты, выбрав 20 первых сохр и 20 последних сохр!\n\n\n6. ИНСТРУКЦИЯ ПО КНОПКЕ "Сохра Лаг: инструкция"\n\nНажав на эту кнопку Вы получите инструкцию к, возможно, самой сложной команде этого бота. В основном эта команда будет полезна тем пользователям, которые сохранили больше 40 анекдотов.\n\n\n7. ИНСТРУКЦИЯ ПО КНОПКЕ "Найти Сохры по слову: инструкция"\n\nНажав на эту кнопку Вы получите инструкцию о том, как найти сохранённые анекдоты, которые содержат то или иное слово. Процесс данного поиска схож с тем процессом, где Вы ищете анекдоты с тем или иным словом из целой базы анекдотов.\n\n\n8. ИНСТРУКЦИЯ ПО КНОПКЕ "Количество Сохр"\n\nТут всё просто: нажав на эту кнопку, Вы получаете количество анекдотов, которые Вы сохранили!\n\n\n9. ИНСТРУКЦИЯ ПО КНОПКЕ "Последние 5 удалённых Сохр".\n\nЭта кнопка выполняет точно такие же функции, что и кнопка "Последние 5 удалённых Сохранёнок" в главном меню.\n\nНажав на эту кнопку Вы получите 5 последних удалённых Вами сохранённых анекдотов. Чтобы добавить анекдот обратно в сохранённые, нажмите на соответствующую кнопку под сообщением и подтвердите выбор, нажав на кнопку "Да"!')
    else:
        await message.answer('error in isn')
    
    
            
# activation of help saved anecs button:
@dp.message_handler(lambda message: message.text.lower() == 'рандомная сохра')
async def random_saved_anec(message: types.message):
    with general_base1.connection:
        general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (message.chat.id,))
        isn = general_base1.cursor.fetchall()[0][0]
    if isn == 1:
        await message.answer('На данный момент эта команда недоступна так как Вы находитесь в разделе "Начальная инструкция".\n\nЭта команда будет доступна, как только Вы завершите или пропустите начальную инструкцию')
    elif isn == 0:
        with general_base1.connection:
            general_base1.cursor.execute("SELECT COUNT(*) FROM saved_anecs_by_user WHERE user_id = %s AND not_deleted = True", (message.chat.id,))
            ken = general_base1.cursor.fetchall()[0][0]
        if ken < 20:
            with general_base1.connection:
                general_base1.cursor.execute("SELECT subscribed FROM users_sub_best_anec_day WHERE user_id = %s LIMIT 1", (message.chat.id,))
                ku = general_base1.cursor.fetchall()[0][0]
                general_base1.cursor.execute("SELECT in_a_row_started FROM anecs_in_a_row WHERE user_id = %s LIMIT 1", (message.chat.id,))
                status = general_base1.cursor.fetchall()[0][0]
                general_base1.cursor.execute("SELECT subscribed FROM users_sub_random_anec WHERE user_id = %s LIMIT 1", (message.chat.id,))
                kz = general_base1.cursor.fetchall()[0][0]

            #keyboard
            markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
            await main_markup(markup, ku, status, kz)
            await message.answer('Вы cохранили меньше 20 анекдотов. Поэтому, при нажатии на кнопку "Сохранённые Анеки", Вам автоматически будут присылаться все сохранённые Вами анекдоты!', reply_markup = markup)
        else:
            with general_base1.connection:
                general_base1.cursor.execute("SELECT cluster_num, id_entry, anec_text, source, epoch_time_added FROM saved_anecs_by_user AS sabu INNER JOIN anecdotes_general_table AS agt ON sabu.id_anec = agt.id_entry WHERE user_id = %s AND not_deleted = True ORDER BY RANDOM() LIMIT 1", (message.chat.id,))
                duta = general_base1.cursor.fetchall()

            markup = types.InlineKeyboardMarkup(row_width = 2)
            item_1 = types.InlineKeyboardButton("Удалить Анек из \"Сохранённых\"", callback_data = 'delete_saved')
            markup.add(item_1)

            final = 'ID: {}-{}\n***anecbot***\n\n{}\n\nИстoчник: {}\nДата сохранения Анека: {}'.format(duta[0][0], duta[0][1], duta[0][2], duta[0][3], datetime.fromtimestamp(duta[0][4]).strftime('%Y-%m-%d')) 
            if len(final) <= 4096:
                await message.answer(final, reply_markup = markup)  
            else:
                for x in range(0, len(final) - 4096, 4096):
                    await message.answer(final[x : x + 4096])
                k = len(final)//4096
                await message.answer('ID: {}-{}\n***anecbot***\n\n'.format(duta[0][0], duta[0][1]) + final[k * 4096 : k * 4096 + 4096], reply_markup = markup)   
    else:
        await message.answer('error in isn')
    
    

# activation of 5 random saved anecs button:
@dp.message_handler(lambda message: message.text.lower() == '5 рандомных сохр')
async def five_random_saved_anecs(message: types.message):
    with general_base1.connection:
        general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (message.chat.id,))
        isn = general_base1.cursor.fetchall()[0][0]
    if isn == 1:
        await message.answer('На данный момент эта команда недоступна так как Вы находитесь в разделе "Начальная инструкция".\n\nЭта команда будет доступна, как только Вы завершите или пропустите начальную инструкцию')
    elif isn == 0:
        with general_base1.connection:
            general_base1.cursor.execute("SELECT COUNT(*) FROM saved_anecs_by_user WHERE user_id = %s AND not_deleted = True", (message.chat.id,))
            ken = general_base1.cursor.fetchall()[0][0]
        if ken < 20:
            with general_base1.connection:
                general_base1.cursor.execute("SELECT subscribed FROM users_sub_best_anec_day WHERE user_id = %s LIMIT 1", (message.chat.id,))
                ku = general_base1.cursor.fetchall()[0][0]
                general_base1.cursor.execute("SELECT in_a_row_started FROM anecs_in_a_row WHERE user_id = %s LIMIT 1", (message.chat.id,))
                status = general_base1.cursor.fetchall()[0][0]
                general_base1.cursor.execute("SELECT subscribed FROM users_sub_random_anec WHERE user_id = %s LIMIT 1", (message.chat.id,))
                kz = general_base1.cursor.fetchall()[0][0]

            #keyboard
            markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
            await main_markup(markup, ku, status, kz)
            await message.answer('Вы cохранили меньше 20 анекдотов. Поэтому, при нажатии на кнопку "Сохранённые Анеки", Вам автоматически будут присылаться все сохранённые Вами анекдоты!', reply_markup = markup)
        else:
            with general_base1.connection:
                general_base1.cursor.execute("SELECT cluster_num, id_entry, anec_text, source, epoch_time_added FROM saved_anecs_by_user AS sabu INNER JOIN anecdotes_general_table AS agt ON sabu.id_anec = agt.id_entry WHERE user_id = %s AND not_deleted = True ORDER BY RANDOM() LIMIT 5", (message.chat.id,))
                duta = general_base1.cursor.fetchall()

            markup = types.InlineKeyboardMarkup(row_width = 2)
            item_1 = types.InlineKeyboardButton("Удалить Анек из \"Сохранённых\"", callback_data = 'delete_saved')
            markup.add(item_1)

            for i in range(5):
                final = '{}) ID: {}-{}\n***anecbot***\n\n{}\n\nИстoчник: {}\nДата сохранения Анека: {}'.format(i + 1, duta[i][0], duta[i][1], duta[i][2], duta[i][3], datetime.fromtimestamp(duta[i][4]).strftime('%Y-%m-%d')) 
                if len(final) <= 4096:
                    await message.answer(final, reply_markup = markup)  
                else:
                    for x in range(0, len(final) - 4096, 4096):
                        await message.answer(final[x : x + 4096])
                    k = len(final)//4096
                    await message.answer('{}) ID: {}-{}\n***anecbot***\n\n'.format(i + 1, duta[i][0], duta[i][1]) + final[k * 4096 : k * 4096 + 4096], reply_markup = markup) 
    else:
        await message.answer('error in isn')
    
    
    
# activation of first added saved anecs button:
@dp.message_handler(lambda message: message.text.lower() == 'первые сохры')
async def first_added_saved_anecs(message: types.message):
    with general_base1.connection:
        general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (message.chat.id,))
        isn = general_base1.cursor.fetchall()[0][0]
    if isn == 1:
        await message.answer('На данный момент эта команда недоступна так как Вы находитесь в разделе "Начальная инструкция".\n\nЭта команда будет доступна, как только Вы завершите или пропустите начальную инструкцию')
    elif isn == 0:
        with general_base1.connection:
            general_base1.cursor.execute("SELECT COUNT(*) FROM saved_anecs_by_user WHERE user_id = %s AND not_deleted = True", (message.chat.id,))
            ken = general_base1.cursor.fetchall()[0][0]
        if ken < 20:
            with general_base1.connection:
                general_base1.cursor.execute("SELECT subscribed FROM users_sub_best_anec_day WHERE user_id = %s LIMIT 1", (message.chat.id,))
                ku = general_base1.cursor.fetchall()[0][0]
                general_base1.cursor.execute("SELECT in_a_row_started FROM anecs_in_a_row WHERE user_id = %s LIMIT 1", (message.chat.id,))
                status = general_base1.cursor.fetchall()[0][0]
                general_base1.cursor.execute("SELECT subscribed FROM users_sub_random_anec WHERE user_id = %s LIMIT 1", (message.chat.id,))
                kz = general_base1.cursor.fetchall()[0][0]

            #keyboard
            markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
            await main_markup(markup, ku, status, kz)
            await message.answer('Вы cохранили меньше 20 анекдотов. Поэтому, при нажатии на кнопку "Сохранённые Анеки", Вам автоматически будут присылаться все сохранённые Вами анекдоты!', reply_markup = markup)
        else:
            markup = types.InlineKeyboardMarkup(row_width = 10)
            item_1 = types.InlineKeyboardButton(1, callback_data = "savedfirst1")
            item_2 = types.InlineKeyboardButton(2, callback_data = "savedfirst2")
            item_3 = types.InlineKeyboardButton(3, callback_data = "savedfirst3")
            item_4 = types.InlineKeyboardButton(4, callback_data = "savedfirst4")
            item_5 = types.InlineKeyboardButton(5, callback_data = "savedfirst5")
            item_6 = types.InlineKeyboardButton(6, callback_data = "savedfirst6")
            item_7 = types.InlineKeyboardButton(7, callback_data = "savedfirst7")
            item_8 = types.InlineKeyboardButton(8, callback_data = "savedfirst8")
            item_9 = types.InlineKeyboardButton(9, callback_data = "savedfirst9")
            item_10 = types.InlineKeyboardButton(10, callback_data = "savedfirst10")
            item_11 = types.InlineKeyboardButton(11, callback_data = "savedfirst11")
            item_12 = types.InlineKeyboardButton(12, callback_data = "savedfirst12")
            item_13 = types.InlineKeyboardButton(13, callback_data = "savedfirst13")
            item_14 = types.InlineKeyboardButton(14, callback_data = "savedfirst14")
            item_15 = types.InlineKeyboardButton(15, callback_data = "savedfirst15")
            item_16 = types.InlineKeyboardButton(16, callback_data = "savedfirst16")
            item_17 = types.InlineKeyboardButton(17, callback_data = "savedfirst17")
            item_18 = types.InlineKeyboardButton(18, callback_data = "savedfirst18")
            item_19 = types.InlineKeyboardButton(19, callback_data = "savedfirst19")
            item_20 = types.InlineKeyboardButton(20, callback_data = "savedfirst20")
            item_21 = types.InlineKeyboardButton('Отмена', callback_data = "exit3")

            markup.add(item_1, item_2, item_3, item_4, item_5)
            markup.add(item_6, item_7, item_8, item_9, item_10)
            markup.add(item_11, item_12, item_13, item_14, item_15)
            markup.add(item_16, item_17, item_18, item_19, item_20)
            markup.add(item_21)
            await message.answer('Эта команда высылает самые первые (по дате добавления) анекдоты, добавленные Вами в сохранённые.\n\nВыберите количество первых сохр, которые Вы хотите получить:', reply_markup = markup)
    else:
        await message.answer('error in isn')
            
    
    
# activation of last added saved anecs button:
@dp.message_handler(lambda message: message.text.lower() == 'последние сохры')
async def last_added_saved_anecs(message: types.message):
    with general_base1.connection:
        general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (message.chat.id,))
        isn = general_base1.cursor.fetchall()[0][0]
    if isn == 1:
        await message.answer('На данный момент эта команда недоступна так как Вы находитесь в разделе "Начальная инструкция".\n\nЭта команда будет доступна, как только Вы завершите или пропустите начальную инструкцию')
    elif isn == 0:
        with general_base1.connection:
            general_base1.cursor.execute("SELECT COUNT(*) FROM saved_anecs_by_user WHERE user_id = %s AND not_deleted = True", (message.chat.id,))
            ken = general_base1.cursor.fetchall()[0][0]
        if ken < 20:
            with general_base1.connection:
                general_base1.cursor.execute("SELECT subscribed FROM users_sub_best_anec_day WHERE user_id = %s LIMIT 1", (message.chat.id,))
                ku = general_base1.cursor.fetchall()[0][0]
                general_base1.cursor.execute("SELECT in_a_row_started FROM anecs_in_a_row WHERE user_id = %s LIMIT 1", (message.chat.id,))
                status = general_base1.cursor.fetchall()[0][0]
                general_base1.cursor.execute("SELECT subscribed FROM users_sub_random_anec WHERE user_id = %s LIMIT 1", (message.chat.id,))
                kz = general_base1.cursor.fetchall()[0][0]

            #keyboard
            markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
            await main_markup(markup, ku, status, kz)
            await message.answer('Вы cохранили меньше 20 анекдотов. Поэтому, при нажатии на кнопку "Сохранённые Анеки", Вам автоматически будут присылаться все сохранённые Вами анекдоты!', reply_markup = markup)
        else:
            markup = types.InlineKeyboardMarkup(row_width = 10)
            item_1 = types.InlineKeyboardButton(1, callback_data = "savedlast1")
            item_2 = types.InlineKeyboardButton(2, callback_data = "savedlast2")
            item_3 = types.InlineKeyboardButton(3, callback_data = "savedlast3")
            item_4 = types.InlineKeyboardButton(4, callback_data = "savedlast4")
            item_5 = types.InlineKeyboardButton(5, callback_data = "savedlast5")
            item_6 = types.InlineKeyboardButton(6, callback_data = "savedlast6")
            item_7 = types.InlineKeyboardButton(7, callback_data = "savedlast7")
            item_8 = types.InlineKeyboardButton(8, callback_data = "savedlast8")
            item_9 = types.InlineKeyboardButton(9, callback_data = "savedlast9")
            item_10 = types.InlineKeyboardButton(10, callback_data = "savedlast10")
            item_11 = types.InlineKeyboardButton(11, callback_data = "savedlast11")
            item_12 = types.InlineKeyboardButton(12, callback_data = "savedlast12")
            item_13 = types.InlineKeyboardButton(13, callback_data = "savedlast13")
            item_14 = types.InlineKeyboardButton(14, callback_data = "savedlast14")
            item_15 = types.InlineKeyboardButton(15, callback_data = "savedlast15")
            item_16 = types.InlineKeyboardButton(16, callback_data = "savedlast16")
            item_17 = types.InlineKeyboardButton(17, callback_data = "savedlast17")
            item_18 = types.InlineKeyboardButton(18, callback_data = "savedlast18")
            item_19 = types.InlineKeyboardButton(19, callback_data = "savedlast19")
            item_20 = types.InlineKeyboardButton(20, callback_data = "savedlast20")
            item_21 = types.InlineKeyboardButton('Отмена', callback_data = "exit4")

            markup.add(item_1, item_2, item_3, item_4, item_5)
            markup.add(item_6, item_7, item_8, item_9, item_10)
            markup.add(item_11, item_12, item_13, item_14, item_15)
            markup.add(item_16, item_17, item_18, item_19, item_20)
            markup.add(item_21)
            await message.answer('Эта команда высылает самые первые (по дате добавления) анекдоты, добавленные Вами в сохранённые.\n\nВыберите количество первых сохр, которые Вы хотите получить:', reply_markup = markup)
    else:
        await message.answer('error in isn')
            
    
    
# activation of saved lag anecs instruction button:
@dp.message_handler(lambda message: message.text.lower() == 'сохра лаг: инструкция')
async def saved_lag_anecs_instruction(message: types.message):
    with general_base1.connection:
        general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (message.chat.id,))
        isn = general_base1.cursor.fetchall()[0][0]
    if isn == 1:
        await message.answer('На данный момент эта команда недоступна так как Вы находитесь в разделе "Начальная инструкция".\n\nЭта команда будет доступна, как только Вы завершите или пропустите начальную инструкцию')
    elif isn == 0:
        with general_base1.connection:
            general_base1.cursor.execute("SELECT COUNT(*) FROM saved_anecs_by_user WHERE user_id = %s AND not_deleted = True", (message.chat.id,))
            ken = general_base1.cursor.fetchall()[0][0]
        if ken < 20:
            with general_base1.connection:
                general_base1.cursor.execute("SELECT subscribed FROM users_sub_best_anec_day WHERE user_id = %s LIMIT 1", (message.chat.id,))
                ku = general_base1.cursor.fetchall()[0][0]
                general_base1.cursor.execute("SELECT in_a_row_started FROM anecs_in_a_row WHERE user_id = %s LIMIT 1", (message.chat.id,))
                status = general_base1.cursor.fetchall()[0][0]
                general_base1.cursor.execute("SELECT subscribed FROM users_sub_random_anec WHERE user_id = %s LIMIT 1", (message.chat.id,))
                kz = general_base1.cursor.fetchall()[0][0]

            #keyboard
            markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
            await main_markup(markup, ku, status, kz)
            await message.answer('Вы cохранили меньше 20 анекдотов. Поэтому, при нажатии на кнопку "Сохранённые Анеки", Вам автоматически будут присылаться все сохранённые Вами анекдоты!', reply_markup = markup)
        else:
            await message.answer('Эта команда позволяет получить все Ваши сохранённые анекдоты за несколько сообщений, если у Вас очень много сохранённых анекдотов (больше, чем 40, например).\n\nКак это работает? Сначала я формирую список из всех Ваших сохранённых анекдотов и сортирую его в порядке убывания по дате добавления (самый последний добавленный анекдот будет первым в списке, а самый первый добавленный анекдот будет последним в списке).\n\nЗатем Ваша очередь выбрать, какие анекдоты из это списка вы хотите. Чтобы команда "сохра лаг" сработала, Вы должны написать мне сообщение в виде "Сохра х лаг y" (без кавычек), где x и y это целые числа. x это число от 0 до 20, которое означает количество анекдотов, которое Вы хотите получить, а y это число от 0 до количества сохранённых Вами анекдотов, оно означает сколько анекдотов я пропущу сначала, в моём списке, который я составил вначале.\n\nЛАЙФХАК: например, если у Вас 100 сохранённых анекдотов, Вы можете получить все эти анекдоты, отправив мне пять сообщений: "Сохра 20 лаг 0", "Сохра 20 лаг 20", "Сохра 20 лаг 40", "Сохра 20 лаг 60" и "Сохра 20 лаг 80".\n\nЧисло Ваших сохранённых анекдотов: {}'.format(ken))
    else:
        await message.answer('error in isn')


        
# activation of saved lag anecs button:
@dp.message_handler(lambda message: 'лаг' in message.text.lower() and message.text.lower()[:5] == 'сохра')
async def saved_lag_anecs_command(message: types.message):
    with general_base1.connection:
        general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (message.chat.id,))
        isn = general_base1.cursor.fetchall()[0][0]
    if isn == 1:
        await message.answer('На данный момент эта команда недоступна так как Вы находитесь в разделе "Начальная инструкция".\n\nЭта команда будет доступна, как только Вы завершите или пропустите начальную инструкцию')
    elif isn == 0:
        with general_base1.connection:
            general_base1.cursor.execute("SELECT COUNT(*) FROM saved_anecs_by_user WHERE user_id = %s AND not_deleted = True", (message.chat.id,))
            ken = general_base1.cursor.fetchall()[0][0]
        if ken < 20:
            with general_base1.connection:
                general_base1.cursor.execute("SELECT subscribed FROM users_sub_best_anec_day WHERE user_id = %s LIMIT 1", (message.chat.id,))
                ku = general_base1.cursor.fetchall()[0][0]
                general_base1.cursor.execute("SELECT in_a_row_started FROM anecs_in_a_row WHERE user_id = %s LIMIT 1", (message.chat.id,))
                status = general_base1.cursor.fetchall()[0][0]
                general_base1.cursor.execute("SELECT subscribed FROM users_sub_random_anec WHERE user_id = %s LIMIT 1", (message.chat.id,))
                kz = general_base1.cursor.fetchall()[0][0]

            #keyboard
            markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
            await main_markup(markup, ku, status, kz)
            await message.answer('Вы cохранили меньше 20 анекдотов. Поэтому, при нажатии на кнопку "Сохранённые Анеки", Вам автоматически будут присылаться все сохранённые Вами анекдоты!', reply_markup = markup)
        else:
            try:
                num = int(message.text.split('лаг')[0][5:].strip())
                lag = int(message.text.split('лаг')[1].strip())
                if num < 0 or lag < 0:
                    await message.answer('Эта команда не работает с отрицательными числами.\nПервое число в этой команде должно быть больше 0, а второе должно быть больше либо равно 0\nИсправьте число(-а) и пропишите эту команду заново')
                elif num == 0:
                    await message.answer('Первое число должно быть больше 0, иначе Вы получите 0 анекдотов...\nИсправьте число и пропишите эту команду заново')
                elif num > 20:
                    await message.answer('За один раз я не могу выслать больше 20 сохранённых анекдотов, поэтому первое число в этой команде должно быть не больше 20\nИсправьте число и пропишите эту команду заново')
                else:
                    if ken <= lag:
                        await message.answer('Введённый Вами лаг (второе число: {}) больше либо равен количеству сохранённых Вами анекдотов (Количество сохранёнок: {}). Второе число в этой команде должно быть строго меньше, чем количество сохрвнённых анекдотов.\nИсправьте число и пропишите эту команду заново'.format(lag, ken))
                    else:
                        if lag == 0:
                            if num == 1:
                                await message.answer('Вы ввели нулевой лаг (второе число: {}), поэтому высылаю Вам самый последний добавленный анекдот'.format(lag))
                            elif num in [2, 3, 4]:
                                await message.answer('Вы ввели нулевой лаг (второе число: {}), поэтому высылаю Вам {} последних добавленных анекдота'.format(lag, num))
                            else:
                                await message.answer('Вы ввели нулевой лаг (второе число: {}), поэтому высылаю Вам {} последних добавленных анекдотов'.format(lag, num))

                        elif num + lag > ken:
                            if ken - lag == 1:
                                await message.answer('Учитывая введённый лаг (второе число: {}), бот пропускает это количество анекдотов. В этом случае остаётся {} самый первый добавленный анекдотов (это меньше, чем введённое Вами первое число {}. Высылаю вам самый первый сохранённый анекдот'.format(lag, ken - lag, num))
                            elif ken - lag in [2, 3, 4]:
                                await message.answer('Учитывая введённый лаг (второе число: {}), бот пропускает это количество анекдотов. В этом случае остаётся {} самых первых добавленных анекдота (это меньше, чем введённое Вами первое число {}. Высылаю вам {} первых сохранённых анедкота'.format(lag, ken - lag, num , ken - lag))
                            else:    
                                await message.answer('Учитывая введённый лаг (второе число: {}), бот пропускает это количество анекдотов. В этом случае остаётся {} самых первых добавленных анекдотов (это меньше, чем введённое Вами первое число {}. Высылаю вам {} первых сохранённых анедкотов'.format(lag, ken - lag, num , ken - lag))
                        else:
                            if lag % 10 == 1 and (lag // 10) % 10 != 1:
                                if num == 1:
                                    await message.answer('Сортирую анекдоты по дате сохранения в порядке убывания, пропускаю {} анекдот и высылаю следующую по порядку сохранёнку'.format(lag))
                                elif num in [2, 3, 4]:
                                    await message.answer('Сортирую анекдоты по дате сохранения в порядке убывания, пропускаю {} анекдот и высылаю {} следующие по порядку сохранёнки'.format(lag, num))
                                else:
                                    await message.answer('Сортирую анекдоты по дате сохранения в порядке убывания, пропускаю {} анекдот и высылаю {} следующих по порядку сохранёнок'.format(lag, num))
                            elif lag % 10 in [2, 3, 4] and (lag // 10) % 10 != 1:
                                if num == 1:
                                    await message.answer('Сортирую анекдоты по дате сохранения в порядке убывания, пропускаю {} анекдота и высылаю следующую по порядку сохранёнку'.format(lag))
                                elif num in [2, 3, 4]:
                                    await message.answer('Сортирую анекдоты по дате сохранения в порядке убывания, пропускаю {} анекдота и высылаю {} следующие по порядку сохранёнки'.format(lag, num))
                                else:
                                    await message.answer('Сортирую анекдоты по дате сохранения в порядке убывания, пропускаю {} анекдота и высылаю {} следующих по порядку сохранёнок'.format(lag, num))
                            else:
                                if num == 1:
                                    await message.answer('Сортирую анекдоты по дате сохранения в порядке убывания, пропускаю {} анекдотов и высылаю следующую по порядку сохранёнку'.format(lag))
                                elif num in [2, 3, 4]:
                                    await message.answer('Сортирую анекдоты по дате сохранения в порядке убывания, пропускаю {} анекдотов и высылаю {} следующие по порядку сохранёнки'.format(lag, num))
                                else:
                                    await message.answer('Сортирую анекдоты по дате сохранения в порядке убывания, пропускаю {} анекдотов и высылаю {} следующих по порядку сохранёнок'.format(lag, num))
                        #sending sohra lag anecs finally:
                        await asyncio.sleep(1)
                        with general_base1.connection:
                            general_base1.cursor.execute("SELECT cluster_num, id_entry, anec_text, source, epoch_time_added FROM saved_anecs_by_user AS sabu INNER JOIN anecdotes_general_table AS agt ON sabu.id_anec = agt.id_entry WHERE user_id = %s AND not_deleted = True ORDER BY epoch_time_added DESC LIMIT %s OFFSET %s", (message.chat.id, min(num, ken - lag), lag))
                            duta = general_base1.cursor.fetchall()

                        markup = types.InlineKeyboardMarkup(row_width = 2)
                        item_1 = types.InlineKeyboardButton("Удалить Анек из \"Сохранённых\"", callback_data = 'delete_saved')
                        markup.add(item_1)

                        for i in range(min(num, ken - lag)):
                            final = '{}) ID: {}-{}\n***anecbot***\n\n{}\n\nИстoчник: {}\nДата сохранения Анека: {}'.format(lag + i + 1, duta[i][0], duta[i][1], duta[i][2], duta[i][3], datetime.fromtimestamp(duta[i][4]).strftime('%Y-%m-%d')) 
                            if len(final) <= 4096:
                                await message.answer(final, reply_markup = markup)  
                            else:
                                for x in range(0, len(final) - 4096, 4096):
                                    await message.answer(final[x : x + 4096])
                                k = len(final)//4096
                                await message.answer('{}) ID: {}-{}\n***anecbot***\n\n'.format(lag + i + 1, duta[i][0], duta[i][1]) + final[k * 4096 : k * 4096 + 4096], reply_markup = markup)       

            except ValueError as v:
                await message.answer('Не получилось обработать команду. Проверьте, что Вы напечатали ровно одно целое число между словами "Сохра" и "Лаг", а также ровно одно целое число после слова "Лаг"\nПропишите эту команду заново')
    else:
        await message.answer('error in isn')
    
    
    
# activation of find saved anecs by word instruction button:
@dp.message_handler(lambda message: message.text.lower() == 'найти сохру по слову: инструкция')
async def find_saved_by_word_instruction(message: types.message):
    with general_base1.connection:
        general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (message.chat.id,))
        isn = general_base1.cursor.fetchall()[0][0]
    if isn == 1:
        await message.answer('На данный момент эта команда недоступна так как Вы находитесь в разделе "Начальная инструкция".\n\nЭта команда будет доступна, как только Вы завершите или пропустите начальную инструкцию')
    elif isn == 0:
        with general_base1.connection:
            general_base1.cursor.execute("SELECT COUNT(*) FROM saved_anecs_by_user WHERE user_id = %s AND not_deleted = True", (message.chat.id,))
            ken = general_base1.cursor.fetchall()[0][0]
        if ken < 20:
            with general_base1.connection:
                general_base1.cursor.execute("SELECT subscribed FROM users_sub_best_anec_day WHERE user_id = %s LIMIT 1", (message.chat.id,))
                ku = general_base1.cursor.fetchall()[0][0]
                general_base1.cursor.execute("SELECT in_a_row_started FROM anecs_in_a_row WHERE user_id = %s LIMIT 1", (message.chat.id,))
                status = general_base1.cursor.fetchall()[0][0]
                general_base1.cursor.execute("SELECT subscribed FROM users_sub_random_anec WHERE user_id = %s LIMIT 1", (message.chat.id,))
                kz = general_base1.cursor.fetchall()[0][0]

            #keyboard
            markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
            await main_markup(markup, ku, status, kz)
            await message.answer('Вы cохранили меньше 20 анекдотов. Поэтому, при нажатии на кнопку "Сохранённые Анеки", Вам автоматически будут присылаться все сохранённые Вами анекдоты!', reply_markup = markup)
        else:
            await message.answer('Механизм поиска сохранённого анекдота похож на поиск анекдотов по слову из всей моей базы!\nНапишите мне "Найти сохра" (без кавычек) и потом своё(-и) слово(-а) через пробел, чтобы я выслал Вам все Ваши сохранённые анекдоты, которые содержат указанные(-ое) Вами слова!')
    else:
        await message.answer('error in isn')
            


# activation of find saved anecs by word button:
@dp.message_handler(lambda message: message.text.lower()[:11] == 'найти сохра')
async def find_saved_by_word_command(message: types.message): 
    with general_base1.connection:
        general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (message.chat.id,))
        isn = general_base1.cursor.fetchall()[0][0]
    if isn == 1:
        await message.answer('На данный момент эта команда недоступна так как Вы находитесь в разделе "Начальная инструкция".\n\nЭта команда будет доступна, как только Вы завершите или пропустите начальную инструкцию')
    elif isn == 0:
        with general_base1.connection:
            general_base1.cursor.execute("SELECT COUNT(*) FROM saved_anecs_by_user WHERE user_id = %s AND not_deleted = True", (message.chat.id,))
            ken = general_base1.cursor.fetchall()[0][0]
        if ken < 20:
            with general_base1.connection:
                general_base1.cursor.execute("SELECT subscribed FROM users_sub_best_anec_day WHERE user_id = %s LIMIT 1", (message.chat.id,))
                ku = general_base1.cursor.fetchall()[0][0]
                general_base1.cursor.execute("SELECT in_a_row_started FROM anecs_in_a_row WHERE user_id = %s LIMIT 1", (message.chat.id,))
                status = general_base1.cursor.fetchall()[0][0]
                general_base1.cursor.execute("SELECT subscribed FROM users_sub_random_anec WHERE user_id = %s LIMIT 1", (message.chat.id,))
                kz = general_base1.cursor.fetchall()[0][0]

            #keyboard
            markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
            await main_markup(markup, ku, status, kz)
            await message.answer('Вы cохранили меньше 20 анекдотов. Поэтому, при нажатии на кнопку "Сохранённые Анеки", Вам автоматически будут присылаться все сохранённые Вами анекдоты!', reply_markup = markup)

        else:
            y = message['text'][11:].strip() 
            if len(y) > 250:
                await message.answer('Вы ввели слишком много слов для поиска анекдота!\n\nСократите количество слов, чтобы я начал искать анекдоты, содержащие эту последовательность из слов!')   
            elif y == '':
                await message.answer('Вы не написали слово. Напишите слово после команды "Найти сохра", чтобы выбрать слово, по которому искать сохранёнку(-и).')
            else:
                await message.answer('Процесс поиска может занять некоторое время, подождите...')
                word_raw_nlp = nlp(y)
                lemmas = [token.lemma_ for token in word_raw_nlp]
                a_lemmas = [lemma for lemma in lemmas if lemma.isalpha() or lemma == '-PRON-']
                word_clean = ' '.join(a_lemmas)
                markup = types.InlineKeyboardMarkup(row_width = 2)
                item_1 = types.InlineKeyboardButton("Удалить Анек из \"Сохранённых\"", callback_data = 'delete_saved')
                markup.add(item_1)

                with general_base1.connection:
                    general_base1.cursor.execute("SELECT cluster_num, id_entry, anec_text, source, epoch_time_added, anec_cl FROM saved_anecs_by_user AS sabu INNER JOIN anecdotes_general_table AS agt ON sabu.id_anec = agt.id_entry WHERE user_id = %(user_id)s AND not_deleted = True AND anec_cl LIKE %(word)s ORDER BY epoch_time_added DESC", {'user_id': message.chat.id, 'word': '%{}%'.format(word_clean)})
                    dalta = general_base1.cursor.fetchall()

                if dalta == []:
                    await message.answer('Не удалось найти сохранёнку с этим словом. Выберите другое слово и напишите его после фразы "Найти сохра"')        
                elif len(dalta) <= 20:
                    await message.answer('Количество сохранёнок со словом {}: {}\nВысылаю все эти анекдоты в порядке убывания даты сохранения (от позднего к раннему):'.format(y, len(dalta)))
                    await asyncio.sleep(1)
                    for i in range(len(dalta)):
                        final = '{}) ID: {}-{}\n***anecbot***\n\n{}\n\nИстoчник: {}\nДата сохранения Анека: {}'.format(i + 1, dalta[i][0], dalta[i][1], dalta[i][2], dalta[i][3], datetime.fromtimestamp(dalta[i][4]).strftime('%Y-%m-%d')) 
                        if len(final) <= 4096:
                            await message.answer(final, reply_markup = markup)  
                        else:
                            for x in range(0, len(final) - 4096, 4096):
                                await message.answer(final[x : x + 4096])
                            k = len(final)//4096
                            await message.answer('{}) ID: {}-{}\n***anecbot***\n\n'.format(i + 1, dalta[i][0], dalta[i][1]) + final[k * 4096 : k * 4096 + 4096], reply_markup = markup)                                     
                else:
                    await message.answer('Количество сохранёнок со словом "{}": {}\nЯ могу прислать максимум 20 сохранёнок, поэтому высылаю 20 сохранёнок с этим словом, выбранных из {} случайным образом\n\nТакже вы можете написать больше слов после фразы "Найти сохра", чтобы сузить поиск!'.format(y, len(dalta), len(dalta)))
                    kasu = np.random.choice(range(len(dalta)), 20, replace = False)
                    await asyncio.sleep(1)
                    j = 1
                    for i in kasu:
                        final = '{}) ID: {}-{}\n***anecbot***\n\n{}\n\nИстoчник: {}\nДата сохранения Анека: {}'.format(j , dalta[i][0], dalta[i][1], dalta[i][2], dalta[i][3], datetime.fromtimestamp(dalta[i][4]).strftime('%Y-%m-%d')) 
                        if len(final) <= 4096:
                            await message.answer(final, reply_markup = markup)  
                        else:
                            for x in range(0, len(final) - 4096, 4096):
                                await message.answer(final[x : x + 4096])
                            k = len(final)//4096
                            await message.answer('{}) ID: {}-{}\n***anecbot***\n\n'.format(j, dalta[i][0], dalta[i][1]) + final[k * 4096 : k * 4096 + 4096], reply_markup = markup) 
                        j += 1
    else:
        await message.answer('error in isn')
                        
                             
                             
# activation of number of saved anecs button:
@dp.message_handler(lambda message: message.text.lower() == 'количество сохр')
async def number_of_saved(message: types.message):
    with general_base1.connection:
        general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (message.chat.id,))
        isn = general_base1.cursor.fetchall()[0][0]
    if isn == 1:
        await message.answer('На данный момент эта команда недоступна так как Вы находитесь в разделе "Начальная инструкция".\n\nЭта команда будет доступна, как только Вы завершите или пропустите начальную инструкцию')
    elif isn == 0:
        with general_base1.connection:
            general_base1.cursor.execute("SELECT COUNT(*) FROM saved_anecs_by_user WHERE user_id = %s AND not_deleted = True", (message.chat.id,))
            ken = general_base1.cursor.fetchall()[0][0]
        await message.answer('Количество сохранённых анекдотов: {}'.format(ken))
    else:
        await message.answer('error in isn')
        
                                        
                                        
# activation of saved anecs button:
@dp.message_handler(lambda message: message.text.lower() == 'последние 5 удалённых сохранёнок' or message.text.lower() == 'последние 5 удалённых сохр')
async def last_five_deleted_saved_anecs(message: types.message):
    with general_base1.connection:
        general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (message.chat.id,))
        isn = general_base1.cursor.fetchall()[0][0]
    if isn == 1:
        await message.answer('На данный момент эта команда недоступна так как Вы находитесь в разделе "Начальная инструкция".\n\nЭта команда будет доступна, как только Вы завершите или пропустите начальную инструкцию')
    elif isn == 0:
        with general_base1.connection:
            general_base1.cursor.execute("SELECT COUNT(*) FROM saved_anecs_by_user WHERE user_id = %s AND not_deleted = False", (message.chat.id,))
            kus = general_base1.cursor.fetchall()[0][0]

            general_base1.cursor.execute("SELECT cluster_num, id_entry, anec_text, source, epoch_time_deleted FROM saved_deleted_anecs_by_user AS sdabu INNER JOIN anecdotes_general_table AS agt ON sdabu.id_anec = agt.id_entry WHERE user_id = %s ORDER BY epoch_time_deleted DESC LIMIT 5", (message.chat.id,))
            dita = general_base1.cursor.fetchall()
        if kus == 0:
            await message.answer('На данный момент у Вас нет анекдотов, удалённых из "Сохранённых".\nУдалить сохранённый анекдот, можно в любой момент, когда Вы его получаете.\nСначала, нажимайте на кнопку "Добавить в "Сохранённые"" под анекдотом, чтобы сохранить анекдот. Если у Вас меньше 20 сохранённых анекдотов, Вы можете получить все Ваши сохранённые анекдоты, нажав на кнопку "Сохранённые Анеки". Если у Вас 20 сохранёнок и больше, нажимайте на эту же кнопку и получайте Ваши сохранёнки нажимая новые появившиеся кнопки на клавиатуре!')
        elif kus > 0:
            markup = types.InlineKeyboardMarkup(row_width = 2)
            item_1 = types.InlineKeyboardButton("Добавить в \"Сохранённые\" обратно", callback_data = 'recover_saved')
            markup.add(item_1)
            if kus == 1:
                await message.answer('Всего Вы удалили из сохранённых 1 анекдот. Высылаю Вам этот анекдот')
            elif kus in [2, 3, 4]:
                await message.answer('Всего Вы удалили из сохранённых {} анекдота. Высылаю Вам все эти анекдоты'.format(kus))
            elif kus == 5:
                await message.answer('Всего Вы удалили из сохранённых 5 анекдотов. Высылаю Вам все эти анекдоты')
            elif kus > 5:
                await message.answer('Высылаю Вам последние 5 удалённых Вами анекдотов из сохранённых!')
            await asyncio.sleep(1)
            for i in range(len(dita)):
                final = '{}) ID: {}-{}\n***anecbot***\n\n{}\n\nИстoчник: {}\nДата Удаления из сохранёнок: {}'.format(i + 1, dita[i][0], dita[i][1], dita[i][2], dita[i][3], datetime.fromtimestamp(dita[i][4]).strftime('%Y-%m-%d')) 
                if len(final) <= 4096:
                    await message.answer(final, reply_markup = markup)  
                else:
                    for x in range(0, len(final) - 4096, 4096):
                        await message.answer(final[x : x + 4096])
                    k = len(final)//4096
                    await message.answer('ID: {}-{}\n***anecbot***\n\n'.format(dita[i][0], dita[i][1]) + final[k * 4096 : k * 4096 + 4096], reply_markup = markup)   
        else:
            await message.answer('error in kus')
    else:
        await message.answer('error in isn')
 


 # activation of skipping start instruction button:
@dp.message_handler(lambda message: message.text.lower() == 'пропустить начальную инструкцию')
async def skipping_start_instruction(message: types.message):
    with general_base1.connection:
        general_base1.cursor.execute("SELECT is_novice FROM user_novice_or_not WHERE user_id = %s", (message.chat.id,))
        isn = general_base1.cursor.fetchall()[0][0]
    if isn == 0:
        await message.answer('Вы и так уже не находитесь в начальной инструкции!')
    elif isn == 1:
        markup = types.InlineKeyboardMarkup(row_width = 2)
        item_1 = types.InlineKeyboardButton("Да", callback_data = 'skip_intro')
        item_2 = types.InlineKeyboardButton('Отмена', callback_data = 'not_skip_intro')
        markup.add(item_1, item_2)
        await message.answer('Вы действительно хотите пропустить изначальную инструкцию? (Если Вы новый пользователь, то я не рекомендую это делать!)', reply_markup = markup)
    else:
        await message.answer('error in isn')


        
 # main markup
async def main_markup(markup, ku, status, kz):    
    #keyboard
    item1 = types.KeyboardButton("Анек")
    item2 = types.KeyboardButton("10 Анеков")
    item3 = types.KeyboardButton("Много Анеков")
    if status == 0:   
        item4 = types.KeyboardButton("СТАРТ Анеки подряд")
    elif status == 1:
        item4 = types.KeyboardButton("СТОП Анеки подряд")
    else:
        item4 = types.KeyboardButton("error")
    item10 = types.KeyboardButton("Сохранённые Анеки")
    item5 = types.KeyboardButton("Выбор источников")
    item6 = types.KeyboardButton("Поиск Анека по слову: инструкция")
    item7 = types.KeyboardButton("Список источников")
    item8 = types.KeyboardButton("help")
    if ku == 0:
        item9 = types.KeyboardButton("Анек дня: подписаться")
    elif ku == 1:
        item9 = types.KeyboardButton("Анек дня: отписаться")
    else:
        await message.answer('error in ku')
    if kz == 0:
        item12 = types.KeyboardButton("Рандомный Анек: подписаться")
    elif kz == 1:
        item12 = types.KeyboardButton("Рандомный Анек: отписаться")
    else:
        await message.answer('error in kz')
    item11 = types.KeyboardButton('Последние 5 удалённых сохранёнок')
    markup.add(item1, item2) 
    markup.add(item3, item4)
    markup.add(item10, item5)
    markup.add(item6)
    markup.add(item7, item8)
    markup.add(item9)
    markup.add(item12)
    markup.add(item11)
    
 
    
# function which sends at most top 5 anecs of the day to the telegram channel!!!! And poll to vote for top1!!!
async def anec_of_day_top5_to_channel(): 
    td = timedelta(days = 1)
    # add td back!!!!!! subtract td in date_to_use!!!!
    date_to_use = (datetime.now() - td).strftime('%Y-%m-%d')
    date_in_messages = datetime.now().strftime('%Y-%m-%d')
    with general_base1.connection:
        general_base1.cursor.execute("SELECT id_entry_from_general_base, AVG(rating) as avg FROM users_history WHERE date_feedback = %s GROUP BY id_entry_from_general_base ORDER BY avg desc LIMIT 5", (date_to_use,))
        data = general_base1.cursor.fetchall()
    
    # when no one marked anecdotes
    if len(data) == 0:
        await bot.send_message(id_of_channel, 'Cегодня ({}) не нашлось ни одного претендента на звание "Анек Дня".\nОценивайте анекдоты в AnecBot (@bot_anecbot), чтобы в следующие дни появлялись претенденты!'.format(date_in_messages), disable_notification = True)
        with general_base1.connection:
            general_base1.cursor.execute("SELECT user_id from users_sub_best_anec_day WHERE subscribed = True")
            keka = general_base1.cursor.fetchall()
        kan = 0
        for i in range(len(keka)):
            try:
                await bot.send_message(keka[i][0], 'Cегодня ({}) не нашлось ни одного претендента на звание "Анек Дня".\nОценивайте анекдоты в боте и голосуйте за анекдот дня на канале AnecBot channel (t.me/anecbot_channel), чтобы в следующие дни появлялись анекдоты дня!'.format(date_in_messages), disable_notification = True)
            except:
                print('cannot send to one of the chats in the table (user or chat no longer use the bot)')
                kan += 1
        await bot.send_message(my_id, 'Количество чатов, куда не прислали, что нет анека дня: {} из {}'.format(kan, len(keka)))
    # when only one anecdote is marked
    elif len(data) == 1:
        general_base1.add_anec_of_the_day_to_anec_of_day_table(data[0][0], date_in_messages, 1)
        with general_base1.connection:
            general_base1.cursor.execute("SELECT anec_text, source, cluster_num, date FROM anecdotes_general_table WHERE id_entry = %s LIMIT 1", (data[0][0],))
            data_one = general_base1.cursor.fetchall()
            
        final_mes = 'АНЕК ДНЯ: {}\nID: {}\n***anecbot***\n\n{}\n\nИсточник: {}'.format(date_in_messages, data[0][0], data_one[0][0], data_one[0][1])
        final_mes_sub = 'АНЕК ДНЯ: {}\nID: {}-{}\n***anecbot***\n\n{}\n\nИстoчник: {}\nДата oпубликования в источнике: {}\n\nОцените анекдот:'.format(date_in_messages, data_one[0][2], data[0][0], data_one[0][0], data_one[0][1], data_one[0][3])
        # send to channel
        if len(final_mes) <= 4096:
            await bot.send_message(id_of_channel, final_mes, disable_notification = True) 
        else:
            for x in range(0, len(final_mes) - 4096, 4096):
                await bot.send_message(id_of_channel, final_mes[x : x + 4096], disable_notification = True)
            k = len(final_mes)//4096
            await bot.send_message(id_of_channel, final_mes[k * 4096 : k * 4096 + 4096], disable_notification = True)
        await bot.send_message(id_of_channel, 'Сегодня ({}) нашёлся только один претендент на звание "Анек Дня". Этот анекдот-победитель опубликовался сообщением выше. Оценивайте анекдоты в AnecBot (@bot_anecbot), чтобы в следующие дни появлялось больше претендентов на это звание! Также, все, кто подписан на получения анекдота дня в Anecbot, могут лично оценить "Анек Дня", так как бот лично пришлёт Вам этот анекдот!'.format(date_in_messages), disable_notification = True)
        # send anec of day to subscribers
        with general_base1.connection:
            general_base1.cursor.execute("SELECT user_id from users_sub_best_anec_day WHERE subscribed = True")
            keka = general_base1.cursor.fetchall()
        kan = 0
        for i in range(len(keka)):
            try:
                await bot.send_message(keka[i][0], 'Сегодня ({}) нашёлся только один претендент на звание "Анек Дня". Этот анекдот-победитель опубликуется сообщением ниже'.format(date_in_messages), disable_notification = True)
                if len(final_mes_sub) <= 4096:
                    await bot.send_message(keka[i][0], final_mes_sub, disable_notification = True) 
                else:
                    for x in range(0, len(final_mes_sub) - 4096, 4096):
                        await bot.send_message(keka[i][0], final_mes_sub[x : x + 4096], disable_notification = True)
                    k = len(final_mes_sub)//4096
                    await bot.send_message(keka[i][0], 'ID: {}-{}\n***anecbot***\n\n'.format(chosen_cluster, id_entry) + final_mes_sub[k * 4096 : k * 4096 + 4096], disable_notification = True)
                await bot.send_message(keka[i][0], 'Оценивайте анекдоты в этом боте и голосуйте за лучший анекдот в опросах на канале AnecBot channel (t.me/anecbot_channel), чтобы в следующие дни появлялось больше претендентов на это звание!', disable_notification = True)
            except:
                print('cannot send to one of the chats in the table (user or chat no longer use the bot)')
                kan += 1
        await bot.send_message(my_id, 'Количество чатов, куда не прислали анек дня: {} из {}'.format(kan, len(keka)))
    # when more than one anecdote is marked!
    else:
        if len(data) < 5:
            await bot.send_message(id_of_channel, 'Сегодня ({}) нашлось {} претендента на звание "Анек Дня". Анекдоты-претенденты опубликуются в сообщениях ниже. Оценивайте анекдоты в AnecBot (@bot_anecbot), чтобы в следующие дни появлялось больше претендентов на это звание!'.format(date_in_messages, len(data)), disable_notification = True)
        elif len(data) == 5:
            await bot.send_message(id_of_channel, 'Сегодня ({}) нашлось 5 претендентов на звание "Анек Дня". Анекдоты-претенденты опубликуются в сообщениях ниже. Оценивайте анекдоты в AnecBot (@bot_anecbot), чтобы в следующие дни тоже появлялись претенденты на это звание!'.format(date_in_messages), disable_notification = True)
        else:
            await bot.send_message(id_of_channel, 'error in data len', disable_notification = True)
        # first pretender
        with general_base1.connection:
            general_base1.cursor.execute("SELECT anec_text, source FROM anecdotes_general_table WHERE id_entry = %s LIMIT 1", (data[0][0],))
            data_first = general_base1.cursor.fetchall()
            
        final_mes1 = 'ПЕРВЫЙ ПРЕТЕНДЕНТ: {}\nID: {}\n***anecbot***\n\n{}\n\nИсточник: {}'.format(date_in_messages, data[0][0], data_first[0][0], data_first[0][1])
        if len(final_mes1) <= 4096:
            await bot.send_message(id_of_channel, final_mes1, disable_notification = True) 
        else:
            for x in range(0, len(final_mes1) - 4096, 4096):
                await bot.send_message(id_of_channel, final_mes1[x : x + 4096], disable_notification = True)
            k = len(final_mes1)//4096
            await bot.send_message(id_of_channel, final_mes1[k * 4096 : k * 4096 + 4096], disable_notification = True)
        # second pretender
        with general_base1.connection:
            general_base1.cursor.execute("SELECT anec_text, source FROM anecdotes_general_table WHERE id_entry = %s LIMIT 1", (data[1][0],))
            data_second = general_base1.cursor.fetchall()
            
        final_mes2 = 'ВТОРОЙ ПРЕТЕНДЕНТ: {}\nID: {}\n***anecbot***\n\n{}\n\nИсточник: {}'.format(date_in_messages, data[1][0], data_second[0][0], data_second[0][1])
        if len(final_mes2) <= 4096:
            await bot.send_message(id_of_channel, final_mes2, disable_notification = True) 
        else:
            for x in range(0, len(final_mes2) - 4096, 4096):
                await bot.send_message(id_of_channel, final_mes2[x : x + 4096], disable_notification = True)
            k = len(final_mes2)//4096
            await bot.send_message(id_of_channel, final_mes2[k * 4096 : k * 4096 + 4096], disable_notification = True)
        # third pretender: if exists:
        if len(data) >= 3:
            with general_base1.connection:
                general_base1.cursor.execute("SELECT anec_text, source FROM anecdotes_general_table WHERE id_entry = %s LIMIT 1", (data[2][0],))
                data_third = general_base1.cursor.fetchall()
                
            final_mes3 = 'ТРЕТИЙ ПРЕТЕНДЕНТ: {}\nID: {}\n***anecbot***\n\n{}\n\nИсточник: {}'.format(date_in_messages, data[2][0], data_third[0][0], data_third[0][1])
            if len(final_mes3) <= 4096:
                await bot.send_message(id_of_channel, final_mes3, disable_notification = True) 
            else:
                for x in range(0, len(final_mes3) - 4096, 4096):
                    await bot.send_message(id_of_channel, final_mes3[x : x + 4096], disable_notification = True)
                k = len(final_mes3)//4096
                await bot.send_message(id_of_channel, final_mes3[k * 4096 : k * 4096 + 4096], disable_notification = True)
            # fourth pretender: if exists:
            if len(data) >= 4:
                with general_base1.connection:
                    general_base1.cursor.execute("SELECT anec_text, source FROM anecdotes_general_table WHERE id_entry = %s LIMIT 1", (data[3][0],))
                    data_fourth = general_base1.cursor.fetchall()
                    
                final_mes4 = 'ЧЕТВЕРТЫЙ ПРЕТЕНДЕНТ: {}\nID: {}\n***anecbot***\n\n{}\n\nИсточник: {}'.format(date_in_messages, data[3][0], data_fourth[0][0], data_fourth[0][1])
                if len(final_mes4) <= 4096:
                    await bot.send_message(id_of_channel, final_mes4, disable_notification = True) 
                else:
                    for x in range(0, len(final_mes4) - 4096, 4096):
                        await bot.send_message(id_of_channel, final_mes4[x : x + 4096], disable_notification = True)
                    k = len(final_mes4)//4096
                    await bot.send_message(id_of_channel, final_mes4[k * 4096 : k * 4096 + 4096], disable_notification = True)
                #fifth pretender: if exists:
                if len(data) == 5:
                    with general_base1.connection:
                        general_base1.cursor.execute("SELECT anec_text, source FROM anecdotes_general_table WHERE id_entry = %s LIMIT 1", (data[4][0],))
                        data_fifth = general_base1.cursor.fetchall()
                    
                    final_mes5 = 'ПЯТЫЙ ПРЕТЕНДЕНТ: {}\nID: {}\n***anecbot***\n\n{}\n\nИсточник: {}'.format(date_in_messages, data[4][0], data_fifth[0][0], data_fifth[0][1])
                    if len(final_mes5) <= 4096:
                        await bot.send_message(id_of_channel, final_mes5, disable_notification = True) 
                    else:
                        for x in range(0, len(final_mes5) - 4096, 4096):
                            await bot.send_message(id_of_channel, final_mes5[x : x + 4096], disable_notification = True)
                        k = len(final_mes5)//4096
                        await bot.send_message(id_of_channel, final_mes5[k * 4096 : k * 4096 + 4096], disable_notification = True)
                    # poll if 5 pretenders
                    # you can modify the poll here and do the same for other cases!!!
                    mese = await bot.send_poll(id_of_channel, 'Какой из претендентов Вам понравился больше всего?', ['ПЕРВЫЙ (ID: {})'.format(data[0][0]), 'ВТОРОЙ (ID: {})'.format(data[1][0]), 'ТРЕТИЙ (ID: {})'.format(data[2][0]), 'ЧЕТВЕРТЫЙ (ID: {})'.format(data[3][0]), 'ПЯТЫЙ (ID: {})'.format(data[4][0])], disable_notification = True)
                    general_base1.delete_previous_message_id_from_id_of_poll_message_by_day_current()
                    general_base1.add_message_id_to_two_tables_of_id_of_poll_message_by_day(date_in_messages, mese['message_id'])
                #poll if 4 pretenders
                else:
                    mese = await bot.send_poll(id_of_channel, 'Какой из претендентов Вам понравился больше всего?', ['ПЕРВЫЙ (ID: {})'.format(data[0][0]), 'ВТОРОЙ (ID: {})'.format(data[1][0]), 'ТРЕТИЙ (ID: {})'.format(data[2][0]), 'ЧЕТВЕРТЫЙ (ID: {})'.format(data[3][0])], disable_notification = True)
                    general_base1.delete_previous_message_id_from_id_of_poll_message_by_day_current()
                    general_base1.add_message_id_to_two_tables_of_id_of_poll_message_by_day(date_in_messages, mese['message_id'])
            # poll if 3 pretenders
            else:
                mese = await bot.send_poll(id_of_channel, 'Какой из претендентов Вам понравился больше всего?', ['ПЕРВЫЙ (ID: {})'.format(data[0][0]), 'ВТОРОЙ (ID: {})'.format(data[1][0]), 'ТРЕТИЙ (ID: {})'.format(data[2][0])], disable_notification = True)
                general_base1.delete_previous_message_id_from_id_of_poll_message_by_day_current()
                general_base1.add_message_id_to_two_tables_of_id_of_poll_message_by_day(date_in_messages, mese['message_id'])
        # poll if 2 pretenders
        else:
            mese = await bot.send_poll(id_of_channel, 'Какой из претендентов Вам понравился больше всего?', ['ПЕРВЫЙ (ID: {})'.format(data[0][0]), 'ВТОРОЙ (ID: {})'.format(data[1][0])], disable_notification = True)
            general_base1.delete_previous_message_id_from_id_of_poll_message_by_day_current()
            general_base1.add_message_id_to_two_tables_of_id_of_poll_message_by_day(date_in_messages, mese['message_id'])
            
            
# function to send anecs of the day to users, considering that some anecs > 4096 characters long!
async def anec_of_day_sender(receiver_id, final_mes, markup, chosen_cluster, id_entry):    
    if len(final_mes) <= 4096:
        await bot.send_message(receiver_id, final_mes, disable_notification = True, reply_markup = markup) 
    else:
        for x in range(0, len(final_mes) - 4096, 4096):
            await bot.send_message(receiver_id, final_mes[x : x + 4096], disable_notification = True)
        k = len(final_mes)//4096
        await bot.send_message(receiver_id, 'ID: {}-{}\n***anecbot***\n\n'.format(chosen_cluster, id_entry) + final_mes[k * 4096 : k * 4096 + 4096], disable_notification = True, reply_markup = markup)
    
           
    
# function which sends anec of the day to all users, who subscribed:
async def anec_of_day_sender_general():
    # this is the evening part, when poll is stoped and then the anec of the day is shown
    td = timedelta(days = 1)
    date_to_use = (datetime.now() - td).strftime('%Y-%m-%d')
    date_in_messages = datetime.now().strftime('%Y-%m-%d')
    with general_base1.connection:
        general_base1.cursor.execute("SELECT user_id from users_sub_best_anec_day WHERE subscribed = True")
        keka = general_base1.cursor.fetchall()    
    markup = types.InlineKeyboardMarkup(row_width = 10)
    item_1 = types.InlineKeyboardButton(1, callback_data = "mark 1")
    item_2 = types.InlineKeyboardButton(2, callback_data = "mark 2")
    item_3 = types.InlineKeyboardButton(3, callback_data = "mark 3")
    item_4 = types.InlineKeyboardButton(4, callback_data = "mark 4")
    item_5 = types.InlineKeyboardButton(5, callback_data = "mark 5")
    item_6 = types.InlineKeyboardButton(6, callback_data = "mark 6")
    item_7 = types.InlineKeyboardButton(7, callback_data = "mark 7")
    item_8 = types.InlineKeyboardButton(8, callback_data = "mark 8")
    item_9 = types.InlineKeyboardButton(9, callback_data = "mark 9")
    item_10 = types.InlineKeyboardButton(10, callback_data = "mark 10")
    item_11 = types.InlineKeyboardButton('Добавить в "Сохранённые"', callback_data = "add_to_save")
    markup.add(item_1, item_2, item_3, item_4, item_5)
    markup.add(item_6, item_7, item_8, item_9, item_10)
    markup.add(item_11)
    
    with general_base1.connection:
        general_base1.cursor.execute("SELECT * FROM id_of_poll_message_by_day_current WHERE date = %s", (date_in_messages,))
        ca = general_base1.cursor.fetchall()
    
    # indication that there was a poll
    if ca != []:
        message_id_needed = ca[0][2]
        mano = await bot.stop_poll(id_of_channel, message_id_needed)
        # several pretenders, no one voted
        if mano['total_voter_count'] == 0:
            await bot.send_message(id_of_channel, 'Cегодня ({}) ни один анекдот не получил звание "Анек Дня".\nГолосуйте за претендентов в опросах на этом канале, чтобы анекдоты получали это звание!'.format(date_in_messages), disable_notification = True)
            kan = 0
            for i in range(len(keka)):
                try:
                    await bot.send_message(keka[i][0], 'Cегодня ({}) не нашлось ни одного претендента на звание "Анек Дня".\nГолосуйте за анекдот дня в опросах на канале AnecBot channel (t.me/anecbot_channel), чтобы в следующие дни появлялись анекдоты дня!'.format(date_in_messages), disable_notification = True)
                except:
                    print('cannot send to one of the chats in the table (user or chat no longer use the bot)')
                    kan += 1
            await bot.send_message(my_id, 'Количество чатов, куда не прислали, что не проголосовали: {} из {}'.format(kan, len(keka)))
        
        # several pretenders, there are votes (main case!)
        else:
            num_options = len(mano['options'])
            li_votes = []
            li_pretender = []
            li_id = []
            for i in range(num_options):
                li_votes.append(mano['options'][i]['voter_count'])
                li_pretender.append(mano['options'][i]['text'].split(' (ID')[0])
                li_id.append(mano['options'][i]['text'].split('(ID: ')[1].split(')')[0])
            li_pretenders_win = []
            li_ids_win = []
            for j in range(len(li_votes)):
                if li_votes[j] == max(li_votes):
                    li_pretenders_win.append(li_pretender[j])
                    li_ids_win.append(li_id[j])
            
            # sending who win to the channel, to users and to the base at the same time!!!!            
            if len(li_pretenders_win) == 1:
                # to channel
                await bot.send_message(id_of_channel, 'Сегодня ({}) {} ПРЕТЕНДЕНТ получил звание "Анек дня". Посмотреть на результаты голосования, победителя и других претендентов можно в предыдущих сообщениях канала. Не забывайте, что претенденты выбираются путем Вашего оценивания анекдотов в AnecBot\n(@bot_anecbot)!'.format(date_in_messages, li_pretenders_win[0]), disable_notification = True)
                # add to the base
                general_base1.add_anec_of_the_day_to_anec_of_day_table(li_ids_win[0], date_in_messages, 0)
                # to users
                with general_base1.connection:
                    general_base1.cursor.execute("SELECT anec_text, source, cluster_num, date FROM anecdotes_general_table WHERE id_entry = %s LIMIT 1", (li_ids_win[0],))
                    data0 = general_base1.cursor.fetchall()
                    final_mes0 = 'АНЕК ДНЯ: {}\nID: {}-{}\n***anecbot***\n\n{}\n\nИстoчник: {}\nДата oпубликования в источнике: {}\n\nOцените анекдот:'.format(date_in_messages, data0[0][2], li_ids_win[0], data0[0][0], data0[0][1], data0[0][3])
                kan = 0
                for i in range(len(keka)):
                    try:
                        await bot.send_message(keka[i][0], 'Cегодня ({}) 1 анекдот получил звание "Анек Дня"'.format(date_in_messages), disable_notification = True)
                        #here send all anecs of the day (NOT disable notif)
                        await anec_of_day_sender(keka[i][0], final_mes0, markup, data0[0][2], li_ids_win[0])
                        await bot.send_message(keka[i][0], 'Не забывайте голосовать за анекдот дня в опросах на канале AnecBot channel (t.me/anecbot_channel), чтобы в следующие дни тоже появлялись анекдоты дня!', disable_notification = True)
                    except:
                        print('cannot send to one of the chats in the table (user or chat no longer use the bot)')
                        kan += 1
                await bot.send_message(my_id, 'Количество чатов, куда не прислали анек дня: {} из {}'.format(kan, len(keka)))
            
            elif len(li_pretenders_win) == 2:
                # to channel
                await bot.send_message(id_of_channel, 'Сегодня ({}) {} и {} ПРЕТЕНДЕНТЫ получили звание "Анек дня". Посмотреть на результаты голосования, победителей и других претендентов можно в предыдущих сообщениях канала. Не забывайте, что претенденты выбираются путем Вашего оценивания анекдотов в AnecBot\n(@bot_anecbot)!'.format(date_in_messages, li_pretenders_win[0], li_pretenders_win[1]), disable_notification = True)
                # add to base
                for i in li_ids_win:
                    general_base1.add_anec_of_the_day_to_anec_of_day_table(i, date_in_messages, 0)
                # to users
                with general_base1.connection:
                    general_base1.cursor.execute("SELECT anec_text, source, cluster_num, date FROM anecdotes_general_table WHERE id_entry = %s LIMIT 1", (li_ids_win[0],))
                    data0 = general_base1.cursor.fetchall()
                    final_mes0 = 'АНЕК ДНЯ: {}\nID: {}-{}\n***anecbot***\n\n{}\n\nИстoчник: {}\nДата oпубликования в источнике: {}\n\nOцените анекдот:'.format(date_in_messages, data0[0][2], li_ids_win[0], data0[0][0], data0[0][1], data0[0][3])
                    general_base1.cursor.execute("SELECT anec_text, source, cluster_num, date FROM anecdotes_general_table WHERE id_entry = %s LIMIT 1", (li_ids_win[1],))
                    data1 = general_base1.cursor.fetchall()
                    final_mes1 = 'АНЕК ДНЯ: {}\nID: {}-{}\n***anecbot***\n\n{}\n\nИстoчник: {}\nДата oпубликования в источнике: {}\n\nOцените анекдот:'.format(date_in_messages, data1[0][2], li_ids_win[1], data1[0][0], data1[0][1], data1[0][3])
                kan = 0    
                for i in range(len(keka)):
                    try:
                        await bot.send_message(keka[i][0], 'Cегодня ({}) 2 анекдота получили звание "Анек Дня"'.format(date_in_messages), disable_notification = True)
                        #here send all anecs of the day (NOT disable notif)
                        await anec_of_day_sender(keka[i][0], final_mes0, markup, data0[0][2], li_ids_win[0])
                        await anec_of_day_sender(keka[i][0], final_mes1, markup, data1[0][2], li_ids_win[1])
                        await bot.send_message(keka[i][0], 'Не забывайте голосовать за анекдот дня в опросах на канале AnecBot channel (t.me/anecbot_channel), чтобы в следующие дни тоже появлялись анекдоты дня!', disable_notification = True)
                    except:
                        print('cannot send to one of the chats in the table (user or chat no longer use the bot)')
                        kan += 1
                await bot.send_message(my_id, 'Количество чатов, куда не прислали анек дня: {} из {}'.format(kan, len(keka)))
            
            elif len(li_pretenders_win) == 3:
                # to channel
                await bot.send_message(id_of_channel, 'Сегодня ({}) {}, {} и {} ПРЕТЕНДЕНТЫ получили звание "Анек дня". Посмотреть на результаты голосования, победителей и других претендентов можно в предыдущих сообщениях канала. Не забывайте, что претенденты выбираются путем Вашего оценивания анекдотов в AnecBot\n(@bot_anecbot)!'.format(date_in_messages, li_pretenders_win[0], li_pretenders_win[1], li_pretenders_win[2]), disable_notification = True)
                # add to base
                for i in li_ids_win:
                    general_base1.add_anec_of_the_day_to_anec_of_day_table(i, date_in_messages, 0)
                # to users
                with general_base1.connection:
                    general_base1.cursor.execute("SELECT anec_text, source, cluster_num, date FROM anecdotes_general_table WHERE id_entry = %s LIMIT 1", (li_ids_win[0],))
                    data0 = general_base1.cursor.fetchall()
                    final_mes0 = 'АНЕК ДНЯ: {}\nID: {}-{}\n***anecbot***\n\n{}\n\nИстoчник: {}\nДата oпубликования в источнике: {}\n\nOцените анекдот:'.format(date_in_messages, data0[0][2], li_ids_win[0], data0[0][0], data0[0][1], data0[0][3])
                    general_base1.cursor.execute("SELECT anec_text, source, cluster_num, date FROM anecdotes_general_table WHERE id_entry = %s LIMIT 1", (li_ids_win[1],))
                    data1 = general_base1.cursor.fetchall()
                    final_mes1 = 'АНЕК ДНЯ: {}\nID: {}-{}\n***anecbot***\n\n{}\n\nИстoчник: {}\nДата oпубликования в источнике: {}\n\nOцените анекдот:'.format(date_in_messages, data1[0][2], li_ids_win[1], data1[0][0], data1[0][1], data1[0][3])
                    general_base1.cursor.execute("SELECT anec_text, source, cluster_num, date FROM anecdotes_general_table WHERE id_entry = %s LIMIT 1", (li_ids_win[2],))
                    data2 = general_base1.cursor.fetchall()
                    final_mes2 = 'АНЕК ДНЯ: {}\nID: {}-{}\n***anecbot***\n\n{}\n\nИстoчник: {}\nДата oпубликования в источнике: {}\n\nOцените анекдот:'.format(date_in_messages, data2[0][2], li_ids_win[2], data2[0][0], data2[0][1], data2[0][3])
                kan = 0    
                for i in range(len(keka)):
                    try:
                        await bot.send_message(keka[i][0], 'Cегодня ({}) 3 анекдота получили звание "Анек Дня"'.format(date_in_messages), disable_notification = True)
                        #here send all anecs of the day (NOT disable notif)
                        await anec_of_day_sender(keka[i][0], final_mes0, markup, data0[0][2], li_ids_win[0])
                        await anec_of_day_sender(keka[i][0], final_mes1, markup, data1[0][2], li_ids_win[1])
                        await anec_of_day_sender(keka[i][0], final_mes2, markup, data2[0][2], li_ids_win[2])
                        await bot.send_message(keka[i][0], 'Не забывайте голосовать за анекдот дня в опросах на канале AnecBot channel (t.me/anecbot_channel), чтобы в следующие дни тоже появлялись анекдоты дня!', disable_notification = True)
                    except:
                        print('cannot send to one of the chats in the table (user or chat no longer use the bot)')
                        kan += 1
                await bot.send_message(my_id, 'Количество чатов, куда не прислали анек дня: {} из {}'.format(kan, len(keka)))
            
            elif len(li_pretenders_win) == 4:
                # to channel
                await bot.send_message(id_of_channel, 'Сегодня ({}) {}, {}, {} и {} ПРЕТЕНДЕНТЫ получили звание "Анек дня". Посмотреть на результаты голосования, победителей и других претендентов можно в предыдущих сообщениях канала. Не забывайте, что претенденты выбираются путем Вашего оценивания анекдотов в AnecBot\n(@bot_anecbot)!'.format(date_in_messages, li_pretenders_win[0], li_pretenders_win[1], li_pretenders_win[2], li_pretenders_win[3]), disable_notification = True)
                # add to base
                for i in li_ids_win:
                    general_base1.add_anec_of_the_day_to_anec_of_day_table(i, date_in_messages, 0)
                # to users
                with general_base1.connection:
                    general_base1.cursor.execute("SELECT anec_text, source, cluster_num, date FROM anecdotes_general_table WHERE id_entry = %s LIMIT 1", (li_ids_win[0],))
                    data0 = general_base1.cursor.fetchall()
                    final_mes0 = 'АНЕК ДНЯ: {}\nID: {}-{}\n***anecbot***\n\n{}\n\nИстoчник: {}\nДата oпубликования в источнике: {}\n\nOцените анекдот:'.format(date_in_messages, data0[0][2], li_ids_win[0], data0[0][0], data0[0][1], data0[0][3])
                    general_base1.cursor.execute("SELECT anec_text, source, cluster_num, date FROM anecdotes_general_table WHERE id_entry = %s LIMIT 1", (li_ids_win[1],))
                    data1 = general_base1.cursor.fetchall()
                    final_mes1 = 'АНЕК ДНЯ: {}\nID: {}-{}\n***anecbot***\n\n{}\n\nИстoчник: {}\nДата oпубликования в источнике: {}\n\nOцените анекдот:'.format(date_in_messages, data1[0][2], li_ids_win[1], data1[0][0], data1[0][1], data1[0][3])
                    general_base1.cursor.execute("SELECT anec_text, source, cluster_num, date FROM anecdotes_general_table WHERE id_entry = %s LIMIT 1", (li_ids_win[2],))
                    data2 = general_base1.cursor.fetchall()
                    final_mes2 = 'АНЕК ДНЯ: {}\nID: {}-{}\n***anecbot***\n\n{}\n\nИстoчник: {}\nДата oпубликования в источнике: {}\n\nOцените анекдот:'.format(date_in_messages, data2[0][2], li_ids_win[2], data2[0][0], data2[0][1], data2[0][3])
                    general_base1.cursor.execute("SELECT anec_text, source, cluster_num, date FROM anecdotes_general_table WHERE id_entry = %s LIMIT 1", (li_ids_win[3],))
                    data3 = general_base1.cursor.fetchall()
                    final_mes3 = 'АНЕК ДНЯ: {}\nID: {}-{}\n***anecbot***\n\n{}\n\nИстoчник: {}\nДата oпубликования в источнике: {}\n\nOцените анекдот:'.format(date_in_messages, data3[0][2], li_ids_win[3], data3[0][0], data3[0][1], data3[0][3])
                kan = 0    
                for i in range(len(keka)):
                    try:
                        await bot.send_message(keka[i][0], 'Cегодня ({}) 4 анекдота получили звание "Анек Дня"'.format(date_in_messages), disable_notification = True)
                        #here send all anecs of the day (NOT disable notif)
                        await anec_of_day_sender(keka[i][0], final_mes0, markup, data0[0][2], li_ids_win[0])
                        await anec_of_day_sender(keka[i][0], final_mes1, markup, data1[0][2], li_ids_win[1])
                        await anec_of_day_sender(keka[i][0], final_mes2, markup, data2[0][2], li_ids_win[2])
                        await anec_of_day_sender(keka[i][0], final_mes3, markup, data3[0][2], li_ids_win[3])
                        await bot.send_message(keka[i][0], 'Не забывайте голосовать за анекдот дня в опросах на канале AnecBot channel (t.me/anecbot_channel), чтобы в следующие дни тоже появлялись анекдоты дня!', disable_notification = True)
                    except:
                        print('cannot send to one of the chats in the table (user or chat no longer use the bot)')
                        kan += 1
                await bot.send_message(my_id, 'Количество чатов, куда не прислали анек дня: {} из {}'.format(kan, len(keka)))
            
            elif len(li_pretenders_win) == 5:
                # to channel
                await bot.send_message(id_of_channel, 'Сегодня ({}) ВСЕ ПРЕТЕНДЕНТЫ получили звание "Анек дня". Посмотреть на результаты голосования, победителей и других претендентов можно в предыдущих сообщениях канала. Не забывайте, что претенденты выбираются путем Вашего оценивания анекдотов в AnecBot\n(@bot_anecbot)!'.format(date_in_messages), disable_notification = True)
                # add to base
                for i in li_ids_win:
                    general_base1.add_anec_of_the_day_to_anec_of_day_table(i, date_in_messages, 0)
                # to users
                with general_base1.connection:
                    general_base1.cursor.execute("SELECT anec_text, source, cluster_num, date FROM anecdotes_general_table WHERE id_entry = %s LIMIT 1", (li_ids_win[0],))
                    data0 = general_base1.cursor.fetchall()
                    final_mes0 = 'АНЕК ДНЯ: {}\nID: {}-{}\n***anecbot***\n\n{}\n\nИстoчник: {}\nДата oпубликования в источнике: {}\n\nOцените анекдот:'.format(date_in_messages, data0[0][2], li_ids_win[0], data0[0][0], data0[0][1], data0[0][3])
                    general_base1.cursor.execute("SELECT anec_text, source, cluster_num, date FROM anecdotes_general_table WHERE id_entry = %s LIMIT 1", (li_ids_win[1],))
                    data1 = general_base1.cursor.fetchall()
                    final_mes1 = 'АНЕК ДНЯ: {}\nID: {}-{}\n***anecbot***\n\n{}\n\nИстoчник: {}\nДата oпубликования в источнике: {}\n\nOцените анекдот:'.format(date_in_messages, data1[0][2], li_ids_win[1], data1[0][0], data1[0][1], data1[0][3])
                    general_base1.cursor.execute("SELECT anec_text, source, cluster_num, date FROM anecdotes_general_table WHERE id_entry = %s LIMIT 1", (li_ids_win[2],))
                    data2 = general_base1.cursor.fetchall()
                    final_mes2 = 'АНЕК ДНЯ: {}\nID: {}-{}\n***anecbot***\n\n{}\n\nИстoчник: {}\nДата oпубликования в источнике: {}\n\nOцените анекдот:'.format(date_in_messages, data2[0][2], li_ids_win[2], data2[0][0], data2[0][1], data2[0][3])
                    general_base1.cursor.execute("SELECT anec_text, source, cluster_num, date FROM anecdotes_general_table WHERE id_entry = %s LIMIT 1", (li_ids_win[3],))
                    data3 = general_base1.cursor.fetchall()
                    final_mes3 = 'АНЕК ДНЯ: {}\nID: {}-{}\n***anecbot***\n\n{}\n\nИстoчник: {}\nДата oпубликования в источнике: {}\n\nOцените анекдот:'.format(date_in_messages, data3[0][2], li_ids_win[3], data3[0][0], data3[0][1], data3[0][3])
                    general_base1.cursor.execute("SELECT anec_text, source, cluster_num, date FROM anecdotes_general_table WHERE id_entry = %s LIMIT 1", (li_ids_win[4],))
                    data4 = general_base1.cursor.fetchall()
                    final_mes4 = 'АНЕК ДНЯ: {}\nID: {}-{}\n***anecbot***\n\n{}\n\nИстoчник: {}\nДата oпубликования в источнике: {}\n\nOцените анекдот:'.format(date_in_messages, data4[0][2], li_ids_win[4], data4[0][0], data4[0][1], data4[0][3])
                kan = 0    
                for i in range(len(keka)):
                    try:
                        await bot.send_message(keka[i][0], 'Cегодня ({}) 5 анекдотов получили звание "Анек Дня"'.format(date_in_messages), disable_notification = True)
                        #here send all anecs of the day (NOT disable notif)
                        await anec_of_day_sender(keka[i][0], final_mes0, markup, data0[0][2], li_ids_win[0])
                        await anec_of_day_sender(keka[i][0], final_mes1, markup, data1[0][2], li_ids_win[1])
                        await anec_of_day_sender(keka[i][0], final_mes2, markup, data2[0][2], li_ids_win[2])
                        await anec_of_day_sender(keka[i][0], final_mes3, markup, data3[0][2], li_ids_win[3])
                        await anec_of_day_sender(keka[i][0], final_mes4, markup, data4[0][2], li_ids_win[4])
                        await bot.send_message(keka[i][0], 'Не забывайте голосовать за анекдот дня в опросах на канале AnecBot channel (t.me/anecbot_channel), чтобы в следующие дни тоже появлялись анекдоты дня!', disable_notification = True)
                    except:
                        print('cannot send to one of the chats in the table (user or chat no longer use the bot)')
                        kan += 1
                await bot.send_message(my_id, 'Количество чатов, куда не прислали анек дня: {} из {}'.format(kan, len(keka)))
            
            else:
                await bot.send_message(id_of_channel, 'error in pretenders_win len', disable_notification = True)
                await bot.send_message(id_of_channel, len(li_pretenders_win), disable_notification = True)
        

        
        
async def random_anec_sender():
    with general_base1.connection:
        general_base1.cursor.execute("SELECT user_id FROM users_sub_random_anec WHERE subscribed = True")
        keka_random = general_base1.cursor.fetchall()
        general_base1.cursor.execute("SELECT distinct on (source_id) anec_text, source, date, id_entry, cluster_num FROM anecdotes_general_table ORDER BY source_id, RANDOM()")
        random_anecs_data = general_base1.cursor.fetchall()
    kun = 0
    
    markup = types.InlineKeyboardMarkup(row_width = 10)
    item_1 = types.InlineKeyboardButton(1, callback_data = "mark 1")
    item_2 = types.InlineKeyboardButton(2, callback_data = "mark 2")
    item_3 = types.InlineKeyboardButton(3, callback_data = "mark 3")
    item_4 = types.InlineKeyboardButton(4, callback_data = "mark 4")
    item_5 = types.InlineKeyboardButton(5, callback_data = "mark 5")
    item_6 = types.InlineKeyboardButton(6, callback_data = "mark 6")
    item_7 = types.InlineKeyboardButton(7, callback_data = "mark 7")
    item_8 = types.InlineKeyboardButton(8, callback_data = "mark 8")
    item_9 = types.InlineKeyboardButton(9, callback_data = "mark 9")
    item_10 = types.InlineKeyboardButton(10, callback_data = "mark 10")
    item_11 = types.InlineKeyboardButton('Добавить в "Сохранённые"', callback_data = "add_to_save")
    markup.add(item_1, item_2, item_3, item_4, item_5)
    markup.add(item_6, item_7, item_8, item_9, item_10)
    markup.add(item_11) 
    
    for i in range(len(keka_random)):
        try:
            ra = random.randint(0, 9)
            anec = random_anecs_data[ra][0]
            source = random_anecs_data[ra][1]
            date = random_anecs_data[ra][2]
            id_entry = random_anecs_data[ra][3]
            cluster_num = random_anecs_data[ra][4]
            final = 'ID: {}-{}\n***anecbot***\n\n{}\n\nИстoчник: {}\nДата oпубликования в источнике: {}\n\nOцените анекдот:'.format(cluster_num, id_entry, anec, source, date)
            
            await bot.send_message(keka_random[i][0], 'Высылаю рандомный анекдот!', disable_notification = True)
            if len(final) <= 4096:
                await bot.send_message(keka_random[i][0], final, reply_markup = markup, disable_notification = True)  
            else:
                for x in range(0, len(final) - 4096, 4096):
                    await bot.send_message(keka_random[i][0], final[x : x + 4096], reply_markup = markup, disable_notification = True)
                k = len(final)//4096
                await bot.send_message(keka_random[i][0], 'ID: {}-{}\n***anecbot***\n\n'.format(cluster_num, id_entry) + final[k * 4096 : k * 4096 + 4096], reply_markup = markup, disable_notification = True)
            await bot.send_message(keka_random[i][0], 'Чтобы отписаться от ежедневной рассылки рандомных анекдотов, нажмите на кнопку "Рандомный Анек: отписаться" на 7ом ряду клавиатуры', disable_notification = True)
        except:
            kun += 1
    await bot.send_message(my_id, 'not send random anec: {}/{}'.format(kun, len(keka_random)))
 

 
 # function which sends reminder to those who did not finish initial instruction
async def notification_for_no_instruction_sender():
    with general_base1.connection:
        general_base1.cursor.execute("SELECT user_id FROM user_novice_or_not WHERE is_novice = True")
        keka_reminder = general_base1.cursor.fetchall()  
     
    text_remind = 'Привет, это AnecBot!\nЯ подбираю анекдоты специально для Вас из базы, содержащей более чем 170000 анекдотов! Также Вы можете сохранять, находить по слову и оценивать анекдоты, чтобы Я высылал Вам более релевантные анекдоты в следующий раз!\n\n Посмотрите историю этой переписки выше, чтобы вспомнить, как закончить начальную инструкцию и выйти в главное меню. Напоминаю, что если Вы не видите специальных кнопок на клавиатуре, то накжмите на квадратик с 4-мя кружочками внутри рядом в верхнем углу клавиатуры справа рядом со значком микрофона.\n\n(Вы можете выйти в главное меню, нажав на кнопку "Пропустить начальную инструкцию", НО я не рекомендую Вам этого делать, если Вы до этого не проходили до конца эту инструкцию)'
    kun = 0
    for i in range(len(keka_reminder)):
        try:            
            await bot.send_message(keka_reminder[i][0], text_remind, disable_notification = True) 
        except:
            kun += 1
    await bot.send_message(my_id, text_remind, disable_notification = True)
    await bot.send_message(my_id, 'not send initial instruction reminder: {}/{}'.format(kun, len(keka_reminder)), disable_notification = True)

                                    
                                    
# executes the function and checkes, whether it's time to do that: UNCOMMENT AFTER COMPLETION!!!!!
# this function scheduler allows to sent some stuff to the users and in the AnecBot channel at the specified time!!!
# functions used here can be found above!!!!
async def scheduler():
    # get timezones of server and Moscow   
    local_tz = get_localzone() 
    non_local = tz.gettz('Europe/Moscow')
    # current time and utc0 time
    ts = time.time()
    utc_now = datetime.utcfromtimestamp(ts)
    #times in both timezones
    local_now = utc_now.replace(tzinfo=pytz.utc).astimezone(local_tz)
    non_local_now = utc_now.replace(tzinfo=pytz.utc).astimezone(non_local)
    #timestamps in both timezones
    server_time = datetime(local_now.year, local_now.month, local_now.day, local_now.hour, local_now.minute, local_now.second).timestamp()
    moscow_time = datetime(non_local_now.year, non_local_now.month, non_local_now.day, non_local_now.hour, non_local_now.minute, non_local_now.second).timestamp()
    # difference in timezones in hours
    hour_delta_moscow_minus_server = round((moscow_time - server_time)/3600)
    #ENTER MOSCOW DESIRED TIMES HERE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    top5_to_channel = '10:00'
    sender_general = '22:00'
    random1 = '13:00'
    random2 = '18:00'
    reminder_no_instruction = '19:00'
    # converting to server times to the format, which is used by aioschedule!!!
    if hour_delta_moscow_minus_server > 10:
        ttc_h = int(top5_to_channel.split(':')[0]) - hour_delta_moscow_minus_server + 24
    else:
        ttc_h = int(top5_to_channel.split(':')[0]) - hour_delta_moscow_minus_server
    ttc = f'{ttc_h}:{top5_to_channel[-2:]}'
    sg_h = int(sender_general.split(':')[0]) - hour_delta_moscow_minus_server
    sg = f'{sg_h}:{sender_general[-2:]}'
    r1_h = int(random1.split(':')[0]) - hour_delta_moscow_minus_server
    r1 = f'{r1_h}:{random1[-2:]}'
    r2_h = int(random2.split(':')[0]) - hour_delta_moscow_minus_server
    r2 = f'{r2_h}:{random2[-2:]}'
    rni_h = int(reminder_no_instruction.split(':')[0]) - hour_delta_moscow_minus_server
    rni = f'{rni_h}:{reminder_no_instruction[-2:]}'
    #  Aioschedule: NECESSARY TO TURN OFF SINCE ALL ANECS OF THE DAY ARE SENT TO USERS!!!!
    # all function in .do() can be found 
    # sending top5 anecdotes of the day to the channel so that in channel the users can vote for the best anec of the day
    aioschedule.every().day.at(ttc).do(anec_of_day_top5_to_channel)
    # poll in the channel is automatically parsed and anecs with the biggest amount of votes are sent to all users, who subscribed
        # to receiving anecs of the day
    aioschedule.every().day.at(sg).do(anec_of_day_sender_general)
    # random anecs are sent twice a day to all users who subscribed to this option
    aioschedule.every().day.at(r1).do(random_anec_sender)
    aioschedule.every().day.at(r2).do(random_anec_sender)
    # gentle reminder is sent every week to those who did not complete the initial instruction in the bot
    aioschedule.every().saturday.at(rni).do(notification_for_no_instruction_sender)
    
    # every ten second aioscheduler checks whether it's the time to implement some function!!!
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(10)
        
        
# another function needed to connect scheduler and webhook!!!, when bot starts:
async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
    asyncio.create_task(scheduler())
    await bot.send_message(my_id, 'Бот снова работает!\nЖелаем Вам смешных анекдотов!')
    
# when bot shuts down:
async def on_shutdown(dp):    
    logging.warning('Shutting down..')
    
    general_base1.cursor.close()
    general_base1.connection.close()
    await bot.send_message(my_id, 'Бот временно прекратил свою работу.\nЛибо ведутся профилактические работы, либо что-то пошло не так!\n\nКак только бот снова заработает, Вы увидите в этом канале соотвтетствующее сообщение!')
 

    
# Secret command for me to get some stats about number of bot users (using bot itself to get these stats):
@dp.message_handler(commands = ['secret_info_bot_number_users_using_and_anecs_marked'])
async def small_stat(message: types.message):
    with general_base1.connection:
        general_base1.cursor.execute("SELECT COUNT(*) FROM users_sources")
        all_users_pressed_start = general_base1.cursor.fetchall()[0][0]
        general_base1.cursor.execute("SELECT COUNT(*) FROM users_sources WHERE user_id > -1")
        people_pressed_start = general_base1.cursor.fetchall()[0][0]
        general_base1.cursor.execute("SELECT COUNT(*) FROM users_sub_best_anec_day")
        all_users_finished_starting_instruction = general_base1.cursor.fetchall()[0][0]
        general_base1.cursor.execute("SELECT COUNT(*) FROM users_sub_best_anec_day WHERE user_id > -1")
        people_finished_starting_instruction = general_base1.cursor.fetchall()[0][0]
        general_base1.cursor.execute("SELECT COUNT(*) FROM users_history")
        anecs_marked = general_base1.cursor.fetchall()[0][0]
        
        general_base1.cursor.execute("SELECT COUNT(*) FROM users_sub_best_anec_day WHERE subscribed = True")
        percent_subscribed_to_anec_day = round(general_base1.cursor.fetchall()[0][0] / all_users_finished_starting_instruction * 100, 2)
        general_base1.cursor.execute("SELECT COUNT(*) FROM users_sub_random_anec WHERE subscribed = True")
        percent_subscribed_to_random_anec = round(general_base1.cursor.fetchall()[0][0] / all_users_finished_starting_instruction * 100, 2)
        
        general_base1.cursor.execute("SELECT COUNT(*) FROM users_sources WHERE source_1_chosen = True")
        percent_subscribed_to_source1 = round(general_base1.cursor.fetchall()[0][0] / all_users_pressed_start * 100, 2)
        general_base1.cursor.execute("SELECT COUNT(*) FROM users_sources WHERE source_2_chosen = True")
        percent_subscribed_to_source2 = round(general_base1.cursor.fetchall()[0][0] / all_users_pressed_start * 100, 2)
        general_base1.cursor.execute("SELECT COUNT(*) FROM users_sources WHERE source_3_chosen = True")
        percent_subscribed_to_source3 = round(general_base1.cursor.fetchall()[0][0] / all_users_pressed_start * 100, 2)
        general_base1.cursor.execute("SELECT COUNT(*) FROM users_sources WHERE source_4_chosen = True")
        percent_subscribed_to_source4 = round(general_base1.cursor.fetchall()[0][0] / all_users_pressed_start * 100, 2)
        general_base1.cursor.execute("SELECT COUNT(*) FROM users_sources WHERE source_5_chosen = True")
        percent_subscribed_to_source5 = round(general_base1.cursor.fetchall()[0][0] / all_users_pressed_start * 100, 2)
        general_base1.cursor.execute("SELECT COUNT(*) FROM users_sources WHERE source_6_chosen = True")
        percent_subscribed_to_source6 = round(general_base1.cursor.fetchall()[0][0] / all_users_pressed_start * 100, 2)
        general_base1.cursor.execute("SELECT COUNT(*) FROM users_sources WHERE source_7_chosen = True")
        percent_subscribed_to_source7 = round(general_base1.cursor.fetchall()[0][0] / all_users_pressed_start * 100, 2)
        general_base1.cursor.execute("SELECT COUNT(*) FROM users_sources WHERE source_8_chosen = True")
        percent_subscribed_to_source8 = round(general_base1.cursor.fetchall()[0][0] / all_users_pressed_start * 100, 2)
        general_base1.cursor.execute("SELECT COUNT(*) FROM users_sources WHERE source_9_chosen = True")
        percent_subscribed_to_source9 = round(general_base1.cursor.fetchall()[0][0] / all_users_pressed_start * 100, 2)
        general_base1.cursor.execute("SELECT COUNT(*) FROM users_sources WHERE source_10_chosen = True")
        percent_subscribed_to_source10 = round(general_base1.cursor.fetchall()[0][0] / all_users_pressed_start * 100, 2)
        
        general_base1.cursor.execute("SELECT COUNT(*) FROM users_sources WHERE source_1_chosen = True and source_2_chosen = True and source_3_chosen = True and source_4_chosen = True and source_5_chosen = True and source_6_chosen = True and source_7_chosen = True and source_8_chosen = True and source_9_chosen = True and source_10_chosen = True")
        percent_subscribed_to_all_sources = round(general_base1.cursor.fetchall()[0][0] / all_users_pressed_start * 100, 2)
        
    await message.answer([all_users_pressed_start, people_pressed_start, all_users_finished_starting_instruction, people_finished_starting_instruction, anecs_marked])
    await message.answer([percent_subscribed_to_anec_day, percent_subscribed_to_random_anec])
    await message.answer([percent_subscribed_to_source1, percent_subscribed_to_source2, percent_subscribed_to_source3, percent_subscribed_to_source4, percent_subscribed_to_source5])
    await message.answer([percent_subscribed_to_source6, percent_subscribed_to_source7, percent_subscribed_to_source8, percent_subscribed_to_source9, percent_subscribed_to_source10])
    await message.answer(percent_subscribed_to_all_sources)
    

    
# command when no valid command is written:
@dp.message_handler(content_types = ['text'])
async def not_understand_command(message: types.message):
    if message.chat.id > -1:
        await message.answer('Я не понял команду. Удостоверьтесь, что Вы правильно ввели желаемую команду.\n\nЕсли Вы ввели правильную команду, но я её не понимаю, обратитесь с проблемой в чат AnecBot chat\n(t.me/anecbot_chat)')
    
    
       
  # executing long polling for running bot locally . IF RUNNING LOCALLY, COMMENT WEBHOOK if __name__ ... below!!!!
    # To run the bot locally, just uncomment the if __name__ ... below (2 lines below) and 
    # in the command line move to the path with this file and type: python bot_anecbot.py
#if __name__ == '__main__':
#    executor.start_polling(dp, skip_updates = True, on_startup = on_startup, on_shutdown = on_shutdown)

# to run the bot on webhooks, I tried https://github.com/aahnik/webhook-aiogram-heroku !!!!!
#WORKS FOR HEROKU WHEN RUN USING WEBHOOKS!!!!!
if __name__ == '__main__':
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown = on_shutdown,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
   
    
    
    
    
    
    
