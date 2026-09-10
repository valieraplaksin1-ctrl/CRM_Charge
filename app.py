from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from database import db, init_db, Client
import os
import json

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crm.db'
app.config['SECRET_KEY'] = 'super-secret-key-change-me'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    init_db(app)


@app.route('/', methods=['GET', 'POST'])
def login():
    """Страница входа"""
    if request.method == 'POST':
        agent_name = request.form.get('agent_name', '').strip()
        
        if agent_name:
            session['agent_name'] = agent_name
            return redirect(url_for('dashboard'))
    
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    """Главная панель"""
    if 'agent_name' not in session:
        return redirect(url_for('login'))
    
    agent_name = session['agent_name']
    status_filter = request.args.get('status', 'все')
    
    if status_filter == 'все':
        clients = Client.query.all()
    else:
        clients = Client.query.filter_by(status=status_filter).all()
    
    total = Client.query.count()
    new_count = Client.query.filter_by(status='Новый').count()
    in_work = Client.query.filter_by(status='В работе').count()
    processed = Client.query.filter_by(status='Обработан').count()
    
    return render_template('dashboard.html', 
                         clients=clients,
                         agent_name=agent_name,
                         status_filter=status_filter,
                         total=total,
                         new_count=new_count,
                         in_work=in_work,
                         processed=processed)


@app.route('/client/<int:client_id>', methods=['GET', 'POST'])
def client_profile(client_id):
    """Профиль клиента"""
    if 'agent_name' not in session:
        return redirect(url_for('login'))
    
    client = Client.query.get_or_404(client_id)
    agent_name = session['agent_name']
    
    if request.method == 'POST':
        client.status = request.form.get('status', client.status)
        client.agent = agent_name
        
        new_comment = request.form.get('comment', '').strip()
        if new_comment:
            from datetime import datetime
            timestamp = datetime.now().strftime('%d.%m.%Y %H:%M')
            comment_text = f"[{timestamp}] {agent_name}: {new_comment}"
            
            if client.comments:
                client.comments += "\n" + comment_text
            else:
                client.comments = comment_text
        
        db.session.commit()
        return redirect(url_for('client_profile', client_id=client_id))
    
    return render_template('client.html', client=client, agent_name=agent_name)


@app.route('/api/clients', methods=['GET'])
def api_get_clients():
    """API для получения списка клиентов (для Mini App)"""
    status_filter = request.args.get('status', 'все')
    
    if status_filter == 'все':
        clients = Client.query.all()
    else:
        clients = Client.query.filter_by(status=status_filter).all()
    
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'phone': c.phone,
        'email': c.email,
        'status': c.status,
        'agent': c.agent or '-'
    } for c in clients])


@app.route('/api/stats', methods=['GET'])
def api_get_stats():
    """API для получения статистики"""
    total = Client.query.count()
    new_count = Client.query.filter_by(status='Новый').count()
    in_work = Client.query.filter_by(status='В работе').count()
    processed = Client.query.filter_by(status='Обработан').count()
    
    return jsonify({
        'total': total,
        'new': new_count,
        'in_work': in_work,
        'processed': processed
    })


@app.route('/logout')
def logout():
    """Выход"""
    session.pop('agent_name', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)