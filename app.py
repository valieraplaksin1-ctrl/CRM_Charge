from flask import Flask, render_template, request, jsonify, session, redirect, url_for, make_response
from flask_session import Session
from config import BOT_TOKEN, WEB_APP_URL, FLASK_ENV, DEBUG
from database import *
import os
import time
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'crm_secret_key_2024'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Инициализация БД
init_db()

# Отключение кеширования шаблонов
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

def login_required(f):
    """Декоратор для проверки авторизации"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        user = get_user(username)
        if user and user[2] == password:
            session['user_id'] = user[0]
            session['username'] = user[1]
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': 'Неверные учётные данные'}), 401
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        data = request.json
        action = data.get('action')
        admin_password = data.get('password')
        
        # Проверка пароля админки
        if admin_password != 'benzolaloh':
            return jsonify({'success': False, 'message': 'Неверный пароль'}), 401
        
        if action == 'get_users':
            users = get_all_users()
            return jsonify({'users': [{'id': u[0], 'username': u[1], 'password': u[2], 'created_at': u[3]} for u in users]})
        
        elif action == 'add_user':
            username = data.get('username')
            user_password = data.get('user_password')
            if add_user(username, user_password):
                return jsonify({'success': True})
            return jsonify({'success': False, 'message': 'Пользователь уже существует'}), 400
        
        elif action == 'update_password':
            user_id = data.get('user_id')
            new_password = data.get('new_password')
            if update_user_password(user_id, new_password):
                return jsonify({'success': True})
            return jsonify({'success': False}), 400
        
        elif action == 'delete_user':
            user_id = data.get('user_id')
            delete_user(user_id)
            return jsonify({'success': True})
        
        elif action == 'get_stats':
            user_id = data.get('user_id')
            calls_today = count_user_calls_today(user_id)
            shift_time = get_today_shift(user_id)
            return jsonify({'calls': calls_today, 'shift_time': shift_time})
        
        elif action == 'get_user_clients':
            user_id = data.get('user_id')
            working_clients = get_working_clients(user_id)
            return jsonify({'clients': [{
                'id': c[0], 'name': c[1], 'phone': c[2], 'email': c[3]
            } for c in working_clients]})
        
        return jsonify({'success': False}), 400
    
    response = make_response(render_template('admin.html', v=int(time.time())))
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    return response

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    shift = get_current_shift(user_id)
    shift_active = shift is not None
    duration = get_shift_duration(user_id) if shift_active else 0
    return render_template('dashboard.html', shift_active=shift_active, duration=duration)

@app.route('/api/shift', methods=['POST'])
@login_required
def shift_api():
    user_id = session['user_id']
    action = request.json.get('action')
    
    if action == 'start':
        start_shift(user_id)
        return jsonify({'success': True})
    elif action == 'end':
        end_shift(user_id)
        return jsonify({'success': True})
    elif action == 'status':
        shift = get_current_shift(user_id)
        shift_active = shift is not None
        duration = get_shift_duration(user_id) if shift_active else 0
        return jsonify({'active': shift_active, 'duration': duration})
    
    return jsonify({'success': False}), 400

@app.route('/clients')
@login_required
def clients():
    return render_template('clients.html')

@app.route('/api/clients', methods=['GET', 'POST'])
@login_required
def clients_api():
    user_id = session['user_id']
    
    if request.method == 'GET':
        action = request.args.get('action')
        
        if action == 'current':
            # Получить текущего клиента агента
            current = get_current_client(user_id)
            if current:
                return jsonify({
                    'id': current[0],
                    'name': current[1],
                    'phone': current[2],
                    'email': current[3]
                })
            # Если нет текущего - получить нового
            client = get_available_clients()
            if client:
                set_current_client(user_id, client[0])
                return jsonify({
                    'id': client[0],
                    'name': client[1],
                    'phone': client[2],
                    'email': client[3]
                })
            return jsonify({'error': 'Нет доступных клиентов'}), 404
        
        elif action == 'working':
            clients_list = get_working_clients(user_id)
            return jsonify({'clients': [
                {'id': c[0], 'name': c[1], 'phone': c[2], 'email': c[3]} 
                for c in clients_list
            ]})
    
    elif request.method == 'POST':
        data = request.json
        action = data.get('action')
        client_id = data.get('client_id')
        
        if action == 'skip':
            # Получить следующего клиента (текущий остается available)
            client = get_available_clients()
            if client:
                set_current_client(user_id, client[0])
                return jsonify({
                    'id': client[0],
                    'name': client[1],
                    'phone': client[2],
                    'email': client[3]
                })
            return jsonify({'error': 'Нет доступных клиентов'}), 404
        
        elif action == 'add_comment':
            comment = data.get('comment')
            add_comment(client_id, user_id, comment)
            return jsonify({'success': True})
        
        elif action == 'take':
            assign_client(client_id, user_id)
            # Получить следующего клиента
            client = get_available_clients()
            if client:
                set_current_client(user_id, client[0])
            return jsonify({'success': True})
        
        elif action == 'delete':
            delete_client(client_id)
            # Получить следующего клиента
            client = get_available_clients()
            if client:
                set_current_client(user_id, client[0])
            return jsonify({'success': True})
    
    return jsonify({'success': False}), 400

@app.route('/working-clients')
@login_required
def working_clients():
    return render_template('working_clients.html')

@app.route('/api/working-clients/<int:client_id>', methods=['GET', 'POST'])
@login_required
def working_client_api(client_id):
    user_id = session['user_id']
    
    if request.method == 'GET':
        # Получаем данные клиента
        client = get_client_by_id(client_id)
        if not client:
            return jsonify({'error': 'Клиент не найден'}), 404
        
        # Получаем комментарии по ID и по номеру телефона
        comments_by_id = get_comments(client_id)
        comments_by_phone = get_all_comments_by_phone(client[2])  # client[2] это phone
        
        # Объединяем и удаляем дубликаты
        all_comments = {}
        for c in comments_by_phone + comments_by_id:
            key = (c[0], c[1], c[2])  # (user_id, comment, created_at)
            all_comments[key] = c
        
        comments_list = [
            {'user': get_username(c[0]), 'text': c[1], 'date': c[2]}
            for c in all_comments.values()
        ]
        
        # Сортируем по дате (новые первыми)
        comments_list.sort(key=lambda x: x['date'], reverse=True)
        
        return jsonify({
            'id': client[0],
            'name': client[1],
            'phone': client[2],
            'email': client[3],
            'comments': comments_list
        })
    
    elif request.method == 'POST':
        data = request.json
        action = data.get('action')
        
        if action == 'add_comment':
            comment = data.get('comment')
            add_comment(client_id, user_id, comment)
            return jsonify({'success': True})
        
        elif action == 'delete':
            delete_client(client_id)
            return jsonify({'success': True})
    
    return jsonify({'success': False}), 400

if __name__ == '__main__':
    app.run(debug=DEBUG, host='0.0.0.0', port=5000)
