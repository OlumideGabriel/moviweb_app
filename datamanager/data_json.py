import json
from flask import request
from .data_manager import DataManagerInterface
import requests
import uuid
import datetime

API_KEY = "aeb2943f"
REQUEST_URL = f"https://www.omdbapi.com/?apikey={API_KEY}&t="


def get_movie_from_api(movie_title):
    """
    Helper function to get movie data from IMDP Api
    :param movie_title:
    :return: dict{movie} data. Title, Year, Poster, Rating, Director,
    """
    url = REQUEST_URL + movie_title
    try:
        response = requests.get(url)
        if response.status_code == requests.codes.ok:
            imdb_movie = response.json()

            default_poster = "/static/uploads/images/default_image.png"

            movie = {
                'id': str(uuid.uuid4()),  # Convert UUID to string for JSON serialization
                'title': imdb_movie["Title"],
                'year': imdb_movie["Year"][:4],
                'poster': default_poster if imdb_movie["Poster"] == 'N/A' else imdb_movie["Poster"],
                'rating': imdb_movie["imdbRating"],
                'director': imdb_movie["Director"]
            }
            return movie
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
    except ValueError as e:
        print(f"JSON decoding failed: {e}")
        return None


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

    def del_user(self, user_id):
        users = self.get_all_users()
        if str(user_id) in users:
            del users[str(user_id)]
            self._save_all_users(users)
            return {'message': f"User ID {user_id} deleted successfully"}
        raise ValueError(f"User with ID {user_id} not found")

    def update_user(self, user_id):
        users = self.get_all_users()
        if str(user_id) in users:
            updated_name = request.form['name']
            user = users.get(str(user_id))
            if updated_name in users:
                return {'message': f"User {user['name']} already exits"}
            user['name'] = updated_name
            self._save_all_users(users)
            return {'message': f"User ID {user_id} updated successfully"}
        raise ValueError(f"User with ID {user_id} not found")

    def get_user_movies(self, user_id):
        users = self.get_all_users()
        user = users.get(str(user_id))
        if user:
            return user['movies']
        return TypeError(f"User with ID {user_id} not found")

    def add_user_movie(self, user_id, movie_title):
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
        try:
            if user:
                for existing_movie in user['movies']:
                    if existing_movie['title'].lower() == movie_title.lower():
                        return {'message': f"The movie title {movie_title} already exists"}

                new_movie = get_movie_from_api(movie_title)
                if new_movie is not None:
                    user['movies'].append(new_movie)
                    self._save_all_users(users)
                    return {'message': f"The movie title {movie_title} Added successfully"}
                return {'message': f"Internet Error"}
            else:
                return {'message': f"User with ID {user_id} not found"}
        except KeyError:
            return {'message': f"Movie may not exists. try rephrasing the title"}

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

                    # Validate and update year
                    while True:
                        try:
                            year = int(request.form['year'])
                            current_year = datetime.datetime.now().year
                            if 1900 <= year <= current_year:  # Example range check
                                movie['year'] = year
                                break
                            else:
                                return {"error": "Year is out of range. Please enter a valid year."}
                        except ValueError:
                            return {"error": "Invalid year input. Please enter a valid year."}

                    # Validate and update rating
                    while True:
                        try:
                            rating = float(request.form['rating'])
                            if 1.0 <= rating <= 10.0:
                                movie['rating'] = round(rating, 1)
                                break
                            else:
                                return {"error": "Rating must be between 1 and 10. Please enter a valid rating."}
                        except ValueError:
                            return {"error": "Invalid rating input. Please enter a valid rating."}

                    self._save_all_users(users)
                    return {'message': f"Movie updated successfully"}
        return {"error": "Movie not found"}

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
