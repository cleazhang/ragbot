from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for, g
from app.llm_models import ChatGlm3, ChatGlm4, get_answer_from_query, update_db
from app.utils import load_embeddings, store_feedback_to_file
from langchain_community.embeddings import HuggingFaceEmbeddings
from werkzeug.security import generate_password_hash, check_password_hash
from collections import defaultdict
from pathlib import Path
import json
import os


main_blueprint = Blueprint('main', __name__)


# Global variables
db = None
all_files_path = []
# Store user history information
user_history = defaultdict(list)
# Store user-specific database instances
user_db = defaultdict(lambda: None)
# User file path list
user_files_path = defaultdict(list)

# Load embedding model
# embedding = FlagModel('../llm_models/bge-m3',
#                   query_instruction_for_retrieval="Represent this sentence for searching relevant passages:",
#                   use_fp16=False,devices="cuda:0")

APP_DIR = Path(__file__).resolve().parent
FLASK_ROOT = APP_DIR.parent
PROJECT_ROOT = FLASK_ROOT.parent
UPLOAD_DIR = PROJECT_ROOT / 'uploads'
DB_DIR = PROJECT_ROOT / 'db'
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
DB_DIR.mkdir(parents=True, exist_ok=True)

EMBEDDING_MODEL_PATH = os.environ.get(
    'EMBEDDING_MODEL_PATH',
    str(PROJECT_ROOT / 'llm_models' / 'bge-m3')
)
EMBEDDING_DEVICE = os.environ.get('EMBEDDING_DEVICE', 'cpu')

# Lazy-load embedding to avoid loading the model at startup (may be slow)
_embedding = None
def get_embedding():
    global _embedding
    if _embedding is None:
        try:
            _embedding = HuggingFaceEmbeddings(
                model_name=EMBEDDING_MODEL_PATH,
                model_kwargs={'device': EMBEDDING_DEVICE}
            )
            print('Semantic model loaded successfully')
        except Exception as e:
            print(f'⚠️  Warning: Failed to load embedding model: {e}')
            print('   Using default model: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
            _embedding = HuggingFaceEmbeddings(
                model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                model_kwargs={'device': EMBEDDING_DEVICE}
            )
    return _embedding


USER_DATA_FILE = DB_DIR / 'users.json'

@main_blueprint.route('/')
def index():
    """Home page route"""
    if 'username' not in session:
        return redirect(url_for('main.login_page'))
    return render_template('index.html')

@main_blueprint.route('/login')
def login_page():
    """Login page"""
    if 'username' in session:
        return redirect(url_for('main.index'))
    return render_template('login.html')

@main_blueprint.route('/register_page')
def register_page():
    """Registration page"""
    if 'username' in session:
        return redirect(url_for('main.index'))
    return render_template('register.html')
    
@main_blueprint.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    # Read user data
    try:
        with open(USER_DATA_FILE, 'r') as f:
            users = json.load(f)
    except FileNotFoundError:
        users = {}
    
    # Check username and password
    if username in users and check_password_hash(users[username], password):
        # Login successful, set session
        session.permanent = True
        session['username'] = username
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'message': 'Login failed, please check your username or password.'}), 401
    
@main_blueprint.route('/logout')
def logout():
    session.pop('username', None)
    return jsonify({'message': 'Logged out'}), 200

@main_blueprint.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    
    # Read existing user data
    try:
        with open(USER_DATA_FILE, 'r') as f:
            try:
                users = json.load(f)
            except json.JSONDecodeError:
                users = {}
    except FileNotFoundError:
        users = {}
    
    # Check if username already exists
    if username in users:
        return jsonify({'message': 'Username already exists.'}), 400
    
    # Hash the password
    password_hash = generate_password_hash(password)
    
    # Add new user
    users[username] = password_hash
    
    # Write to file
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(users, f, indent=4)
    
    return jsonify({'message': 'Registration successful'}), 201

    
@main_blueprint.route('/clear_uploads', methods=['POST'])
def clear_uploads():
    if 'username' not in session:
        return jsonify({'message': 'Not logged in'}), 401
    
    # Get current username
    username = session['username']

    # Clear user-specific file paths and database instance
    user_files_path[username] = []
    user_db[username] = None

    # Return success message
    return jsonify({'message': 'Files deleted successfully'})



@main_blueprint.route('/upload', methods=['POST'])
def upload_file():
    if 'username' not in session:
        return jsonify({'message': 'Not logged in'}), 401
    
    # Get current username
    username = session['username']

    # Check if files are included in the request
    if 'file' not in request.files:
        return jsonify({'message': 'No file part in the request'}), 400

    files = request.files.getlist('file')
    files_path = []

    for file in files:
        # If the user did not select a file, the browser may still submit an empty filename
        if file.filename == '':
            return jsonify({'message': 'No selected file'}), 400
        if file:
            filename = file.filename
            file_path = UPLOAD_DIR / filename
            file.save(str(file_path))
            files_path.append(str(file_path))
            print(f'File saved to {file_path}')


    # Update user-specific file paths and database instance
    user_files_path[username].extend(files_path)
    embedding = get_embedding()
    user_db[username] = update_db(user_files_path[username], user_db[username], embedding)
    
    # Return file path list (converted to strings)
    return jsonify({'files': [str(fp) for fp in files_path], 'message': 'Files uploaded successfully'})

@main_blueprint.route('/ask', methods=['POST'])
def ask_model():
    if 'username' not in session:
        return jsonify({'message': 'Not logged in'}), 401
    
    # Get form data using request.form
    query = request.form.get('query')
    username = session['username']  # Get current username
    
    if not query:
        return jsonify({'message': 'Query parameter is missing'}), 400
    
    # Get user history
    history = user_history[username]
    
    # Get user-specific database instance
    db = user_db[username]
    
    result = get_answer_from_query(query=query, db=db,history=history)
    answer = result['answer']
    retrieved_result = result['retrieved_result']

    # Store user history information
    user_history[username].append({
        'query': query,
        'answer': answer
    })

    # Build response dictionary
    response = {
        'answer': answer,
        'retrieved_result': retrieved_result
    }

    # Return JSON response using jsonify
    return jsonify(response)


@main_blueprint.route('/feedback', methods=['POST'])
def feedback():
    if 'username' not in session:
        return jsonify({'message': 'Not logged in'}), 401
    
    # Get data from frontend
    rating = request.form.get('rating')
    answer = request.form.get('answer')
    retrieved_result = request.form.get('retrieved_result')
    if rating=='search result error':
        # Format data
        feedback_data = f"Rating: {rating}\nAnswer: {answer}\nText List: {retrieved_result}\n\n"
        
        # Store feedback in a text file
        store_feedback_to_file(feedback_data)
        
        # Return success message
        return jsonify({"message": "Feedback received!"})
    else:
        # Return success message
        return jsonify({"message": "Feedback received!"})
    

@main_blueprint.route('/clear_history', methods=['POST'])
def clear_history():
    if 'username' not in session:
        return jsonify({'message': 'Not logged in'}), 401
    
    username = session['username']  # Get current username
    
    # Clear user history information
    if username in user_history:
        user_history[username] = []
    
    # Return success message
    return jsonify({'message': 'History cleared successfully'})
