# DiggerOfDelphi-local v.0.0.1

System runs as a webserver, gives the user the option to select files, enter their API key and then label heavy equipment in photos. Only uses Google Gemini Pro Vision at the moment

To setup:
First build docker container:

May need to pull base container using "docker pull python:3.9-slim"

Then build using "docker build -t laebel-app ."

Docker container can be run using "docker run -p 5000:5000 -it label-app"

Container will prompt you at the terminal if you would like to make a new encryption key, say "y". This encryption key is used to encrypt your API-key while it's stored in the app database

Open up your browser to 127.0.0.1:5000 and start labeling some photos. Option to download the json is at the bottom of the screen

To use you'll need a google gemini api key. There is a free tier and you can sign up at https://ai.google.dev/
