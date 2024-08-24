import telebot
from app.main import db, Giveaway, Channel

API_TOKEN = '7514207604:AAE_p_eFFQ3yOoNn-GSvTSjte2l8UEHl7b8'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, "Welcome to the Giveaway Bot! Use /create_giveaway to create a giveaway.")

@bot.message_handler(commands=['create_giveaway'])
def handle_create_giveaway(message):
    bot.reply_to(message, "Send the giveaway details in the format: /create_giveaway [channel_username] [giveaway_name] [prize_amount] [participants_count] [end_date]")

# Add more handlers as needed

if __name__ == '__main__':
    bot.polling(none_stop=True)

