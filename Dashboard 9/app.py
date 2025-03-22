from flask import Flask, jsonify, request, redirect, send_file, url_for
from pymongo import MongoClient
from bson import ObjectId
import os
import json
import datetime
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='static')

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB limit

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['user_management']
users_collection = db['users']

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Helper function to convert ObjectId to string
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)

# Read HTML files
def get_html_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(filepath):
        with open(filepath, 'r') as file:
            return file.read()
    return "<h1>File not found</h1>"

# Serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

# Main routes
@app.route('/')
def index():
    return get_html_file('index.html')

@app.route('/user')
def user_list():
    return get_html_file('index.html')

@app.route('/user/<id>')
def user_details(id):
    try:
        # Check if the ID is valid before trying to find the user
        if not ObjectId.is_valid(id):
            print(f"Invalid ObjectId format: {id}")
            return redirect('/user')
            
        # Validate that the user exists
        user = users_collection.find_one({'_id': ObjectId(id)})
        if not user:
            print(f"User not found with ID: {id}")
            return redirect('/user')
            
        return get_html_file('user.html')
    except Exception as e:
        print(f"Error displaying user details: {e}")
        return redirect('/user')

# Add this route to serve static HTML files
@app.route('/<filename>.html')
def serve_html(filename):
    return get_html_file(f'{filename}.html')

# API Endpoints
@app.route('/api/users', methods=['GET'])
def get_users():
    users = list(users_collection.find().sort('createdAt', -1))  # Sort newest first
    return JSONEncoder().encode(users)

@app.route('/api/users', methods=['POST'])
def add_user():
    user_data = request.json
    
    # Validate input
    if not user_data.get('name') or not user_data.get('email'):
        return jsonify({"error": "Name and email are required"}), 400
    
    # Add timestamps
    now = datetime.datetime.now().isoformat()
    user_data['createdAt'] = now
    user_data['updatedAt'] = now
    
    # Add default profile fields if not provided
    if 'bio' not in user_data:
        user_data['bio'] = ""
    if 'status' not in user_data:
        user_data['status'] = "active"
    if 'loginCount' not in user_data:
        user_data['loginCount'] = 0
    if 'lastLogin' not in user_data:
        user_data['lastLogin'] = None
    if 'isPublic' not in user_data:
        user_data['isPublic'] = True
    if 'profileImage' not in user_data:
        user_data['profileImage'] = None
    
    try:
        result = users_collection.insert_one(user_data)
        # Fetch the inserted user to return complete data
        inserted_user = users_collection.find_one({'_id': result.inserted_id})
        return JSONEncoder().encode(inserted_user), 201
    except Exception as e:
        print(f"Error creating user: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/users/<id>', methods=['GET'])
def get_user(id):
    try:
        user = users_collection.find_one({'_id': ObjectId(id)})
        if not user:
            return jsonify({"error": "User not found"}), 404
        return JSONEncoder().encode(user)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users/<id>', methods=['PUT'])
def update_user(id):
    user_data = request.json
    
    # Validate input
    if not user_data.get('name') or not user_data.get('email'):
        return jsonify({"error": "Name and email are required"}), 400
    
    # Update timestamp
    user_data['updatedAt'] = datetime.datetime.now().isoformat()
    
    # Ensure fields are present
    if 'bio' not in user_data:
        user_data['bio'] = ""
    if 'isPublic' not in user_data:
        user_data['isPublic'] = True
    
    try:
        result = users_collection.update_one(
            {'_id': ObjectId(id)},
            {'$set': user_data}
        )
        
        if result.matched_count == 0:
            return jsonify({"error": "User not found"}), 404
        
        # Return the updated user
        updated_user = users_collection.find_one({'_id': ObjectId(id)})
        return JSONEncoder().encode(updated_user)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users/<id>', methods=['DELETE'])
def delete_user_api(id):
    try:
        result = users_collection.delete_one({'_id': ObjectId(id)})
        
        if result.deleted_count == 0:
            return jsonify({"error": "User not found"}), 404
            
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users/<id>/profile-image', methods=['POST'])
def upload_profile_image(id):
    try:
        # Check if the ID is valid
        if not ObjectId.is_valid(id):
            return jsonify({"error": "Invalid user ID"}), 400
            
        # Check if user exists
        user = users_collection.find_one({'_id': ObjectId(id)})
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Check if removing the image
        if 'removeImage' in request.form:
            # If user has an existing image, delete it
            if 'profileImage' in user and user['profileImage']:
                try:
                    # Extract filename from the URL
                    filename = os.path.basename(user['profileImage'])
                    old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                except Exception as e:
                    print(f"Error removing old image: {e}")
            
            # Update user to remove profile image
            users_collection.update_one(
                {'_id': ObjectId(id)},
                {'$set': {'profileImage': None}}
            )
            
            return jsonify({"message": "Profile image removed"})
        
        # Check if file is in the request
        if 'profileImage' not in request.files:
            return jsonify({"error": "No file provided"}), 400
            
        file = request.files['profileImage']
        
        # Check if browser submitted an empty file
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
            
        # Check file type
        if not allowed_file(file.filename):
            return jsonify({"error": "File type not allowed"}), 400
            
        # Create a unique filename to prevent collisions
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        
        # Save the file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        # Create the URL for the image
        image_url = url_for('uploaded_file', filename=unique_filename, _external=True)
        
        # If user has an existing image, delete it
        if 'profileImage' in user and user['profileImage']:
            try:
                # Extract filename from the URL
                old_filename = os.path.basename(user['profileImage'])
                old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], old_filename)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
            except Exception as e:
                print(f"Error removing old image: {e}")
        
        # Update user with new profile image
        users_collection.update_one(
            {'_id': ObjectId(id)},
            {'$set': {'profileImage': image_url}}
        )
        
        return jsonify({"profileImage": image_url})
    except Exception as e:
        print(f"Error in profile image upload: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
