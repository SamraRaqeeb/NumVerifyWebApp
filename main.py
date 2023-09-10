from flask import Flask, request, render_template, redirect, url_for, flash
import phonenumbers
from phonenumbers import timezone, carrier, geocoder, NumberParseException
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.secret_key = 'samra@12345'

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Sample user data (replace with your user database)
users = {
    'samra': {'password': 'samra@123'},
    'atif': {'password': 'atif'},
    'hadi': {'password': 'hadi'}
}

class User(UserMixin):
    def __init__(self, id):
        self.id = id
        self.username = None
        self.password_hash = None

    def get_id(self):
        return str(self.id)

# User loader function for Flask-Login
@login_manager.user_loader
def load_user(username):
    if username in users:
        return User(username)
    return None

@app.route('/', methods=['GET', 'POST'])
@login_required  # Require authentication for this route
def index():
    formatted_number = None  # Initialize formatted_number here

    if request.method == 'POST':
        number = request.form['number']
        format_option = request.form['format']

        try:
            phone = phonenumbers.parse(number)
            timezones = timezone.time_zones_for_number(phone)
            carr = carrier.name_for_number(phone, "en")
            reg = geocoder.description_for_number(phone, "en")

            is_valid = phonenumbers.is_valid_number(phone)
            is_possible = phonenumbers.is_possible_number(phone)
            number_type = phonenumbers.number_type(phone)
            is_toll_free = carr.lower().find("toll free") != -1
            country_code = phone.country_code
            national_number = phone.national_number

            if format_option == 'national':
                formatted_number = phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.NATIONAL)
            elif format_option == 'international':
                formatted_number = phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            else:
                formatted_number = number

            return render_template('result.html', number=formatted_number, country_code=country_code, national_number=national_number, timezones=timezones, carrier=carr, region=reg, is_valid=is_valid, is_possible=is_possible, number_type=number_type, is_toll_free=is_toll_free)
        except NumberParseException:
            error_msg = "Invalid phone number format. Please enter a valid number."
            return render_template('index.html', error=error_msg)

    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username]['password'] == password:
            user = User(username)
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))

        flash('Invalid username or password.', 'error')

    return render_template('login.html')

@app.route('/logout')
@login_required  # Require authentication for this route
def logout():
    logout_user()
    flash('Logout successful!', 'success')
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
