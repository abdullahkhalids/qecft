#!/bin/bash

# creating the virtual environment
echo "creating the virtual environment"
python -m venv envqecft
source envqecft/bin/activate

# dependencies
echo "installing the dependencies"
pip install -r requirements.txt

# Start the Flask server
echo "Starting Flask server..."
cd forum 
export FLASK_APP=forumcreator.py
flask run &
sleep 5

# Start the Isso server
cd ..
echo "Starting Isso server..."
isso -c isso.cfg
