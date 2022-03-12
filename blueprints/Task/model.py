from blueprints import db
from datetime import datetime
from sqlalchemy.sql import func
from flask_restful import fields


class Task(db.Model):
    __tablename__ = "task"
    Task_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Title = db.Column(db.String(255))
    Action_Time = db.Column(db.DateTime)
    Created_Time = db.Column(db.DateTime, server_default=func.now())
    Updated_Time = db.Column(db.DateTime, onupdate=func.now())
    Is_Finished = db.Column(db.Boolean, default=False)
    Objective = db.relationship('Objective', backref='task', lazy=True)

    response_fields = {
        'Task_ID': fields.Integer,
        'Title': fields.String,
        'Action_Time': fields.DateTime,
        'Created_Time': fields.DateTime,
        'Updated_Time' : fields.DateTime,
        'Is_Finished' : fields.Boolean
    }

    error_data = {
        'data': fields.String
    }

    response_on_error = {
        'message': fields.String,
        'error_key': fields.String,
        'error_message': fields.String,
        'error_data': fields.Nested(error_data)
    }

    def __init__(self, Title, Action_Time):
        self.Title = Title
        self.Action_Time = Action_Time

    def __repr__(self):
        return '<Task %r>' % self.Task_ID