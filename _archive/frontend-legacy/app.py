"""
Flask web application for Safety Event Classification System
Provides a hospital-suitable interface for processing safety incidents
"""

import os
import sys
import json
import pandas as pd
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import tempfile
import io
from functools import wraps

# Add model directory to path
model_paths = [
    os.path.join(os.path.dirname(__file__), '..', 'model'),  # Local: ../model
    os.path.join(os.path.dirname(__file__), 'model'),         # Docker: ./model (mounted)
]
for path in model_paths:
    if path not in sys.path:
        sys.path.insert(0, path)

# Try to import simplified prompt utils first (preferred for web frontend)
try:
    from simple_prompt_utils import (
        prompt1_single_incident,
        prompt2_single_incident,
        prompt3_single_incident
    )
    print("Using simplified prompt utilities")
except ImportError:
    # Fallback to original prompt utils
    from prompt_utils import (
        prompt1_single_incident,
        prompt2_single_incident,
        prompt3_single_incident
    )
    print("Using original prompt utilities")

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
app.config['ALLOWED_EXTENSIONS'] = {'csv', 'xlsx'}
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access the Safety Event Classification System.'

# User class for Flask-Login with role support
class User(UserMixin):
    def __init__(self, id, username, password_hash, role='viewer', email=''):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role = role  # 'admin', 'doctor', 'nurse', 'viewer'
        self.email = email
    
    def has_role(self, role):
        """Check if user has specific role"""
        return self.role == role
    
    def can_manage_users(self):
        """Only admins can manage users"""
        return self.role == 'admin'
    
    def can_classify(self):
        """Doctors, nurses, and admins can classify events"""
        return self.role in ['admin', 'doctor', 'nurse']

# In-memory user storage (in production, use a database)
# Default credentials: username='admin', password='hospital2024', role='admin'
users = {
    'admin': {
        'id': 1,
        'username': 'admin',
        'password_hash': generate_password_hash('hospital2024'),
        'role': 'admin',
        'email': 'admin@hospital.com'
    }
}

# Password reset tokens (in production, use Redis or database)
reset_tokens = {}

# Counter for new user IDs
next_user_id = 2

@login_manager.user_loader
def load_user(user_id):
    for username, user_data in users.items():
        if str(user_data['id']) == str(user_id):
            return User(
                user_data['id'], 
                user_data['username'], 
                user_data['password_hash'],
                user_data.get('role', 'viewer'),
                user_data.get('email', '')
            )
    return None

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def role_required(*roles):
    """Decorator to require specific roles"""
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if current_user.role not in roles:
                return jsonify({"error": "Insufficient permissions"}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def classify_single_incident(description, department=None):
    """
    Classify a single safety event incident
    
    Args:
        description: Incident description text
        department: Department where incident occurred (optional)
    
    Returns: dict with classification results including rationales and department
    """
    # Valid departments
    valid_departments = [
        "internal medicine",
        "surgery", 
        "ob/gyn/nicu",
        "radiology/imaging",
        "outpatient/ER"
    ]
    
    # Validate and normalize department
    if department:
        department = department.lower().strip()
        if department not in valid_departments:
            department = "unspecified"
    
    result = {
        "incident": description,
        "department": department,
        "gaps_deviation_check": 'N/A',
        "gaps_rationale": 'N/A',
        "reached_patient_check": 'N/A',
        "reached_patient_rationale": 'N/A',
        "harm_level_check": 'N/A',
        "harm_level_rationale": 'N/A',
        "final_classification_code": 'Unknown',
        "final_rationale": 'N/A',
        "status": "success"
    }
    
    try:
        # Step 1: GAPS deviation check
        try:
            gaps_deviation_bool, gaps_rationale = prompt1_single_incident(description)
            result["gaps_deviation_check"] = "Yes" if gaps_deviation_bool else "No"
            result["gaps_rationale"] = gaps_rationale
        except Exception as e:
            result["status"] = "error"
            result["final_rationale"] = f"Error in GAPS deviation check (Step 1): {type(e).__name__}: {str(e)}"
            print(f"ERROR in prompt1: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return result
        
        if not gaps_deviation_bool:
            result["final_classification_code"] = "NSE"
            result["final_rationale"] = f"No deviation from Generally Accepted Performance Standards (GAPS). {gaps_rationale}"
            return result
        
        # Step 2: Reached patient check
        try:
            reached_patient_bool, reached_patient_rationale = prompt2_single_incident(description)
            result["reached_patient_check"] = "Yes" if reached_patient_bool else "No"
            result["reached_patient_rationale"] = reached_patient_rationale
        except Exception as e:
            result["status"] = "error"
            result["final_rationale"] = f"Error in reached patient check (Step 2): {type(e).__name__}: {str(e)}"
            print(f"ERROR in prompt2: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return result
        
        if not reached_patient_bool:
            result["final_classification_code"] = "NME"
            result["final_rationale"] = f"Deviation occurred but did not reach the patient. {reached_patient_rationale}"
            return result
        
        # Step 3: Harm level check
        try:
            harm_level_bool, harm_level_rationale = prompt3_single_incident(description)
            result["harm_level_check"] = "Yes" if harm_level_bool else "No"
            result["harm_level_rationale"] = harm_level_rationale
        except Exception as e:
            result["status"] = "error"
            result["final_rationale"] = f"Error in harm level check (Step 3): {type(e).__name__}: {str(e)}"
            print(f"ERROR in prompt3: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return result
        
        if harm_level_bool:
            result["final_classification_code"] = "SSE"
            result["final_rationale"] = f"Deviation reached the patient and caused moderate/severe harm or death. {harm_level_rationale}"
        else:
            result["final_classification_code"] = "PSE"
            result["final_rationale"] = f"Deviation reached the patient with no or minimal harm. {harm_level_rationale}"
        
        return result
        
    except Exception as e:
        result["status"] = "error"
        result["final_rationale"] = f"Unexpected error during classification: {type(e).__name__}: {str(e)}"
        print(f"UNEXPECTED ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return result

def process_csv_file(file_path):
    """
    Process a CSV or Excel file containing multiple incidents
    Returns: list of classification results
    """
    try:
        # Read file based on extension
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        # Look for common column names
        description_col = None
        for col in df.columns:
            if any(keyword in col.lower() for keyword in ['description', 'incident', 'event', 'brief']):
                description_col = col
                break
        
        if description_col is None:
            # Use first column if no matching column found
            description_col = df.columns[0]
        
        # Look for department column
        department_col = None
        for col in df.columns:
            if 'department' in col.lower():
                department_col = col
                break
        
        results = []
        for idx, row in df.iterrows():
            description = str(row[description_col])
            if description and description.strip() and description.lower() != 'nan':
                # Extract department if column exists
                department = None
                if department_col and department_col in row.index:
                    dept_value = str(row[department_col])
                    if dept_value and dept_value.strip() and dept_value.lower() != 'nan':
                        department = dept_value.strip()
                
                result = classify_single_incident(description, department)
                results.append(result)
        
        return results
        
    except Exception as e:
        return [{"status": "error", "rationale": f"Error processing file: {str(e)}"}]

# ============ Authentication Routes ============
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and authentication"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        user_data = users.get(username)
        
        if user_data and check_password_hash(user_data['password_hash'], password):
            user = User(user_data['id'], user_data['username'], user_data['password_hash'])
            login_user(user, remember=True)
            
            if request.is_json:
                return jsonify({"success": True, "message": "Login successful"})
            return redirect(url_for('index'))
        else:
            if request.is_json:
                return jsonify({"success": False, "message": "Invalid username or password"}), 401
            flash('Invalid username or password', 'error')
            return render_template('login.html'), 401
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Logout current user"""
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        global next_user_id
        data = request.get_json() if request.is_json else request.form
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        email = data.get('email', '').strip()
        role = data.get('role', 'viewer')  # Default role is viewer
        
        # Validation
        if not username or not password or not email:
            error_msg = "All fields are required"
            if request.is_json:
                return jsonify({"success": False, "message": error_msg}), 400
            flash(error_msg, 'error')
            return render_template('register.html'), 400
        
        if username in users:
            error_msg = "Username already exists"
            if request.is_json:
                return jsonify({"success": False, "message": error_msg}), 400
            flash(error_msg, 'error')
            return render_template('register.html'), 400
        
        if len(password) < 8:
            error_msg = "Password must be at least 8 characters"
            if request.is_json:
                return jsonify({"success": False, "message": error_msg}), 400
            flash(error_msg, 'error')
            return render_template('register.html'), 400
        
        # Validate role
        valid_roles = ['admin', 'doctor', 'nurse', 'viewer']
        if role not in valid_roles:
            role = 'viewer'
        
        # Create new user
        users[username] = {
            'id': next_user_id,
            'username': username,
            'password_hash': generate_password_hash(password),
            'role': role,
            'email': email
        }
        next_user_id += 1
        
        success_msg = f"Registration successful! You can now log in as {role}."
        if request.is_json:
            return jsonify({"success": True, "message": success_msg})
        flash(success_msg, 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Password reset request page"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        
        if not username or not email:
            error_msg = "Username and email are required"
            if request.is_json:
                return jsonify({"success": False, "message": error_msg}), 400
            flash(error_msg, 'error')
            return render_template('forgot_password.html'), 400
        
        # Check if user exists and email matches
        user_data = users.get(username)
        if user_data and user_data.get('email') == email:
            # Generate reset token (in production, use secure tokens and send email)
            import secrets
            token = secrets.token_urlsafe(32)
            reset_tokens[token] = {
                'username': username,
                'expires': None  # In production, add expiration time
            }
            
            # In production, send email with reset link
            # For now, return token directly (development only)
            success_msg = f"Password reset token generated. Token: {token}"
            if request.is_json:
                return jsonify({
                    "success": True, 
                    "message": "Password reset instructions sent to your email",
                    "token": token  # Remove in production
                })
            flash(success_msg, 'success')
            return redirect(url_for('reset_password', token=token))
        else:
            error_msg = "Invalid username or email"
            if request.is_json:
                return jsonify({"success": False, "message": error_msg}), 400
            flash(error_msg, 'error')
            return render_template('forgot_password.html'), 400
    
    return render_template('forgot_password.html')

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """Password reset page"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    token = request.args.get('token') or (request.get_json() or {}).get('token')
    
    if not token or token not in reset_tokens:
        flash('Invalid or expired reset token', 'error')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        new_password = data.get('password', '')
        
        if len(new_password) < 8:
            error_msg = "Password must be at least 8 characters"
            if request.is_json:
                return jsonify({"success": False, "message": error_msg}), 400
            flash(error_msg, 'error')
            return render_template('reset_password.html', token=token), 400
        
        # Update password
        username = reset_tokens[token]['username']
        if username in users:
            users[username]['password_hash'] = generate_password_hash(new_password)
            del reset_tokens[token]
            
            success_msg = "Password reset successfully! You can now log in with your new password."
            if request.is_json:
                return jsonify({"success": True, "message": success_msg})
            flash(success_msg, 'success')
            return redirect(url_for('login'))
        else:
            error_msg = "User not found"
            if request.is_json:
                return jsonify({"success": False, "message": error_msg}), 400
            flash(error_msg, 'error')
            return redirect(url_for('forgot_password'))
    
    return render_template('reset_password.html', token=token)

@app.route('/api/change-password', methods=['POST'])
@login_required
def change_password():
    """Change password for logged-in user"""
    data = request.get_json()
    
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')
    
    if not current_password or not new_password:
        return jsonify({"success": False, "message": "All fields are required"}), 400
    
    # Verify current password
    user_data = users.get(current_user.username)
    if not user_data or not check_password_hash(user_data['password_hash'], current_password):
        return jsonify({"success": False, "message": "Current password is incorrect"}), 401
    
    if len(new_password) < 8:
        return jsonify({"success": False, "message": "New password must be at least 8 characters"}), 400
    
    # Update password
    users[current_user.username]['password_hash'] = generate_password_hash(new_password)
    
    return jsonify({"success": True, "message": "Password changed successfully"})

@app.route('/api/users', methods=['GET'])
@role_required('admin')
def list_users():
    """List all users (admin only)"""
    user_list = []
    for username, data in users.items():
        user_list.append({
            'id': data['id'],
            'username': username,
            'role': data.get('role', 'viewer'),
            'email': data.get('email', '')
        })
    return jsonify({"users": user_list})

@app.route('/api/users/<username>', methods=['DELETE'])
@role_required('admin')
def delete_user(username):
    """Delete a user (admin only)"""
    if username == 'admin':
        return jsonify({"success": False, "message": "Cannot delete admin user"}), 400
    
    if username == current_user.username:
        return jsonify({"success": False, "message": "Cannot delete your own account"}), 400
    
    if username in users:
        del users[username]
        return jsonify({"success": True, "message": f"User {username} deleted successfully"})
    else:
        return jsonify({"success": False, "message": "User not found"}), 404

@app.route('/api/users/<username>/role', methods=['PUT'])
@role_required('admin')
def update_user_role(username):
    """Update user role (admin only)"""
    data = request.get_json()
    new_role = data.get('role')
    
    valid_roles = ['admin', 'doctor', 'nurse', 'viewer']
    if new_role not in valid_roles:
        return jsonify({"success": False, "message": "Invalid role"}), 400
    
    if username == 'admin' and new_role != 'admin':
        return jsonify({"success": False, "message": "Cannot change admin user role"}), 400
    
    if username in users:
        users[username]['role'] = new_role
        return jsonify({"success": True, "message": f"Role updated to {new_role}"})
    else:
        return jsonify({"success": False, "message": "User not found"}), 404

# ============ Main Application Routes ============
@app.route('/')
@login_required
def index():
    """Render main page"""
    return render_template('index.html')

@app.route('/api/classify', methods=['POST'])
@role_required('admin', 'doctor', 'nurse')
def classify():
    """API endpoint for classifying a single incident (requires classification permission)"""
    data = request.get_json()
    
    if not data or 'description' not in data:
        return jsonify({"error": "No description provided"}), 400
    
    description = data['description'].strip()
    if not description:
        return jsonify({"error": "Description cannot be empty"}), 400
    
    # Extract optional department parameter
    department = data.get('department', None)
    
    result = classify_single_incident(description, department)
    return jsonify(result)

@app.route('/api/classify-batch', methods=['POST'])
@role_required('admin', 'doctor', 'nurse')
def classify_batch():
    """API endpoint for classifying multiple incidents from a file (requires classification permission)"""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Please upload CSV or XLSX file"}), 400
    
    try:
        # Save file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process file
        results = process_csv_file(filepath)
        
        # Clean up
        os.remove(filepath)
        
        return jsonify({"results": results, "count": len(results)})
        
    except Exception as e:
        return jsonify({"error": f"Error processing file: {str(e)}"}), 500

@app.route('/api/export', methods=['POST'])
@login_required
def export_results():
    """Export results as CSV file"""
    data = request.get_json()
    
    if not data or 'results' not in data:
        return jsonify({"error": "No results to export"}), 400
    
    try:
        df = pd.DataFrame(data['results'])
        
        # Create CSV in memory
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        
        # Convert to bytes
        csv_bytes = io.BytesIO(output.getvalue().encode('utf-8'))
        
        return send_file(
            csv_bytes,
            mimetype='text/csv',
            as_attachment=True,
            download_name='safety_event_results.csv'
        )
        
    except Exception as e:
        return jsonify({"error": f"Error exporting results: {str(e)}"}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

@app.route('/api/download-template')
@login_required
def download_template():
    """Download CSV template for incident reporting"""
    try:
        template_path = os.path.join(os.path.dirname(__file__), 'safety_incident_template.csv')
        return send_file(
            template_path,
            mimetype='text/csv',
            as_attachment=True,
            download_name='safety_incident_template.csv'
        )
    except Exception as e:
        return jsonify({"error": f"Error downloading template: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
