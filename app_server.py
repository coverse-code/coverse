import json
import os
import secrets
import time
from copy import deepcopy
from pathlib import Path

from flask import Flask, jsonify, request, session, send_file, send_from_directory

DATA_FILE = Path(__file__).with_name('coverse_data.json')
SECRET_FILE = Path(__file__).with_name('.coverse_secret')
ROOT_DIR = Path(__file__).resolve().parent


def get_secret_key():
    configured_key = os.environ.get('COVERSE_SECRET_KEY')
    if configured_key:
        return configured_key

    try:
        if SECRET_FILE.exists():
            return SECRET_FILE.read_text(encoding='utf-8').strip()

        generated_key = secrets.token_hex(32)
        SECRET_FILE.write_text(generated_key, encoding='utf-8')
        return generated_key
    except OSError:
        return secrets.token_hex(32)


app = Flask(__name__, static_folder=None)
app.config.update(
    SECRET_KEY=get_secret_key(),
    MAX_CONTENT_LENGTH=1024 * 1024 * 1024,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=False,
)

LOGIN_ATTEMPTS = {}
RATE_WINDOW_SECONDS = 60
MAX_LOGIN_ATTEMPTS = 5


def client_ip():
    return request.remote_addr or 'unknown'


def rate_limited(key):
    now = time.monotonic()
    attempts = [
        stamp for stamp in LOGIN_ATTEMPTS.get(key, [])
        if now - stamp < RATE_WINDOW_SECONDS
    ]
    LOGIN_ATTEMPTS[key] = attempts

    if len(attempts) >= MAX_LOGIN_ATTEMPTS:
        return True

    attempts.append(now)
    return False


@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['Referrer-Policy'] = 'no-referrer'
    response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; connect-src 'self'"
    )
    return response


def read_data():
    if not DATA_FILE.exists():
        return {}

    try:
        return json.loads(DATA_FILE.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return {}


def write_data(data):
    temporary_file = DATA_FILE.with_suffix('.tmp')
    temporary_file.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )
    temporary_file.replace(DATA_FILE)


def find_user_by_credentials(users, phone, username, password):
    normalized_phone = str(phone).strip()
    normalized_username = str(username).strip().lower()
    normalized_password = str(password)

    for item in users:
        if (
            str(item.get('phone', '')).strip() == normalized_phone and
            str(item.get('username', '')).strip().lower() == normalized_username and
            str(item.get('password', '')) == normalized_password
        ):
            return item

    return None


def session_user(data):
    user_id = session.get('user_id')
    return next(
        (user for user in data.get('users', []) if user.get('id') == user_id),
        None
    )


def public_user(user):
    return {
        key: value
        for key, value in user.items()
        if key != 'password'
    }


def data_for_user(data, user):
    if user.get('role') != 'student':
        return {
            **data,
            'users': [public_user(item) for item in data.get('users', [])]
        }

    student_id = user.get('id')
    filtered = deepcopy(data)
    filtered['users'] = [public_user(user)]
    filtered['grades'] = [
        item for item in data.get('grades', [])
        if item.get('studentId') == student_id
    ]
    filtered['attendance'] = [
        item for item in data.get('attendance', [])
        if item.get('studentId') == student_id
    ]
    return filtered


def authorized_save(data, incoming, user):
    if user.get('role') != 'student':
        existing_users = {
            item.get('id'): item
            for item in data.get('users', [])
        }
        incoming_users = incoming.get('users', [])
        if not isinstance(incoming_users, list):
            return None

        safe_users = []
        for item in incoming_users:
            if not isinstance(item, dict):
                return None
            existing = existing_users.get(item.get('id'))
            if existing:
                protected = ('id', 'role', 'isMain', 'isAdmin', 'hiddenFromList')
                if any(item.get(key) != existing.get(key) for key in protected):
                    return None
            elif item.get('role') != 'student' or item.get('isAdmin') or item.get('isMain'):
                return None

            if existing and 'password' not in item:
                item = {**item, 'password': existing.get('password', '')}
            safe_users.append(item)

        incoming_ids = {item.get('id') for item in safe_users}
        required_ids = {
            item.get('id') for item in data.get('users', [])
            if item.get('role') != 'student'
        }
        if not required_ids.issubset(incoming_ids):
            return None

        return {**incoming, 'users': safe_users}

    stored = deepcopy(data)
    incoming_users = incoming.get('users', [])
    current_id = user.get('id')
    candidate = next(
        (item for item in incoming_users if item.get('id') == current_id),
        None
    )
    stored_user = session_user(data)
    if not isinstance(candidate, dict) or not stored_user:
        return None

    editable = ('full_name', 'birth', 'jshshir', 'phone', 'username', 'password')
    for key in editable:
        if key in candidate:
            stored_user[key] = candidate[key]
    stored['users'] = [
        stored_user if item.get('id') == current_id else item
        for item in data.get('users', [])
    ]
    return stored

@app.route('/')
def home():
    return send_from_directory(ROOT_DIR, 'index.html')

@app.route('/about')
def about():
    return send_from_directory(ROOT_DIR, 'about.html')

@app.route('/new-link')
def new_link():
    return send_file(ROOT_DIR / 'new_link.html')

@app.route('/app')
def app_page():
    return send_file(ROOT_DIR / 'converse.html')

@app.route('/app/desktop')
def app_desktop_page():
    return send_file(ROOT_DIR / 'converse.html')

@app.route('/app/tablet')
def app_tablet_page():
    return send_file(ROOT_DIR / 'converse.html')

@app.route('/app/mobile')
def app_mobile_page():
    return send_file(ROOT_DIR / 'converse.html')

@app.route('/desktop')
def desktop_page():
    return send_file(ROOT_DIR / 'converse.html')

@app.route('/tablet')
def tablet_page():
    return send_file(ROOT_DIR / 'converse.html')

@app.route('/mobile')
def mobile_page():
    return send_file(ROOT_DIR / 'converse.html')

@app.route('/admin')
def admin_page():
    return send_file(ROOT_DIR / 'converse.html')


@app.post('/api/login')
def api_login():
    if rate_limited(f'login:{client_ip()}'):
        return jsonify({'ok': False, 'error': 'Too many attempts'}), 429

    credentials = request.get_json(silent=True) or {}
    phone = str(credentials.get('phone', '')).strip()
    username = str(credentials.get('username', '')).strip().lower()
    password = str(credentials.get('password', ''))
    users = read_data().get('users', [])

    user = find_user_by_credentials(users, phone, username, password)

    if not user:
        return jsonify({'ok': False, 'error': 'Invalid credentials'}), 401

    session.clear()
    session['user_id'] = user.get('id')
    session['user_role'] = user.get('role', 'student')
    return jsonify({'ok': True, 'user': public_user(user)})


@app.post('/api/logout')
def api_logout():
    session.clear()
    return jsonify({'ok': True})


@app.get('/api/health')
def api_health():
    return jsonify({'ok': True, 'status': 'running', 'port': 8000})


@app.get('/api/public-data')
def get_public_data():
    data = read_data()
    return jsonify({
        'ok': True,
        'data': {
            'publicEntries': data.get('publicEntries', [])
        }
    })


@app.get('/api/data')
def get_data():
    data = read_data()
    user = session_user(data)
    if not user:
        return jsonify({'ok': False, 'error': 'Authentication required'}), 401

    return jsonify({'ok': True, 'data': data_for_user(data, user)})


@app.post('/api/save')
def save_data():
    stored = read_data()
    user = session_user(stored)
    if not user:
        return jsonify({'ok': False, 'error': 'Authentication required'}), 401

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({'ok': False, 'error': 'Invalid data'}), 400

    allowed_keys = {
        'users', 'groups', 'subjects', 'grades',
        'attendance', 'notices', 'publicEntries'
    }
    if set(data) - allowed_keys:
        return jsonify({'ok': False, 'error': 'Invalid fields'}), 400

    safe_data = authorized_save(stored, data, user)
    if safe_data is None:
        return jsonify({'ok': False, 'error': 'Insufficient permissions'}), 403

    write_data(safe_data)
    return jsonify({'ok': True})

HOST = os.environ.get('COVERSE_HOST', '0.0.0.0')
PORT = int(os.environ.get('COVERSE_PORT', '8000'))


def main():
    app.run(
        host=HOST,
        port=PORT,
        debug=False,
        use_reloader=False,
        threaded=True,
    )


if __name__ == '__main__':
    main()
