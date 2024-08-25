from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import random
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, CallbackContext
from telegram.error import TelegramError
from flask_cors import CORS  # Import CORS

# Configuration class for Flask and other services
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'b9a8bd545b2265939a1216abf1b76193')
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres.elaqzrcvbknbzvbkdwgp:iCcxsx4TpDLdwqzq@aws-0-eu-central-1.pooler.supabase.com:6543/postgres'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TELEGRAM_API_TOKEN = '7514207604:AAE_p_eFFQ3yOoNn-GSvTSjte2l8UEHl7b8'

# Initialize Flask app and load configuration
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
CORS(app)  # Enable CORS for all routes

# Initialize Telegram bot
bot = Bot(token=app.config['TELEGRAM_API_TOKEN'])
application = Application.builder().token(app.config['TELEGRAM_API_TOKEN']).build()

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.String(50), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    channels = db.relationship('Channel', backref='owner', lazy=True)
    giveaways = db.relationship('Giveaway', backref='creator', lazy=True)

class Channel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    chat_id = db.Column(db.Integer, unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    giveaways = db.relationship('Giveaway', backref='channel', lazy=True)

class Giveaway(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bot_username = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    participant_count = db.Column(db.Integer, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    posted = db.Column(db.Boolean, default=False)
    winners = db.Column(db.PickleType, nullable=True)
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    url = db.Column(db.String(200), nullable=True)

class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    giveaway_id = db.Column(db.Integer, db.ForeignKey('giveaway.id'), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    profile_pic = db.Column(db.String(200), nullable=False)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)

# Utility functions for the bot
def check_bot_admin(channel_username):
    try:
        chat = bot.get_chat(channel_username)
        chat_id = chat.id
        member = bot.get_chat_member(chat_id, bot.id)
        return chat_id, member.status in ['administrator', 'creator']
    except TelegramError as e:
        raise Exception(f"Error checking bot admin status: {str(e)}")

def post_to_channel(chat_id, message):
    try:
        bot.send_message(chat_id=chat_id, text=message)
    except TelegramError as e:
        raise Exception(f"Error posting to channel: {str(e)}")

def post_winners_to_channel(chat_id, message):
    try:
        bot.send_message(chat_id=chat_id, text=message)
    except TelegramError as e:
        raise Exception(f"Error posting winners to channel: {str(e)}")

# Flask Routes
@app.route('/')
def home():
    return render_template('home.html', channels=Channel.query.all())

@app.route('/add_channel', methods=['POST'])
def add_channel():
    channel_username = request.form.get('channel_username')
    try:
        chat_id, bot_is_admin = check_bot_admin(channel_username)
        if bot_is_admin:
            new_channel = Channel(username=channel_username, chat_id=chat_id, user_id=1)  # Adjust user_id as needed
            db.session.add(new_channel)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Channel added successfully!'})
        else:
            return jsonify({'success': False, 'message': 'Bot is not an admin in this channel. Please make the bot an admin and try again.'}), 403
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/create_giveaway', methods=['POST'])
def create_giveaway():
    channel_username = request.form.get('channel')
    giveaway_name = request.form.get('giveaway_name')
    prize_amount = float(request.form.get('prize_amount'))
    participants_count = int(request.form.get('participants_count'))
    end_date = datetime.fromisoformat(request.form.get('end_date'))
    
    selected_channel = Channel.query.filter_by(username=channel_username).first()
    
    if selected_channel:
        new_giveaway = Giveaway(
            bot_username=request.form.get('bot_username'),
            amount=prize_amount,
            participant_count=participants_count,
            end_date=end_date,
            channel_id=selected_channel.id,
            user_id=1  # Adjust as needed
        )
        db.session.add(new_giveaway)
        db.session.commit()

        message = (
            f"🎉 New Giveaway Alert! 🎉\n\n"
            f"💰 Amount: {new_giveaway.amount} Birr\n"
            f"👥 Participants: {new_giveaway.participant_count}\n"
            f"🕒 Ends on: {new_giveaway.end_date.strftime('%Y-%m-%d %H:%M')}\n\n"
            f"Join now and stand a chance to win!"
        )
        try:
            post_to_channel(selected_channel.chat_id, message)
        except Exception as e:
            return jsonify({'success': False, 'message': f'Failed to post giveaway to channel: {str(e)}'}), 500
        
        new_giveaway.url = f"https://t.me/giveaway_setota_bot/Giveaway/giveaway/{new_giveaway.id}"
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Giveaway created successfully!'})
    else:
        return jsonify({'success': False, 'message': 'Channel not found.'}), 404

@app.route('/announce_winners/<int:giveaway_id>', methods=['GET'])
def announce_winners(giveaway_id):
    giveaway = Giveaway.query.get_or_404(giveaway_id)
    participants = Participant.query.filter_by(giveaway_id=giveaway_id).all()

    winners = random.sample(participants, min(giveaway.participant_count, len(participants)))

    giveaway.winners = [winner.id for winner in winners]
    db.session.commit()

    winner_list = "\n".join([f"@{winner.username}" for winner in winners])
    message = (
        f"🎉 Congratulations to the winners of our recent giveaway! 🎉\n\n"
        f"The following participants were randomly selected:\n\n"
        f"{winner_list}\n\n"
        f"View more details here: {giveaway.url}"
    )
    try:
        post_winners_to_channel(giveaway.channel_id, message)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to post winners to channel: {str(e)}'}), 500

    return jsonify({'success': True, 'winners': [{'username': winner.username} for winner in winners]})

# Telegram Command Handlers
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Welcome to the Giveaway Bot!")

async def create(update: Update, context: CallbackContext):
    # Extract data from the message and create a giveaway
    await update.message.reply_text("Giveaway created successfully!")

async def join(update: Update, context: CallbackContext):
    # Extract data from the message and join a giveaway
    await update.message.reply_text("You have joined the giveaway!")

application.add_handler(CommandHandler('start', start))
application.add_handler(CommandHandler('create', create))
application.add_handler(CommandHandler('join', join))

# Main application entry point
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure all tables are created

    # Run Flask application
    app.run(host='0.0.0.0', port=5000, debug=True)
