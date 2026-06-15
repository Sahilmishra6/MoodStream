from flask import Flask, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from db_config import get_db_connection
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev_key")

# home page-------------
@app.route('/')
def home():
    return render_template('index.html')
# about page--------------------
@app.route('/about')
def about():
    return render_template('about.html')

# -------------------------------------
# Login Required Decorator
# -------------------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function

# -------------------------------------
# Login Route
# -------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password']

        db = cursor = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
            user = cursor.fetchone()
        except Exception as e:
            return f"Database error: {e}"
        finally:
            if cursor: cursor.close()
            if db: db.close()

        if user and check_password_hash(user['password'], password):
            session['user'] = user['id']
            session['username'] = user['username']
            return redirect('/dashboard')

        flash("Invalid email or password")
        return redirect('/')

    return render_template('login.html')

# -------------------------------------
# Signup Route
# -------------------------------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not username or not email or not password:
            flash("All fields are required")
            return redirect('/signup')

        db = cursor = None
        try:
            db = get_db_connection()
            cursor = db.cursor()

            cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
            if cursor.fetchone():
                flash("Email already registered")
                return redirect('/signup')

            hashed_password = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                (username, email, hashed_password)
            )
            db.commit()
        except Exception as e:
            return f"Database error: {e}"
        finally:
            if cursor: cursor.close()
            if db: db.close()

        flash("Signup successful! Please login.")
        return redirect('/')

    return render_template('signup.html')

# -------------------------------------
# Dashboard Route
# -------------------------------------
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=session.get('username'))

# -------------------------------------
# Mood + Genre Selection Route (UPDATED)
# -------------------------------------
@app.route('/mood', methods=['GET', 'POST'])
@login_required
def mood():
    if request.method == 'POST':
        selected_mood = request.form.get('mood')
        selected_genre = request.form.get('genre')  # NEW

        if not selected_mood or not selected_genre:
            flash("Please select both mood and genre")
            return redirect('/mood')

        session['mood'] = selected_mood
        session['genre'] = selected_genre  # NEW

        return redirect('/recommendation')

    return render_template('mood.html')

# -------------------------------------
# Recommendation Route (UPDATED)
# -------------------------------------
@app.route('/recommendation')
@login_required
def recommendation():
    mood = session.get('mood')
    genre = session.get('genre')  # NEW

    if not mood or not genre:
        return redirect('/mood')

    db = cursor = None
    try:
        db = get_db_connection()
        cursor = db.cursor()

        # Music filtered by mood + genre
        cursor.execute(
            "SELECT * FROM music WHERE mood=%s",
            (mood,)
        )
        music = cursor.fetchall()

        # Movies filtered by mood + genre
        cursor.execute(
            "SELECT * FROM movies WHERE genre=%s",
            (genre)
        )
        movies = cursor.fetchall()

    except Exception as e:
        return f"Database error: {e}"

    finally:
        if cursor: cursor.close()
        if db: db.close()

    return render_template(
        'recommendation.html',
        music=music,
        movies=movies,
        mood=mood,
        genre=genre  # optional for display
    )

# -------------------------------------
# Logout Route
# -------------------------------------
@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash("Logged out successfully")
    return redirect('/')



# -------------------------------------
# Run App
# -------------------------------------
if __name__ == '__main__':
    import os
    # Pull the port from Render's environment, or fallback to 5001 for local testing
    port = int(os.environ.get("PORT", 5001))
    
    # host="0.0.0.0" allows Render to see the application
    # debug should ideally be False in production, but we can leave it or manage it via env
    app.run(host="0.0.0.0", port=port, debug=False)
