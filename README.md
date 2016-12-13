#Food and Stuff (EC601)
##v0.4 
###How to run:
####The project files are inside the "ML Engine" folder

#####Requirements: 

1. python 2.7.12 with sqlite

2. Dataset (https://www.dropbox.com/s/v8ko9iy8ot7in7f/dataset.zip?dl=0)

Note: The zip file above contains "linked_cate_name.json" which is our pre-processed dataset. Make sure you change the path inside server.py to wherever you download it.

#####Step 1: Setup python environment (may need sudo on Linux)
```
pip install Flask-SqlAlchemy wtforms flask flask_googlemaps
```

#####Step 2: Setup database
```
python tabledef.py
```

######Populate database with dummy data
```
python dummy.py
```

#####Step 3: Runing the application

######For Windows 10, you'll have to run without NGINX: 
```
python server.py
```
######For Linux (may need sudo for Linux to host on port 80): 
```
./start.sh
```

####Feel free to reach out at ssingh02@bu.edu if you have any trouble running this application.
