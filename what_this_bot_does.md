# AnecBot [Try it out](http://t.me/bot_anecbot)
This is the bot which contains over 170000 jokes (anecdotes or anecs) where users have the opportunity to rate these jokes, save them, choose the list of sources (by subscribing/unsubscribing to specific sources in the specific section of the bot) from which the jokes can be received and find any joke from the base by word (by typing this word to the bot). Also bot contains some simple recommendation algorithm, based on the marks of the users to certain jokes.  
  
Furthermore, user can subscribe to the option to receive some random joke 2 times per day and every day top 5 anecdotes (with highest marks (grades) from the users during the day) are translated to the specific Telegram channel automatically and the poll is created automatically where the members of the channel can vote for the best joke of the day. Then the joke with the largest number of votes is sent to all the bot users, who subscribed to the option of receiving this joke of the day.
  
This Telegram bot was written in Python with the usage of PostgreSQL databases, and nlp (lemmatization), TfidfVectorizer, pairwise.linear_kernel, linkage and fcluster ML algorithms were used to group the jokes.  

The jokes were parsed from various sourses in Telegram and VK social media

## Some screenshots of the user interface
In general, the user will see the keyboard with the buttons like that:   
<img src = "https://user-images.githubusercontent.com/92990826/194267276-4bbe03dd-806b-490f-a79e-6667b7c76b0a.png" width=50% height=50%>     
  
After the user presses the button Анек, for example, the joke is sent and the inline keyborad button appears under the message with the joke like in the photo below:  
<img src = "https://user-images.githubusercontent.com/92990826/194269050-58ded322-841c-4dd7-97da-f9a51624688e.png" width=50% height=50%>  
So after the joke is sent, the user can rate the joke from 1 to 10 by clicking one of the inline buttons, and additionally the joke can be saved by clicking the lowest inline button. To see this saved joke later, the user can click on specific button in the main keyboard, like the one in the first photo.  
  
Of course, to store jokes, saved jokes and ratings of the users, I need database, with which I work with throughout my code. 

