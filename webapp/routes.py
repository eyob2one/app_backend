from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, User, Channel, Giveaway, Participant
from bot.main import post_to_channel, post_winners_to_channel, bot
from datetime import datetime
from telegram import Bot
import random

app = Flask(__name__)
app.config.from_object('config.Config')

db.init_app(app)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/add_channel', methods=['GET', 'POST'])
def add_channel():
    if request.method == 'POST':
        telegram_id = request.form['telegram_id']
        username = request.form['username']
        channel_name = request.form['channel_name']
        channel_link = request.form['channel_link']

        user = User.query.filter_by(telegram_id=telegram_id).first()
        if not user:
            user = User(telegram_id=telegram_id, username=username)
            db.session.add(user)
            db.session.commit()

        channel = Channel(name=channel_name, link=channel_link, owner=user)
        db.session.add(channel)
        db.session.commit()

        flash('Channel added successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('add_channel.html')

@app.route('/add_payment', methods=['GET', 'POST'])
def add_payment():
    if request.method == 'POST':
        payment_method = request.form['payment_method']
        account_details = request.form['account_details']
        # Assuming this logic is implemented to handle payments
        flash('Payment method added successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('add_payment.html')

@app.route('/create_giveaway', methods=['POST'])
def create_giveaway():
    channel = request.form['channel']
    giveaway_name = request.form['giveaway_name']
    prize_amount = request.form['prize_amount']
    participants_count = request.form['participants_count']
    end_date = request.form['end_date']
    
    # Fetch the selected channel from the database
    selected_channel = Channel.query.filter_by(username=channel).first()
    
    if selected_channel:
        # Save giveaway to the database
        new_giveaway = Giveaway(
            channel_id=selected_channel.id,
            name=giveaway_name,
            prize_amount=prize_amount,
            participants_count=participants_count,
            end_date=end_date
        )
        db.session.add(new_giveaway)
        db.session.commit()

        # Optionally, you can post a message to the channel
        bot.send_message(selected_channel.chat_id, f"🎉 New Giveaway: {giveaway_name}!\nPrize: {prize_amount} Birr\nParticipants: {participants_count}\nEnd Date: {end_date}")
        
        return redirect(url_for('home'))
    else:
        return "Channel not found.", 404

@app.route('/announce_winners/<int:giveaway_id>', methods=['GET'])
def announce_winners(giveaway_id):
    giveaway = Giveaway.query.get_or_404(giveaway_id)
    participants = Participant.query.filter_by(giveaway_id=giveaway_id).all()

    winners = random.sample(participants, giveaway.participant_count)

    giveaway.winners = [winner.id for winner in winners]
    db.session.commit()

    post_winners_to_channel(giveaway, winners)

    return render_template('announce_winners.html', winners=winners)
