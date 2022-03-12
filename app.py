from flask_restful import Resource, Api
from blueprints import app

api = Api(app, catch_all_404s=True)

if __name__ == '__main__':
    app.run(debug=True)