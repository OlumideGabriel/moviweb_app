Welcome to **MovieHub** - a dynamic and interactive web application that allows you to manage users and their favorite movies. Built with Python, Flask, HTML, CSS, JavaScript, and Bootstrap, MovieHub provides a seamless experience for creating, reading, updating, and deleting user and movie information.

## Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [View Live Website](#view-live-website)
- [Setup](#setup)
- [Usage](#usage)
- [API Integration](#api-integration)
- [Contributing](#contributing)
- [Screenshots](#screenshots)

## Features

- **User Management**: Create, read, update, and delete user profiles.
- **Movie Management**: Add movies to user profiles, view movie details, update movie information, and delete movies.
- **External API Integration**: Fetch movie data from the OMDb API.
- **Responsive Design**: Built with Bootstrap to ensure a seamless experience across devices.
- **Error Handling**: Comprehensive error handling to manage various scenarios gracefully.

## Tech Stack

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Data Management**: JSON
- **External API**: OMDb API

## View Live Website

   Copy and paste link in browser 
   ```
   https://olumidegabriel.pythonanywhere.com/
   ```

## Setup

1. **Clone the Repository**

   ```bash
   git clone https://github.com/your-username/MovieHub.git
   cd MovieHub
   ```

2. **Create a Virtual Environment**

   ```bash
   python -m venv venv
   ```

3. **Activate the Virtual Environment**

   - **Windows**:

     ```bash
     venv\Scripts\activate
     ```

   - **macOS/Linux**:

     ```bash
     source venv/bin/activate
     ```

4. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

5. **Set Up the Environment Variables**

   Create a `.env` file in the root directory and add your OMDb API key:

   ```env
   API_KEY=your_omdb_api_key
   ```

6. **Run the Application**

   ```bash
   flask run
   ```

7. **Open Your Browser**

   Navigate to `http://127.0.0.1:5000` to view the application.

## Usage

### User Management

- **Add User**: Go to the 'Add User' page, enter the user's name, and click 'Submit'.
- **View Users**: Navigate to the 'Users' page to see all registered users.
- **Update User**: Click on a user's name on the 'Manage Users' page, modify the details, and save changes.
- **Delete User**: Use the delete button next to a user’s name on the 'Manage Users' page.

### Movie Management

- **Add Movie**: On a user’s movie list page, enter the movie title and click 'Add Movie'.
- **View Movies**: See all movies listed under a user’s profile.
- **Update Movie**: Click on a movie title to edit its details.
- **Delete Movie**: Remove a movie using the delete button next to it.

## API Integration

MovieHub uses the [OMDb API](http://www.omdbapi.com/) to fetch movie details. Ensure you have an API key and add it to the `.env` file as shown in the setup section.

## Contributing

We welcome contributions to MovieHub! To contribute:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature-name`.
3. Make your changes and commit them: `git commit -m 'Add some feature'`.
4. Push to the branch: `git push origin feature-name`.
5. Create a pull request.

Please ensure your code adheres to our coding standards and includes appropriate tests.

## Screenshots

![Home Page](static/uploads/screenshots/home.png)
*Home Page*

![User List](static/uploads/screenshots/users.png)
*User List*

![User Added Successfully](static/uploads/screenshots/success.png)
*User Added Successfully*

![Movie List](static/uploads/screenshots/movies.png)
*Movie List*

![Movie Update Error](static/uploads/screenshots/movie-error.png)
*Movie Update Error*

## Acknowledgments

- [OMDb API](http://www.omdbapi.com/) for providing movie data.
- Flask community for excellent documentation and support.
- Bootstrap for the responsive design framework.
- FontAwesome for Icons
