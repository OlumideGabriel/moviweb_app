from flask import Flask, jsonify, render_template, url_for, request, redirect
import json
from datamanager.data_json import JSONDataManager
import uuid

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


@app.route('/users/<user_id>', methods=['GET'])
def user_movies(user_id):
    user = data_manager.get_user_name(user_id)
    movies = data_manager.get_user_movies(user_id)

    return render_template('movies.html', movies=movies, user=user, user_id=user_id)  # Temporarily returning users as a string


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        new_user = request.form['name']
        all_users = data_manager.get_all_users_names()
        while new_user in all_users:
            error = 'User already exists, kindly add a unique name'
            return render_template('add_user.html', message=error)
        else:
            data_manager.add_user(new_user)
            return redirect(url_for('list_users'))
    return render_template('add_user.html')


@app.route('/users/<user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    if request.method == 'POST':
        movie = {
            'id': str(uuid.uuid4()),  # Convert UUID to string for JSON serialization
            'title': request.form['title'],
            'director': request.form['director'],
            'year': request.form['year'],
            'rating': request.form['rating']
        }
        data_manager.add_user_movie(user_id, movie)
        return redirect(url_for('user_movies', user_id=user_id))

    return render_template('add_movie.html', user_id=user_id)


@app.route('/users/<user_id>/update_movie/<movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):

    if request.method == 'POST':
        data_manager.update_user_movie(user_id, movie_id)
        return redirect(url_for('user_movies', user_id=user_id, movie_id=movie_id))

    users = data_manager.get_all_users()
    user = users.get(str(user_id))
    if user:
        for movie in user['movies']:
            if str(movie['id']) == str(movie_id):
                old_movie = movie
                return render_template('update.html', user_id=user_id, old_movie=old_movie)


@app.route('/users/<user_id>/delete_movie/<movie_id>', methods=['GET', 'POST'])
def delete_movie(user_id, movie_id):
    if request.method == 'POST':
        data_manager.delete_user_movie(user_id, movie_id)
        return redirect(url_for('user_movies', user_id=user_id))

    return redirect(url_for('user_movies', user_id=user_id))


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
