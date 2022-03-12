from flask import Flask
from flask import request
from functools import wraps
from datetime import timedelta
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin

app = Flask(__name__)

from flask import json
from werkzeug.exceptions import HTTPException

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@127.0.0.1:3306/test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app, origins="*", allow_headers=[
    "Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
    supports_credentials=True, intercept_exceptions=False)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

@app.before_request
def before_request():
    if request.method != 'OPTIONS':  # <-- required
        pass
    else :
        return {}, 200, {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': '*', 'Access-Control-Allow-Methods': '*'}


from flask import json
from werkzeug.exceptions import HTTPException

from blueprints.Task.model import Task
from blueprints.Objective.model import Objective

from blueprints.Task.resources import bp_task
app.register_blueprint(bp_task, url_prefix='/task')