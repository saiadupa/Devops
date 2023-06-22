from flask import Flask, render_template, request, redirect, url_for
import re
import hashlib
import sqlite3
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string

app = Flask(__name__)

NAME_REGEX = re.compile(r"^[a-zA-Z]+(?:\s+[a-zA-Z]+)*$")
USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_]{6,}$")
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
PASSWORD_REGEX = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$")


def create_table():
    conn = sqlite3.connect('devops.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS users
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 first_name TEXT,
                 last_name TEXT,
                 username TEXT,
                 email TEXT,
                 password TEXT,
                 dob TEXT,
                 otp TEXT)''')
    conn.commit()
    conn.close()


def register_user(first_name, last_name, username, email, password, dob):
    otp = generate_otp()
    conn = sqlite3.connect('devops.db')
    conn.execute(
        "INSERT INTO users (first_name, last_name, username, email, password, dob, otp) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (first_name, last_name, username, email, password, dob, otp))
    conn.commit()
    conn.close()
    send_otp_email(email, otp)


def generate_otp(length=4):
    return ''.join(random.choices(string.digits, k=length))


def send_otp_email(email, otp):
    smtp_host = 'smtp.gmail.com'
    smtp_port = 587
    sender_email = '20e51a6602@hitam.org'
    sender_password = 'jithenderadupa'

    subject = 'OTP for Registration'
    message = f'Your OTP is: {otp}'

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain'))

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, msg.as_string())


@app.route('/')
def index():
    return render_template('form.html')


@app.route('/register', methods=['POST'])
def register():
    create_table()

    first_name = request.form['first_name']
    last_name = request.form['last_name']
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    dob = request.form['dob']
    if not NAME_REGEX.match(first_name):
        return "Invalid first name"

    if not NAME_REGEX.match(last_name):
        return "Invalid last name"

    if not USERNAME_REGEX.match(username):
        return "Invalid username"

    if not EMAIL_REGEX.match(email):
        return "Invalid email"

    if not PASSWORD_REGEX.match(password):
        return "Invalid password"

    try:
        dob = datetime.datetime.strptime(dob, '%Y-%m-%d').strftime('%Y-%m-%d')
    except ValueError:
        return "Invalid date of birth"

    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    register_user(first_name, last_name, username, email, hashed_password, dob)

    return redirect(url_for('verify_otp', username=username))


@app.route('/verify_otp/<username>', methods=['GET', 'POST'])
def verify_otp(username):
    if request.method == 'GET':
        return render_template('otp.html', username=username)

    otp = request.form['otp']

    conn = sqlite3.connect('devops.db')
    cursor = conn.cursor()
    cursor.execute("SELECT otp FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    if result:
        if result[0] == otp:
            cursor.execute("UPDATE users SET otp=NULL WHERE username=?", (username,))
            conn.commit()
            conn.close()
            return redirect(url_for('success', username=username))

    return "Invalid OTP"


@app.route('/success/<username>')
def success(username):
    return render_template('main.html', username=username)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect('devops.db')
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    if result:
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        if result[0] == hashed_password:
            conn.close()
            return redirect(url_for('success', username=username))

    conn.close()
    return "Invalid username or password"


if __name__ == '__main__':
    app.run(debug=True)
