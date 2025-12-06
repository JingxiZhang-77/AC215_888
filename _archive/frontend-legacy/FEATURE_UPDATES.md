# Feature Updates - Safety Event Classification System

## New Features Summary

This document summarizes the two major feature additions to the Safety Event Classification System.

---

## Feature 1: AI Rationales for Classification Decisions

### Overview
The model now generates detailed, human-readable rationales for each classification decision step, providing transparency and explainability for the AI's reasoning process.

### Implementation Details

#### Backend Changes (Model)
- **File Modified**: `src/model/simple_prompt_utils.py`
- **Key Changes**:
  - All prompt functions now return `tuple[bool, str]` instead of just `bool`
  - `_parse_yes_no_response()` extracts both decision and rationale from LLM response
  - Each prompt explicitly requests "1-2 sentence explanation" after Yes/No answer

#### Backend Changes (Frontend App)
- **File Modified**: `src/frontend/app.py`
- **Key Changes**:
  - `classify_single_incident()` now captures and stores rationales for each step:
    - `gaps_rationale`: Why GAPS deviation was/wasn't detected
    - `reached_patient_rationale`: Why error did/didn't reach patient
    - `harm_level_rationale`: Why harm was/wasn't significant
    - `final_rationale`: Overall classification reasoning
  - Result dictionary expanded to include all rationale fields

#### Frontend Changes
- **File Modified**: `src/frontend/static/script.js`
- **Key Changes**:
  - `createResultElement()` function updated to display rationale sections
  - Shows only rationales for steps that were actually evaluated
  - Separate sections for each analysis step with proper labeling

- **File Modified**: `src/frontend/static/styles.css`
- **Key Changes**:
  - Added `.rationale-section` styling with left border indicators
  - Color-coded sections (blue for analysis steps, green for final)
  - Professional card-like appearance for each rationale

### User Experience
- **Before**: Only showed Yes/No/N/A for each check step
- **After**: Shows detailed reasoning for each decision, e.g.:
  - "GAPS Deviation Analysis: Yes, because the nurse administered medication without verifying the patient's identity, violating standard safety protocols."
  - "Patient Impact Analysis: Yes, the patient received the wrong medication."
  - "Harm Level Analysis: No, the error was caught quickly and no lasting harm occurred."

### Example Output
```json
{
  "incident": "Nurse gave wrong medication...",
  "gaps_deviation_check": "Yes",
  "gaps_rationale": "Standard protocol requires patient ID verification before medication administration.",
  "reached_patient_check": "Yes",
  "reached_patient_rationale": "The patient received the incorrect medication.",
  "harm_level_check": "No",
  "harm_level_rationale": "Error was identified within minutes and corrected before any adverse effects.",
  "final_classification_code": "PSE",
  "final_rationale": "Deviation reached the patient with no or minimal harm. Error was identified within minutes..."
}
```

---

## Feature 2: User Registration, Password Reset & Role-Based Access Control

### Overview
Comprehensive authentication system with self-service registration, password recovery, and granular role-based permissions to control access to system resources.

### User Roles

| Role | Can Classify Events | Can Export | Can Manage Users |
|------|-------------------|------------|------------------|
| **Admin** | ✅ | ✅ | ✅ |
| **Doctor** | ✅ | ✅ | ❌ |
| **Nurse** | ✅ | ✅ | ❌ |
| **Viewer** | ❌ | ❌ | ❌ |

### New Routes & Templates

#### 1. User Registration
- **Route**: `GET/POST /register`
- **Template**: `templates/register.html`
- **Features**:
  - Username uniqueness validation
  - Email requirement
  - Password strength (minimum 8 characters)
  - Role selection (default: viewer)
  - Automatic redirect to login after success

#### 2. Password Reset Request
- **Route**: `GET/POST /forgot-password`
- **Template**: `templates/forgot_password.html`
- **Features**:
  - Username and email verification
  - Secure token generation (using `secrets.token_urlsafe()`)
  - In development: shows token directly
  - In production: would email token to user

#### 3. Password Reset Completion
- **Route**: `GET/POST /reset-password?token=<token>`
- **Template**: `templates/reset_password.html`
- **Features**:
  - Token validation
  - Password confirmation matching
  - Minimum 8 character requirement
  - Token invalidation after use

#### 4. Change Password (API)
- **Route**: `POST /api/change-password`
- **Features**:
  - Requires current password verification
  - Only for logged-in users
  - JSON API endpoint

### Admin User Management APIs

#### List Users
```bash
GET /api/users
```
Returns all users with their roles and emails (admin only).

#### Delete User
```bash
DELETE /api/users/<username>
```
Remove a user account (cannot delete 'admin' or your own account).

#### Update User Role
```bash
PUT /api/users/<username>/role
Body: {"role": "doctor"}
```
Change a user's role (cannot demote 'admin' user).

### Backend Changes

#### File: `src/frontend/app.py`
- Enhanced `User` class with role support:
  - `role` property (admin/doctor/nurse/viewer)
  - `email` property
  - Helper methods: `has_role()`, `can_manage_users()`, `can_classify()`
- New decorator: `@role_required(*roles)` for granular permission control
- In-memory storage expanded with:
  - `reset_tokens` dictionary for password reset tokens
  - `next_user_id` counter for auto-incrementing IDs
- Routes updated with role-based decorators:
  - `/api/classify` and `/api/classify-batch` require admin/doctor/nurse roles
  - User management routes require admin role

### Frontend Changes

#### File: `templates/index.html`
- Added user info section in header:
  - Displays current username
  - Shows role badge with color coding
  - Visual role indicators (different colors per role)

#### File: `templates/login.html`
- Added links to:
  - "Forgot Password?" → `/forgot-password`
  - "Create Account" → `/register`

#### File: `static/styles.css`
- New styles for:
  - `.user-section`: User info and logout button container
  - `.user-info`: Username and role display
  - `.user-role`: Role badge styling
  - `.role-admin`, `.role-doctor`, `.role-nurse`, `.role-viewer`: Color-coded role badges

#### File: `static/script.js`
- Enhanced error handling:
  - Detects 403 (Forbidden) responses
  - Shows user-friendly "Access denied" messages for viewers
  - Includes role information in error messages

### Security Features

1. **Password Security**:
   - PBKDF2 hashing via Werkzeug
   - Minimum 8 character requirement
   - No plaintext storage

2. **Token Security**:
   - Cryptographically secure tokens (`secrets.token_urlsafe(32)`)
   - One-time use (deleted after password reset)
   - In production: should add expiration times

3. **Session Management**:
   - Flask-Login secure sessions
   - "Remember Me" functionality
   - Automatic logout on session expiration

4. **Role-Based Access**:
   - Decorator-based permission checks
   - 403 responses for insufficient permissions
   - Cannot delete/modify admin user

### Production Recommendations

1. **Database Integration**:
   ```python
   # Replace in-memory users dict with database (PostgreSQL, MySQL, etc.)
   from flask_sqlalchemy import SQLAlchemy
   ```

2. **Email Integration**:
   ```python
   # Add email service for password resets
   from flask_mail import Mail, Message
   ```

3. **Environment Variables**:
   ```bash
   export SECRET_KEY="secure-random-key-here"
   export DATABASE_URL="postgresql://..."
   export MAIL_SERVER="smtp.hospital.com"
   ```

4. **Rate Limiting**:
   ```python
   from flask_limiter import Limiter
   limiter = Limiter(app, default_limits=["100 per hour"])
   ```

5. **Token Expiration**:
   ```python
   reset_tokens[token] = {
       'username': username,
       'expires': datetime.now() + timedelta(hours=1)
   }
   ```

---

## Testing the Features

### Testing Rationales
1. Start the application: `./run.sh`
2. Log in with admin credentials
3. Enter a test incident in the text input
4. Click "Classify Incidents"
5. Review the results section - you should see:
   - Decision indicators (Yes/No/N/A)
   - **NEW**: Detailed rationale sections for each step
   - **NEW**: Final classification reasoning

### Testing Registration
1. Navigate to `http://localhost:8080`
2. Click "Create Account" on login page
3. Fill in registration form with:
   - Username: `test_nurse`
   - Email: `nurse@hospital.com`
   - Password: `testpass123`
   - Role: `Nurse`
4. Click "Create Account"
5. Log in with new credentials
6. Verify you can classify events

### Testing Password Reset
1. Log out
2. Click "Forgot Password?" on login page
3. Enter username and email
4. Copy the reset token shown (dev mode)
5. Follow the reset link
6. Enter new password
7. Log in with new password

### Testing Role-Based Access
1. Register a new user with "Viewer" role
2. Log in as viewer
3. Try to classify an incident
4. Verify you get "Access denied" message
5. Log out and log in as admin/doctor/nurse
6. Verify you can classify incidents

### Testing Admin APIs (using browser console)
```javascript
// List all users
fetch('/api/users').then(r => r.json()).then(console.log);

// Update role
fetch('/api/users/test_nurse/role', {
  method: 'PUT',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({role: 'doctor'})
}).then(r => r.json()).then(console.log);

// Delete user
fetch('/api/users/test_nurse', {
  method: 'DELETE'
}).then(r => r.json()).then(console.log);
```

---

## Documentation Updates

### Updated Files
1. **AUTHENTICATION.md** - Comprehensive guide covering:
   - User roles and permissions
   - Registration process
   - Password reset workflow
   - Admin user management APIs
   - Security features
   - Production deployment recommendations

2. **FEATURE_UPDATES.md** (this file) - Feature summary and testing guide

### Key Documentation Sections
- User role hierarchy and capabilities
- Step-by-step guides for all new features
- API endpoint documentation with examples
- Security best practices
- Production migration checklist

---

## Files Modified/Created

### Modified Files
1. `src/model/simple_prompt_utils.py` - Rationale generation
2. `src/frontend/app.py` - Authentication enhancements, role-based access
3. `src/frontend/static/script.js` - Rationale display, permission handling
4. `src/frontend/static/styles.css` - Rationale styling, user info display
5. `src/frontend/templates/index.html` - User info section in header
6. `src/frontend/templates/login.html` - Registration and reset links
7. `src/frontend/AUTHENTICATION.md` - Expanded documentation

### Created Files
1. `src/frontend/templates/register.html` - User registration page
2. `src/frontend/templates/forgot_password.html` - Password reset request
3. `src/frontend/templates/reset_password.html` - Set new password
4. `src/frontend/FEATURE_UPDATES.md` - This feature summary

---

## Next Steps

### Immediate
- ✅ Model generates rationales for each decision
- ✅ Frontend displays rationales in organized sections
- ✅ User registration with role selection
- ✅ Password reset with secure tokens
- ✅ Role-based access control
- ✅ Admin user management APIs
- ✅ Comprehensive documentation

### Recommended Enhancements
- [ ] Database integration for persistent user storage
- [ ] Email service for password reset tokens
- [ ] Rate limiting for login/registration endpoints
- [ ] Token expiration for password resets
- [ ] User profile management page
- [ ] Audit logging for admin actions
- [ ] Two-factor authentication (2FA)
- [ ] Password complexity requirements
- [ ] Account lockout after failed attempts

---

## Support

For questions or issues:
1. Review AUTHENTICATION.md for detailed setup instructions
2. Check TESTING.md for comprehensive testing procedures
3. Refer to this document for feature-specific guidance
