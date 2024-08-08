import json
from flask import request
from .data_manager import DataManagerInterface
import requests
import uuid
import datetime

# OMDb API configuration
API_KEY = "aeb2943f"
REQUEST_URL = f"https://www.omdbapi.com/?apikey={API_KEY}&t="


def get_movie_from_api(movie_title):
    """
    Helper function to fetch movie data from the OMDb API.

    :param movie_title: The title of the movie to search for.
    :return: A dictionary containing movie data (title, year, poster, rating, director) or None if an error occurs.
    """
    url = REQUEST_URL + movie_title
    try:
        # Send a GET request to the OMDb API
        response = requests.get(url)
        if response.status_code == requests.codes.ok:
            imdb_movie = response.json()

            # Fallback poster image if no poster is available
            default_poster = "/static/uploads/images/default_image.png"

            # Create a dictionary with movie information
            movie = {
                'id': str(uuid.uuid4()),  # Generate a unique ID for the movie
                'title': imdb_movie["Title"],
                'year': imdb_movie["Year"][:4],  # Only take the first 4 characters (year)
                'poster': default_poster if imdb_movie["Poster"] == 'N/A' else imdb_movie["Poster"],
                'rating': imdb_movie["imdbRating"],
                'director': imdb_movie["Director"]
            }
            return movie
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")  # Print an error message if the request fails
        return None
    except ValueError as e:
        print(f"JSON decoding failed: {e}")  # Print an error message if JSON decoding fails
        return None


class JSONDataManager(DataManagerInterface):
    def __init__(self, filename):
        """
        Initialize the JSONDataManager with the file that stores user data.

        :param filename: The path to the JSON file.
        """
        self.filename = filename

    def get_all_users(self):
        """
        Retrieve all users from the JSON file.

        :return: A dictionary of users.
        """
        with open(self.filename, 'r') as file:
            users = json.load(file)
        return users

    def get_all_users_names(self):
        """
        Retrieve a list of all user names.

        :return: A list of user names.
        """
        users = self.get_all_users()
        return [user_info["name"] for key, user_info in users.items()]

    def get_user_name(self, user_id):
        """
        Get the name of a user by their ID.

        :param user_id: The ID of the user.
        :return: The name of the user or an empty list if not found.
        """
        users = self.get_all_users()
        user = users.get(str(user_id))
        if user:
            return user['name']
        return []

    def add_user(self, user_name):
        """
        Add a new user to the JSON file.

        :param user_name: The name of the new user.
        :return: A success message indicating the user was added.
        """
        users = self.get_all_users()
        new_id = str(max(map(int, users.keys())) + 1)  # Generate a new user ID

        # Create a new user entry
        users[new_id] = {
            'name': user_name,
            'movies': []
        }
        self._save_all_users(users)
        return {'message': f"New user {users[new_id]['name']} added successfully"}

    def del_user(self, user_id):
        """
        Delete a user by their ID.

        :param user_id: The ID of the user to delete.
        :return: A success message if the user is deleted, or raises a ValueError if not found.
        """
        users = self.get_all_users()
        if str(user_id) in users:
            del users[str(user_id)]
            self._save_all_users(users)
            return {'message': f"User ID {user_id} deleted successfully"}
        raise ValueError(f"User with ID {user_id} not found")

    def update_user(self, user_id):
        """
        Update a user's name by their ID.

        :param user_id: The ID of the user to update.
        :return: A success message if the user is updated, or an error message if the name already exists.
        """
        users = self.get_all_users()
        if str(user_id) in users:
            updated_name = request.form['name']  # Get the new name from the form
            user = users.get(str(user_id))
            if updated_name in users:
                return {'message': f"User {user['name']} already exists"}
            user['name'] = updated_name
            self._save_all_users(users)
            return {'message': f"User ID {user_id} updated successfully"}
        raise ValueError(f"User with ID {user_id} not found")

    def get_user_movies(self, user_id):
        """
        Get all movies associated with a specific user by their ID.

        :param user_id: The ID of the user.
        :return: A list of movies or raises a TypeError if the user is not found.
        """
        users = self.get_all_users()
        user = users.get(str(user_id))
        if user:
            return user['movies']
        return TypeError(f"User with ID {user_id} not found")

    def add_user_movie(self, user_id, movie_title):
        """
        Add a new movie to a user's movie list.

        :param user_id: The ID of the user.
        :param movie_title: The title of the movie to add.
        :return: A success message if the movie is added, or an error message if the movie already exists.
        """
        users = self.get_all_users()
        user = users.get(str(user_id))
        try:
            if user:
                # Check if the movie already exists in the user's movie list
                for existing_movie in user['movies']:
                    if existing_movie['title'].lower() == movie_title.lower():
                        return {'message': f"The movie title {movie_title} already exists"}

                new_movie = get_movie_from_api(movie_title)  # Fetch movie data from the API
                if new_movie is not None:
                    user['movies'].append(new_movie)  # Add the new movie to the user's movie list
                    self._save_all_users(users)
                    return {'message': f"The movie title {movie_title} added successfully"}
                return {'message': f"Internet Error"}
            else:
                return {'message': f"User with ID {user_id} not found"}
        except KeyError:
            return {'message': f"Movie may not exist. Try rephrasing the title"}

    def update_user_movie(self, user_id, movie_id):
        """
        Update an existing movie in a user's movie list.

        :param user_id: The ID of the user.
        :param movie_id: The ID of the movie to update.
        :return: A success message if the movie is updated, or raises an error if the movie is not found.
        """
        users = self.get_all_users()
        user = users.get(str(user_id))
        if user:
            for movie in user['movies']:
                if str(movie['id']) == str(movie_id):
                    # Update movie details based on the new input received
                    movie['title'] = request.form['title']
                    movie['director'] = request.form['director']

                    # Validate and update the year
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

                    # Validate and update the rating
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
        """
        Delete a movie from a user's movie list.

        :param user_id: The ID of the user.
        :param movie_id: The ID of the movie to delete.
        :return: A success message if the movie is deleted, or raises a ValueError if the user is not found.
        """
        users = self.get_all_users()
        user = users.get(user_id)
        if user:
            # Filter out the movie to be deleted
            user_movies = user['movies']
            user['movies'] = [movie for movie in user_movies if str(movie['id']) != str(movie_id)]
            self._save_all_users(users)
            return {'message': f"{user['name']} movie deleted successfully"}
        else:
            raise ValueError("User not found")

    def _save_all_users(self, users):
        """
        Save all user data back to the JSON file.

        :param users: A dictionary of users to save.
        """
        with open(self.filename, 'w') as file:
            json.dump(users, file, indent=4)  # Write the user data to the file with pretty formatting
