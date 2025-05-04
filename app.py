from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
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
    return render_template('index.html')

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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 