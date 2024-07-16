import json
import os
from flask import request
from .data_manager import DataManagerInterface

file_path = '../data/data.json'


class JSONDataManager(DataManagerInterface):
    def __init__(self, filename):
        self.filename = filename

    def get_all_users(self):
        with open(self.filename, 'r') as file:
            users = json.load(file)
        return users

    def get_all_users_names(self):
        """
        :return: A list of names of all users
        """
        users = self.get_all_users()
        return [user_info["name"] for key, user_info in users.items()]

    def get_user_name(self, user_id):
        users = self.get_all_users()
        user = users.get(str(user_id))
        if user:
            return user['name']
        return []

    def add_user(self, user_name):
        users = self.get_all_users()
        new_id = str(max(map(int, users.keys())) + 1)

        users[new_id] = {
            'name': user_name,
            'movies': []
        }
        self._save_all_users(users)
        return {'message': f"New user {users[new_id]['name']} Added successfully"}

    def get_user_movies(self, user_id):
        users = self.get_all_users()
        user = users.get(str(user_id))
        if user:
            return user['movies']
        return []

    def add_user_movie(self, user_id, movie):
        """Input: given a user_id, Method takes in a dictionary containing data of a new movie,
        and appends to the user_movie list.
            {
              id:
              Title:
              Director: ....
            }
         """
        users = self.get_all_users()
        user = users.get(str(user_id))
        if user:
            for existing_movie in user['movies']:
                if existing_movie['title'] == movie['title']:
                    return {'message': f"The movie title {movie['title']} already exists"}
            user['movies'].append(movie)
        else:
            return {'message': f"User with ID {user_id} not found"}

        self._save_all_users(users)
        return {'message': f"The movie title {movie['title']} Added successfully"}

    def update_user_movie(self, user_id, movie_id):
        """
        Update existing movie in a user's movie list

        :param user_id: The ID of the user
        :param movie_id: The ID of the movie to update
        :return: A dictionary with a success message or raises an error if the movie is not found
        """
        users = self.get_all_users()
        user = users.get(str(user_id))
        if user:
            for movie in user['movies']:
                if str(movie['id']) == str(movie_id):
                    # Update movie details based on the new input received
                    movie['title'] = request.form['title']
                    movie['director'] = request.form['director']
                    movie['year'] = request.form['year']
                    movie['rating'] = request.form['rating']

                    self._save_all_users(users)
                    return {'message': f"Movie ID {movie_id} updated successfully"}
        raise ValueError("Movie not found")

    def delete_user_movie(self, user_id, movie_id):
        users = self.get_all_users()
        user = users.get(user_id)
        if user:
            user_movies = user['movies']
            user['movies'] = [movie for movie in user_movies if str(movie['id']) != str(movie_id)]
            self._save_all_users(users)
            return {'message': f"{user['name']} movie deleted successfully"}
        else:
            raise ValueError("User not found")

    def _save_all_users(self, users):
        with open(self.filename, 'w') as file:
            json.dump(users, file, indent=4)

# bob = JSONDataManager(file_path)
# # print(bob.get_all_users())
# # print(bob.get_user_movies(2))
# movie = {
#         "id": 90,
#         "title": "Dunes",
#         "director": "Nolan",
#         "year": 2017,
#         "rating": 9.8
#       }
# # #
# print(bob.add_user_movie(1, movie))
# #
# # print(bob.get_all_users_names())
