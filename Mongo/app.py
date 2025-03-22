from flask import Flask, render_template, Response, abort, redirect, url_for, request, session, flash, jsonify
import os
import logging
from datetime import datetime, timedelta
import secrets
import random

# Import all backend functionality
from backend import (
    initialize_mongodb, test_connection, find_all_documents, get_db,
    get_analytics_data, generate_user_growth_chart, generate_distribution_chart,
    generate_performance_chart, create_placeholder_chart, HAS_MATPLOTLIB
)

# Utility functions
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            # Store the requested URL for redirecting after login
            if request.path != url_for('login') and request.path != url_for('logout'):
                session['next'] = request.url
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Initialize Flask
app = Flask(__name__, template_folder='.')
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)
logging.basicConfig(level=logging.DEBUG)
logger = app.logger

# Initialize MongoDB connection
try:
    initialize_mongodb()
except Exception as e:
    logger.error(f"Failed to initialize MongoDB: {e}")

# Authentication Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    # If user is already logged in, redirect to dashboard
    if session.get('logged_in'):
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Simple authentication - replace with actual auth logic against DB
        if username == 'admin' and password == 'admin':
            session.permanent = True
            session['logged_in'] = True
            session['username'] = username
            session['role'] = 'admin'
            session['login_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # Set a flag to show welcome alert in index page
            session['show_welcome_alert'] = True  
            # Redirect directly to index
            return redirect(url_for('home'))
        else:
            # Keep error message for login failures
            flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    # Clear all session data
    session.clear()
    # Redirect to login page
    return redirect(url_for('login'))

# Main Dashboard Routes
@app.route('/')
@login_required
def home():
    try:
        # Test connection first
        test_connection()
        # Get documents
        all_docs = find_all_documents()
        logger.info(f"Total documents fetched for dashboard: {len(all_docs)}")
        
        # Calculate session time
        login_time = datetime.strptime(session.get('login_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '%Y-%m-%d %H:%M:%S')
        current_time = datetime.now()
        session_duration = current_time - login_time
        hours, remainder = divmod(session_duration.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        session_time = f"{hours}h {minutes}m"
        
        # Check for welcome alert flag
        show_welcome_alert = session.pop('show_welcome_alert', False)
        welcome_status = "show" if show_welcome_alert else "hide"
        
        if not all_docs:
            logger.warning("No documents found in collection")
            return render_template('index.html', 
                                  error="No documents found in collection", 
                                  all_docs=[],
                                  current_date=datetime.now().strftime('%A, %B %d, %Y'),
                                  username=session.get('username'),
                                  role=session.get('role'),
                                  session_time=session_time,
                                  welcome_status=welcome_status)
                                  
        return render_template('index.html', 
                              all_docs=all_docs,
                              current_date=datetime.now().strftime('%A, %B %d, %Y'),
                              username=session.get('username'),
                              role=session.get('role'),
                              session_time=session_time,
                              welcome_status=welcome_status)
    except Exception as e:
        logger.error(f"Error in index route: {str(e)}")
        return render_template('index.html', 
                              error=str(e), 
                              all_docs=[],
                              current_date=datetime.now().strftime('%A, %B %d, %Y'))

@app.route('/students')
@login_required
def students():
    try:
        # Test connection first
        test_connection()
        # Get documents
        all_docs = find_all_documents()
        logger.info(f"Total documents fetched for students: {len(all_docs)}")
        
        # Calculate session time
        login_time = datetime.strptime(session.get('login_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '%Y-%m-%d %H:%M:%S')
        current_time = datetime.now()
        session_duration = current_time - login_time
        hours, remainder = divmod(session_duration.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        session_time = f"{hours}h {minutes}m"
        
        # Check for welcome alert flag
        show_welcome_alert = session.pop('show_welcome_alert', False)
        welcome_status = "show" if show_welcome_alert else "hide"
        
        if not all_docs:
            logger.warning("No documents found in collection")
            return render_template('students.html', 
                                  error="No documents found in collection", 
                                  all_docs=[],
                                  current_date=datetime.now().strftime('%A, %B %d, %Y'),
                                  username=session.get('username'),
                                  role=session.get('role'),
                                  session_time=session_time,
                                  welcome_status=welcome_status)
                                  
        return render_template('students.html', 
                              all_docs=all_docs,
                              current_date=datetime.now().strftime('%A, %B %d, %Y'),
                              username=session.get('username'),
                              role=session.get('role'),
                              session_time=session_time,
                              welcome_status=welcome_status)
    except Exception as e:
        logger.error(f"Error in students route: {str(e)}")
        return render_template('students.html', 
                              error=str(e), 
                              all_docs=[],
                              current_date=datetime.now().strftime('%A, %B %d, %Y'))

# Analytics Routes
@app.route('/analytics')
@login_required
def analytics():
    try:
        # Test connection first
        test_connection()
        
        # Get analytics data
        analytics_data = get_analytics_data()
        
        # Calculate session time
        login_time = datetime.strptime(session.get('login_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '%Y-%m-%d %H:%M:%S')
        current_time = datetime.now()
        session_duration = current_time - login_time
        hours, remainder = divmod(session_duration.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        session_time = f"{hours}h {minutes}m"
        
        # Get current date for display
        current_date = datetime.now().strftime('%A, %B %d, %Y')
        
        # Add session and user info to analytics data
        analytics_data.update({
            'username': session.get('username', 'User'),
            'role': session.get('role', 'Guest'),
            'session_time': session_time,
            'current_date': current_date
        })
        
        # Render template with data
        return render_template('analytics.html', **analytics_data)
    except Exception as e:
        logger.error(f"Analytics error: {str(e)}")
        return render_template('analytics.html', 
                              error=f"An error occurred: {str(e)}",
                              current_date=datetime.now().strftime('%A, %B %d, %Y'),
                              username=session.get('username', 'User'))

# Settings Routes
@app.route('/settings')
@login_required
def settings():
    try:
        # Test connection first
        test_connection()
        
        # Calculate session time
        login_time = datetime.strptime(session.get('login_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '%Y-%m-%d %H:%M:%S')
        current_time = datetime.now()
        session_duration = current_time - login_time
        hours, remainder = divmod(session_duration.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        session_time = f"{hours}h {minutes}m"
        
        # Get current date for display
        current_date = datetime.now().strftime('%A, %B %d, %Y')
        
        # Get MongoDB connection string (redacted for security)
        connection_string = "mongodb://localhost:27017/" + get_db().name
        masked_connection = "mongodb://****:****@" + connection_string.split("@")[-1] if "@" in connection_string else connection_string
        
        # Render settings template
        return render_template('settings.html',
                              current_date=current_date,
                              username=session.get('username', 'User'),
                              role=session.get('role', 'Guest'),
                              session_time=session_time,
                              connection_string=masked_connection)
    except Exception as e:
        logger.error(f"Settings error: {str(e)}")
        return render_template('settings.html', 
                              error=f"An error occurred: {str(e)}",
                              current_date=datetime.now().strftime('%A, %B %d, %Y'),
                              username=session.get('username', 'User'))

# Profile Routes
@app.route('/profile')
@login_required
def profile():
    try:
        # Test connection first
        test_connection()
        
        # Calculate session time
        login_time = datetime.strptime(session.get('login_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '%Y-%m-%d %H:%M:%S')
        current_time = datetime.now()
        session_duration = current_time - login_time
        hours, remainder = divmod(session_duration.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        session_time = f"{hours}h {minutes}m"
        
        # Get current date for display
        current_date = datetime.now().strftime('%A, %B %d, %Y')
        
        # Get user info - in a real app, this would come from your user database
        user_info = {
            'username': session.get('username', 'User'),
            'role': session.get('role', 'Guest'),
            'full_name': session.get('full_name', session.get('username')),
            'email': session.get('email', 'admin@example.com'),
            'join_date': session.get('join_date', 'January 2023'),
            'last_active': 'Today',
            'job_title': session.get('job_title', 'Database Administrator'),
            'department': session.get('department', 'IT'),
            'profile_image': session.get('profile_image', None),
            'session_time': session_time,
            'current_date': current_date,
            'preferences': session.get('preferences', {
                'dark_mode': False,
                'compact_view': False,
                'language': 'en',
                'date_format': 'MM/DD/YYYY',
                'email_notifications': True,
                'system_alerts': True,
                'analytics_reports': True
            }),
            'tfa_enabled': session.get('tfa_enabled', False)
        }
        
        # Get recent activities - in a real app, these would come from an activity log
        activities = [
            {'icon': 'fas fa-sign-in-alt', 'title': 'Logged in to the system', 'time': 'Today at 9:30 AM'},
            {'icon': 'fas fa-database', 'title': 'Created new database backup', 'time': 'Yesterday at 5:15 PM'},
            {'icon': 'fas fa-pencil-alt', 'title': 'Updated user settings', 'time': 'Jan 15, 2023 at 11:45 AM'},
            {'icon': 'fas fa-user-plus', 'title': 'Added new user account', 'time': 'Jan 12, 2023 at 3:30 PM'},
            {'icon': 'fas fa-chart-line', 'title': 'Generated monthly analytics report', 'time': 'Jan 10, 2023 at 9:15 AM'},
            {'icon': 'fas fa-server', 'title': 'System maintenance completed', 'time': 'Jan 5, 2023 at 7:00 PM'},
        ]
        
        # Render profile template with data
        return render_template('profile.html', **user_info, activities=activities)
    except Exception as e:
        logger.error(f"Profile error: {str(e)}")
        return render_template('profile.html', 
                              error=f"An error occurred: {str(e)}",
                              current_date=datetime.now().strftime('%A, %B %d, %Y'),
                              username=session.get('username', 'User'))

# Profile API Endpoints
@app.route('/api/profile/update', methods=['POST'])
@login_required
def update_profile():
    try:
        # Get profile data from request
        data = request.get_json()
        
        # In a real app, you would update the user record in your database
        # For this demo, we'll just store in session
        if 'fullName' in data:
            session['full_name'] = data['fullName']
        
        if 'email' in data:
            session['email'] = data['email']
            
        if 'jobTitle' in data:
            session['job_title'] = data['jobTitle']
            
        if 'department' in data:
            session['department'] = data['department']
        
        # Log the update for demonstration
        logger.info(f"Profile updated for user {session.get('username')}")
        
        return jsonify({
            "success": True,
            "message": "Profile updated successfully"
        })
    except Exception as e:
        logger.error(f"Profile update error: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Failed to update profile: {str(e)}"
        }), 400

@app.route('/api/profile/preferences', methods=['POST'])
@login_required
def update_preferences():
    try:
        # Get preferences from request
        data = request.get_json()
        
        # Store preferences in session
        if 'preferences' not in session:
            session['preferences'] = {}
            
        # Update preferences
        preferences = {
            'dark_mode': data.get('darkMode', False),
            'compact_view': data.get('compactView', False),
            'language': data.get('language', 'en'),
            'date_format': data.get('dateFormat', 'MM/DD/YYYY'),
            'email_notifications': data.get('emailNotifications', True),
            'system_alerts': data.get('systemAlerts', True),
            'analytics_reports': data.get('analyticsReports', True)
        }
        
        session['preferences'] = preferences
        
        # Log the update
        logger.info(f"Preferences updated for user {session.get('username')}")
        
        return jsonify({
            "success": True,
            "message": "Preferences saved successfully"
        })
    except Exception as e:
        logger.error(f"Preferences update error: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Failed to update preferences: {str(e)}"
        }), 400

@app.route('/api/generate-tfa', methods=['GET'])
@login_required
def generate_tfa():
    try:
        # In a real app, you would generate a TFA secret and QR code
        # For this demo, we'll just return dummy data
        
        # Set TFA as enabled in session
        session['tfa_enabled'] = True
        
        return jsonify({
            "success": True,
            "secret": "ABCDEFGHIJKLMNOP",
            "qrCode": "/static/placeholder-qr.png"
        })
    except Exception as e:
        logger.error(f"TFA generation error: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Failed to generate TFA: {str(e)}"
        }), 400

@app.route('/api/verify-tfa', methods=['POST'])
@login_required
def verify_tfa():
    try:
        # Get verification code from request
        data = request.get_json()
        code = data.get('code')
        
        # In a real app, you would verify the code against the user's TFA secret
        # For this demo, we'll just accept any code
        if code:
            # Set TFA as enabled in session
            session['tfa_enabled'] = True
            
            return jsonify({
                "success": True,
                "message": "Two-factor authentication enabled successfully"
            })
        else:
            return jsonify({
                "success": False,
                "message": "Invalid verification code"
            }), 400
    except Exception as e:
        logger.error(f"TFA verification error: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Failed to verify TFA: {str(e)}"
        }), 400

@app.route('/api/disable-tfa', methods=['POST'])
@login_required
def disable_tfa():
    try:
        # In a real app, you would disable TFA for the user
        # For this demo, we'll just update the session
        session['tfa_enabled'] = False
        
        return jsonify({
            "success": True,
            "message": "Two-factor authentication disabled successfully"
        })
    except Exception as e:
        logger.error(f"TFA disable error: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Failed to disable TFA: {str(e)}"
        }), 400

# API Endpoints
@app.route('/api/analytics')
@login_required
def get_analytics_api():
    try:
        # Test connection first
        test_connection()
        
        # Get analytics data
        analytics_data = get_analytics_data()
        
        # Return JSON response with just what's needed for API
        return jsonify({
            "success": True,
            "data": {
                "totalUsers": analytics_data['total_users'],
                "userGrowth": {
                    "labels": analytics_data['user_growth_labels'],
                    "data": analytics_data['user_growth_data']
                }
            }
        })
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/refresh-chart/<chart_type>')
@login_required
def refresh_chart(chart_type):
    try:
        # Different chart types need different data
        if chart_type == 'user-growth':
            # Generate new data for user growth
            today = datetime.now()
            user_growth_labels = [(today - timedelta(days=i)).strftime('%d %b') for i in range(9, -1, -1)]
            user_growth_data = [random.randint(5, 25) for _ in range(10)]
            
            # Generate new chart
            chart_path = generate_user_growth_chart(user_growth_labels, user_growth_data)
            
            return jsonify({
                "success": True,
                "image_path": chart_path
            })
            
        elif chart_type == 'distribution':
            # Generate new data for distribution
            distribution_labels = ['Students', 'Courses', 'Assignments', 'Grades', 'Attendance']
            distribution_data = [random.randint(10, 50) for _ in range(5)]
            
            # Generate new chart
            chart_path = generate_distribution_chart(distribution_labels, distribution_data)
            
            return jsonify({
                "success": True,
                "image_path": chart_path
            })
            
        elif chart_type == 'performance':
            # Generate new data for performance
            performance_labels = ['Find', 'Insert', 'Update', 'Delete', 'Aggregate']
            performance_data = [random.randint(3, 20) for _ in range(5)]
            
            # Generate new chart
            chart_path = generate_performance_chart(performance_labels, performance_data)
            
            return jsonify({
                "success": True,
                "image_path": chart_path
            })
            
        else:
            return jsonify({
                "success": False,
                "error": "Unknown chart type"
            }), 400
            
    except Exception as e:
        logger.error(f"Chart refresh error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/export-analytics/<format>')
@login_required
def export_analytics(format):
    try:
        # This is a placeholder - in a real app, you would generate and return the file
        if format.lower() in ['csv', 'excel', 'pdf']:
            return jsonify({
                "success": True,
                "message": f"Analytics data exported to {format.upper()} format"
            })
        else:
            return jsonify({"error": "Unsupported format requested"}), 400
    except Exception as e:
        logger.error(f"Export error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/test-connection', methods=['POST'])
@login_required
def test_connection_api():
    try:
        # Get connection string from request
        data = request.get_json()
        connection_string = data.get('connectionString', None)
        timeout = int(data.get('timeout', 30))
        
        # If a new connection string is provided, test it
        if connection_string:
            from pymongo import MongoClient
            from pymongo.errors import ServerSelectionTimeoutError
            
            # Try connecting with the provided string
            client = MongoClient(connection_string, 
                                serverSelectionTimeoutMS=timeout * 1000,
                                maxPoolSize=None)
            # Force a connection attempt
            client.admin.command('ping')
            client.close()
            
            return jsonify({
                "success": True,
                "message": "Connection successful"
            })
        else:
            # Use the existing connection
            test_connection()
            return jsonify({
                "success": True,
                "message": "Connection to current database successful"
            })
    except Exception as e:
        logger.error(f"Connection test error: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Connection failed: {str(e)}"
        }), 400

@app.route('/api/save-settings', methods=['POST'])
@login_required
def save_settings():
    try:
        # Get settings from request
        data = request.get_json()
        
        # Store settings in session
        if 'settings' not in session:
            session['settings'] = {}
            
        # Update settings
        session['settings'].update(data)
        
        # Apply any immediate settings changes
        if 'theme' in data:
            # In a real app, you might update a user profile in the database
            logger.info(f"Theme changed to {data['theme']}")
            
        return jsonify({
            "success": True,
            "message": "Settings saved successfully"
        })
    except Exception as e:
        logger.error(f"Save settings error: {str(e)}")
        return jsonify({
            "success": False, 
            "message": f"Failed to save settings: {str(e)}"
        }), 400

@app.route('/api/change-password', methods=['POST'])
@login_required
def change_password():
    try:
        data = request.get_json()
        current_password = data.get('currentPassword')
        new_password = data.get('newPassword')
        
        # In a real app, you would verify the current password against the database
        # and update with the new password
        
        # For demo purposes:
        if current_password == 'admin':  # The default login password
            # In a real app, you would update the password in your database
            logger.info(f"Password changed for user {session.get('username')}")
            return jsonify({
                "success": True,
                "message": "Password changed successfully"
            })
        else:
            return jsonify({
                "success": False,
                "message": "Current password is incorrect"
            }), 401
    except Exception as e:
        logger.error(f"Change password error: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Failed to change password: {str(e)}"
        }), 400

@app.route('/api/get-settings')
@login_required
def get_settings():
    try:
        # Return settings from session
        user_settings = session.get('settings', {})
        return jsonify({
            "success": True,
            "settings": user_settings
        })
    except Exception as e:
        logger.error(f"Get settings error: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Failed to retrieve settings: {str(e)}"
        }), 400
        
@app.route('/api/reset-settings', methods=['POST'])
@login_required
def reset_settings():
    try:
        # Clear settings from session
        if 'settings' in session:
            session.pop('settings')
        
        return jsonify({
            "success": True,
            "message": "Settings reset successfully"
        })
    except Exception as e:
        logger.error(f"Reset settings error: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Failed to reset settings: {str(e)}"
        }), 400

# Static File Serving
@app.route('/<path:filename>')
def serve_file(filename):
    try:
        # Set default content type
        content_type = 'application/octet-stream'
        
        # Handle special case for placeholder chart
        if filename == 'static/placeholder-chart.png':
            # Create a simple placeholder image on the fly
            img_buf = create_placeholder_chart()
            if img_buf:
                return Response(img_buf.getvalue(), content_type='image/png')
            # If matplotlib fails, return a 404
            return abort(404)
        
        # Support for all file types including images from matplotlib
        file_path = os.path.join(os.path.dirname(__file__), filename)
        if not os.path.exists(file_path):
            return abort(404)
            
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Determine content type
        if filename.endswith('.css'):
            content_type = 'text/css'
        elif filename.endswith('.js'):
            content_type = 'application/javascript'
        elif filename.endswith('.png'):
            content_type = 'image/png'
        elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
            content_type = 'image/jpeg'
        elif filename.endswith('.svg'):
            content_type = 'image/svg+xml'
        elif filename.endswith('.gif'):
            content_type = 'image/gif'
            
        return Response(content, content_type=content_type)
    except Exception as e:
        logger.error(f"Error serving {filename}: {e}")
        return abort(404)

# Run the application
if __name__ == '__main__':
    logger.info("Starting MongoDB Dashboard application")
    app.run(debug=True, port=5000)