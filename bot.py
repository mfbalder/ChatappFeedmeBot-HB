import time
import psycopg2
import random

dbconn = psycopg2.connect('dbname=restaurantrec host=localhost port=5432')
cursor = dbconn.cursor()

# stopword_list = stopwords.words("english")

city = None
question_path = []
query_filters = []
last_state = None

query = "SELECT r.name FROM restaurants AS r join categories AS c ON r.id=c.business_id join categorylookup AS l ON l.category=c.category"

d = {
	1: {
		'return': 'question',
		'bot_statement': 'What city are you in?',
		'branches': {
			'answer': [2, " WHERE r.city = '?'", "where", None]
		}
	},
	2: {
		'return': 'question',
		'bot_statement': 'Are you hungry?',
		'branches': {
			('yes', 'ya', 'yeah', 'sure', 'definitely'): [3, " AND EXISTS(SELECT 1 FROM categories AS c1 WHERE c1.business_id=r.id AND c1.category NOT IN('Bars', 'Breweries', 'Coffee & Tea', 'Dive Bars', 'Sports Bars', 'Cafes', 'Tea Rooms', 'Wine Bars', 'Pubs'))", "add_to_query", 'c1'],
			('no', 'nope', 'nah', 'not'): [4, " AND EXISTS(SELECT 1 FROM categories AS c1 WHERE c1.business_id=r.id AND c1.category IN ('Bars', 'Breweries', 'Coffee & Tea', 'Dive Bars', 'Sports Bars', 'Cafes', 'Tea Rooms', 'Wine Bars', 'Pubs'))", 'add_to_query', 'c1']
		}
	},
	3: {
		'return': 'question',
		'bot_statement': 'Snack or meal?',
		'branches': {
			('snack',): [6, " AND EXISTS(SELECT 1 FROM categories as c2 WHERE c2.business_id=r.id AND c2.category IN ('Bakeries', 'Ice Cream & Frozen Yogurt', 'Donuts', 'Cafes', 'Candy Stores', 'Desserts', 'Pretzels', 'Cupcakes', 'Gelato', 'Patisserie/Cake Shop', 'Shaved Ice'))", 'add_to_query', "c2"],
			('meal',): [5, " AND EXISTS(SELECT 1 FROM categories as c2 WHERE c2.business_id=r.id AND c2.category IN ('Restaurants'))", "add_to_query", None]
		}
	},
	4: {
		'return': 'question',
		'bot_statement': 'Ok then. Is a stiff drink in order?',
		'branches': {
			('yes', 'ya', 'yeah', 'sure', 'definitely', 'yessir'): [10, " AND EXISTS(SELECT 1 FROM categories as c3 WHERE c3.business_id=r.id AND c3.category IN ('Bars', 'Breweries', 'Dive Bars', 'Sports Bars', 'Wine Bars', 'Pubs'))", "add_to_query", None],
			('no', 'nope', 'nah', 'not'): [11, " AND EXISTS(SELECT 1 FROM categories as c3 WHERE c3.business_id=r.id AND c3.category IN ('Coffee & Tea', 'Cafes', 'Tea Rooms'))", "add_to_query", None]
		}
	},
	5: {
		'return': 'question',
		'bot_statement': 'Are we thinking breakfast, lunch or dinner?',
		'branches': {
			('breakfast', 'brunch'): [8, " AND EXISTS(SELECT 1 FROM categories as c4 WHERE c4.business_id=r.id AND c4.category='Breakfast & Brunch')", "add_to_query"],
			('lunch',): [7, " AND r.lunch=True", "add_to_query"],
			('dinner',): [7, " AND r.dinner=True", "add_to_query"]
		}
	},
	6: {
		'return': 'question',
		'bot_statement': 'Personally WOOF! I really like tennis balls and peanut butter. Which do you prefer?',
		'branches': {
			('tennis ball', 'ball'): [15, " AND EXISTS(SELECT 1 FROM categories as c3 WHERE c3.business_id=r.id AND c3.category IN ('Donuts', 'Desserts', 'Bakeries', 'Cafes', 'Cupcakes', 'Pretzels', 'Patisserie/Cake Shop'))", "add_to_query"],
			('peanut',): [15, " AND EXISTS(SELECT 1 FROM categories as c3 WHERE c3.business_id=r.id AND c3.category IN ('Ice Cream & Frozen Yogurt', 'Gelato', 'Shaved Ice'))", "add_to_query"],
			('trick question',): [15, " AND EXISTS(SELECT 1 FROM categories as c3 WHERE c3.business_id=r.id AND c3.category = 'Candy Stores')", "add_to_query"]
		}
	},
	7: {
		'return': 'question',
		'bot_statement': 'Eat in, take out, or delivery?',
		'branches': {
			('eat in', 'in'): [8, None, None],
			('takeout', 'tk', 'out', 'pick up'): [8, " AND r.takeout=True", "add_to_query"],
			('delivery', 'deliver', 'delivered'): [8, " AND r.delivery=True", "add_to_query"],
			("LAZY",): [8, " AND r.drive_thru=True", "add_to_query"]
		}
	},
	8: {
		'return': 'question',
		'bot_statement': 'What about dietary concerns? Gluten? Soy? Vegan? Etc.?',
		'branches': {
			('nope', 'no', 'nah', 'none', 'negative'): [9, None, "no_change"],
			('vegetarian',): [9, " AND (r.vegetarian=True OR EXISTS(SELECT 1 FROM categories AS c7 WHERE c7.business_id=r.id AND c7.category='Vegetarian'))", "add_to_query"],
			('vegan',): [9, " AND r.vegan=True", "add_to_query"],
			('gf', 'gluten', 'gluten-free'): [9, " AND (r.gluten_free=True OR EXISTS(SELECT 1 FROM categories as c5 WHERE c5.business_id=r.id AND c5.category='Gluten-Free'))", "add_to_query"],
			('soy',): [9, " AND r.soy_free=True", "add_to_query"],
			('halal',): [9, " AND r.halal=True", "add_to_query"],
			('kosher',): [9, " AND r.kosher=True AND EXISTS(SELECT 1 FROM categories at c5 WHERE c5.business_id=r.id AND c5.category='Kosher')", "add_to_query"]
		}
	},
	9: {
		'return': 'question',
		'bot_statement': "And last but not least, what's your price range?",
		'branches': {
			('poor', 'no money', 'feed me', 'please sir I want some more'): [15, " AND r.price_range=1", "add_to_query"],
			('cheap', 'not too bad', 'just got a job'): [15, " AND r.price_range=2", "add_to_query"],
			('going on a date', 'need to impress', 'pretend I haz money'): [15, " AND r.price_range=3", "add_to_query"],
			('no object', 'rich', 'wealthy', 'darling', 'Mark Zuckerberg'): [15, " AND r.price_range=4", "add_to_query"],
			('whatev',): [15]
		}
	},
	10: {
		'return': 'question',
		'bot_statement': 'Righto, bar it is! What kind of vibe were we thinkin? Chill? Intimate? Romantic...? Ooo! Are you going on a date?? Tell me, tell me!',
		'branches': {
			('intimate','quiet'): [12, " AND r.intimate=True", "add_to_query"],
			('romantic', 'hot date'): [16, " AND r.romantic=True", "add_to_query"],
			('chill', 'casual','yo'): [13, " AND (r.casual=True OR r.divey=True", "add_to_query"]
		}
	},
	11: {
		'return': 'question',
		'bot_statement': 'Do you have a preference for coffee or tea?\nTea, right? You know you like tea! (Tea.)',
		'branches': {
			('lovely cucumber sandwiches', 'high society'): [17, " AND EXISTS(SELECT 1 FROM categories AS c4 WHERE c4.business_id=r.id AND c4.category IN ('Tea Rooms')", "add_to_query"],
			('nah', 'nope', 'no preference', "don't care", 'negative'): [17, None, None]
		}

	},
	12: {
		'return': 'question',
		'bot_statement': "You just want wine, don't you?",
		'branches': {
			('yes sir', 'yup', "that's correct", 'shush'): [16, " AND EXISTS(SELECT 1 FROM categories AS c4 WHERE c4.business_id=r.id AND c4.category IN ('Wine Bars'))", "add_to_query"]
		}
	},
	13: {
		'return': 'question',
		'bot_statement': 'Mirror mirror on the wall, tell me the one that just wants to watch sports and drink beers of them all...',
		'branches': {
			('hey now', 'fine'): [16, " AND EXISTS(SELECT 1 FROM categories as c4 WHERE c4.business_id=r.id AND c4.category IN ('Dive Bars', 'Sports Bars')", "add_to_query"]
		}
	}, 
	15: {
		'return': 'prequery question',
		'bot_statement': "Here are your category choices. Pick one: ",
		'next_step': [20, " AND EXISTS(SELECT 1 FROM categories as c6 WHERE c6.business_id=r.id AND c6.category = '?') AND EXISTS(SELECT 1 from categorylookup as l WHERE l.category=c.category)", "add_to_query"]
	},
	16: {

	},
	17: {

	},
	20: {
		'return': 'query',
		'bot_statement': "I give you... ?!",
	}

}


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
		user_answer = ' '.join([word.capitalize() for word in user_answer.split()])
		final_search = " AND EXISTS(SELECT 1 FROM categories as c6 WHERE c6.business_id=r.id AND c6.category = '?') AND EXISTS(SELECT 1 from categorylookup as l WHERE l.category=c.category)".replace('?', user_answer)
		query = query + final_search
		cursor.execute(query)
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