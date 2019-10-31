from flask import Flask
from flask_restful import Api, Resource, reqparse

app = Flask(__name__)
api = Api(app)

users = [
    {
        'name':'Stacy',
        'role':['admin', 'user'],
        'age':20
    },
    {
        'name':'Eric',
        'role':'user',
        'age':102
    },
    {
        'name':'Anushree',
        'role':'user',
        'age':28
    }
]

# create api endpoints via user resource class
class User(Resource):
    # method to get user data
    def get(self, name):
        for user in users:
            if(name == user['name']):
                return user, 200
        return 'User not found', 404

    # method to create a new user
    def post(self, name):
        # create parser and add values to it
        parser = reqparse.RequestParser()
        parser.add_argument('age')
        parser.add_argument('role')
        # store parsed arguments in args
        args = parser.parse_args()

        for user in users:
            # if user exists return message with bad request code
            if(name == user['name']):
                return 'User with name {} already exists'.format(name), 400

        # create new user with passed-in args
        user = {
            'name': name,
            'role': args['role'],
            'age': args['age']
        }
        users.append(user)
        return user, 201

    # update user details or create on if not exists
    def put(self, name):
        # create parser and add values to it
        parser = reqparse.RequestParser()
        parser.add_argument('age')
        parser.add_argument('role')
        # store parsed arguments in args
        args = parser.parse_args()

        for user in users:
            if(name == user['name']):
                user['age'] = args['age']
                user['role'] = args['role']
                return user, 201

        user = {
            'name': name,
            'role': args['role'],
            'age': args['age']
        }
        users.append(user)
        return user, 201

    # delete a user
    def delete(self, name):
        global users
        users = [user for user in users if user['name'] != name]
        return '{} is deleted.'.format(name), 200

# after implementing all the methods in your User resource,
# add the resource to your api and specify the route,
# then finally run the flask application

api.add_resource(User, '/user/<string:name>')

# rem running in debug mode enable flask to reload
# automatically when code is updated and give warning messages
# if something goes wrong-- dev only feature
app.run(debug=True)
