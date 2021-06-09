# Team 5's Lancometer 3.0

This is the final version of the prototype, sitting at 256 commits

## Documentation

Here are links to documentation for the libraries we will be using most

#### JavaScript Libraries
- [Bootstrap 4.6 Documentation](https://getbootstrap.com/docs/4.6/getting-started/introduction/)
- [jQuery 3.6 Documentation](https://api.jquery.com/)
- [Leaflet 1.7 Documentation](https://leafletjs.com/)
  
#### Backend Libraries
- [Flask 2.0.x Documentation](https://flask.palletsprojects.com/en/2.0.x/)
- [Jinja 3.0.x Documentation](https://jinja.palletsprojects.com/en/3.0.x/)
- [SQLAlchemy 13 Documentation](https://docs.sqlalchemy.org/en/13/)
- [Flask-PyMongo Documentation](https://flask-pymongo.readthedocs.io/en/latest/)

#### WSGI Server
- [Gunicorn](https://docs.gunicorn.org/en/stable/index.html)

### Git Commands:
- git help
- git status
- git add FILENAME
- git pull
- git push
- git commit -m "HELPFUL AND DESCRIPTIVE COMMENT"
- git switch BRANCH

### Requirements

To get the environment set up properly, type:

	python -m venv env
	
	env\Scripts\Activate
	
    python -m pip install --upgrade pip

	python -m pip install -r requirements.txt

## Running the App

To run the flask application do:
	
	python wsgi.py

## Blueprints

Each blueprint is stored within its own subfolder (e.g /user/account) 
and imported into the main application within /user/__init__.py.

Each blueprint can then be developed within the folder and have its own routes without interacting with the other components.

