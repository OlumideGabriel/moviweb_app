import json
import os
from data_manager import DataManagerInterface

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
        return [users["name"] for key, users in users.items()]

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
            user['movies'].append(movie)
            self._save_all_users(users)
        else:
            users[user_id] = {'movies': [movie]}  # add user[name] as well*
            self._save_all_users(users)

    def update_user_movie(self, user_id, old_movie_title, new_movie):
        """
        Update existing movie in a user's movie list

        :param user_id:
        :param old_movie_title:
        :param new_movie:
        :return:
        """
        users = self.get_all_users()
        user = users.get(str(user_id))
        if user:
            user_movies = user['movies']
            for i, movie in enumerate(user_movies):
                if movie['title'] == old_movie_title:
                    user_movies[i] = new_movie
                    self._save_all_users(users)
                    return
        raise ValueError("Movie not found")

    def delete_user_movie(self, user_id, movie_title):
        users = self.get_all_users()
        user = users.get(user_id)
        if user:
            user_movies = user['movies']
            user['movies'] = [movie for movie in user_movies if movie['title'] != movie_title]
            self._save_all_users(users)
        else:
            raise ValueError("User not found")

    def _save_all_users(self, users):
        with open(self.filename, 'w') as file:
            json.dump(users, file, indent=4)


# bob = JSONDataManager(file_path)
# print(bob.get_all_users())
# print(bob.get_user_movies(2))
# movie = {
#         "id": 78,
#         "title": "Dune",
#         "director": "Nolan",
#         "year": 2017,
#         "rating": 9.8
#       }
#
# bob.add_user_movie(1, movie)
#
# print(bob.get_all_users_names())
