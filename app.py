from flask import Flask, render_template, request, jsonify, session
import json
import os
import uuid  # для генерації унікальних імен гостей
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'supersecret_subtrack_key_2026'

DB_FILE = 'db.json'

def init_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump({'users': {}}, f, indent=2, ensure_ascii=False)

init_db()

def load_db():
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)

def get_user_data(username):
    db = load_db()
    return db['users'].get(username)

@app.route('/')
def index():
    return render_template('index.html')

# --- АВТОРИЗАЦІЯ ---
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    if not username or not password:
        return jsonify({'error': 'Логін та пароль обов\'язкові'}), 400
    
    db = load_db()
    if username in db['users']:
        return jsonify({'error': 'Користувач з таким логіном вже існує'}), 400
    
    db['users'][username] = {
        'password': generate_password_hash(password),
        'subscriptions': [],
        'cards': [],
        'connectedServices': {},
        'syncLog': [],
        'theme': 'dark',
        'currency': '₴'
    }
    save_db(db)
    session['user'] = username
    return jsonify({'status': 'ok', 'username': username})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    user = get_user_data(username)
    if not user or not check_password_hash(user['password'], password):
        return jsonify({'error': 'Невірний логін або пароль'}), 401
    
    session['user'] = username
    return jsonify({'status': 'ok', 'username': username})

# --- НОВИЙ МАРШРУТ ДЛЯ ГОСТЯ ---
@app.route('/api/guest', methods=['POST'])
def guest_login():
    # Генеруємо унікальне ім'я для гостя
    guest_id = uuid.uuid4().hex[:8]
    username = f"guest_{guest_id}"
    
    db = load_db()
    # Якщо таке ім'я вже існує (дуже малоймовірно) - додаємо ще цифр
    while username in db['users']:
        guest_id = uuid.uuid4().hex[:8]
        username = f"guest_{guest_id}"
    
    # Створюємо гостя без пароля (ставимо пустий хеш)
    db['users'][username] = {
        'password': generate_password_hash(''),  # порожній пароль
        'subscriptions': [],
        'cards': [],
        'connectedServices': {},
        'syncLog': [],
        'theme': 'dark',
        'currency': '₴'
    }
    save_db(db)
    
    # Входимо в систему
    session['user'] = username
    return jsonify({'status': 'ok', 'username': username})

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({'status': 'ok'})

@app.route('/api/me', methods=['GET'])
def me():
    username = session.get('user')
    if not username:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = get_user_data(username)
    if not user:
        session.pop('user', None)
        return jsonify({'error': 'User not found'}), 401
    
    return jsonify({
        'username': username,
        'theme': user.get('theme', 'dark'),
        'currency': user.get('currency', '₴')
    })

# --- API ДАНИХ КОРИСТУВАЧА ---
@app.route('/api/data', methods=['GET'])
def get_user_data_api():
    username = session.get('user')
    if not username:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = get_user_data(username)
    if not user:
        return jsonify({'error': 'User not found'}), 401
    
    return jsonify({
        'subscriptions': user.get('subscriptions', []),
        'cards': user.get('cards', []),
        'connectedServices': user.get('connectedServices', {}),
        'syncLog': user.get('syncLog', []),
        'theme': user.get('theme', 'dark'),
        'currency': user.get('currency', '₴')
    })

@app.route('/api/data', methods=['POST'])
def update_user_data_api():
    username = session.get('user')
    if not username:
        return jsonify({'error': 'Unauthorized'}), 401
    
    new_data = request.get_json()
    if new_data is None:
        return jsonify({'error': 'Invalid JSON'}), 400
    
    db = load_db()
    if username not in db['users']:
        return jsonify({'error': 'User not found'}), 401
    
    db['users'][username].update({
        'subscriptions': new_data.get('subscriptions', []),
        'cards': new_data.get('cards', []),
        'connectedServices': new_data.get('connectedServices', {}),
        'syncLog': new_data.get('syncLog', []),
        'theme': new_data.get('theme', 'dark'),
        'currency': new_data.get('currency', '₴')
    })
    save_db(db)
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True)