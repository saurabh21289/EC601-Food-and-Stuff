#Food and Stuff (EC601)
##Demo v0.4 is live at <a href="http://foodandstuff.us.to:8080" target="_blank">http://foodandstuff.us.to:8080</a>
#####Technologies used are `Python 2.7.12 with SQLite, Mrjob, Flask_googlemaps, Pandas, NumPy, Flask with NGINX, Html5, JavaScript, Bootstrap, Jinja2, Google maps API, Charts.js, SQLAlchemy`

###How to run:
####The project files are inside the "ML Engine" folder.
#####Requirements: 

1. python 2.7.12 with sqlite

2. Extract dataset file (linked_cate_name.json) inside the "ML Engine Folder" 

  Link to dataset: https://github.com/saurabh21289/EC601-Food-and-Stuff/raw/master/linked_cate_name.zip -or- https://www.dropbox.com/s/v8ko9iy8ot7in7f/dataset.zip?dl=0

Note: The zip file above contains "linked_cate_name.json" which is our pre-processed dataset. Ensure that you place this file inside the "ML Engine" folder so that server.py can locate it.

#####Step 1: Setup python environment (may need sudo on Linux)
```
pip install Flask-SqlAlchemy wtforms flask flask_googlemaps
```

#####Step 2: Setup database (may need sudo for Linux)
```
python tabledef.py
```

######Populate database with dummy data (may need sudo for Linux)
```
python dummy.py
```

#####Step 3: Running the application without NGINX

######For both Windows 10 and Linux:
```
python server.py
```
######Tip: If want to use NGINX, install uWSGI using `sudo pip install uwsgi`. Then run:
```
./start.sh
```
#####The server runs on `http://localhost:5000` by default. If you want to host on a different port, change inside `server.py` for Windows and in `start.sh` for Linux.
####Feel free to reach out at ssingh02@bu.edu if you have any trouble running this application.
