import random
import time
import os

from flask import Flask, render_template, session, request, redirect
from flask.ext.socketio import SocketIO, emit, join_room, leave_room, send

import bot
from send_message import send_text_message


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'secret!')
socketio = SocketIO(app)


################################
# connected_users --> {username: ['room1 they're in', 'room2', 'room3']}

# next_state, last_state --> Int (to track where Ronnie is in his path)

# ronniechat --> Boolean (to indicate whether Ronnie is currently in the path)
################################
connected_users = {'AskRonnie': []}
ronniechat = False
next_state = None
last_state = None


def get_user():
	return session.get("user")

def reset_ronnie():
	"""Resets AskRonnie bot so that it's ready to start from the beginning"""
	global ronniechat, next_state

	ronniechat = False
	bot.query = """SELECT r.name FROM restaurants AS r join categories AS c
				   ON r.id=c.business_id join categoryLookup AS l 
				   ON l.category=c.category"""
	last_state = None
	next_state = None


################################
		#Flask Routes
################################

@app.route('/')
def index():
	user = get_user()
	if user is None:
		return redirect("/login")

	# creates a list of all the users that are logged in, without the current user
	users_to_display = [u for u in connected_users if u != user]

	return render_template('index.html', users = users_to_display,
										 user=user)

@app.route('/login')
def login():
	return render_template("login.html")


@app.route("/signup_form")
def signup_form():
	return render_template("signup.html")


@app.route('/logout')
def logout():
	global connected_users

	user = get_user()
	if user:
		# deletes the current user from the app's list of connected users
		del connected_users[user]
		print "connected_users in logout: ", connected_users

		# clears the user's session
		session.clear()
		print "session in logout ", session

		# reset Ronnie
		reset_ronnie()

	return redirect("/login")


@app.route("/set_session")
def set_session():
	"""Is run on submit of the login form, & adds user to the session."""

	global connected_users

	# get the current logged in user, and set that to the session
	user = request.args.get("user")
	session["user"] = user
	print session

	# add that user to the list of connected users
	connected_users.setdefault(get_user(), [])
	print "connected users in set_session", connected_users

	return redirect("/")


@app.route("/refresh_users")
def refresh_connected_users():
	"""Refreshes the Connected Users box on the page, so it's up to date.

	Whenever a user logs into or out of the system, this is called to refresh 
	all users' connected list.
	"""

	global connected_users

	user = request.args.get("user")

	return render_template("logged_in_users.html", 
							user=user, 
							users=[x for x in connected_users if x != user])


@app.route("/send_text")
def send_text():
	"""When user clicks on Ronnie's 'text address' link, this calls the Twilio text function."""
	
	location = request.args.get("location")
	phone_num = request.args.get("number")

	return send_text_message(location, phone_num)


################################
		#SOCKET FUNCTIONS
################################

def send_message(message, room):
	emit('message to display', { 'message': message, 
								 'user': session['user'], 
								 'room': room }, 
							   room=room)

def send_command(command, body, room, origin=None):
	emit('interpret command', { 'command': command, 
							    'body': body, 
							    'origin': origin }, 
							  room=room)


################################
		#SOCKET EVENTS
################################


@socketio.on('refresh connected users', namespace='/chat')
def refresh_connecteduser_lists():
	"""Tells every connected user to call refresh_connectedusers()

	This is called anytime anyone logs into or out of the app.
	"""

	global connected_users

	if connected_users:
		for key in connected_users:
			# tell every user's browser to 'Update List'
			send_command('UL', "None", key)


@socketio.on('message event', namespace='/chat')
def new_message(message):
	"""When a message is submitted, sends message to the appropriate room."""

	print message['data']
	send_message(message['data'], message['room'])


def ronnie_thinking(message):
	"""Displays a status message for Ronnie that is called randomly and sent to the chat."""

	thinking_messages = ["sniffing his butt", 
						 "eating grass", 
						 "eating garbage", 
						 "chasing an ant", 
						 "being chased by a poodle", 
						 "rolling in the mud",
						 ]

	random_thinking_message = random.choice(thinking_messages)

	status_message = "Ronnie's currently %s, please stand by." % random_thinking_message
	emit('message to display', { 'message': status_message, 
								 'user': 'Ronnie', 
								 'room': message['room'] }, 
								room=message['room'])


def no_ronnie_chat_yet(message):
	"""When Ronnie is not in his path but is sent a message, sends a filler message."""

	filler_chat = ["Hi I'm Ronnie! I have just met you and I looooove you."
					  + " Will you be my master?",
				   "Here comes the Ronnie, strong and brave - woof!",
	    		   "You know, if you bothered to say hi to me I might just be" 
   		    		  + " more helpful. Or...you could scratch my belly!",
   				  ]

	emit('message to display', { 'message': random.choice(filler_chat), 
								 'user': 'Ronnie', 
								 'room': message['room'] }, 
								room=message['room'])


@socketio.on('talk to ronnie', namespace='/chat')
def talk_to_ronnie(message):
	"""Manages the conversation with Ronnie and his path.

	If a Ronnie chat window has been opened, messages are relayed through 
	this function, instead of through 'message event'

	Uses the bot.py traverse_questions() function to determine what the 
	next state should be, and what question to ask based on the previous 
	question, and how it was answered (message['message'])
	"""

	global next_state, last_state, ronniechat, city

	answer = message['message']

	# if the user asks Ronnie for more information about a venue
	if "tell me" in answer.lower():
		# get the address of that venue
		location,venue = bot.tell_me_more(answer, city)

		# Ronnie replys with the address of the business, and a link to text
		# the address to user's phone 
		msg = "It's at " + location + " <a class='get_phone' href='/send_text?location=%s&number='>Click to have the address texted to you</a>" % location
		emit('message to display', { 'message': msg, 
									 'user': 'Ronnie', 
									 'room': message['room'] }, 
									room=message['room'])
		return

	# if Ronnie is not currently in his path
	if not ronniechat: 
		# if the user greets Ronnie, start the path
		if "hi ronnie" in answer.lower() or "hello ronnie" in answer.lower() or 'howdy' in answer.lower():
			ronniechat = True
			next_state, question = bot.traverse_questions(0, None)
			last_state = 0
			print "query: ", bot.query
			print "last state: ", last_state
			print "next state: ", 1
			emit('message to display', { 'message': "Well hello there friend!\n" + question, 
										 'user': 'Ronnie', 
										 'room': message['room'] }, 
										room=message['room'])
		else:
			no_ronnie_chat_yet(message)
		return
			
	# if Ronnie is currently in his path
	elif ronniechat:
		# if the user thanks Ronnie, have him respond, then reset himself
		if "thank" in answer.lower():
			emit('message to display', { 'message': "You're welcome %s. Now give \
											me a treat human!" % get_user(), 
										 'user': 'Ronnie', 
										 'room': message['room'] }, 
										room=message['room'])
			reset_ronnie()
			return 

		# if the most recent question was 'what city are you in?'
		elif next_state == 1:
			# 1 is now the last state
			last_state = 1
			# use traverse_questions() to determine the next state, and question to ask
			next_state, question = bot.traverse_questions(1, answer)
			# save the answer as 'city', for further reference
			city = answer

			# Ronnie responds with the next question
			emit('message to display', { 'message': question, 
										 'user': 'Ronnie', 
										 'room': message['room'] }, 
										room=message['room'])
		
		# for all other states/questions
		else:
			answer = answer.lower()
			s, q = bot.traverse_questions(next_state, answer)
			last_state = next_state

			# if traverse_questions returns nothing (meaning the user hasn't 
			# answered the question), respond with filler, but don't change 
			# the state yet
			if s is None and q is None:
				filler_chat = ["That's cool!", 
							   "Awesome.", 
							   "Totally.", 
							   "I know what you mean."
							  ]
				emit('message to display', { 'message': random.choice(filler_chat), 
											 'user': 'Ronnie', 
											 'room': message['room'] }, 
			
											room=message['room'])
			# if the user has answered the question, set the next state and next question	
			else:	
				next_state = s
				question = q

				print "query: ", bot.query
				print "last state: ", last_state
				print "next state: ", next_state
				print "next question: ", question
				
				# 30% of the time, have Ronnie send a random status message
				chance = random.random()
				if chance > 0.7:
					ronnie_thinking(message)

				emit('message to display', { 'message': question, 
											 'user': 'Ronnie', 
											 'room': message['room'] }, 
											room=message['room'])
		return


@socketio.on('receive command', namespace='/chat')
def receive_command(command):
	"""Sends any commands (join, update list, etc.) to a user's room to be interpreted"""

	send_command(command['command'], command['body'], command['room'])

@socketio.on('join room', namespace='/chat')
def on_join(data):
	"""Joins the user to a Flask-SocketIO room"""

	global connected_users

	user = data['username']
	room = data['room']
	join_room(room)
	print "%s has joined room: %s" % (user, room)

	if room not in connected_users.get(user, []):
		connected_users.setdefault(user, []).append(room)
	print "connected users in join room", connected_users
	refresh_connecteduser_lists()


@socketio.on('open chat', namespace='/chat')
def open_chat(data):
	"""Tells both the sending and receiving users' browsers to open new chat windows.

	Is called when a username in 'Connected Users' is clicked on
	"""

	room = data['room']
	submitting_user = data['submitting']
	receiving_user = data['receiving']
	
	# open a chat window in both users' windows
	emit('open chat box', { 'template': render_template("chat_box.html", 
									    room=room, 
									    receiving_user=receiving_user), 
						    'receiving_user': receiving_user, 
						    'chat_room': room }, 
						   room=submitting_user)

	emit('open chat box', { 'template': render_template("chat_box.html", 
										room=room, 
										receiving_user=submitting_user), 
						    'chat_room': room }, 
						   room=receiving_user)



####################################
	#Socket Connection Functions
####################################	

@socketio.on('connect', namespace='/chat')
def test_connect():
	print('Connected')
	emit('connected', {'data': 'Connected'})


@socketio.on('disconnect', namespace='/chat')
def test_disconnect():
	print('%s Client disconnected') % session.get("user")

if __name__ == '__main__':
    socketio.run(app)


# 