# AskRonnie

### What is AskRonnie?

AskRonnie is a restaurant suggestion engine chatbot built into a homegrown websocket chat application. It creates a simple web interface to interact with, and it does the work for you -- no more poking around restaurant review websites, checking boxes and searching countless times to find the right match! The bot interacts with the user, generating real time evaluations and asking the questions it needs to best help you. It does this using a custom built algorithm, and analyzing data from over 35,000 business on Yelp. At the end, you have exactly the kind of restaurant or bar you need.

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