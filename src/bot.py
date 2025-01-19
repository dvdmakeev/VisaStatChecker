import os
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

from auth import authenticate_google_sheets
from statist import SAMPLE_SPREADSHEET_ID, get_top_visa_countries, TimePeriod


BOT_TOKEN = os.environ.get('BOT_TOKEN')


VALID_OPTIONS = ["Week", "Month", "3 Month", "6 Month"]


bot = telebot.TeleBot(BOT_TOKEN)


# /start command handler
@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Create a reply keyboard
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    # Add buttons
    markup.add(
        KeyboardButton("Week"),
        KeyboardButton("Month"),
        KeyboardButton("3 Month"),
        KeyboardButton("6 Month")
    )

    # Send a welcome message with the keyboard
    bot.send_message(
        message.chat.id,
        "Choose an option:",
        reply_markup=markup
    )

# General handler for valid options
@bot.message_handler(func=lambda msg: msg.text in VALID_OPTIONS)
def handle_options(message):
    time_periods = {
        "Week": TimePeriod.WEEK.value,
        "Month": TimePeriod.MONTH.value,
        "3 Month": TimePeriod.THREE_MONTH.value,
        "6 Month": TimePeriod.SIX_MONTH.value
    }

    service_sheets = authenticate_google_sheets()
    time_period = time_periods[message.text]

    top_visa_countries = get_top_visa_countries(
        service_sheets,
        SAMPLE_SPREADSHEET_ID,
        time_period,
        only_first_visa=True)

    bot.reply_to(message, str(top_visa_countries))

# Catch-all handler for invalid inputs
@bot.message_handler(func=lambda msg: True)
def handle_invalid_input(message):
    bot.reply_to(
        message,
        "Invalid input. Please use the buttons to select one of the options."
    )

bot.infinity_polling()
