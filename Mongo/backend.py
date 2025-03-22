from pymongo import MongoClient, ASCENDING
from pymongo.errors import ServerSelectionTimeoutError, OperationFailure
from bson import json_util
import json
import logging
import os
import uuid
from datetime import datetime, timedelta
import random
import io

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB connection variables
client = None
DB_NAME = 'Sowberry'
COLLECTION_NAME = 'Students'

# Try importing optional dependencies
try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    logger.warning("Matplotlib not installed. Chart generation disabled.")
    HAS_MATPLOTLIB = False

try:
    import polars as pl
    import numpy as np
    HAS_POLARS = True
except ImportError:
    logger.warning("Polars not installed. Using fallback data processing.")
    HAS_POLARS = False

# MongoDB Connection Functions
def initialize_mongodb():
    global client
    try:
        if client is not None:
            return True
        client = MongoClient('mongodb://localhost:27017/', 
                           serverSelectionTimeoutMS=5000,
                           maxPoolSize=None)
        client.admin.command('ping')
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        if "_id_1" not in collection.index_information():
            collection.create_index([("_id", ASCENDING)])
        doc_count = collection.count_documents({})
        logger.info(f"Connected to MongoDB - Collection Size: {doc_count}")
        return True
    except Exception as e:
        logger.error(f"MongoDB Connection Error: {e}")
        raise

def test_connection():
    global client
    try:
        if client is None:
            initialize_mongodb()
        client.admin.command('ping')
    except Exception as e:
        logger.error(f"MongoDB connection test failed: {e}")
        raise Exception(f"MongoDB connection failed: {str(e)}")

def get_db():
    global client
    if client is None:
        initialize_mongodb()
    return client[DB_NAME]

def find_all_documents():
    db = get_db()
    collection = db[COLLECTION_NAME]
    try:
        cursor = collection.find(
            projection={"_id": 0},
            batch_size=1000
        )
        result = list(cursor)
        logger.info(f"Successfully fetched {len(result)} documents")
        return json.loads(json_util.dumps(result))
    except Exception as e:
        logger.error(f"Error fetching documents: {e}")
        raise

# Analytics Data Processing Functions
def mongo_to_polars(collection, query=None):
    """Convert MongoDB collection to Polars DataFrame with error handling"""
    if not HAS_POLARS:
        # Fallback to list of dicts if Polars is not available
        if query is None:
            query = {}
        cursor = collection.find(query)
        result = []
        for doc in cursor:
            if '_id' in doc:
                doc_id = str(doc.pop('_id'))
                doc['id'] = doc_id
            result.append(doc)
        return result
        
    try:
        if query is None:
            query = {}
        # Use proper error handling for MongoDB operations
        try:
            cursor = collection.find(query)
            data = list(cursor)
        except Exception as e:
            logger.error(f"MongoDB query failed: {str(e)}")
            return pl.DataFrame()
        
        # Convert to Polars DataFrame
        if data:
            # Normalize the data structure (MongoDB documents can be nested)
            flat_data = []
            for doc in data:
                # Remove MongoDB _id which isn't serializable
                if '_id' in doc:
                    doc_id = str(doc.pop('_id'))
                    doc['id'] = doc_id
                flat_data.append(doc)
            
            # Create Polars DataFrame
            return pl.from_dicts(flat_data)
        return pl.DataFrame()
    except Exception as e:
        logger.error(f"Failed to convert MongoDB data to Polars: {str(e)}")
        return pl.DataFrame()

# Chart Directory Management
def ensure_charts_dir():
    """Create charts directory if it doesn't exist"""
    try:
        # Make the path absolute to avoid relative path issues
        base_dir = os.path.abspath(os.path.dirname(__file__))
        charts_dir = os.path.join(base_dir, 'static', 'charts')
        if not os.path.exists(charts_dir):
            os.makedirs(charts_dir)
        return charts_dir
    except Exception as e:
        logger.error(f"Failed to create charts directory: {str(e)}")
        # Fallback to /tmp if available
        if os.path.exists('/tmp'):
            return '/tmp'
        # Otherwise use current directory
        return os.path.abspath(os.path.dirname(__file__))

# Chart Generation Functions
def generate_user_growth_chart(labels, data):
    """Generate a line chart showing user growth over time"""
    if not HAS_MATPLOTLIB:
        return None
        
    try:
        plt.figure(figsize=(10, 4))
        plt.plot(labels, data, marker='o', linestyle='-', color='#3498db', linewidth=2)
        plt.fill_between(labels, data, color='#3498db', alpha=0.2)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.title('User Growth Over Time', fontsize=14)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('New Users', fontsize=12)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save the chart
        charts_dir = ensure_charts_dir()
        filename = f"user_growth_{uuid.uuid4().hex[:8]}.png"
        filepath = os.path.join(charts_dir, filename)
        
        # Ensure the path exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        plt.savefig(filepath, dpi=100, bbox_inches='tight')
        plt.close()
        
        # Use forward slashes for URL path (works in all browsers)
        return os.path.join('static', 'charts', filename).replace('\\', '/')
    except Exception as e:
        logger.error(f"Failed to generate user growth chart: {str(e)}")
        return None

def generate_distribution_chart(labels, data):
    """Generate a pie chart showing data distribution"""
    if not HAS_MATPLOTLIB:
        return None
        
    try:
        plt.figure(figsize=(6, 5))
        colors = ['#3498db', '#2ecc71', '#9b59b6', '#f1c40f', '#e74c3c']
        plt.pie(data, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors, shadow=True)
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        plt.title('Data Distribution', fontsize=14)
        plt.tight_layout()
        
        # Save the chart
        charts_dir = ensure_charts_dir()
        filename = f"distribution_{uuid.uuid4().hex[:8]}.png"
        filepath = os.path.join(charts_dir, filename)
        
        # Ensure the path exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        plt.savefig(filepath, dpi=100, bbox_inches='tight')
        plt.close()
        
        # Use forward slashes for URL path
        return os.path.join('static', 'charts', filename).replace('\\', '/')
    except Exception as e:
        logger.error(f"Failed to generate distribution chart: {str(e)}")
        return None

def generate_performance_chart(labels, data):
    """Generate a bar chart showing query performance"""
    if not HAS_MATPLOTLIB:
        return None
        
    try:
        plt.figure(figsize=(6, 5))
        bar_colors = ['#f1c40f']
        plt.bar(labels, data, color=bar_colors)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.title('Query Performance', fontsize=14)
        plt.xlabel('Operation Type', fontsize=12)
        plt.ylabel('Time (ms)', fontsize=12)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save the chart
        charts_dir = ensure_charts_dir()
        filename = f"performance_{uuid.uuid4().hex[:8]}.png"
        filepath = os.path.join(charts_dir, filename)
        
        # Ensure the path exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        plt.savefig(filepath, dpi=100, bbox_inches='tight')
        plt.close()
        
        # Use forward slashes for URL path
        return os.path.join('static', 'charts', filename).replace('\\', '/')
    except Exception as e:
        logger.error(f"Failed to generate performance chart: {str(e)}")
        return None

def create_placeholder_chart():
    """Create a simple placeholder chart if Matplotlib is available"""
    if not HAS_MATPLOTLIB:
        return None
        
    try:
        plt.figure(figsize=(6, 4))
        plt.text(0.5, 0.5, 'Chart not available', 
                 horizontalalignment='center', verticalalignment='center',
                 fontsize=14)
        plt.axis('off')
        
        img_buf = io.BytesIO()
        plt.savefig(img_buf, format='png')
        plt.close()
        
        img_buf.seek(0)
        return img_buf
    except Exception as e:
        logger.error(f"Failed to create placeholder chart: {str(e)}")
        return None

# Analytics Data Generation (Mock data for now)
def get_analytics_data():
    """Get analytics data for dashboard"""
    try:
        db = get_db()
        collection = db[COLLECTION_NAME]
        
        # Get total users
        total_users = collection.count_documents({})
        
        # User growth data (last 10 days)
        today = datetime.now()
        user_growth_labels = [(today - timedelta(days=i)).strftime('%d %b') for i in range(9, -1, -1)]
        user_growth_data = [random.randint(5, 25) for _ in range(10)]
        user_growth = 12.5  # Growth percentage
        
        # Generate charts
        user_growth_chart = generate_user_growth_chart(user_growth_labels, user_growth_data)
        
        distribution_labels = ['Students', 'Courses', 'Assignments', 'Grades', 'Attendance']
        distribution_data = [45, 20, 15, 10, 10]
        distribution_chart = generate_distribution_chart(distribution_labels, distribution_data)
        
        performance_labels = ['Find', 'Insert', 'Update', 'Delete', 'Aggregate']
        performance_data = [4, 8, 12, 6, 15]
        performance_chart = generate_performance_chart(performance_labels, performance_data)
        
        # Other metrics (mock data)
        db_size = "2.45 GB"
        db_growth = 8.3
        avg_query_time = random.randint(5, 15)
        query_improvement = 22.7
        active_sessions = random.randint(10, 50)
        session_growth = 15.2
        
        # Return all data
        return {
            'total_users': total_users,
            'user_growth': user_growth,
            'user_growth_labels': user_growth_labels,
            'user_growth_data': user_growth_data,
            'user_growth_chart': user_growth_chart or '/static/placeholder-chart.png',
            'distribution_chart': distribution_chart or '/static/placeholder-chart.png',
            'performance_chart': performance_chart or '/static/placeholder-chart.png',
            'db_size': db_size,
            'db_growth': db_growth,
            'avg_query_time': avg_query_time,
            'query_improvement': query_improvement,
            'active_sessions': active_sessions,
            'session_growth': session_growth,
            'has_matplotlib': HAS_MATPLOTLIB
        }
    except Exception as e:
        logger.error(f"Error getting analytics data: {str(e)}")
        raise

# Initialize MongoDB connection when module is imported
initialize_mongodb()

# Module testing
if __name__ == "__main__":
    logger.info("\nTesting backend functionality:")
    try:
        test_connection()
        print("MongoDB connection successful")
        
        docs = find_all_documents()
        print(f"Found {len(docs)} documents")
        
        analytics = get_analytics_data()
        print(f"Analytics data generated successfully")
        print(f"Total users: {analytics['total_users']}")
        
        print("All backend tests passed successfully")
    except Exception as e:
        print(f"Error testing backend: {str(e)}")