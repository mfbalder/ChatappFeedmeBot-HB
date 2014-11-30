from flask import Flask, render_template, session, request, redirect
from flask.ext.socketio import SocketIO, emit, join_room, leave_room, send
import bot
import random
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
app.secret_key = "ABC"


################################
# connected_users --> {username: ['room1 they're in', 'room2', 'room3']}

# next_state --> Int (to track where Ronnie is in his path)
################################
connected_users = {'AskRonnie': []}
ronniechat = False
next_state = None
last_state = None
city = None



class UserUnAuth(Exception):
	"""User isn't logged in."""

def get_user():
	# try:
	# 	return session.get("user")
	# except TypeError:
	#   return UserUnAuth 
	# 	return redirect("/login")

	return session.get("user")

################################
		#Flask Routes
################################

@app.route('/')
def index():
	# FIXME: send unauth users to login form

	# user = session.get("user")   # "joel" or None
	user = get_user()
	if user is None:
		return redirect("/login")


	# print "index: user=", user
	users_to_display = [u for u in connected_users if u != user]
	return render_template('index.html', 
		users = users_to_display,
		user=user)

@app.route('/login')
def login():
	return render_template("login.html")

@app.route("/signup_form")
def signup_form():
	return render_template("signup.html")

@app.route("/signup_user")
def signup_user():
	pass


@app.route('/logout')
def logout():
	# delete the current user from the connected_users dictionary
	global connected_users
	# user = request.args.get("user")
	user = get_user()
	if user:
		del connected_users[user]
		print "connected_users in logout: ", connected_users

		# clear the user's session
		session.clear()
		print "session in logout ", session
		print "I think you are ", session.get("user")

		# reset Ronnie
		# bot.last_state = 0

		# reload the login page
		print "This is the list of connected users after %s has logged out" % user
		print connected_users
	return redirect("/login")
	# return render_template("login.html")

@app.route("/set_session")
def set_session():
	global connected_users

	# get the current logged in user, and set that to the session
	user = request.args.get("user")
	print "set_session: user=", user
	session["user"] = user
	print session

	# add that user to the list of connected users
	connected_users.setdefault(get_user(), [])
	print "connected users in set_session", connected_users
	return redirect("/")

@app.route("/refresh_users")
def refresh_connected_users():
	"""Whenever a new user logs into the system, this is called to refresh all users' connected list"""
	global connected_users
	user = request.args.get("user")
	print "user in refresh_users", user
	return render_template("logged_in_users.html", user=user, users=[x for x in connected_users if x != user])


################################
		#SOCKET FUNCTIONS
################################

def send_message(message, room):
	emit('message to display', {'message': message, 'user': session['user'], 'room': room}, room=room)

def send_command(command, body, room, origin=None):
	emit('interpret command', {'command': command, 'body': body, 'origin': origin}, room=room)


################################
		#SOCKET EVENTS
################################


@socketio.on('refresh connected users', namespace='/chat')
def refresh_connecteduser_lists():
	"""tells every connected user to update their connected user list"""
	global connected_users
	print "These are the users being told to update: ", connected_users
	if connected_users:
		for key in connected_users:
			send_command('UL', "None", key)

@socketio.on('message event', namespace='/chat')
def new_message(message):
	"""Called when a message is submitted, sends message back to the client to be displayed"""
	print message['data']
	send_message(message['data'], message['room'])

def ronnie_thinking(message):
	thinking_messages = ["sniffing his butt", "eating grass", "eating garbage", "chasing an ant",
						 "being chased by a poodle", "rolling in the mud"]
	status_message = "Ronnie's currently %s, please stand by." % random.choice(thinking_messages)
	emit('message to display', {'message': status_message, 'user': 'Ronnie', 'room': message['room']}, room=message['room'])


def delay():
	time.sleep(10)

def no_ronnie_chat_yet(message):
	filler_chat = ["Hi I'm Ronnie! I have just met you and I looooove you. Will you be my master?",
					"Here comes the Ronnie, strong and brave - woof!",
					"You know, if you bothered to say hi to me I might just be more helpful. Or...you could scratch my belly!"]
	emit('message to display', {'message': random.choice(filler_chat), 'user': 'Ronnie', 'room': message['room']}, room=message['room'])

@socketio.on('talk to ronnie', namespace='/chat')
def talk_to_ronnie(message):
	"""
		If a Ronnie chat window has been opened, messages are relayed through this function,
			instead of through 'message event'

		Uses the bot.py traverse_questions() function to determine what the next state should be, and
			what question to ask based on the previous question, and how it was answered (message['message'])
	"""
	global next_state
	global ronniechat
	global city

	answer = message['message']

	if "tell me about" in answer.lower():
		location = bot.tell_me_more(answer, city)
		emit('message to display', {'message': "It's at " + location + ". Would you like me to text you the address?", 'user': 'Ronnie', 'room': message['room']}, room=message['room'])
		return

	if ronniechat == False: 
		if "hi ronnie" in answer.lower() or "hello ronnie" in answer.lower() or 'howdy' in answer.lower():
			ronniechat = True
			next_state, question = bot.traverse_questions(0, None)
			bot.last_state = 0
			print "query: ", bot.query
			print "last state: ", bot.last_state
			print "next state: ", 1
			emit('message to display', {'message': "Well hello there friend!\n" + question, 'user': 'Ronnie', 'room': message['room']}, room=message['room'])
		else:
			no_ronnie_chat_yet(message)
		return
			
	if ronniechat == True:
		if "thank" in answer.lower():
			emit('message to display', {'message': "You're welcome %s. Now give me a treat human!" % get_user(), 'user': 'Ronnie', 'room': message['room']}, room=message['room'])
			ronniechat = False
			bot.query = "SELECT r.name FROM restaurants AS r join categories AS c ON r.id=c.business_id join categorylookup AS l ON l.category=c.category"
			bot.last_state = None
			next_state = None
			return 


		elif next_state == 1:
			bot.last_state = 1
			next_state, question = bot.traverse_questions(1, answer)
			city = answer

			print "query: ", bot.query
			print "last state: ", bot.last_state
			print "next state: ", next_state
			print "next question: ", question

			emit('message to display', {'message': question, 'user': 'Ronnie', 'room': message['room']}, room=message['room'])
		
		else:
			answer = answer.lower()
			print "In the webapp else: the last state is %d and the answer for that is %s" % (bot.last_state, answer)
			s, q = bot.traverse_questions(next_state, answer)
			bot.last_state = next_state

			# if traverse_questions returns nothing (meaning the user hasn't answered the question),
			# respond, but don't change the state yet
			if s == None and q == None:
				filler_chat = ["That's cool!", "Awesome.", "Totally.", "I know what you mean."]
				emit('message to display', {'message': random.choice(filler_chat), 'user': 'Ronnie', 'room': message['room']}, room=message['room'])
			else:	
				next_state = s
				question = q
				# print bot.last_state
				print "query: ", bot.query
				print "last state: ", bot.last_state
				print "next state: ", next_state
				print "next question: ", question
				
				chance = random.random()
				if chance > 0.7:
					ronnie_thinking(message)
				emit('message to display', {'message': question, 'user': 'Ronnie', 'room': message['room']}, room=message['room'])
				# send_message(question, message['room'])
		return

@socketio.on('receive command', namespace='/chat')
def receive_command(command):
	"""Sends any commands (join, update list, etc.) to a user's room to be interpreted"""
	print command
	send_command(command['command'], command['body'], command['room'])

@socketio.on('join room', namespace='/chat')
def on_join(data):
	global connected_users
	user = data['username']
	room = data['room']
	join_room(room)
	print "%s has joined room: %s" % (user, room)

	if room not in connected_users.get(user, []):
		connected_users.setdefault(user, []).append(room)
	print "connected users in join room", connected_users
	# send_message("Success! Connected to %s" % room, room)
	refresh_connecteduser_lists()

@socketio.on('open chat', namespace='/chat')
def open_chat(data):
	room = data['room']
	submitting_user = data['submitting']
	receiving_user = data['receiving']
	
	# open a chat window in both users' windows
	emit('open chat box', {'template': render_template("chat_box.html", room=room, receiving_user=receiving_user), 'receiving_user': receiving_user, 'chat_room': room}, room=submitting_user)
	emit('open chat box', {'template': render_template("chat_box.html", room=room, receiving_user=submitting_user), 'chat_room': room}, room=receiving_user)





####################################
	#Socket Connection Functions
####################################	

@socketio.on('connect', namespace='/chat')
def test_connect():
	# check for awayness eventually
	print('Connected')
	emit('connected', {'data': 'Connected'})

@socketio.on('disconnect', namespace='/chat')
def test_disconnect():
	print('%s Client disconnected') % session.get("user")

if __name__ == '__main__':
    socketio.run(app)


# 