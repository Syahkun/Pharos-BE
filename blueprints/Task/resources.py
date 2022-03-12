from flask import Flask
from flask import Blueprint

from flask_restful import Api
from flask_restful import reqparse
from flask_restful import Resource
from flask_restful import marshal

from blueprints.containers.ResponOnError import ResponOnError

from blueprints.Helper import internalServerError
from blueprints.Helper import response_on_fails
from blueprints.Helper import convertToBoolean
from blueprints.Helper import response_list
from blueprints.Helper import response_get
from blueprints.Helper import error_param
from blueprints.Helper import timeToUnix
from blueprints.Helper import unixToTime
from blueprints.Helper import zero
from blueprints.Helper import one

from datetime import datetime

from blueprints import app
from blueprints import db

import datetime
import hashlib
import time
import uuid
import json
import ast

from blueprints.Task.model import Task
from blueprints.Objective.model import Objective

bp_task = Blueprint('task', __name__)

api = Api(bp_task)

class Add(Resource):
    
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('Title', location='json')
        parser.add_argument('Action_Time', location='json')
        parser.add_argument('Objective_List', location='json')
        args = parser.parse_args()

        Title = args['Title']
        Action_Time = unixToTime(args['Action_Time'])
        if Action_Time == "NoneType":
            data = ResponOnError()
            data.error_key = "ERROR PARAM Action_Time"
            data.error_message = "Action_Time MUST BE INTEGER!"
            marshal_data = marshal(data, Task.response_on_error)
            return marshal_data, 404, {'Content-Type': 'application/json'}
            
        task = Task(Title, Action_Time)
        app.logger.debug('DEBUG: %s', task)    
        db.session.add(task)
        db.session.commit()

        Task_ID = task.Task_ID
        Objective_List = ast.literal_eval(args['Objective_List'])
        for Objective_Name in Objective_List:
            objective = Objective(Task_ID, Objective_Name, None)
            app.logger.debug('DEBUG: %s', objective)
            db.session.add(objective)
            db.session.commit()

        return {"message": "Success"}, 200, {'Content-Type': 'application/json'}

class GetByID(Resource):

    def get(self, Task_ID):
        try:
            task = Task.query.get(Task_ID)
            marshal_task = marshal(task, Task.response_fields)

            marshal_task['Objective_List'] = []

            if task is not None:

                if task.Action_Time is not None:
                    Action_Time = timeToUnix(task.Action_Time)
                    marshal_task['Action_Time'] = Action_Time

                if task.Created_Time is not None:
                    Created_Time = timeToUnix(task.Created_Time)
                    marshal_task['Created_Time'] = Created_Time

                if task.Updated_Time is not None:
                    Updated_Time = timeToUnix(task.Updated_Time)
                    marshal_task['Created_Time'] = Updated_Time

                objectives = Objective.query.filter_by(Task_ID=Task_ID).all()

                if objectives is not None:
                    for objective in objectives:
                        objective = marshal(objective, Objective.response_fields)
                        marshal_task['Objective_List'].append(objective)
                response_get['data'] = marshal_task
                return response_get, 200, {'Content-Type': 'application/json'}

            data = ResponOnError()
            data.error_key = "ERROR ID NOT FOUND"
            marshal_data = marshal(data, Task.response_on_error)
            return marshal_data, 404, {'Content-Type': 'application/json'}
        except:
            return internalServerError(), 500, {'Content-Type': 'application/json'}

class Update(Resource):

    def put(self, Task_ID):
        parser = reqparse.RequestParser()
        parser.add_argument('Title', location='json')
        parser.add_argument('Objective_List', location='json')

        args = parser.parse_args()

        Title = args['Title']
        Objective_List = args['Objective_List']

        task = Task.query.get(Task_ID)
        objectives = Objective.query.filter_by(Task_ID=Task_ID).all()
        
        if task is None:
            data = ResponOnError()
            data.error_key = "ERROR ID NOT FOUND"
            marshal_data = marshal(data, Task.response_on_error)
            return marshal_data, 404, {'Content-Type': 'application/json'}

        Is_Finished = task.Is_Finished
        Is_Finished = True 

        if objectives is not None:
                for objective in objectives:
                    db.session.delete(objective)
                    db.session.commit()

        if Objective_List is not None and Objective_List != '[]' and Objective_List:

            Objective_List = ast.literal_eval(Objective_List)

            for objective in Objective_List:

                objective = Objective(Task_ID, objective['Objective_Name'], objective['Is_Finished'])
                app.logger.debug('DEBUG: %s', objective)
                db.session.add(objective)
                db.session.commit()
                
                if objective.Is_Finished == False:
                    Is_Finished = False

        task.Is_Finished = Is_Finished

        if Title is not None:
            task.Title = Title

        db.session.commit()

        return { "message": "Success" }, 200

class Delete(Resource):

    def delete(self, Task_ID):
        task = Task.query.get(Task_ID)
        if task is None:
            data = ResponOnError()
            data.error_key = "ERROR ID NOT FOUND"
            marshal_data = marshal(data, Task.response_on_error)
            return marshal_data, 404, {'Content-Type': 'application/json'}
        db.session.delete(task)
        db.session.commit()
        return { "message": "Success" }, 200

class GetBySearch(Resource):

    def get(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('Page', type=int, location='args', required=True)
            parser.add_argument('Limit', type=int, location='args', required=True)
            parser.add_argument('Title', location='args')
            parser.add_argument('Action_Time_Start', location='args')
            parser.add_argument('Action_Time_End', location='args')
            parser.add_argument('Is_Finished', location='args')
            args = parser.parse_args()

            Page = args['Page']
            Limit = args['Limit']
            Title = args['Title']
            Action_Time_Start = args['Action_Time_Start']
            Action_Time_End = args['Action_Time_End']
            Is_Finished = args['Is_Finished']

            offset = (Page*Limit-Limit)
            query = Task.query
            
            Total_All_Data = len(query.all())
            Max_Page = round(Total_All_Data/Limit)

            Pagination_Data = response_list['data']['Pagination_Data']
            Pagination_Data['Total_All_Data'] = Total_All_Data
            Pagination_Data['Max_Data_Per_Page'] = Limit
            Pagination_Data['Current_Page'] = Page
            Pagination_Data['Max_Page'] = Max_Page

            if Max_Page == zero:
                Pagination_Data['Max_Page'] = one

            if Title is not None and Title:
                query = query.filter(Task.Title.like("%{}%".format(Title)))

            if ((Action_Time_Start != None and Action_Time_Start) and 
            (Action_Time_End != None and Action_Time_End)):

                Action_Time_Start = unixToTime(Action_Time_Start)
                if Action_Time_Start == "NoneType":
                    data = ResponOnError()
                    data.error_key = "ERROR PARAM Action_Time_Start"
                    data.error_message = "Action_Time_Start MUST BE INTEGER!"
                    marshal_data = marshal(data, Task.response_on_error)
                    return marshal_data, 404, {'Content-Type': 'application/json'}

                Action_Time_End = unixToTime(Action_Time_End)
                if Action_Time_End == "NoneType":
                    data = ResponOnError()
                    data.error_key = "ERROR PARAM Action_Time_End"
                    data.error_message = "Action_Time_End MUST BE INTEGER!"
                    marshal_data = marshal(data, Task.response_on_error)
                    return marshal_data, 404, {'Content-Type': 'application/json'}

                query = query.filter(Task.Action_Time >= Action_Time_Start,
                                    Task.Action_Time <= Action_Time_End)

            if Is_Finished is not None and Is_Finished:

                Is_Finished = convertToBoolean(Is_Finished)
                if Is_Finished == "NoneType":
                    data = ResponOnError()
                    data.error_key = "ERROR PARAM Is_Finished"
                    data.error_message = "YOU MUST WRITE ONLY false OR true!"
                    marshal_data = marshal(data, Task.response_on_error)
                    return marshal_data, 404, {'Content-Type': 'application/json'}
                    
                query = query.filter(Task.Is_Finished == Is_Finished)
            
            response_list['data']['List_Data'] = []

            List_Data = response_list['data']['List_Data']
            for row in query.limit(Limit).offset(offset).all():
                task, status_respon, header = GetByID.get(self, row.Task_ID)
                List_Data.append(task['data'])

            return response_list, 200, {'Content-Type': 'application/json'}

        except:
            return internalServerError(), 500, {'Content-Type': 'application/json'}

api.add_resource(Add, '', '/add')
api.add_resource(GetBySearch, '', '/get')
api.add_resource(Update, '', '/update/<Task_ID>')
api.add_resource(GetByID, '', '/get/<Task_ID>')
api.add_resource(Delete, '', '/delete/<Task_ID>')