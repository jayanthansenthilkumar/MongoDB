from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson import ObjectId
import os
import json

app = Flask(__name__)

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['user_management']
users_collection = db['users']

# Helper function to convert ObjectId to string
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)

# Read the HTML file
def get_dashboard_html():
    with open(os.path.join(os.path.dirname(__file__), 'index.html'), 'r') as file:
        return file.read()

@app.route('/')
def index():
    return get_dashboard_html()

# API Endpoints
@app.route('/api/users', methods=['GET'])
def get_users():
    users = list(users_collection.find())
    return JSONEncoder().encode(users)

@app.route('/api/users', methods=['POST'])
def add_user():
    user_data = request.json
    
    # Validate input
    if not user_data.get('name') or not user_data.get('email'):
        return jsonify({"error": "Name and email are required"}), 400
    
    result = users_collection.insert_one(user_data)
    return jsonify({"success": True, "id": str(result.inserted_id)}), 201

@app.route('/api/users/<id>', methods=['GET'])
def get_user(id):
    user = users_collection.find_one({'_id': ObjectId(id)})
    if not user:
        return jsonify({"error": "User not found"}), 404
    return JSONEncoder().encode(user)

@app.route('/api/users/<id>', methods=['PUT'])
def update_user(id):
    user_data = request.json
    
    # Validate input
    if not user_data.get('name') or not user_data.get('email'):
        return jsonify({"error": "Name and email are required"}), 400
    
    result = users_collection.update_one(
        {'_id': ObjectId(id)},
        {'$set': user_data}
    )
    
    if result.matched_count == 0:
        return jsonify({"error": "User not found"}), 404
        
    return jsonify({"success": True})

@app.route('/api/users/<id>', methods=['DELETE'])
def delete_user_api(id):
    result = users_collection.delete_one({'_id': ObjectId(id)})
    
    if result.deleted_count == 0:
        return jsonify({"error": "User not found"}), 404
        
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=True)
