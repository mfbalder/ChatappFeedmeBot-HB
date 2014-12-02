import time
import psycopg2
import random
from bot_path import path as d

dbconn = psycopg2.connect('dbname=restaurantrec host=localhost port=5432')
cursor = dbconn.cursor()


last_state = None
query = "SELECT r.name FROM restaurants AS r join categories AS c ON r.id=c.business_id join categorylookup AS l ON l.category=c.category"



def tell_me_more(answer, city):
	"""

	Takes the user's request (for a particular business) and the city it's in.

		answer --> assumes the form of "tell me about _________"
			ex. "tell me about Steve's Bakery"

		city --> a city in string form
			ex. "Las Vegas"
		
	Returns the address, and the business name.

	"""

	full_answer = answer.split()
	user_answer = ' '.join(full_answer[3:])

	q = "SELECT r.address FROM restaurants as r WHERE r.name = %s and r.city = %s"

	try:
		cursor.execute(q, (user_answer, city))
		result = cursor.fetchone()
		return result[0], user_answer
	except TypeError:
		return "an unknown location. Are you sure you meant %s?" % user_answer, user_answer


def fifteen(query):
	"""

	Takes the current query as an arguement.

		query --> a piece of a PostgreSQL query in string form
			ex. "SELECT r.name FROM restaurants as r WHERE r.vegan=TRUE"

	For state #15, the path lets the user select from 5 random categories that remain available.

	Function queries for all the available categories, chooses 5 at random, and returns them as 
	  a comma-separated string

	"""
	cat_choices = query.replace('r.name', 'c.category') + " AND r.stars>=4 GROUP BY c.category"
	cursor.execute(cat_choices)
	results = cursor.fetchall()

	try:
		result_choices = random.sample(results, 5)
	except ValueError:
		result_choices = results

	choices = [x[0]for x in result_choices]
	str_result_choices = ", ".join(choices)
	if not str_result_choices:
		return None

	return str_result_choices



def get_next_state(current_state, answer):
	"""
	
	Takes the most recent state, and the user's answer to that state's question, as arguements.

		current_state --> an integer
			ex. 12

		answer --> the answer the user submitted, a string
			ex. "yes I think I would like a snack"

	Returns the next state in the path, based on the given answer.

	"""
	for branch in d[locals()['current_state']]['branches']:
		for each in branch:

			# check to see which branch matches the user's input
			if each in answer:

				# get the next state, and the question for that state
				next_state = d[locals()['current_state']]['branches'][locals()['branch']][0]
				return next_state

	return None



def get_query_action_and_addition(current_state, answer):
	for branch in d[locals()['current_state']]['branches']:
		for each in branch:
			# check to see which branch matches the user's input
			if each in answer:
				action = d[locals()['current_state']]['branches'][locals()['branch']][2]
				addition = d[locals()['current_state']]['branches'][locals()['branch']][1]
				return action, addition
	print "in get query, i didn't find anything!!"
	return None, None

def get_next_question(next_state):
	try:
		return d[locals()['next_state']]['bot_statement']
	except KeyError:
		return None


def traverse_questions(state, user_answer):
	"""last state --> the state that a question was just asked from (int)
	   user_answer --> the user's answer to that question (str)

	   Checks that state's branches to see which of them match the answer.
	   Gets the next state from that branch.
	   Adds that state to the list tracking the path of states.

	   Returns the next state and that state's question"""

	# global question_path
	global query
	global cursor
	global last_state


	if state == 0:
		return 1, d[1]['bot_statement']
	if state == 20:
		user_answer = ' '.join([word.capitalize() for word in user_answer.split()])
		final_search = " AND EXISTS(SELECT 1 FROM categories as c6 WHERE c6.business_id=r.id AND c6.category = '?') AND EXISTS(SELECT 1 from categorylookup as l where l.category=c.category)".replace('?', user_answer)
		query = query + final_search
		cursor.execute(query + " ORDER BY r.stars LIMIT 1")
		result = cursor.fetchone()

		return None, "I give you..." + result[0] + "!"

	try:
		if d[locals()['state']]['return'] == 'question':
			next_state = get_next_state(state, user_answer)
			if next_state == None:
				return None, None

			bot_question = get_next_question(next_state)

			if state == 1:
				query_addition = d[1]['branches']['answer'][1].replace('?', user_answer)
				query = query + query_addition
				return next_state, bot_question

			query_action, query_addition = get_query_action_and_addition(state, user_answer)


			if next_state == 15:

				query = query + query_addition

				choices = fifteen(query)
				print choices
				if choices:
					return 20, "Here are your category choices. Pick one: " + choices
				else:
					return state, "I got nothin WOOF! Try a different answer " + bot_question

			if query_action == 'add_to_query':
				cursor.execute(query + query_addition + " GROUP BY r.name")
				results = cursor.fetchall()

				if results:
					query = query + query_addition
			elif query_action == 'end':
				cursor.execute(query + query_addition + " ORDER BY r.stars LIMIT 1")
				result = cursor.fetchone()
				return None, "I give you..." + result[0] + "!"

			return next_state, bot_question
	except KeyError:
		return None, None
	

def main():
	pass

if __name__ == "__main__":
	main()