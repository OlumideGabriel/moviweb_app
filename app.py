from flask import Flask, render_template, url_for, request, redirect, flash, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from functools import wraps
from datamanager.data_json import JSONDataManager
from datamanager.user_manager import User

app = Flask(__name__)
app.secret_key = 'your_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to login page if not logged in

try:
    # Code that might raise an exception
    data_manager = JSONDataManager('data/data.json')
    user_data = 'data/data.json'
except IOError as e:
    # Code to handle the exception
    print("An IOError occurred: ", str(e))


@login_manager.user_loader
def load_user(user_id):
    return User.get_user_by_id(user_id, filename=user_data)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id or not data_manager.is_admin(user_id):
            flash("You do not have permission to access this page.", "danger")
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)

    return decorated_function


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.get_user_by_username(username, filename=user_data)
        if user and user.password == password:
            login_user(user)
            session['user_id'] = user.id  # Store the user ID in session
            flash('Logged in successfully.')
            return redirect(url_for('profile', username=current_user.username))
        else:
            flash('Invalid username or password.')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = User.get_user_by_username(username, filename=user_data)
        if existing_user:
            flash('Username already exists. Please choose another one.')
        else:
            new_user = data_manager.create_user(username, password)
            login_user(new_user)
            session['user_id'] = new_user.id  # Store the user ID in session
            flash('Registration successful. You are now logged in.')
            return redirect(url_for('profile', username=current_user.username))
    return render_template('register.html')


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/user/<username>')
@login_required
def profile(username):
    user_id, user_info = data_manager.get_user_by_username(username)
    current_user_id, current_user_info = data_manager.get_user_by_username(current_user.username)

    movies = data_manager.get_user_movies(user_id)
    movie_count = str(len(movies))
    return render_template('profile.html', user=user_info, user_id=user_id, current_user_info=current_user_info,
                           movie_count=movie_count)


@app.route('/user/<username>/ManageProfile', methods=['GET', 'POST'])
@login_required
def update_profile(username):
    user_id, user_info = data_manager.get_user_by_username(username)

    if request.method == 'POST':
        data_manager.update_profile(user_id)
        users = data_manager.get_all_users()
        user = users.get(str(user_id))
        return redirect(url_for('profile', username=user['username']))

    if username == current_user.username or not user_info['is_admin']:

        users = data_manager.get_all_users()
        user = users.get(str(user_id))
        return render_template('manage_profile.html', user_id=user_id, user=user)

    message = f"User is Admin: No access to edit user"
    user_id, user_info = data_manager.get_user_by_username(username)

    current_user_id, current_user_info = data_manager.get_user_by_username(current_user.username)
    return render_template('profile.html', user_id=user_id, user=user_info, error=message,
                           current_user_info=current_user_info)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('user_id', None)  # Remove the user ID from the session
    flash('You have been logged out.')
    return redirect(url_for('login'))


@app.route('/users')
@login_required
def list_users():
    data = data_manager.get_all_users()
    users = [{"id": user_id, "name": user_info["username"], "is_admin": user_info["is_admin"]} for user_id, user_info in
             data.items()]
    user = data.get(str(current_user.id))
    return render_template('users.html', users=users, user=user)


@app.route('/ManageUsers')
@admin_required
def manage_users():
    data = data_manager.get_all_users()
    users = [{"id": user_id, "name": user_info["username"]} for user_id, user_info in data.items()]
    return render_template('manage_users.html', users=users)


@app.route('/users/<user_id>', methods=['GET'])
@login_required
def user_movies(user_id):
    user = data_manager.get_user_name(user_id)
    movies = data_manager.get_user_movies(user_id)
    movie_count = str(len(movies))
    plural = '' if len(movies) == 1 else 's'

    current_user_id, current_user_info = data_manager.get_user_by_username(current_user.username)

    return render_template('movies.html', movies=movies, user=user, user_id=user_id, movie_count=movie_count,
                           plural=plural, current_user_info=current_user_info)


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        new_user = request.form['username']
        all_users = data_manager.get_all_users_names()
        if new_user in all_users:
            error = 'User already exists, kindly add a unique name'
            return render_template('add_user.html', error=error)
        else:
            response = data_manager.add_user(new_user)
            if 'message' in response:
                message = response['message']
                return render_template('add_user.html', message=message)
    return render_template('add_user.html')


@app.route('/users/delete_user/<user_id>', methods=['POST'])
@login_required
@admin_required  # Only admin can delete users
def delete_user(user_id):
    data_manager.del_user(user_id)
    return redirect(url_for('manage_users'))


@app.route('/users/update_user/<user_id>', methods=['GET', 'POST'])
@login_required
@admin_required  # Only admin can update users and assign admin status
def update_user(user_id):
    if request.method == 'POST':
        data_manager.update_user(user_id)
        return redirect(url_for('manage_users'))

    data = data_manager.get_all_users()
    users = [{"id": user_id, "name": user_info["username"], "is_admin": user_info["is_admin"]} for user_id, user_info in
             data.items()]
    user = data.get(str(user_id))
    return render_template('update_user.html', user=user, users=users, user_id=user_id)


@app.route('/users/<user_id>/add_movie', methods=['GET', 'POST'])
@login_required
def add_movie(user_id):
    if request.method == 'POST':
        movie_title = request.form['title']
        data_manager.add_user_movie(user_id, movie_title)

        return redirect(url_for('user_movies', user_id=user_id))

    return render_template('add_movie.html', user_id=user_id)


@app.route('/users/<user_id>/update_movie/<movie_id>', methods=['GET', 'POST'])
@login_required
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
@login_required
def delete_movie(user_id, movie_id):
    data_manager.delete_user_movie(user_id, movie_id)
    return redirect(url_for('user_movies', user_id=user_id))


# Error handlers
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'), 500


@app.errorhandler(ValueError)
def handle_value_error(error):
    return render_template('400.html', error=error), 400


@app.errorhandler(KeyError)
def handle_value_error(error):
    return render_template('KeyError.html', error=error), 400


@app.errorhandler(TypeError)
def handle_value_error(error):
    return render_template('404.html', error=error), 400


@app.errorhandler(405)
def handle_method_not_allowed(error):
    return render_template('405.html', error=error), 405


if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0', debug=True)
