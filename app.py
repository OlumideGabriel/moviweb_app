from flask import Flask
from data_manager.data_json import JSONDataManager

app = Flask(__name__)
data_manager = JSONDataManager('movies.json')  # Use the appropriate path to your JSON file


@app.route('/')
def home():
    return "Welcome to MovieWeb App!"


if __name__ == '__main__':
    app.run(debug=True)
