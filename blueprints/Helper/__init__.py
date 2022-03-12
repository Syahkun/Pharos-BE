from blueprints.containers.ResponOnError import ResponOnError
from blueprints.Task.model import Task
from flask_restful import marshal
import time
import datetime

response_on_fails = {
    "message": "Failed", 
    "error_key": "ERROR_KEY_HERE", 
    "error_message": "Error Representation in text",
    "error_data": {}
}

error_param = {
    "error_param" : "Data not found"
}

response_list ={
    "message": "Success",
    "data": {
        "List_Data": [],
        "Pagination_Data": {
            "Current_Page": 1, 
            "Max_Data_Per_Page": 10, 
            "Max_Page": 1, 
            "Total_All_Data": 4
        }
    }
}

response_get = {
    "message": "Success",
    "data": {}
}


zero = 0
one = 1

def timeToUnix(date_time):
    try:
        unixtime = time.mktime(date_time.timetuple())
        unixtime = int(unixtime)
        return unixtime
    except:
        return "NoneType"

def unixToTime(date_time):
    try:
        date_time = int(date_time)
        value = datetime.datetime.fromtimestamp(date_time)
        return f"{value:%Y-%m-%d}"
    except:
        return "NoneType"

def convertToBoolean(string):
    if string == "false":
        return False
    elif string == "true":
        return True
    else:
        return "NoneType"

def internalServerError():
    data = ResponOnError()
    data.message = "Failed"
    data.error_key = "ERROR INTERNAL SERVER"
    marshal_data = marshal(data, Task.response_on_error)
    return marshal_data