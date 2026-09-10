# Файл для работы с базой данных
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Создаём объект базы данных
db = SQLAlchemy()

# Модель для хранения информации о клиентах
class Client(db.Model):
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), default='Новый')
    agent = db.Column(db.String(100), nullable=True)
    comments = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Client {self.name}>'


def init_db(app):
    with app.app_context():
        db.create_all()
        
        if Client.query.first() is None:
            example_clients = [
                Client(name='Иван Петров', phone='+7-900-123-45-67', email='ivan@example.com', status='Новый'),
                Client(name='Мария Сидорова', phone='+7-900-234-56-78', email='maria@example.com', status='Новый'),
                Client(name='Алексей Смирнов', phone='+7-900-345-67-89', email='alex@example.com', status='Новый'),
                Client(name='Елена Иванова', phone='+7-900-456-78-90', email='elena@example.com', status='Новый'),
                Client(name='Дмитрий Козлов', phone='+7-900-567-89-01', email='dmitry@example.com', status='Новый'),
                Client(name='Ольга Новикова', phone='+7-900-678-90-12', email='olga@example.com', status='Новый'),
                Client(name='Сергей Волков', phone='+7-900-789-01-23', email='sergey@example.com', status='Новый'),
                Client(name='Анна Морозова', phone='+7-900-890-12-34', email='anna@example.com', status='Новый'),
            ]
            
            for client in example_clients:
                db.session.add(client)
            
            db.session.commit()
            print('База данных инициализирована!')