# bot/utils.py

from telegram import Update, CallbackContext
import pytz
from datetime import datetime

def delete_previous_message(update: Update, context: CallbackContext):
    try:
        context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id - 1)
    except:
        pass

def convert_to_eat(date_string):
    """
    Converts a date string in the format 'YYYY-MM-DD HH:MM' to a datetime object in Eastern Africa Time (EAT) timezone.
    
    Args:
    - date_string (str): Date and time in 'YYYY-MM-DD HH:MM' format.

    Returns:
    - datetime: Datetime object in EAT timezone.
    """
    try:
        # Parse the input date string
        local_time = datetime.strptime(date_string, '%Y-%m-%d %H:%M')
        
        # Define EAT timezone
        eat = pytz.timezone('Africa/Nairobi')
        
        # Localize the datetime object to EAT timezone
        eat_time = eat.localize(local_time)
        
        return eat_time
    except ValueError:
        raise ValueError("The date and time format should be 'YYYY-MM-DD HH:MM'.")