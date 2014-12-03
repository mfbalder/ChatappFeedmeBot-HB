# AskRonnie

### What is AskRonnie?

AskRonnie is a restaurant suggestion engine chatbot built into a homegrown websocket chat application. It creates a simple web interface to interact with, and it does the work for you -- no more poking around restaurant review websites, checking boxes and searching countless times to find the right match! The bot interacts with the user, generating real time evaluations and asking the questions in a method inspired by decision trees. It does this using a custom built algorithm, and analyzing data from over 35,000 business on Yelp. At the end, you have exactly the kind of restaurant or bar you need.

AskRonnie is built in Python with a Flask framework. It uses a PostgreSQL database with a combination of SQLAlchemy and Psycopg2. Websocket functionality is enabled using the Flask-SocketIO library.

### Contents:
- [Getting Started](#getting-started-with-the-chat-application-andor-askronnie)
- [Features](#features)
- [File Breakdown](#file-breakdown)

### Getting started with the chat application and/or AskRonnie:

1. Clone this repository
	```
	$ git clone https://github.com/mfbalder/ChatappFeedmeBot-HB.git
	```

2. Create and activate a Python virtual environment in the ChatappFeedmeBot-HB directory
	```
	$ virtualenv env
	$ source env/bin/activate 
	```

3. Once you are working in your virtual environment, install the necessary modules
	```
	(env)$ pip install -r requirements.txt
	```

4. I am unable to share Yelp's dataset online, but the data was inserted into a PostgreSQL database. 
To recreate that schema on your machine's local instance of PostgreSQL, enter into the command line 
your psql path, followed by:
	```
	-i restaurantrec.sql
	```

	On my machine, this looks like:

	```
	(env)$ /Applications/Postgres.app/Contents/Versions/9.3/bin'/psql -i /restaurantrec.sql
	```

5. This application uses the Twilio API for texting purposes. To utilize the API, sign up at
www.twilio.com to receive a Auth Token, Account SID, and phone number. Then do the following
to add them to your environment variables:

	From the project directory:

	```
	(env)$ deactivate
	$ cd env/bin
	$ subl activate
	```

	This opens the activate file for the virtual environment.
	Scroll to the bottom of the file, and add:

	```
	export TWILIO_ACCOUNT_SID="[your account SID #]"
	export TWILIO_AUTH_TOKEN="[your auth token #]"
	export TWILIO_NUMBER="+[your twilio phone number]"
	```

	Save the activate file, then in the terminal:

	```
	$ cd ../..
	$ source env/bin/activate
	```

	You should now have access to the appropriate environment variables!


### Features:

- Fully featured chat application using websockets for bi-directional, real time conversations
	* Allows for multiple users with login/logout
	* Supports simultaneous conversations per user
	* Persistant chat bot
	* Displays all users logged in at any given time, updates as users log in and out
	* Flask app renders HTML, handles websockets
- Restaurant recommendation engine chat bot using a subsect of the Yelp dataset
	* Uses a python dictionary to create a state path of questions & queries
	* Custom algorithm to traverse the path of questions
	* Uses Twilio API to text the chosen business's address to the user on request



### File Breakdown:

```webapp.py```: Handles the Flask application, in addition to the socket event handlers

```bot.py```: Manages the brains of the AskRonnie chatbot

```bot_path.py```: Contains the question path dictionary for AskRonnie

```send_message.py```: Handles the call to thw Twilio API

```Templates```: All html files extend from ```base.html``` using Jinja

```Static```: All images, css and javascript files




![picture](https://github.com/mfbalder/ChatappFeedmeBot-HB/blob/master/static/Screen%20Shot%202014-12-01%20at%204.49.08%20PM.png)

![picture](https://github.com/mfbalder/ChatappFeedmeBot-HB/blob/master/static/Screen%20Shot%202014-12-01%20at%204.49.54%20PM.png) 



