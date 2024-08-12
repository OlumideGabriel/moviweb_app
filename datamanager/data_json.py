import json
import random
import string
from flask import request, current_app
from .data_manager import DataManagerInterface
from .user_manager import User
import requests
import uuid
import datetime
import os
from werkzeug.utils import secure_filename

# OMDb API configuration
API_KEY = "aeb2943f"
REQUEST_URL = f"https://www.omdbapi.com/?apikey={API_KEY}&t="
PROFILE_IMAGE = f"/static/uploads/profile_images/default_avatar.jpg"


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


def save_profile_image(profile_image, user_id):
    """
    Save the uploaded profile image to the server.

    :param profile_image: The image file uploaded by the user.
    :param user_id: The ID of the user to associate with the profile image.
    :return: The filename of the saved image.
    """
    # Ensure the upload directory exists
    upload_folder = os.path.join(current_app.root_path, 'static/uploads/profile_images')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    # Generate a secure filename using the user ID to avoid conflicts
    filename = secure_filename(f"user_{user_id}_{profile_image.filename}")

    # Define the path to save the image
    filepath = os.path.join(upload_folder, filename)

    # Save the image file to the designated path
    profile_image.save(filepath)

    # Return the path relative to the static folder to store in the database
    return f'/static/uploads/profile_images/{filename}'


def generate_password(length=10):
    # Define possible characters
    characters = string.ascii_letters + string.digits + string.punctuation

    # Generate a random password
    password = ''.join(random.choice(characters) for i in range(length))

    return password


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

    def is_admin(self, user_id):
        """
        Check if a user is an admin based on their ID.

        :param user_id: The ID of the user to check.
        :return: True if the user is an admin, otherwise False.
        """
        users = self.get_all_users()
        user = users.get(str(user_id))
        return user.get('is_admin', False) if user else False

    def get_all_users_names(self):
        """
        Retrieve a list of all usernames.

        :return: A list of usernames.
        """
        users = self.get_all_users()
        return [user_info["username"] for key, user_info in users.items()]

    def get_user_name(self, user_id):
        """
        Get the name of a user by their ID.

        :param user_id: The ID of the user.
        :return: The name of the user or an empty list if not found.
        """
        users = self.get_all_users()
        user = users.get(str(user_id))
        if user:
            return user['username']
        return []

    def get_user_by_username(self, user_name):
        users = self.get_all_users()
        for user_id, user_info in users.items():
            if user_name.lower() == user_info['username'].lower():
                user = users.get(str(user_id))
                return user_id, user
        raise TypeError(f"User ({user_name}) not found")

    def add_user(self, username):
        """
        Add a new user to the JSON file.

        :param username: The name of the new user.
        :return: A success message indicating the user was added.
        """
        users = self.get_all_users()
        new_id = str(max(map(int, users.keys())) + 1)  # Generate a new user ID

        # Create a new user entry
        users[new_id] = {
            'username': username,
            'password': generate_password(),
            'is_admin': False,
            'profile': PROFILE_IMAGE,
            'movies': []
        }
        self._save_all_users(users)
        return {'message': f"New user {users[new_id]['username']} added successfully"}

    def create_user(self, username, password):
        users = self.get_all_users()
        new_id = str(max(map(int, users.keys())) + 1)  # Generate a new user ID

        # Create a new user entry
        users[new_id] = {
            'username': username,
            'password': password,
            'is_admin': False,
            'profile': "",
            'movies': []
        }
        self._save_all_users(users)
        return User(id=new_id, username=username, password=password)

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
            is_admin = request.form['is_admin']
            user = users.get(str(user_id))
            if updated_name in users:
                return {'message': f"User {user['name']} already exists"}

            # Update the user's information
            user['username'] = updated_name
            user['is_admin'] = True if is_admin == 'True' else False

            self._save_all_users(users)
            return {'message': f"User ID {user_id} updated successfully"}
        raise ValueError(f"User with ID {user_id} not found")

    def update_profile(self, user_id):
        """
        Update a user's name and/or profile image by their ID.

        :param user_id: The ID of the user to update.
        :return: A success message if the user is updated, or an error message if the name already exists.
        """
        users = self.get_all_users()
        if str(user_id) in users:
            updated_name = request.form['username']  # Get the new username from the form
            user = users.get(str(user_id))

            # Check if the new username already exists and is not the current user's username
            if updated_name in [u['username'] for u in users.values()] and updated_name != user['username']:
                return {'message': f"Username '{updated_name}' already exists"}

            # Update the username
            user['username'] = updated_name

            # Handle the profile image upload
            if 'profile_image' in request.files:
                profile_image = request.files['profile_image']
                if profile_image.filename != '':
                    # Save the new profile image (logic to save the file needs to be implemented)
                    filename = save_profile_image(profile_image, user_id)  # Implement this function as needed
                    user['profile'] = filename

            # Save the updated user data
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

# bob = JSONDataManager('../data/data.json')
# # print(bob.is_admin(5))
# print(bob.update_profile(1))
