#!/bin/bash

# creating the virtual environment
echo "Creating the virtual environment"
command -v virtualenv >/dev/null 2>&1 || { echo >&2 "virtualenv is not installed. Installing..."; python3 -m pip install virtualenv; }
python3 -m virtualenv envqecft
source envqecft/bin/activate

# dependencies
echo "Installing the dependencies"
pip3 install -r requirements.txt

# Start the Flask server
echo "Starting Flask server..."
cd forum 
export FLASK_APP=forumcreator.py
flask run --port=8000 &
sleep 5

# Start the Isso server
echo "Starting Isso server..."
isso -c isso.cfg
