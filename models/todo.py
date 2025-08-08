from models import db

class Todo(db.Model):
    __tablename__ = 'todo'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='todo')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


