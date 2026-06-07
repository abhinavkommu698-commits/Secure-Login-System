from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Regexp, ValidationError
import sqlite3
import datetime
import logging
import os
from functools import wraps

app = Flask(__name__)

# ============================================================
# Security Configuration
# ============================================================
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'cybersecure2024keychangeinprod')
app.config['WTF_CSRF_TIME_LIMIT'] = 3600
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(hours=1)

# ============================================================
# Initialize Flask Extensions
# ============================================================
bcrypt = Bcrypt(app)

# CSRF Protection using Flask-WTF to prevent Cross-Site Request Forgery
# This ensures all POST requests include a valid CSRF token
csrf = CSRFProtect(app)

# Flask-Login for session management
# It handles login sessions, user loading, and access control
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'warning'

# ============================================================
# Security Logging Configuration
# ============================================================
# Logging security events helps in forensic analysis and monitoring
logging.basicConfig(
    filename='security.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
security_logger = logging.getLogger('security')

# ============================================================
# Database Setup - SQLite
# ============================================================
# Parameterized queries (sqlite3 module with ? placeholders) inherently prevent SQL Injection
# Never use string formatting or concatenation to build SQL queries
DATABASE = 'database.db'

def get_db_connection():
    """Create and return a database connection with row factory for dict-like access."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize the database with the users table if it doesn't exist."""
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL,
            failed_login_attempts INTEGER DEFAULT 0,
            account_locked_until TEXT DEFAULT NULL
        )
    ''')
    conn.commit()
    conn.close()
    print("[+] Database initialized successfully.")

def upgrade_database():
    """Add missing columns to existing users table and migrate is_active to account_status."""
    conn = get_db_connection()
    columns = [row['name'] for row in conn.execute("PRAGMA table_info(users)").fetchall()]
    
    if 'login_count' not in columns:
        conn.execute('ALTER TABLE users ADD COLUMN login_count INTEGER DEFAULT 0')
    if 'last_login' not in columns:
        conn.execute('ALTER TABLE users ADD COLUMN last_login TEXT DEFAULT NULL')
    
    if 'is_active' in columns and 'account_status' not in columns:
        conn.execute('''
            CREATE TABLE users_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                failed_login_attempts INTEGER DEFAULT 0,
                account_locked_until TEXT DEFAULT NULL,
                login_count INTEGER DEFAULT 0,
                last_login TEXT DEFAULT NULL,
                account_status INTEGER DEFAULT 1
            )
        ''')
        conn.execute('''
            INSERT INTO users_new (id, username, email, password_hash, created_at, failed_login_attempts, account_locked_until, login_count, last_login, account_status)
            SELECT id, username, email, password_hash, created_at, failed_login_attempts, account_locked_until,
                   COALESCE(login_count, 0), last_login, COALESCE(is_active, 1)
            FROM users
        ''')
        conn.execute('DROP TABLE users')
        conn.execute('ALTER TABLE users_new RENAME TO users')
    elif 'account_status' not in columns:
        conn.execute('ALTER TABLE users ADD COLUMN account_status INTEGER DEFAULT 1')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_database()
upgrade_database()

# ============================================================
# User Model for Flask-Login
# ============================================================
class User(UserMixin):
    """User model that implements Flask-Login's UserMixin interface."""
    def __init__(self, id, username, email, password_hash, created_at, failed_login_attempts=0, account_locked_until=None, otp_secret=None, login_count=0, last_login=None, account_status=1):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at
        self.failed_login_attempts = failed_login_attempts
        self.account_locked_until = account_locked_until
        self.otp_secret = otp_secret
        self.login_count = login_count or 0
        self.last_login = last_login
        self.account_status = bool(account_status)
    
    @staticmethod
    def get(user_id):
        """Retrieve a user by ID from the database using parameterized query."""
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE id = ?', (user_id,)
        ).fetchone()
        conn.close()
        if user:
            return User(**dict(user))
        return None

@login_manager.user_loader
def load_user(user_id):
    """Flask-Login callback to reload the user object from the session."""
    return User.get(user_id)

# ============================================================
# Custom Decorators for Authorization
# ============================================================
def admin_required(f):
    """Custom decorator to restrict access to admin users only."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.username != 'admin':
            flash('Access denied. Admin privileges required.', 'danger')
            security_logger.warning(f'Unauthorized access attempt by user: {current_user.username if current_user.is_authenticated else "anonymous"}')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def log_authentication_event(event_type, username, status, ip_address=None):
    """Log authentication events for security monitoring."""
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ip = ip_address or request.remote_addr
    security_logger.info(f'[{event_type}] User: {username}, Status: {status}, IP: {ip}, Time: {timestamp}')

# ============================================================
# WTForms Classes - Input Validation & CSRF
# ============================================================
class RegistrationForm(FlaskForm):
    """
    Registration form with built-in CSRF protection and validation.
    
    Password strength requirements enforced via Regexp validator:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character (!@#$%^&*)
    """
    username = StringField(
        'Username',
        validators=[
            DataRequired(message='Username is required.'),
            Length(min=4, max=20, message='Username must be between 4 and 20 characters.'),
            Regexp(r'^[a-zA-Z0-9_]+$', message='Username can only contain letters, numbers, and underscores.')
        ]
    )
    email = StringField(
        'Email',
        validators=[
            DataRequired(message='Email is required.'),
            Email(message='Enter a valid email address.')
        ]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message='Password is required.'),
            Length(min=8, message='Password must be at least 8 characters long.'),
            Regexp(
                r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*])',
                message='Password must contain uppercase, lowercase, digit, and special character (!@#$%^&*).'
            )
        ]
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(message='Please confirm your password.')]
    )
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        """Check if username already exists in database using parameterized query."""
        conn = get_db_connection()
        user = conn.execute(
            'SELECT id FROM users WHERE username = ?', (username.data,)
        ).fetchone()
        conn.close()
        if user:
            raise ValidationError('This username is already taken. Please choose another.')

    def validate_email(self, email):
        """Check if email already exists in database using parameterized query."""
        conn = get_db_connection()
        user = conn.execute(
            'SELECT id FROM users WHERE email = ?', (email.data,)
        ).fetchone()
        conn.close()
        if user:
            raise ValidationError('An account with this email already exists.')

    def validate_confirm_password(self, confirm_password):
        """Ensure both password fields match."""
        if self.password.data != confirm_password.data:
            raise ValidationError('Passwords must match.')

class LoginForm(FlaskForm):
    """Login form with CSRF protection and input validation."""
    username_email = StringField(
        'Username or Email',
        validators=[DataRequired(message='Please enter your username or email.')]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(message='Password is required.')]
    )
    otp_code = StringField(
        '2FA Code (if enabled)'
    )
    submit = SubmitField('Login')

class LockoutForm(FlaskForm):
    """Simple form for CSRF protection on lockout/support pages."""
    submit = SubmitField('Submit')

# ============================================================
# Routes - Home
# ============================================================
@app.route('/')
def home():
    """Landing page with feature overview."""
    return render_template('home.html')

# ============================================================
# Routes - Registration
# ============================================================
@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration with full validation and bcrypt password hashing."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        username = form.username.data.strip()
        email = form.email.data.strip().lower()
        password = form.password.data
        
        # BCrypt password hashing
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        created_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # SECURITY: Parameterized SQL query prevents SQL injection
        conn = get_db_connection()
        try:
            conn.execute(
                'INSERT INTO users (username, email, password_hash, created_at) VALUES (?, ?, ?, ?)',
                (username, email, password_hash, created_at)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            flash('Registration failed. Username or email may already exist.', 'danger')
            return redirect(url_for('register'))

        conn.close()

        log_authentication_event('REGISTRATION', username, 'SUCCESS')
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

# ============================================================
# Routes - Login
# ============================================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login with credential verification and account lockout protection."""
    form = LoginForm()
    
    if form.validate_on_submit():
        login_input = form.username_email.data.strip().lower()
        password = form.password.data
        
        # SECURITY: Parameterized query to look up user by username OR email
        # Using SQL UNION with parameterized queries prevents SQL Injection
        conn = get_db_connection()
        user = conn.execute('''
            SELECT * FROM users WHERE LOWER(username) = ? OR LOWER(email) = ?
        ''', (login_input, login_input)).fetchone()
        conn.close()
        
        if not user:
            log_authentication_event('LOGIN_FAILED', login_input, 'USER_NOT_FOUND')
            flash('Invalid credentials. Please try again.', 'danger')
            return render_template('login.html', form=form)

        user_dict = dict(user)

        if user_dict.get('account_locked_until'):
            locked_until = datetime.datetime.fromisoformat(user_dict['account_locked_until'])
            if datetime.datetime.now() < locked_until:
                remaining = (locked_until - datetime.datetime.now()).total_seconds() / 60
                flash(f'Account locked due to multiple failed attempts. Try again in {int(remaining)} minutes.', 'danger')
                return render_template('login.html', form=form)
            else:
                conn = get_db_connection()
                conn.execute(
                    'UPDATE users SET failed_login_attempts = 0, account_locked_until = NULL WHERE id = ?',
                    (user_dict['id'],)
                )
                conn.commit()
                conn.close()

        if bcrypt.check_password_hash(user_dict['password_hash'], password):
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            conn = get_db_connection()
            conn.execute(
                'UPDATE users SET failed_login_attempts = 0, login_count = COALESCE(login_count, 0) + 1, last_login = ? WHERE id = ?',
                (now, user_dict['id'])
            )
            conn.commit()
            conn.close()

            user_obj = User.get(user_dict['id'])
            login_user(user_obj)

            log_authentication_event('LOGIN_SUCCESS', user_obj.username, 'SUCCESS')
            flash(f'Welcome back, {user_obj.username}!', 'success')
            next_page = request.args.get('next')
            if next_page and not next_page.startswith('/'):
                next_page = None
            return redirect(next_page or url_for('dashboard'))
        else:
            new_attempts = (user_dict.get('failed_login_attempts') or 0) + 1
            account_locked_until = None
            if new_attempts >= 5:
                account_locked_until = (datetime.datetime.now() + datetime.timedelta(minutes=15)).isoformat()
                flash('Account locked for 15 minutes due to too many failed attempts.', 'danger')

            conn = get_db_connection()
            conn.execute(
                'UPDATE users SET failed_login_attempts = ?, account_locked_until = ? WHERE id = ?',
                (new_attempts, account_locked_until, user_dict['id'])
            )
            conn.commit()
            conn.close()

            log_authentication_event('LOGIN_FAILED', login_input, 'INVALID_PASSWORD')
            flash('Invalid credentials. Please try again.', 'danger')
    
    return render_template('login.html', form=form)

# ============================================================
# Routes - Dashboard (Protected)
# ============================================================
@app.route('/dashboard')
@login_required
def dashboard():
    created_at = datetime.datetime.strptime(current_user.created_at, '%Y-%m-%d %H:%M:%S')
    days_active = (datetime.datetime.now() - created_at).days
    last_login = None
    if current_user.last_login:
        try:
            last_login = datetime.datetime.strptime(current_user.last_login, '%Y-%m-%d %H:%M:%S')
        except Exception:
            last_login = None
    return render_template(
        'dashboard.html',
        user=current_user,
        days_active=days_active,
        last_login=last_login
    )

# ============================================================
# Routes - Logout
# ============================================================
@app.route('/logout')
@login_required
def logout():
    """Log out the current user by clearing their session."""
    username = current_user.username
    logout_user()
    log_authentication_event('LOGOUT', username, 'SUCCESS')
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('home'))

# ============================================================
# Routes - Lockout Info (Public)
# ============================================================
@app.route('/admin/users')
@login_required
def admin_users():
    conn = get_db_connection()
    users = conn.execute(
        'SELECT id, username, email, created_at, account_status FROM users ORDER BY id ASC'
    ).fetchall()
    conn.close()
    return render_template('admin_users.html', users=users)


@app.route('/lockout-info')
def lockout_info():
    """Public page explaining the account lockout policy."""
    return render_template('lockout_info.html')

# ============================================================
# Error Handlers - Security-Focused
# ============================================================
@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors securely without leaking system information."""
    security_logger.warning(f'404 Not Found: {request.path} from IP {request.remote_addr}')
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors without exposing sensitive details to users."""
    security_logger.error(f'500 Internal Server Error: {str(error)}')
    return render_template('500.html'), 500

# ============================================================
# Application Entry Point
# ============================================================
if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════════╗
    ║   Secure Login System - Flask App         ║
    ║   Running in development mode            ║
    ║       Access at: http://localhost:5001        ║
    ╚══════════════════════════════════════════╝
    """)
    # Note: In production, use gunicorn/nginx and set SECRET_KEY in environment
    app.run(debug=True, port=5001)
