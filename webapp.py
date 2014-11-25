from flask import Flask, render_template, session, request, redirect
from flask.ext.socketio import SocketIO, emit, join_room, leave_room, send

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
app.secret_key = "ABC"

# connected_users --> {username: ['room1 they're in', 'room2', 'room3']}
connected_users = {}

class UserUnAuth(Exception):
	"""User isn't logged in."""

def get_user():
	# try:
	# 	return session.get("user")
	# except TypeError:
	#   return UserUnAuth 
	# 	return redirect("/login")

	return session.get("user")

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



# socket functions

def send_message(message, room):
	emit('message to display', {'message': message, 'user': session['user'], 'room': room}, room=room)

def send_command(command, body, room, origin=None):
	emit('interpret command', {'command': command, 'body': body, 'origin': origin}, room=room)



# socket events

@socketio.on('complete pubkey exchange', namespace='/chat')
def complete_pubkey_exchange(data):
	print data
	emit('app message display', {'message': "Your chat has been encrypted!", 'user': session['user'], 'room': data["encrypted_room"]}, room=data["encrypted_room"])
	# send_message("Your chat has been encrypted!", data["encrypted_room"])


@socketio.on('initiate pubkey exchange', namespace='/chat')
def receive_pubkey(data):
	send_command('PUK', {'key':data["key"], 'encrypted_room':data["encrypted_room"]}, data["receiving_user"], data["sending_user"])
	message = "%s has initiated encryption for this conversation. Click 'Encrypt Chat' to complete" % data["sending_user"]
	send_message(message, data["encrypted_room"])

@socketio.on('refresh connected users', namespace='/chat')
def refresh_connecteduser_lists():
	"""tells every connected user to update their connected user list"""
	global connected_users
	print "These are the users being told to update: ", connected_users
	if connected_users:
		for key in connected_users:
			send_command('UL', "None", key)

@socketio.on('my event', namespace='/chat')
def test_message(message):
	"""Called when a message is submitted, sends message back to the client to be displayed"""
	print message['data']
	send_message(message['data'], message['room'])

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