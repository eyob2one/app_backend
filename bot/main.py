import sys
import os
from pathlib import Path

# Add the webapp directory to the Python path
sys.path.append(str(Path(__file__).resolve().parent.parent / 'webapp'))

from webapp.models import db, Giveaway, Channel, Participant
from telegram import Bot
from telegram.error import TelegramError
from webapp.config import BOT_TOKEN
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///giveaways.db'  # Use your preferred database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Your bot's token
API_TOKEN = '7514207604:AAE_p_eFFQ3yOoNn-GSvTSjte2l8UEHl7b8'
bot = Bot(token=API_TOKEN)

# Models
class Channel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    chat_id = db.Column(db.Integer, unique=True, nullable=False)

class Giveaway(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    prize_amount = db.Column(db.Float, nullable=False)
    participants_count = db.Column(db.Integer, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)

# Routes

@app.route('/')
def home():
    channels = Channel.query.all()
    return render_template('home.html', channels=channels)

@app.route('/add_channel', methods=['POST'])


def add_channel():
    channel_username = request.form['channel_username']
    
    try:
        # Try to fetch the channel info using the bot
        chat = bot.get_chat(channel_username)
        
        # Check if the bot is an admin of the channel
        admins = bot.get_chat_administrators(chat.id)
        bot_is_admin = any(admin.user.id == bot.get_me().id for admin in admins)

        if bot_is_admin:
            # Save the channel to the database
            new_channel = Channel(username=channel_username, chat_id=chat.id)
            db.session.add(new_channel)
            db.session.commit()
            return redirect(url_for('home'))
        else:
            return "Bot is not an admin in this channel. Please make the bot an admin and try again.", 403
    
    except Exception as e:
        return f"Failed to add channel: {e}", 400

def post_to_channel(giveaway):
    try:
        channel = Channel.query.get(giveaway.channel_id)
        message = (
            f"🎉 New Giveaway Alert! 🎉\n\n"
            f"💰 Amount: {giveaway.amount} Birr\n"
            f"👥 Participants: {giveaway.participant_count}\n"
            f"🕒 Ends on: {giveaway.end_date.strftime('%Y-%m-%d %H:%M')}\n\n"
            f"Join now and stand a chance to win!"
        )
        bot.send_message(chat_id=channel.link, text=message)
        giveaway.posted = True
        giveaway.url = f"https://t.me/giveaway_setota_bot/Giveaway/{giveaway.id}"
        db.session.commit()
    except TelegramError as e:
        print(f"Failed to post to channel: {e}")

def post_winners_to_channel(giveaway, winners):
    try:
        channel = Channel.query.get(giveaway.channel_id)
        winner_list = "\n".join([f"@{winner.username}" for winner in winners])
        message = (
            f"🎉 Congratulations to the winners of our recent giveaway! 🎉\n\n"
            f"The following participants were randomly selected:\n\n"
            f"{winner_list}\n\n"
            f"View more details here: {giveaway.url}"
        )
        bot.send_message(chat_id=channel.link, text=message)
    except TelegramError as e:
        print(f"Failed to post winners to channel: {e}")
