from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.db import get_db_connection

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def home():
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            session['role'] = user['username']
            print(session['role'])
            return redirect(url_for('patient.home'))
        else:
            flash("Invalid username or password", "error")
            return redirect(url_for('auth.login'))

    return render_template('login.html')
