import requests
import telebot
from telebot import types
import json
from bs4 import BeautifulSoup

bot = telebot.TeleBot("5380240127:AAGJyoEeO7VxpC4W5u7Kb2EffObaBwo8o8Q")

# Start function
@bot.message_handler(commands=["start"])
def start(m, res=False):
    bot.send_message(m.chat.id, 'Я на связи. Что хочется поесть? ')
    keyboard = types.ReplyKeyboardMarkup(row_width=1,resize_keyboard=True)
    button_geo = types.KeyboardButton(text = "Share geo",request_location=True)
    keyboard.add(button_geo)
    bot.send_message(m.chat.id,"Поделись своим гео!",reply_markup=keyboard)

# Getinng location
@bot.message_handler(content_types=["location"])
def location(message):
    if message.location is not None:
        #Getting current position from user
        current_pos = (message.location.latitude, message.location.longitude)
        
        url = f"https://api.foursquare.com/v3/places/nearby?fields=fsq_id%2Ccategories&ll={current_pos[0]}%2C{current_pos[1]}&limit=25"
        headers = {
        "Accept": "application/json",
        "Authorization": "fsq31LC4xea7PRHcvFfLx27CElE3vmLJXjgqMUEWy7pWA/g= "
        }
        response = requests.get(url, headers=headers)
        data = json.loads(response.text)
        data = data.get('results')

        #Sorting data about places which are close to the current position
        sortedides = []
        for item in data:
            for category in item['categories']:
                if category['id'] in range(13000,14000):
                    sortedides.append(item)
        mess = []
        for item in sortedides:
                mess.append(item['fsq_id'])
        #Parcing the sites for info
        info =[]
        for i in mess:
            newurl = f'https://ru.foursquare.com/v/{i}'
            r = requests.get(newurl)
            soup = BeautifulSoup(r.text,'lxml')
            try:
                name = soup.find('div',class_='venueNameSection').find('h1', class_='venueName').text
            except AttributeError:
                pass
            type = soup.find('div',class_='categories').find('span', class_='unlinkedCategory').text
            try:
                time_till_close = soup.find('div',class_='hoursBlock sideVenueBlockRow').find('div',class_='venueRowContent').find('span',class_='open').text
            except AttributeError:
                time_till_close = 'Нет данных о закрытии'
                pass
            try:
                phonenumber = soup.find('div',class_='phoneBlock sideVenueBlockRow').find('div',class_='venueRowContent').find('span', class_='tel').text
            except AttributeError:
                phonenumber = "Нет данных о номере телефона"
                pass

            adress_route = '[Маршрут]({})'.format(soup.find('div',class_='venueDirections').find('span',class_='venueDirectionsLink').find('a',class_='directionsLink').get('href'))
            
            try:
                rating = soup.find('div',class_='venueRateBlock').find('span',itemprop='ratingValue').text+"/10" + " из {} оценок".format(soup.find('div',class_='numRatingsBlock').find('div',class_='numRatings').text)
            except AttributeError:
                rating = 'Нет оценок'
                pass
            #sending message to user about places
            info = [name,type,time_till_close,phonenumber,adress_route,rating]
            bot.send_message(message.chat.id,"\n\n".join(info),parse_mode="Markdown")
    

bot.polling(none_stop = True)
input()
 