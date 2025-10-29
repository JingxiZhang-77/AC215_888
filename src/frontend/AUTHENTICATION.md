# Authentication & User Management Guide

## Overview
The Safety Event Classification System includes comprehensive authentication with user registration, password reset, and role-based access control to protect LLM resources and ensure proper authorization.

## Default Admin Credentials

**Username:** `admin`  
**Password:** `hospital2024`  
**Role:** `admin`  
**Email:** `admin@hospital.com`

> ⚠️ **Important:** Change these default credentials in production!

## User Roles

### Role Hierarchy

1. **Admin** 
   - Full system access
   - Can classify events
   - Can manage users (create, delete, change roles)
   - Can access all API endpoints

2. **Doctor**
   - Can classify events
   - Can export results
   - Cannot manage users

3. **Nurse**
   - Can classify events
   - Can export results
   - Cannot manage users

4. **Viewer**
   - View-only access
   - Cannot classify events
   - Cannot export results
   - Can only view interface

## Features

- **User Registration**: Self-service account creation
- **Password Reset**: Forgot password functionality with secure tokens
- **Role-based Access Control (RBAC)**: Permissions based on user roles
- **Session-based Authentication**: Secure login with Flask-Login
- **Password Hashing**: Passwords stored using Werkzeug's secure hashing (PBKDF2)
- **Protected Routes**: All API endpoints require authentication and appropriate roles
- **Remember Me**: Sessions persist across browser restarts
- **Automatic Redirects**: Unauthenticated users redirected to login page

## How to Use

### 1. Starting the Application

```bash
cd src/frontend
chmod +x run.sh
./run.sh
```

### 2. Creating a New Account

1. Navigate to `http://localhost:8080`
2. Click "Create Account" on the login page
3. Fill in the registration form:
   - Username (unique)
   - Email address
   - Password (minimum 8 characters)
   - Role (Viewer, Nurse, Doctor, or Admin)
4. Click "Create Account"
5. You'll be redirected to login page after successful registration

### 3. Logging In

1. Navigate to `http://localhost:8080`
2. You'll be automatically redirected to the login page
3. Enter your credentials
4. Click "Sign In"
5. You'll be redirected to the main classification interface

### 4. Resetting Your Password

If you forget your password:

1. Click "Forgot Password?" on the login page
2. Enter your username and email address
3. In development mode, you'll receive a reset token directly
4. Click the reset link or copy the token
5. Enter your new password (minimum 8 characters)
6. Confirm the new password
7. Click "Reset Password"
8. Log in with your new password

> **Production Note:** In production, reset tokens should be sent via email and have expiration times.

### 5. Changing Your Password (While Logged In)

Use the `/api/change-password` endpoint:

```javascript
fetch('/api/change-password', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        current_password: 'your_current_password',
        new_password: 'your_new_password'
    })
})
```

### 6. Logging Out

Click the "Logout" button in the top-right corner of the header.

## Security Features

### Protected Endpoints

Classification endpoints require specific roles:

- `/` - Main application interface (all authenticated users)
- `/api/classify` - Single incident classification (admin, doctor, nurse only)
- `/api/classify-batch` - Batch file processing (admin, doctor, nurse only)
- `/api/export` - Results export (all authenticated users)
- `/api/download-template` - Template download (all authenticated users)

### Admin-Only Endpoints

User management endpoints (admin role required):

- `GET /api/users` - List all users
- `DELETE /api/users/<username>` - Delete a user
- `PUT /api/users/<username>/role` - Update user role

### Public Endpoints

- `/login` - Login page (GET and POST)
- `/register` - Registration page (GET and POST)
- `/forgot-password` - Password reset request (GET and POST)
- `/reset-password` - Set new password (GET and POST)
- `/health` - Health check endpoint

## User Management (Admin Only)

### List All Users

```javascript
fetch('/api/users', {
    method: 'GET',
    headers: {
        'Content-Type': 'application/json',
    }
})
.then(response => response.json())
.then(data => console.log(data.users));
```

Response:
```json
{
  "users": [
    {
      "id": 1,
      "username": "admin",
      "role": "admin",
      "email": "admin@hospital.com"
    },
    {
      "id": 2,
      "username": "dr_smith",
      "role": "doctor",
      "email": "smith@hospital.com"
    }
  ]
}
```

### Delete a User

```javascript
fetch('/api/users/dr_smith', {
    method: 'DELETE',
    headers: {
        'Content-Type': 'application/json',
    }
})
.then(response => response.json())
.then(data => console.log(data.message));
```

> **Note:** Cannot delete the 'admin' user or your own account.

### Update User Role

```javascript
fetch('/api/users/dr_smith/role', {
    method: 'PUT',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        role: 'nurse'
    })
})
.then(response => response.json())
.then(data => console.log(data.message));
```

Valid roles: `admin`, `doctor`, `nurse`, `viewer`

## Changing Default Credentials

### Method 1: Update in Code (Temporary)

Edit `src/frontend/app.py`:

```python
users = {
    'admin': {
        'id': 1,
        'username': 'admin',
        'password_hash': generate_password_hash('your_new_password'),
        'role': 'admin',
        'email': 'admin@hospital.com'
    }
}
```

### Method 2: Add New Users (Recommended)

Add additional users to the `users` dictionary:

```python
users = {
    'admin': {
        'id': 1,
        'username': 'admin',
        'password_hash': generate_password_hash('hospital2024')
    },
    'doctor1': {
        'id': 2,
        'username': 'doctor1',
        'password_hash': generate_password_hash('secure_password_123')
    },
    'nurse1': {
        'id': 3,
        'username': 'nurse1',
        'password_hash': generate_password_hash('another_secure_pass')
    }
}
```

### Method 3: Environment Variable (Production)

Set the `SECRET_KEY` environment variable for session security:

```bash
export SECRET_KEY="your-very-secure-random-secret-key-here"
```

Generate a secure key:
```python
import secrets
print(secrets.token_hex(32))
```

## Production Deployment Recommendations

### 1. Use a Database

Replace the in-memory `users` dictionary with a proper database (PostgreSQL, MySQL, MongoDB):

```python
# Example with SQLAlchemy
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
```

### 2. Implement User Registration

Add a registration endpoint to allow administrators to create new users:

```python
@app.route('/register', methods=['POST'])
@admin_required  # Custom decorator for admin-only access
def register():
    # User registration logic
    pass
```

### 3. Add Password Reset

Implement password reset functionality via email:
- Generate secure reset tokens
- Send email with reset link
- Validate token and update password

### 4. Enable Rate Limiting

Protect against brute-force attacks:

```bash
pip install flask-limiter
```

```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")  # Max 5 login attempts per minute
def login():
    # Login logic
    pass
```

### 5. Use HTTPS

Always use HTTPS in production:
- Obtain SSL certificate (Let's Encrypt is free)
- Configure reverse proxy (nginx, Apache)
- Redirect HTTP to HTTPS

### 6. Implement Role-Based Access Control (RBAC)

Add user roles for different permission levels:

```python
class User(UserMixin):
    def __init__(self, id, username, password_hash, role='user'):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role = role  # 'admin', 'doctor', 'nurse', 'viewer'
```

### 7. Enable Logging

Log all authentication attempts:

```python
import logging

logging.info(f"Successful login: {username}")
logging.warning(f"Failed login attempt: {username}")
```

## Troubleshooting

### Issue: "Please log in to access the Safety Event Classification System"

**Solution:** Your session expired or you're not logged in. Navigate to `/login` and sign in.

### Issue: "Invalid username or password"

**Solution:** Check your credentials. Default is username: `admin`, password: `hospital2024`

### Issue: Session keeps expiring

**Solution:** The session uses cookies. Ensure cookies are enabled in your browser.

### Issue: Cannot log out

**Solution:** Clear browser cookies manually or use private/incognito mode for testing.

## API Authentication

When making API calls programmatically, you need to include session cookies:

```python
import requests

# Login first
session = requests.Session()
login_data = {
    'username': 'admin',
    'password': 'hospital2024'
}
session.post('http://localhost:8080/login', json=login_data)

# Now make authenticated API calls
response = session.post('http://localhost:8080/api/classify', json={
    'description': 'Safety incident description...'
})
```

## Security Best Practices

1. ✅ **Change default credentials immediately**
2. ✅ **Use strong passwords** (12+ characters, mixed case, numbers, symbols)
3. ✅ **Set unique SECRET_KEY** in production
4. ✅ **Enable HTTPS** for all production traffic
5. ✅ **Implement rate limiting** to prevent brute-force
6. ✅ **Use a proper database** instead of in-memory storage
7. ✅ **Regular security audits** of authentication code
8. ✅ **Monitor login attempts** and suspicious activity
9. ✅ **Implement session timeout** for inactive users
10. ✅ **Use environment variables** for sensitive configuration

## Support

For issues or questions about authentication:
1. Check the application logs
2. Review this documentation
3. Test with default credentials in a clean browser session
4. Contact your system administrator
