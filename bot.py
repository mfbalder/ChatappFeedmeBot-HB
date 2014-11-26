import time
import psycopg2
import random
from bot_path import path as d

dbconn = psycopg2.connect('dbname=restaurantrec host=localhost port=5432')
cursor = dbconn.cursor()

# stopword_list = stopwords.words("english")

city = None
question_path = []
query_filters = []
last_state = None

query = "SELECT r.name FROM restaurants AS r join categories AS c ON r.id=c.business_id join categorylookup AS l ON l.category=c.category"


def fifteen(query):
	cat_choices = query.replace('r.name', 'c.category') + " AND r.stars>=4 GROUP BY c.category"
	print cat_choices
	cursor.execute(cat_choices)
	results = cursor.fetchall()
	try:
		result_choices = random.sample(results, 5)
	except ValueError:
		result_choices = results
	clean_choices = [x[0]for x in result_choices]
	print clean_choices
	str_result_choices = ", ".join(clean_choices)
	return str_result_choices


def traverse_questions(last_state, user_answer):
	"""last state --> the state that a question was just asked from (int)
	   user_answer --> the user's answer to that question (str)

	   Checks that state's branches to see which of them match the answer.
	   Gets the next state from that branch.
	   Adds that state to the list tracking the path of states.

	   Returns the next state and that state's question"""

	global question_path
	global query
	global join_half
	global where_half
	global cursor



	if last_state == 0:
		return 1, d[1]['bot_statement']

	if last_state == 1:
		next_state = d[1]['branches']['answer'][0]
		query_piece = d[1]['branches']['answer'][1].replace('?', user_answer)
		query = query + query_piece
		cursor.execute(query)
		return next_state, d[2]['bot_statement']

	if d[locals()['last_state']]['return'] == 'question':
	# answer = user_answer.split()

		for branch in d[locals()['last_state']]['branches']:
				for each in branch:
					if each in user_answer:
						# print each
						
						next_state = d[locals()['last_state']]['branches'][locals()['branch']][0]
						bot_question = d[locals()['next_state']]['bot_statement']
						# print "next state: ", next_state
						answer_branch = branch
						question_path.append((last_state, answer_branch))
						# print question_path


						query_action = d[locals()['last_state']]['branches'][locals()['branch']][2]

						query_addition = d[locals()['last_state']]['branches'][locals()['branch']][1]

						if query_action == 'add_to_query':
							cursor.execute(query + query_addition + " GROUP BY r.name")
							results = cursor.fetchall()
							if results != []:
								query = query + query_addition
								print "all: ", results
							else:
								print "it's empty"

						
						if next_state == 15:
							choices = fifteen(query)
							return 20, "Here are your category choices. Pick one: " + choices
						elif next_state == 16:
							return 20, 

						return next_state, locals()['bot_question']

		return None, None

						# if next_state == 20:


		# return next_state, 

	# print "next state before the prequery: ", next_state
	# if d[locals()['last_state']]['return'] == 'prequery question':
	# 	print "I'm getting here!"
	# 	cat_choices = query.replace('r.name', 'c.category') + " AND r.stars>=4 GROUP BY c.category"
	# 	print cat_choices
	# 	bot_question = d[locals()['last_state']]['bot_statement']
	# 	# print bot_question
	# 	cursor.execute(cat_choices)
	# 	results = cursor.fetchall()
	# 	result_choices = random.sample(results, 5)
	# 	clean_choices = [x[0]for x in result_choices]
	# 	print clean_choices
	# 	str_result_choices = ", ".join(clean_choices)
		
	# 	print str_result_choices
	# 	# for item in result_choices:
	# 	# 	print item[0]
	# 	# return d[locals()['last_state']]['next_step'][0], locals()['bot_question'] + result_choices
	# 	return 20, "Here are your category choices. Pick one: " + str_result_choices
	# 	# answer = raw_input()

	# 	# next_state = d[locals()['last_state']]['next_step'][0]
	# 	# query_addition = d[locals()['last_state']]['next_step'][1].replace('?', answer)
	# 	# cursor.execute(query + query_addition + " ORDER BY r.stars LIMIT 1")
	# 	# a = cursor.fetchone()
	# 	# print "I give you...", a[0]

	if d[locals()['last_state']]['return'] == 'query':
		if locals()['last_state'] == 20:
			user_answer = ' '.join([word.capitalize() for word in user_answer.split()])
			final_search = " AND EXISTS(SELECT 1 FROM categories as c6 WHERE c6.business_id=r.id AND c6.category = '?') AND EXISTS(SELECT 1 from categorylookup as l WHERE l.category=c.category)".replace('?', user_answer)
			query = query + final_search
		elif locals()['last_state'] == 16:
			print "16!!!!!"
		print "query time!!!", query
		cursor.execute(query + " ORDER BY r.stars LIMIT 1")
		result = cursor.fetchone()
		print result
		return None, "I give you..." + result[0] + "!"


	# print "next state", next_state				
	return next_state, locals()['bot_question']


def project_logic():
	global stored_info
	# set the current time --> not dealing with this now
	# stored_info.setdefault('current_time', time.strftime("%H:%M"))

	x = 1
	while True:
		if x not in d:
			break
		# prints the next question
		print d[locals()['x']]['bot_statement']

		# gets an answer from the user
		answer = raw_input()
		clean_answer = answer.split()
		# clean_answer = [word for word in answer.split() if word not in stopword_list]
		# print clean_answer

		# gets the value for that branch
		# for item in d[locals()['x']]['branches']:
		# 	for word in clean_answer:
		# 		if word in item:
		# 			next_point = d[locals()['x']]['branches'][locals()['item']]
		# 			x = next_point

		for item in d[locals()['x']]['branches']:
			for each in item:
				if each in clean_answer:
					print each
					next_point = d[locals()['x']]['branches'][locals()['item']]
					print next_point
					x = next_point


# [1, 2, 3, 4] --> list of question #s for order and to keep track of its state
# state machine
# the function is a stateless track
# adding the query string after each branch
# no while loop, pass the current state and the answer into the project_logic function	
# my chat bot as a state machine --> each question is a state, with the branches as transitions
# should i write a class that represents each node --> current state, next state, etc.

	

def main():
	start = raw_input().lower()
	if "hi" in start or "hello" in start and "ronnie" in start:
		print "Well hello there friend!"
		print traverse_questions(0, None)
	else:
		print "I'm Ronnie. I have just met you and a looove you will you be my master?"


if __name__ == "__main__":
	main()