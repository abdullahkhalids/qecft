#!/bin/bash

# creating the virtual environment
echo "Creating the virtual environment"
python3 -m venv envqecft
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
cd ..
echo "Starting Isso server..."
isso -c isso.cfg
