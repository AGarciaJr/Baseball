from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
import pymysql
import logging
from functools import wraps
from datetime import datetime
from sqlalchemy import text
from db import get_db_connection, award_achievement

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize PyMySQL
pymysql.install_as_MySQLdb()

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-please-change')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql://root:password@localhost/Sandlot2TheSQL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure session settings
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)  # Increased length for hash
    is_admin = db.Column(db.Boolean, default=False)
    is_banned = db.Column(db.Boolean, default=False)
    score = db.Column(db.Integer, default=0)

    def set_password(self, password):
        if not password:
            raise ValueError("Password cannot be empty")
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        if not password or not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

class Team(db.Model):
    __tablename__ = 'teams'
    teams_ID = db.Column('teams_ID', db.Integer, primary_key=True)
    teamID = db.Column('teamID', db.String(3), nullable=False)
    yearID = db.Column('yearID', db.Integer, nullable=False)
    team_name = db.Column('team_name', db.String(50))

class UserSelection(db.Model):
    __tablename__ = 'user_selections'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    team_id = db.Column(db.String(3), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    score = None
    if current_user.is_authenticated:
        result = db.session.execute(text("""
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) AS correct
            FROM trivia_answers
            WHERE user_id = :uid
        """), {"uid": current_user.id}).fetchone()

        score = f"{result.correct or 0} / {result.total or 0}"

    return render_template('index.html', score=score)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        logger.debug(f"Registration attempt for username: {username}")
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            logger.debug(f"Username already exists: {username}")
            flash('Username already exists. Please choose a different one.')
            return redirect(url_for('register'))
        
        # Create new user
        user = User(username=username)
        user.set_password(password)
        
        # If this is the first user, make them an admin
        if User.query.count() == 0:
            user.is_admin = True
            logger.debug("First user created, making admin")
        
        db.session.add(user)
        db.session.commit()
        
        logger.debug(f"User created successfully: {username}")
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Username and password are required')
            return render_template('login.html'), 400
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if user.is_banned:
                flash('Your account has been banned. Please contact an administrator.')
                return render_template('login.html'), 403
            
            login_user(user)
            logger.info(f"User logged in successfully: {username}")
            
            # Redirect admins to the admin dashboard
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            
            return redirect(url_for('index'))
        
        flash('Invalid username or password')
        return render_template('login.html'), 401
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logger.debug(f"User logged out: {current_user.username}")
    logout_user()
    return redirect(url_for('index'))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You do not have permission to access this page.')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    users = User.query.all()
    return render_template('admin/dashboard.html', users=users)

@app.route('/admin/user/<int:user_id>/toggle_ban', methods=['POST'])
@login_required
@admin_required
def toggle_user_ban(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot ban yourself.')
        return redirect(url_for('admin_dashboard'))
    
    user.is_banned = not user.is_banned
    db.session.commit()
    action = 'banned' if user.is_banned else 'unbanned'
    flash(f'User {user.username} has been {action}.')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/user/<int:user_id>/toggle_admin', methods=['POST'])
@login_required
@admin_required
def toggle_user_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot modify your own admin status.')
        return redirect(url_for('admin_dashboard'))
    
    user.is_admin = not user.is_admin
    db.session.commit()
    action = 'granted admin privileges to' if user.is_admin else 'removed admin privileges from'
    flash(f'Successfully {action} {user.username}.')
    return redirect(url_for('admin_dashboard'))

@app.route('/select_team', methods=['GET', 'POST'])
@login_required
def select_team():
    if request.method == 'POST':
        team_id = request.form.get('team_id')
        if team_id:
            # Log the selection
            selection = UserSelection(user_id=current_user.id, team_id=team_id)
            db.session.add(selection)
            db.session.commit()
            
            # Get no-hitters for the team
            no_hitters_by = db.session.execute(
                """
                SELECT * FROM no_hitters 
                WHERE pitcher_team = :team_id
                ORDER BY yearID DESC
                """,
                {"team_id": team_id}
            ).fetchall()
            
            no_hitters_against = db.session.execute(
                """
                SELECT * FROM no_hitters 
                WHERE opponent_team = :team_id
                ORDER BY yearID DESC
                """,
                {"team_id": team_id}
            ).fetchall()
            
            return render_template(
                'no_hitters.html',
                no_hitters_by=no_hitters_by,
                no_hitters_against=no_hitters_against,
                team_id=team_id
            )
    
    # Get unique teams for dropdown
    teams = db.session.execute(
        """
        SELECT DISTINCT teamID, team_name 
        FROM teams 
        WHERE team_name IS NOT NULL 
        ORDER BY team_name
        """
    ).fetchall()
    
    return render_template('select_team.html', teams=teams)

@app.route('/snake')
def snake():
    return render_template('snake.html')

@app.route("/api/trivia/random", methods=["GET"])
def get_random_trivia():
    query = text("""
        SELECT id, question_text, choice_a, choice_b, choice_c, choice_d, correct_answer
        FROM trivia_questions
        ORDER BY RAND()
        LIMIT 1
    """)
    result = db.session.execute(query).fetchone()

    if not result:
        return jsonify({"error": "No trivia questions available"}), 404

    return jsonify({
        "id": result.id,
        "question": result.question_text,
        "choices": {
            "A": result.choice_a,
            "B": result.choice_b,
            "C": result.choice_c,
            "D": result.choice_d
        },
        "correct_answer": result.correct_answer
    })

@app.route('/trivia')
@login_required
def trivia_page():
    return render_template('trivia.html')

@app.route('/api/trivia/answer', methods=['POST'])
@login_required
def submit_trivia_answer():
    data = request.get_json()
    question_id = data.get("question_id")
    selected = data.get("selected_answer")

    if not question_id or not selected:
        return jsonify({"error": "Missing question_id or selected_answer"}), 400

    result = db.session.execute(text("""
        SELECT correct_answer FROM trivia_questions
        WHERE id = :qid
    """), {"qid": question_id}).fetchone()

    if not result:
        return jsonify({"error": "Invalid question ID"}), 404

    correct = result.correct_answer == selected

    # Insert into trivia_answers
    db.session.execute(text("""
        INSERT INTO trivia_answers (user_id, question_id, selected_answer, is_correct)
        VALUES (:uid, :qid, :selected, :correct)
    """), {
        "uid": current_user.id,
        "qid": question_id,
        "selected": selected,
        "correct": correct
    })
    db.session.commit()

    # ====== NEW: Check correct count and award achievements ======
    score_result = db.session.execute(text("""
        SELECT SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) AS correct
        FROM trivia_answers
        WHERE user_id = :uid
    """), {"uid": current_user.id}).fetchone()

    correct_score = score_result.correct or 0

    from db import award_achievement
    achievements_awarded = []

    if correct_score >= 10:
        if award_achievement(current_user.id, "Bronze Medal", "Scored 10 correct answers!", "static/achievements/bronze.png"):
            achievements_awarded.append("Bronze Medal")
    if correct_score >= 200:
        if award_achievement(current_user.id, "Silver Medal", "Scored 200 correct answers!", "static/achievements/silver.png"):
            achievements_awarded.append("Silver Medal")
    if correct_score >= 500:
        if award_achievement(current_user.id, "Gold Medal", "Scored 500 correct answers!", "static/achievements/gold.png"):
            achievements_awarded.append("Gold Medal")

    return jsonify({
        "correct": correct,
        "correct_answer": result.correct_answer,
        "achievements": achievements_awarded  # 👈 return this for frontend to toast
    })


@app.route('/api/trivia/score', methods=['GET'])
@login_required
def get_trivia_score():
    result = db.session.execute(text("""
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) AS correct
        FROM trivia_answers
        WHERE user_id = :uid
    """), {"uid": current_user.id}).fetchone()

    return jsonify({
        "total": result.total or 0,
        "correct": result.correct or 0
    })

@app.route('/api/trivia/generate', methods=['POST'])
@login_required
@admin_required
def generate_trivia_batch():
    from scripts.generate_trivia import generate_trivia
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "status": "error",
                "message": "No data provided"
            }), 400
            
        category = data.get('category')
        count = data.get('count', 20)
        
        # Validate count
        try:
            count = int(count)
            if count < 1 or count > 100:
                return jsonify({
                    "status": "error",
                    "message": "Count must be between 1 and 100"
                }), 400
        except (TypeError, ValueError):
            return jsonify({
                "status": "error",
                "message": "Invalid count value"
            }), 400
        
        generated_questions = generate_trivia(category, count)
        return jsonify({
            "status": "success",
            "message": f"✅ Generated {len(generated_questions)} trivia questions" + 
                      (f" for category '{category}'" if category else " across all categories"),
            "questions": generated_questions
        })
    except Exception as e:
        logger.error(f"Error generating trivia: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"❌ Error generating questions: {str(e)}"
        }), 500

@app.route('/profile')
@login_required
def profile():
    result = db.session.execute(text("""
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) AS correct
        FROM trivia_answers
        WHERE user_id = :uid
    """), {"uid": current_user.id}).fetchone()

    stats = {
        "correct": result.correct or 0,
        "total": result.total or 0
    }

    return render_template('profile.html', stats=stats)

@app.route('/team-nohitters-summary')
def team_nohitters_summary():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT t.teamID, MAX(t.team_name) AS team_name, COUNT(*) AS no_hitter_count
        FROM teams t
        JOIN no_hitters nh ON t.teams_ID = nh.team_id OR t.teams_ID = nh.opponent_id
        GROUP BY t.teamID
        ORDER BY t.teamID
    """)
    teams = cur.fetchall()

    cur.close()
    conn.close()
    return render_template('team_nohitters_summary.html', teams=teams)

@app.route('/team-nohitters/<team_id>')
def team_nohitters_detail(team_id):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    # Get display name from one team row
    cur.execute("SELECT teamID, team_name FROM teams WHERE teamID = %s LIMIT 1", (team_id,))
    team = cur.fetchone()

    # No-hitters thrown BY this teamID
    cur.execute("""
        SELECT nh.game_date, t.teamID, t.team_name
        FROM no_hitters nh
        JOIN teams t ON nh.team_id = t.teams_ID
        WHERE t.teamID = %s
    """, (team_id,))
    thrown_by = cur.fetchall()

    # No-hitters thrown AGAINST this teamID
    cur.execute("""
        SELECT nh.game_date, t.teamID AS pitcher_teamID, t.team_name AS pitcher_team_name
        FROM no_hitters nh
        JOIN teams t ON nh.team_id = t.teams_ID
        WHERE nh.opponent_id IN (
            SELECT teams_ID FROM teams WHERE teamID = %s
        )
    """, (team_id,))
    thrown_against = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('team_nohitters_detail.html',
        team=team, thrown_by=thrown_by, thrown_against=thrown_against)

@app.route('/team-nohitters-redirect', methods=['POST'])
def team_nohitters_detail_redirect():
    team_id = request.form['team_id']
    return redirect(url_for('team_nohitters_detail', team_id=team_id))

@app.route('/achievements')
@login_required
def view_achievements():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT name, description, image_path, date_earned
        FROM achievements
        WHERE user_id = %s
        ORDER BY date_earned DESC
    """, (current_user.id,))
    achievements = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("achievements.html", achievements=achievements)

@app.route('/all-nohitters')
@login_required
def all_nohitters():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT nh.game_date, t1.team_name AS pitcher_team, t2.team_name AS opponent_team, nh.is_perfect, nh.num_pitchers, nh.notes
        FROM no_hitters nh
        JOIN teams t1 ON nh.team_id = t1.teams_ID
        JOIN teams t2 ON nh.opponent_id = t2.teams_ID
        ORDER BY nh.game_date DESC
    """)
    nohitters = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('all_nohitters.html', nohitters=nohitters)

@app.route('/api/leaderboard')
def get_leaderboard():
    query = text("""
        SELECT u.username, COUNT(*) AS score
        FROM user u
        JOIN trivia_answers a ON u.id = a.user_id
        WHERE (u.is_banned IS NULL OR u.is_banned = 0)
          AND a.is_correct = 1
        GROUP BY u.id
        ORDER BY score DESC
        LIMIT 10
    """)
    result = db.session.execute(query)
    leaderboard = [{'username': row[0], 'score': row[1]} for row in result]
    return jsonify(leaderboard)



@app.route('/leaderboard')
def leaderboard_page():
    return render_template('leaderboard.html')

@app.route('/api/hangman/start', methods=['GET'])
def start_hangman():
    query = text("""
        SELECT CONCAT(nameFirst, ' ', nameLast) AS fullname
        FROM people
        WHERE playerID IN (
            SELECT playerID FROM halloffame
            WHERE inducted = 'Y'
        )
        AND nameFirst IS NOT NULL AND nameLast IS NOT NULL
        ORDER BY RAND()
        LIMIT 1;
    """)
    result = db.session.execute(query).fetchone()
    if not result:
        return jsonify({'error': 'No names found'}), 404

    word = result[0].upper()

    # Store session data
    session['hangman_word'] = word
    session['correct_guesses'] = []
    session['wrong_guesses'] = []
    session['max_attempts'] = 6

    # Return masked word like "_ _ _ _   _ _ _ _"
    masked = ''.join([char if char == ' ' else '_' for char in word])
    return jsonify({'masked': masked, 'attempts_left': 6})

@app.route('/api/hangman/guess', methods=['POST'])
def guess_letter():
    data = request.get_json()
    letter = data.get('letter', '').upper()

    word = session.get('hangman_word', '')
    correct = session.get('correct_guesses', [])
    wrong = session.get('wrong_guesses', [])
    max_attempts = session.get('max_attempts', 6)

    if not word or not letter.isalpha() or len(letter) != 1:
        return jsonify({'error': 'Invalid state or input'}), 400

    if letter in correct or letter in wrong:
        return jsonify({'message': 'Already guessed'}), 200

    if letter in word:
        correct.append(letter)
        session['correct_guesses'] = correct
    else:
        wrong.append(letter)
        session['wrong_guesses'] = wrong

    masked = ''.join([char if (char in correct or char == ' ') else '_' for char in word])
    attempts_left = max_attempts - len(wrong)

    game_over = attempts_left <= 0
    won = '_' not in masked

    response = {
        'masked': masked,
        'wrong_guesses': wrong,
        'attempts_left': attempts_left,
        'game_over': game_over,
        'won': won
    }

    if game_over:
        response['correct_answer'] = word

    return jsonify(response)

@app.route('/hangman')
def hangman_page():
    return render_template('hangman.html')

@app.route("/api/award_achievement", methods=["POST"])
def api_award_achievement():
    data = request.get_json()
    name = data.get("name")
    description = data.get("description")
    image_path = data.get("image_path", None)

    if not current_user.is_authenticated:
        return jsonify({"success": False, "error": "Unauthorized"}), 401

    success = award_achievement(current_user.id, name, description, image_path)
    return jsonify({"success": success})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 