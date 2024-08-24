from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Homepage for the giveaway creator
@app.route('/')
def home():
    return render_template('create_giveaway.html')

# Page to create a giveaway
@app.route('/create', methods=['GET', 'POST'])
def create_giveaway():
    if request.method == 'POST':
        # Handle giveaway creation logic
        bot_username = request.form['bot_username']
        giveaway_amount = request.form['giveaway_amount']
        participant_count = request.form['participant_count']
        end_date = request.form['end_date']
        # Save the details and redirect to the confirmation page
        return redirect(url_for('giveaway_created'))
    return render_template('create_giveaway.html')

# Confirmation page after giveaway is created
@app.route('/created')
def giveaway_created():
    return "Giveaway created successfully!"

# Page for participants to join the giveaway
@app.route('/join')
def join_giveaway():
    return render_template('join_giveaway.html')

# Page to show winners
@app.route('/winners')
def show_winners():
    return render_template('winners.html')

if __name__ == '__main__':
    app.run(debug=True)
