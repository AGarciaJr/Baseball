from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
import pymysql
import logging

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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 