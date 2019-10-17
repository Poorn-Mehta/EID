#!/bin/bash

# @Subject - ECEN 5783 EID Project-2
# @Author - Rushi Macwan and Poorn Mehta
# @Brief: Script to run the project files from one place

# Running the Tornado_QT_main.py python script

echo "Running the Tornado_QT_main.py python script"
python3 Tornado_QT_main.py &

# Sleeping for 1 second to let Python start and create the Table in database

sleep 4

# Running the Node.JS Webserver Javascript

echo "Running the Node.JS Webserver Javascript"
node node_server.js

echo "System ready to serve an HTML client..."
