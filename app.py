from flask import Flask, render_template, url_for, request, redirect, jsonify
from datamanager.data_json import JSONDataManager

app = Flask(__name__)

try:
    # Code that might raise an exception
    data_manager = JSONDataManager('data/data.json')
except IOError as e:
    # Code to handle the exception
    print("An IOError occurred: ", str(e))


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/users')
def list_users():
    data = data_manager.get_all_users()
    users = [{"id": user_id, "name": user_info["name"]} for user_id, user_info in data.items()]
    return render_template('users.html', users=users)


@app.route('/ManageUsers')
def manage_users():
    data = data_manager.get_all_users()
    users = [{"id": user_id, "name": user_info["name"]} for user_id, user_info in data.items()]
    return render_template('manage_users.html', users=users)


@app.route('/users/<user_id>', methods=['GET'])
def user_movies(user_id):
    user = data_manager.get_user_name(user_id)
    movies = data_manager.get_user_movies(user_id)
    movie_count = str(len(movies))
    plural = '' if len(movies) == 1 else 's'

    return render_template('movies.html', movies=movies, user=user, user_id=user_id, movie_count=movie_count,
                           plural=plural)


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        new_user = request.form['name']
        all_users = data_manager.get_all_users_names()
        while new_user in all_users:
            error = 'User already exists, kindly add a unique name'
            return render_template('add_user.html', error=error)
        else:
            response = data_manager.add_user(new_user)
            if 'message' in response:
                message = response['message']
                return render_template('add_user.html', message=message)
    return render_template('add_user.html')


@app.route('/users/delete_user/<user_id>', methods=['POST'])
def delete_user(user_id):
    data_manager.del_user(user_id)
    return redirect(url_for('manage_users'))


@app.route('/users/update_user/<user_id>', methods=['GET', 'POST'])
def update_user(user_id):
    if request.method == 'POST':
        data_manager.update_user(user_id)
        return redirect(url_for('manage_users'))

    users = data_manager.get_all_users()
    user = users.get(str(user_id))
    return render_template('update_user.html', user=user, user_id=user_id)


@app.route('/users/<user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    if request.method == 'POST':
        movie_title = request.form['title']
        data_manager.add_user_movie(user_id, movie_title)

        return redirect(url_for('user_movies', user_id=user_id))

    return render_template('add_movie.html', user_id=user_id)


@app.route('/users/<user_id>/update_movie/<movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    old_movie = None
    error = None

    if request.method == 'POST':

        response = data_manager.update_user_movie(user_id, movie_id)
        if "error" in response:
            error = response['error']

            movie = {  # This movie retains current data in form while we update info
                'id': movie_id,
                'title': request.form['title'],
                'year': request.form['year'],
                'director': request.form['director'],
                'rating': request.form['rating']
            }

            return render_template('update.html', user_id=user_id, error=error, movie_id=movie_id, old_movie=movie)
        elif "message" in response:
            message = response['message']
            return render_template('update.html', user_id=user_id, message=message, old_movie=old_movie)
        return redirect(url_for('user_movies', user_id=user_id, movie_id=movie_id))

    users = data_manager.get_all_users()
    user = users.get(str(user_id))
    if user:
        for movie in user['movies']:
            if str(movie['id']) == str(movie_id):
                old_movie = movie
                break
    return render_template('update.html', user_id=user_id, old_movie=old_movie, error=error)


@app.route('/users/<user_id>/delete_movie/<movie_id>', methods=['POST'])
def delete_movie(user_id, movie_id):
    data_manager.delete_user_movie(user_id, movie_id)
    return redirect(url_for('user_movies', user_id=user_id))


# Route for handling 404 errors
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(FileNotFoundError)
def page_not_found(error):
    return render_template('file_not_found.html'), 404


@app.errorhandler(KeyError)
def page_not_found(error):
    return render_template('add_movie.html'), 404


# Route for handling other errors (e.g., 500)
@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'), 500


@app.errorhandler(TypeError)
def type_error(error):
    return render_template('400.html'), 400


# Route for handling other errors (e.g., 400)
@app.errorhandler(ValueError)
def handle_value_error(error):
    return render_template('400.html'), 400


# Custom error handler for FileNotFoundError
@app.errorhandler(405)
def handle_file_not_found_error(error):
    return render_template('405.html'), 405


if __name__ == '__main__':
    app.run(port=5003, host='0.0.0.0', debug=True)
