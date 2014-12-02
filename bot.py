import time
import psycopg2
import random
from bot_path import path as d

dbconn = psycopg2.connect('dbname=restaurantrec host=localhost port=5432')
cursor = dbconn.cursor()

# the starting query
query = "SELECT r.name FROM restaurants AS r join categories AS c ON r.id=c.business_id join categorylookup AS l ON l.category=c.category"



def tell_me_more(answer, city):
	"""Returns the address and business name when a user says 'tell me about ___'.

	Takes the user's request and the city as parameters.

		answer --> assumes the form of "tell me about _________"
			ex. "tell me about Steve's Bakery"

		city --> a city in string form
			ex. "Las Vegas"
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
	"""Returns a comma-separated string of 5 random food/business categories that remain.

	Takes the current query as an arguement.

		query --> a piece of a PostgreSQL query in string form
			ex. "SELECT r.name FROM restaurants as r WHERE r.vegan=TRUE"

	For state #15, the path lets the user select from 5 random categories that remain available.
	"""

	# get the categories remaining with the given query, for businesses that are rated highly
	cat_choices = query.replace('r.name', 'c.category') + " AND r.stars>=4 GROUP BY c.category"
	cursor.execute(cat_choices)
	results = cursor.fetchall()

	# if there enough, choose 5 random ones
	try:
		result_choices = random.sample(results, 5)
	# otherwise simply return what there is
	except ValueError:
		result_choices = results

	choices = [x[0]for x in result_choices]
	str_result_choices = ", ".join(choices)
	if not str_result_choices:
		return None

	return str_result_choices



def get_next_state(current_state, answer):
	"""Returns the next state, based on the current state and the user's answer for it.
	
	Takes the most recent state, and the user's answer to that state's question, as arguements.

		current_state --> an integer
			ex. 12

		answer --> the answer the user submitted, a string
			ex. "yes I think I would like a snack"
	"""

	# iterate through the branches for the current state
	for branch in d[locals()['current_state']]['branches']:
		for each in branch:
			# check to see which branch matches the user's input
			if each in answer:
				# get the next state, and the question for that state
				next_state = d[locals()['current_state']]['branches'][locals()['branch']][0]
				return next_state

	return None



def get_query_action_and_addition(current_state, answer):
	"""Gets the piece of query to add to the existing query, and what to do with it."""

	# iterate through the branches for the current state
	for branch in d[locals()['current_state']]['branches']:
		for each in branch:
			# check to see which branch matches the user's input
			if each in answer:
				# get the query addition, and what to do with it
				action = d[locals()['current_state']]['branches'][locals()['branch']][2]
				addition = d[locals()['current_state']]['branches'][locals()['branch']][1]
				return action, addition

	return None, None

def get_next_question(next_state):
	"""Gets the next question, based on what the next state is."""
	try:
		return d[locals()['next_state']]['bot_statement']
	except KeyError:
		return None


def traverse_questions(state, user_answer):
	"""Moves to the next state in the path, based on the current state and the user's answer.

	state --> Int (the state that a question was just asked from)
   	user_answer --> Str (the user's answer to that question)

   	Checks the state's branches to see which of them match the answer.
   	Gets the next state from that branch.
   	Chains the appropriate queries for the given state.

   	Returns the next state and that state's question"""

	global query, cursor

	# if the bot is just starting, return the first question
	if state == 0:
		return 1, d[1]['bot_statement']

	# if the bot has reached the end of the path (where they've chosen 
	# from a list of categories)
	if state == 20:
		user_answer = ' '.join([word.capitalize() for word in user_answer.split()])
		final_search = " AND EXISTS(SELECT 1 FROM categories as c6 WHERE c6.business_id=r.id AND c6.category = '?') AND EXISTS(SELECT 1 from categorylookup as l where l.category=c.category)".replace('?', user_answer)
		query = query + final_search
		# get the result of the final query with the highest rating
		cursor.execute(query + " ORDER BY r.stars LIMIT 1")
		result = cursor.fetchone()

		return None, "I give you..." + result[0] + "!"

	try:
		# if the path state is a question
		if d[locals()['state']]['return'] == 'question':
			# get the next state
			next_state = get_next_state(state, user_answer)
			if next_state == None:
				return None, None

			# get the next question
			bot_question = get_next_question(next_state)

			# if the state is 1 (deals with the city), fill in the query with the city name
			if state == 1:
				# get the piece of query to add
				query_addition = d[1]['branches']['answer'][1].replace('?', user_answer)

				# add the piece to the existing query
				query = query + query_addition

				return next_state, bot_question

			query_action, query_addition = get_query_action_and_addition(state, user_answer)

			# state 15 requires the bot to query for categories that remain, and give
			# the user a choice from 5 random ones
			if next_state == 15:

				# add the new piece of query to the existing query
				query = query + query_addition

				# get the category choices
				choices = fifteen(query)

				# if there exist choices, send them to the user
				if choices:
					return 20, "Here are your category choices. Pick one: " + choices
				# otherwise, don't advance to the next state, but reask the question
				else:
					return state, "I got nothin WOOF! Try a different answer " + bot_question

			# if the action for the given state is 'add to query', execute that new query
			# if the new query returns results, save the new query
			if query_action == 'add_to_query':
				cursor.execute(query + query_addition + " GROUP BY r.name")
				results = cursor.fetchall()
				if results:
					query = query + query_addition
			# if the action for the given state if 'end', get the final result with the highest rating
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