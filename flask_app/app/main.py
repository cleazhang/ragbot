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


# 全局变量
db = None
all_files_path = []
# 存储用户的历史信息
user_history = defaultdict(list)
# 存储用户的数据库实例
user_db = defaultdict(lambda: None)
# 用户的文件路径列表
user_files_path = defaultdict(list)

# 加载嵌入模型
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

# embedding延迟加载，避免启动时就加载模型（可能很慢）
_embedding = None
def get_embedding():
    global _embedding
    if _embedding is None:
        try:
            _embedding = HuggingFaceEmbeddings(
                model_name=EMBEDDING_MODEL_PATH,
                model_kwargs={'device': EMBEDDING_DEVICE}
            )
            print('加载语义模型成功')
        except Exception as e:
            print(f'⚠️  警告: 加载embedding模型失败: {e}')
            print('   使用默认模型: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
            _embedding = HuggingFaceEmbeddings(
                model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                model_kwargs={'device': EMBEDDING_DEVICE}
            )
    return _embedding


USER_DATA_FILE = DB_DIR / 'users.json'

@main_blueprint.route('/')
def index():
    """首页路由"""
    if 'username' not in session:
        return redirect(url_for('main.login_page'))
    return render_template('index.html')

@main_blueprint.route('/login')
def login_page():
    """登录页面"""
    if 'username' in session:
        return redirect(url_for('main.index'))
    return render_template('login.html')

@main_blueprint.route('/register_page')
def register_page():
    """注册页面"""
    if 'username' in session:
        return redirect(url_for('main.index'))
    return render_template('register.html')
    
@main_blueprint.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    # 读取用户数据
    try:
        with open(USER_DATA_FILE, 'r') as f:
            users = json.load(f)
    except FileNotFoundError:
        users = {}
    
    # 检查用户名和密码
    if username in users and check_password_hash(users[username], password):
        # 登录成功，设置 session
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
    
    # 读取现有用户数据
    try:
        with open(USER_DATA_FILE, 'r') as f:
            try:
                users = json.load(f)
            except json.JSONDecodeError:
                users = {}
    except FileNotFoundError:
        users = {}
    
    # 检查用户名是否已存在
    if username in users:
        return jsonify({'message': 'Username already exists.'}), 400
    
    # 哈希处理密码
    password_hash = generate_password_hash(password)
    
    # 添加新用户
    users[username] = password_hash
    
    # 写入文件
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(users, f, indent=4)
    
    return jsonify({'message': 'Registration successful'}), 201

    
@main_blueprint.route('/clear_uploads', methods=['POST'])
def clear_uploads():
    if 'username' not in session:
        return jsonify({'message': 'Not logged in'}), 401
    
    # 获取当前用户名
    username = session['username']

    # 清除用户专有的文件路径列表和数据库实例
    user_files_path[username] = []
    user_db[username] = None

    # 返回成功消息
    return jsonify({'message': 'Files deleted successfully'})



@main_blueprint.route('/upload', methods=['POST'])
def upload_file():
    if 'username' not in session:
        return jsonify({'message': 'Not logged in'}), 401
    
    # 获取当前用户名
    username = session['username']

    # 检查是否有文件在请求中
    if 'file' not in request.files:
        return jsonify({'message': 'No file part in the request'}), 400

    files = request.files.getlist('file')
    files_path = []

    for file in files:
        # 如果用户没有选择文件，浏览器也会提交一个空的文件名
        if file.filename == '':
            return jsonify({'message': 'No selected file'}), 400
        if file:
            filename = file.filename
            file_path = UPLOAD_DIR / filename
            file.save(str(file_path))
            files_path.append(str(file_path))
            print(f'File saved to {file_path}')


    # 更新用户专有的文件路径列表和数据库实例
    user_files_path[username].extend(files_path)
    embedding = get_embedding()
    user_db[username] = update_db(user_files_path[username], user_db[username], embedding)
    
    # 返回文件路径列表（转换为字符串）
    return jsonify({'files': [str(fp) for fp in files_path], 'message': 'Files uploaded successfully'})

@main_blueprint.route('/ask', methods=['POST'])
def ask_model():
    if 'username' not in session:
        return jsonify({'message': 'Not logged in'}), 401
    
    # 使用 request.form 获取表单数据
    query = request.form.get('query')
    username = session['username']  # 获取当前用户名
    
    if not query:
        return jsonify({'message': 'Query parameter is missing'}), 400
    
    # 获取用户的历史记录
    history = user_history[username]
    
    # 获取用户专有的数据库实例
    db = user_db[username]
    
    result = get_answer_from_query(query=query, db=db,history=history)
    answer = result['answer']
    retrieved_result = result['retrieved_result']

    # 存储用户的历史信息
    user_history[username].append({
        'query': query,
        'answer': answer
    })

    # 构建要返回的响应字典
    response = {
        'answer': answer,
        'retrieved_result': retrieved_result
    }

    # 使用 jsonify 返回 JSON 格式的响应
    return jsonify(response)


@main_blueprint.route('/feedback', methods=['POST'])
def feedback():
    if 'username' not in session:
        return jsonify({'message': 'Not logged in'}), 401
    
    # 获取前端传递的数据
    rating = request.form.get('rating')
    answer = request.form.get('answer')
    retrieved_result = request.form.get('retrieved_result')
    if rating=='search result error':
        # 格式化数据
        feedback_data = f"Rating: {rating}\nAnswer: {answer}\nText List: {retrieved_result}\n\n"
        
        # 将评价存储到文本文件
        store_feedback_to_file(feedback_data)
        
        # 返回成功消息
        return jsonify({"message": "Feedback received!"})
    else:
        # 返回成功消息
        return jsonify({"message": "Feedback received!"})
    

@main_blueprint.route('/clear_history', methods=['POST'])
def clear_history():
    if 'username' not in session:
        return jsonify({'message': 'Not logged in'}), 401
    
    username = session['username']  # 获取当前用户名
    
    # 清除用户的历史信息
    if username in user_history:
        user_history[username] = []
    
    # 返回成功消息
    return jsonify({'message': 'History cleared successfully'})