from flask import Flask, jsonify, render_template, url_for
import json
from datamanager.data_json import JSONDataManager

app = Flask(__name__)
data_manager = JSONDataManager('data/data.json')


@app.route('/')
def home():
    return "Welcome to MovieWeb App!"


@app.route('/users')
def list_users():
    data = data_manager.get_all_users()
    users = [{"id": user_id, "name": user_info["name"]} for user_id, user_info in data.items()]
    return render_template('users.html', users=users)


@app.route('/users/<user_id>')
def user_movies(user_id):
    user = data_manager.get_user_name(user_id)
    movies = data_manager.get_user_movies(user_id)

    return render_template('movies.html', movies=movies, user=user)  # Temporarily returning users as a string


@app.route('/add_user')
def add_user():
    pass


@app.route('/users/<user_id>/add_movie')
def add_movie():
    pass


@app.route('/users/<user_id>/update_movie/<movie_id>')
def update_movie():
    pass


@app.route('/users/<user_id>/delete_movie/<movie_id>')
def delete_movie():
    pass


# Route for handling 404 errors
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


# Route for handling other errors (e.g., 500)
@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'), 500


# Route for handling other errors (e.g., 400)
@app.errorhandler(400)
def internal_server_error(error):
    return render_template('400.html'), 400


# Custom error handler for FileNotFoundError
@app.errorhandler(FileNotFoundError)
def handle_file_not_found_error(error):
    return render_template('405.html'), 405


if __name__ == '__main__':
    app.run(debug=True)
