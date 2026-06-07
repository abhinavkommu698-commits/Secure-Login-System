# 🔐 Secure Login System

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-orange)](#)

A production-ready **Secure Login System** built with Python Flask, demonstrating industry-standard cybersecurity practices including bcrypt password hashing, CSRF protection, SQL injection prevention, account lockout policies, and secure session management.

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Security Features](#security-features)
- [Authentication Workflow](#authentication-workflow)
- [Screenshots](#screenshots)
- [Database Schema](#database-schema)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Project Overview

The **Secure Login System** is a cybersecurity-focused web application that demonstrates how to build a secure authentication system from scratch. It implements multiple layers of security to protect against common web vulnerabilities and authentication attacks.

This project is ideal for:
- **Cybersecurity intern portfolios**
- **Academic projects**
- **Interview preparation**
- **Learning secure coding practices**

### Key Highlights

| Feature | Status |
|---------|--------|
| bcrypt Password Hashing | ✅ |
| CSRF Protection (Flask-WTF) | ✅ |
| SQL Injection Prevention | ✅ |
| Account Lockout | ✅ |
| Secure Session Management | ✅ |
| Input Validation & Sanitization | ✅ |
| Security Event Logging | ✅ |
| Responsive Bootstrap 5 UI | ✅ |

---

## ✨ Features

### 1. User Registration
- Username, email, and password with full validation
- Duplicate username/email detection
- **Strong password enforcement**: Minimum 8 characters with uppercase, lowercase, digit, and special character
- Password confirmation with match verification
- Password hashing using bcrypt with automatic salt generation

### 2. User Login
- Username/email-based authentication
- bcrypt password verification
- Account lockout after **5 failed attempts** (15-minute lock)
- Failed attempt counter reset on successful login
- Security event logging for all login attempts

### 3. Security Features
- **bcrypt Password Hashing**: Industry-standard one-way hashing with automatic salting
- **CSRF Protection**: Flask-WTF tokens on every form submission
- **SQL Injection Prevention**: Parameterized SQL queries throughout
- **Account Lockout**: Protection against brute-force attacks
- **Input Validation**: WTForms validators for all user inputs
- **Secure Session Cookies**: HttpOnly, Secure, SameSite=Lax
- **Security Logging**: Comprehensive authentication event logging
- **Error Handling**: Custom 404/500 handlers without information leakage

### 4. Session Management
- Flask-Login for session state management
- Session protection and auto-renewal
- Secure cookie configuration
- Login required decorator for protected routes

### 5. Dashboard
- Protected dashboard page (`@login_required`)
- User information display
- Account creation date and active days
- Total login count and last login timestamp
- Account status: Active
- Security feature status indicators

### 6. Admin Panel
- Route: `/admin/users`
- View all registered users in a Bootstrap table
- Columns: User ID, Username, Email, Created Date, Status
- Password hashes are never displayed
- Accessible only to logged-in users

### 6. Frontend
- **Bootstrap 5** responsive design
- Dark cybersecurity-themed UI
- Gradient backgrounds with neon accents
- Card-based layouts
- Flash message notifications (success, danger, warning, info)
- Password visibility toggles
- Real-time password strength indicator
- Responsive navigation bar

---

## 🛠️ Technologies Used

| Technology | Purpose |
|------------|---------|
| **Python 3.8+** | Backend language |
| **Flask** | Web framework |
| **Flask-Login** | Session management |
| **Flask-Bcrypt** | Password hashing |
| **Flask-WTF** | Form validation & CSRF protection |
| **SQLite** | Database |
| **Bootstrap 5** | Frontend CSS framework |
| **WTForms** | Form handling & validation |
| **email_validator** | Email format validation for WTForms Email() |

---

## 📁 Project Structure

```
Secure-Login-System/
├── app.py                 # Main Flask application
├── database.db            # SQLite database (auto-created)
├── requirements.txt       # Python dependencies
├── README.md              # Documentation
├── .gitignore             # Git ignore rules
├── templates/             # HTML templates
│   ├── base.html          # Base template with layout
│   ├── home.html          # Landing page
│   ├── register.html      # Registration page
│   ├── login.html         # Login page
│   ├── dashboard.html     # Protected dashboard
│   ├── 404.html           # Not found error page
│   ├── 500.html           # Server error page
│   └── lockout_info.html  # Account lockout policy page
└── static/                # Static assets
    ├── css/
    └── js/
```

---

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Step-by-Step Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/secure-login-system.git
   cd secure-login-system
   ```

2. **Create and activate a virtual environment (recommended)**
   ```bash
   python -m venv venv

   # On Windows:
   venv\Scripts\activate

   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   ```
    Open your browser and go to: http://localhost:5000
    ```
    **Note for macOS users:** if port 5000 is in use, you can start on another port by changing the `port` argument in `app.py`, or stop the conflicting service like AirPlay Receiver.

6. **Troubleshooting: Email validation error**
    If you see `Exception: Install 'email_validator' for email validation support.`, run:
    ```bash
    pip install email_validator
    ```
    The `email_validator` package is required by WTForms' `Email()` validator for robust email format checking.

---

## 📖 Usage

### Registration Flow
1. Navigate to `/register` or click "Get Started"
2. Fill in username, email, password, and confirmation
3. Password must contain: uppercase letter, lowercase letter, digit, and special character (!@#$%^&*)
4. Submit the form to create your account
5. You'll be redirected to the login page

### Login Flow
1. Navigate to `/login` or click "Sign In"
2. Enter your username or email and password
3. (Optional) Enter 6-digit 2FA code if enabled
4. Submit credentials
5. On success: redirected to `/dashboard`
6. After 5 failed attempts: account locked for 15 minutes

### Dashboard
- View your account details
- Check security status indicators
- Logout via the navigation bar

---

## 🔒 Security Features

### bcrypt Password Hashing

```
Password → bcrypt.generate_password_hash() → "Hashed_String_With_Salt"
```

- Each password gets a **unique random salt** generated automatically
- bcrypt is computationally intensive (work factor), making brute-force attacks expensive
- The hash includes the salt, so no separate salt storage is needed
- Password verification uses `bcrypt.check_password_hash(hash, password)`

### SQL Injection Prevention

```python
# SAFE: Parameterized query using sqlite3's ? placeholders
conn.execute('SELECT * FROM users WHERE username = ?', (username,))

# NEVER DO THIS: String concatenation
conn.execute(f'SELECT * FROM users WHERE username = "{username}"')
```

All database queries in this project use **parameterized queries** to prevent SQL injection attacks.

### CSRF Protection

Flask-WTF automatically embeds a CSRF token in every form:
```html
<input type="hidden" name="csrf_token" value="..." />
```
This prevents **Cross-Site Request Forgery** attacks by ensuring form submissions originate from your site.

### Account Lockout

- **5 failed login attempts** triggers a 15-minute account lock
- Failed attempt counter **resets on successful login**
- Lockout forces are tracked in the database
- Prevents **credential stuffing** and **brute-force** attacks

### Secure Session Configuration

```python
app.config['SESSION_COOKIE_SECURE'] = True      # HTTPS only
app.config['SESSION_COOKIE_HTTPONLY'] = True     # No JavaScript access
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'   # CSRF protection
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)  # 1-hour timeout
```

### Security Logging

All authentication events are logged to `security.log`:
- Registration attempts (success/failure)
- Login attempts (success/not found/invalid password)
- Account lockout events
- Logout events

---

## 🔄 Authentication Workflow

```
                      ┌──────────────────┐
                      │   Registration    │
                      │   (/register)     │
                      └────────┬─────────┘
                               │
                    [Valid Input?] → Invalid → Flash Error
                               │
                    [Duplicate?]  → Yes → Flash Error
                               │
                    [Password     → Weak → Flash Error
                     Strength OK?]
                               │
                    [bcrypt Hash   → One-way salted hashing
                     Password]
                               │
                    [Parameterized → SQLite INSERT
                     SQL Query]        (injection-safe)
                               │
                               ▼
                    ┌─────────────────────┐
                    │   User Created       │
                    │   Redirect → Login   │
                    └─────────────────────┘

                      ┌──────────────────┐
                      │     Login         │
                      │    (/login)       │
                      └────────┬─────────┘
                               │
                    [Validate      → No → Flash Error
                     Credentials]
                               │
                    [Find User     → Not Found → Flash Error
                     in DB]
                               │
                    [Account       → Locked → Flash Remaining Time
                     Locked?]
                               │
                    [bcrypt.verify → Mismatch → Increment Count
                     Password]          [5+? → Lock 15 min]
                               │
                    [Match!] → Reset Count → Flask-Login → Dashboard
```

### Flask-Login Session Management

1. `login_user(user_obj)` creates a secure session
2. Session ID stored in HttpOnly, Secure cookie
3. `@login_required` decorator protects routes
4. `load_user(user_id)` callback reloads user from DB
5. `logout_user()` clears the session

---

## 📊 Database Schema

### Users Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique user identifier |
| `username` | TEXT | UNIQUE, NOT NULL | Unique username |
| `email` | TEXT | UNIQUE, NOT NULL | User email address |
| `password_hash` | TEXT | NOT NULL | bcrypt hashed password |
| `created_at` | TEXT | NOT NULL | Account creation timestamp |
| `failed_login_attempts` | INTEGER | DEFAULT 0 | Consecutive failed attempts |
| `account_locked_until` | TEXT | DEFAULT NULL | Lockout expiration timestamp |
| `login_count` | INTEGER | DEFAULT 0 | Total successful logins |
| `last_login` | TEXT | DEFAULT NULL | Last successful login timestamp |
| `is_active` | INTEGER | DEFAULT 1 | Account active status |

---

## 📸 Screenshots

### Home Page
```
┌─────────────────────────────────────────────────────────┐
│  🔐 SecureAuth  Home  |  Register  |  Login             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│     Secure Authentication System                        │
│     ═══════════════════════                             │
│     A production-ready secure login system...           │
│                                                         │
│     [ Get Started Free ]    [ Sign In ]                 │
│                                                         │
│     100% Secure   0 Risk   CSRF Protected               │
└─────────────────────────────────────────────────────────┘
```

### Registration Page
```
┌─────────────────────────────────────────────────────────┐
│  🔐 SecureAuth             Home | Register | Login       │
├─────────────────────────────────────────────────────────┤
│              ╔═══════════╗                               │
│              ║ + Create  ║                               │
│              ║  Account  ║                               │
│              ╚═══════════╝                               │
│                                                         │
│  Username:  [_____________________]                     │
│  Email:     [_____________________]                     │
│  Password:  [_____________________]  [👁]               │
│  Confirm:   [_____________________]  [👁]               │
│                                                         │
│  [         REGISTER          ]                          │
│                                                         │
│  Already have an account? Sign in here                  │
└─────────────────────────────────────────────────────────┘
```

### Dashboard Page
```
┌─────────────────────────────────────────────────────────┐
│  🔐 SecureAuth  Home  |  Dashboard  |  [Logout]         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  👤 Welcome, cybersecurity_user!                         │
│     user@example.com                                    │
│     [ Authenticated ]  [ Joined 2024-01-01 ]            │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Password     │  │ SQL          │  │ Session      │  │
│  │ Security     │  │ Injection    │  │ Security     │  │
│  │ [ Hashed ]   │  │ [Protect]    │  │ [ Protected] │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                         │
│  Account Details:                                       │
│  ┌────────┬───────────┐  ┌────────────────────────────┐ │
│  │ User ID│ #101      │  │ Security Features          │ │
│  │ Username│student  │  │ ✓ bcrypt Password Hashing  │ │
│  │ Email  │mail@ex   │  │ ✓ Parameterized SQL        │ │
│  │ Created│2024-...  │  │ ✓ CSRF Protection          │ │
│  │ Status │ Active   │  │ ✓ Account Lockout          │ │
│  └────────┴───────────┘  └────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Login Page
```
┌─────────────────────────────────────────────────────────┐
│  SecureAuth                    Home | Register | Login   │
├─────────────────────────────────────────────────────────┤
│              ╔══════════╗                               │
│              ║ Welcome  ║                               │
│              ║  Back!   ║                               │
│              ╚══════════╝                               │
│                                                         │
│  Username or Email:  [_______________]                  │
│  Password:           [______________]  [👁]             │
│  2FA Code (optional):[____6_digits__]                   │
│                                                         │
│  [         LOGIN          ]                             │
│                                                         │
│  Don't have an account? Register here                   │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 Configuration

### Changing the Secret Key (Production)

```bash
# Set a strong, random secret key as an environment variable
export SECRET_KEY=$(openssl rand -hex 32)
python app.py
```

### Production Deployment

For production, never use Flask's built-in development server. Use a WSGI server:

```bash
pip install gunicorn
gunicorn -w 4 "app:app" --bind 0.0.0.0:8000
```

---

## 🧪 Testing the Security Features

### Test SQL Injection Protection

```bash
# This will be safely rejected by parameterized queries
curl -X POST http://localhost:5000/login \
  -d "username_email=admin' OR '1'='1&password=anything"
# Result: Login fails (no user found), no SQL injection
```

### Test Account Lockout

1. Enter wrong password 5 times for any user
2. Observe: Account locked for 15 minutes
3. Check `security.log` for lockout event

### Test Password Strength

Try registering with:
- `12345678` → ❌ Missing uppercase, lowercase, and special char
- `password` → ❌ Too short, missing digit and special char
- `abcABC123!` → ✅ Strong password

---

## 📝 Code Documentation

### Key Security Patterns Used

#### Parameterized SQL Queries (SQL Injection Prevention)
```python
# In app.py - init_database() and get_db_connection()
# All queries use sqlite3's parameter substitution with ? placeholders
conn.execute('SELECT * FROM users WHERE id = ?', (user_id,))
```

#### bcrypt Password Hashing
```python
# In app.py - Registration route
# bcrypt generates a unique salt for each password automatically
password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

# In app.py - Login route
# check_password_hash extracts the salt from the stored hash
# and recomputes the hash with the provided password
is_valid = bcrypt.check_password_hash(stored_hash, input_password)
```

#### Flask-Login Session Management
```python
# In app.py
login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# In routes
@app.route('/dashboard')
@login_required  # Only authenticated users can access
```

#### CSRF Protection
```python
# In app.py - protected automatically by Flask-WTF
csrf = CSRFProtect(app)

# In templates - {{ form.hidden_tag() }} renders the CSRF token
<form method="POST">
    {{ form.hidden_tag() }}  {# Renders CSRF token hidden input #}
    ...
</form>
```

#### Input Validation with WTForms
```python
# In app.py - RegistrationForm class
username = StringField(
    'Username',
    validators=[
        DataRequired(message='Username is required.'),
        Length(min=4, max=20, message='Username must be 4-20 characters.'),
        Regexp(r'^[a-zA-Z0-9_]+$', message='Only letters, numbers, underscores.')
    ]
)
```

---

## 🚧 Future Enhancements

- [ ] Two-Factor Authentication (TOTP/OTP via email)
- [ ] Password reset functionality
- [ ] Email verification on registration
- [ ] Remember me functionality
- [ ] Password change/update
- [ ] User profile management
- [ ] Admin panel for user management
- [ ] Rate limiting with Flask-Limiter
- [ ] JWT token authentication option
- [ ] Security headers (CSP, HSTS, X-Frame-Options)
- [ ] Docker containerization
- [ ] Unit and integration tests

---

## 🛡️ Security Audit Checklist

- ✅ Password storage: bcrypt with automatic salting
- ✅ Session cookies: HttpOnly, Secure, SameSite=Lax
- ✅ CSRF tokens: Flask-WTF on all forms
- ✅ SQL queries: All parameterized
- ✅ Authentication: bcrypt.verify() for password checks
- ✅ Authorization: @login_required on protected routes
- ✅ Input validation: WTForms validators
- ✅ Account lockout: Brute-force protection
- ✅ Error handling: No sensitive info leak in 404/500
- ✅ Logging: Security events tracked

---

## 📦 Dependencies

All dependencies are listed in `requirements.txt`:

```
Flask==2.3.3
Flask-Login==0.6.2
Flask-Bcrypt==1.0.1
Flask-WTF==1.2.1
Werkzeug==2.3.7
email_validator==2.3.0
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License. See LICENSE for details.

---

## 👨‍💻 Author

Built as a **Cybersecurity Portfolio Project** demonstrating secure coding practices, password hashing, authentication systems, and web security best practices.

---

## ⚠️ Disclaimer

This project is for **educational and portfolio purposes**. In a production environment:
- Use HTTPS (set `SESSION_COOKIE_SECURE = True` with a valid SSL certificate)
- Store the `SECRET_KEY` in environment variables or a secrets manager
- Use a production WSGI server (Gunicorn, uWSGI)
- Configure a proper reverse proxy (Nginx)
- Implement additional security headers
- Use a production database (PostgreSQL, MySQL)

---

⭐ **Star this repo** if you found it helpful for your learning or portfolio!
