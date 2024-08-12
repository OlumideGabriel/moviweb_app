from flask_login import UserMixin
import json


class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    @staticmethod
    def get_user_by_id(user_id, filename):
        with open(filename, 'r') as file:
            users = json.load(file)
        user = users.get(str(user_id))
        if user:
            return User(id=user_id, username=user['username'], password=user['password'])
        return None

    @staticmethod
    def get_user_by_username(username, filename):
        with open(filename, 'r') as file:
            users = json.load(file)
        for user_id, user_info in users.items():
            if user_info['username'] == username:
                return User(id=user_id, username=user_info['username'], password=user_info['password'])
        return None



