# AskRonnie

### What is AskRonnie?

AskRonnie is a restaurant suggestion engine chatbot built into a homegrown websocket chat application. It creates a simple web interface to interact with, and it does the work for you -- no more poking around restaurant review websites, checking boxes and searching countless times to find the right match! The bot interacts with the user, generating real time evaluations and asking the questions it needs to best help you. It does this using a custom built algorithm, and analyzing data from over 35,000 business on Yelp. At the end, you have exactly the kind of restaurant or bar you need.

AskRonnie is built in Python with a Flask framework. It uses a PostgreSQL database with a combination of SQLAlchemy and Psycopg2. Websocket functionality is enabled using the Flask-SocketIO library.

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

### File Breakdown:

webapp



![picture](https://github.com/mfbalder/ChatappFeedmeBot-HB/blob/master/static/Screen\ Shot\ 2014-11-28\ at\ 4.09.21\ PM.png) 

### Why websockets? Why a chat bot?

For my original project, the goal was to get a better understanding of how instant messenging and chat applications work, particularly in the context of websockets, which use a handshake to create the opportunity for continuous, bi-directional communication without having to constantly make new HTTP requests. This allows for rapid, delay-free communication between users, and is perfect for a chat situation. 

Technologies Researched/Used:
* C-based Languages (Python)
* Web Frameworks (Flask)
* Websockets (Flask-SocketIO)
* JQuery
* Encryption (JSEncrypt)
* HTML/CSS
* Jinja