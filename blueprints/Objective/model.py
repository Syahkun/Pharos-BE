from blueprints import db
from datetime import datetime
from sqlalchemy.sql import func
from flask_restful import fields


class Objective(db.Model):
    __tablename__ = "objective"
    Objective_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Task_ID = db.Column(db.Integer, db.ForeignKey('task.Task_ID'))
    Objective_Name = db.Column(db.String(255))
    Is_Finished = db.Column(db.Boolean, default=False)
    # String_Created_Date = db.Column(db.DateTime, server_default=func.now())

    response_fields = {
        'Objective_Name': fields.String,
        'Is_Finished': fields.Boolean
    }

    def __init__(self, Task_ID, Objective_Name, Is_Finished):
        self.Task_ID = Task_ID
        self.Objective_Name = Objective_Name
        self.Is_Finished = Is_Finished

    def __repr__(self):
        return '<Objective %r>' % self.Objective_ID