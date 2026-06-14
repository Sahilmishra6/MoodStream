from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from db_config import get_db_connection

app = Flask(__name__)
app.secret_key = "secret123"

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            session['user'] = user['id']
            return redirect('/dashboard')
        return "Invalid login"

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO users(username,email,password) VALUES(%s,%s,%s)",
            (username, email, password)
        )
        db.commit()
        return redirect('/')

    return render_template('signup.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/mood', methods=['GET', 'POST'])
def mood():
    if request.method == 'POST':
        selected_mood = request.form['mood']
        session['mood'] = selected_mood
        return redirect('/recommendation')

    return render_template('mood.html')


@app.route('/recommendation')
def recommendation():
    mood = session.get('mood')

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM music WHERE mood=%s", (mood,))
    music = cursor.fetchall()

    cursor.execute("SELECT * FROM movies WHERE mood=%s", (mood,))
    movies = cursor.fetchall()

    return render_template(
        'recommendation.html',
        music=music,
        movies=movies,
        mood=mood
    )

if __name__ == '__main__':
    app.run(debug=True)
