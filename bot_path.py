################################
#
#	path = {
#		state: {
#				'return': indication of a 'question', or a 'prequery',
#				'bot_statement': the question the bot is to ask at this state,
#				'branches': {
#						(some, potential, answers, that are checked for in the user's reply): [int to indicate the next state,
#																							   the query to be added if this is the selected branch,
#																							   what should be done next: add to the query, or finish the query],
#						(each tuple indicates a potential next step) : []	
#				}	
#		}
#	}
#
################################

path = {
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
			('yes', 'ya', 'yeah', 'sure', 'definitely'): [3, " AND EXISTS(SELECT 1 FROM categories AS c1 WHERE c1.business_id=r.id AND c1.category NOT IN('Bars', 'Breweries', 'Coffee & Tea', 'Dive Bars', 'Sports Bars', 'Cafes', 'Tea Rooms', 'Wine Bars', 'Pubs', 'Gastropubs', 'Beer Bar'))", "add_to_query", 'c1'],
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
			('yes', 'ya', 'yeah', 'sure', 'definitely', 'yessir', 'please'): [10, " AND EXISTS(SELECT 1 FROM categories as c3 WHERE c3.business_id=r.id AND c3.category IN ('Bars', 'Breweries', 'Dive Bars', 'Sports Bars', 'Wine Bars', 'Pubs'))", "add_to_query", None],
			('no', 'nope', 'nah', 'not'): [11, " AND EXISTS(SELECT 1 FROM categories as c3 WHERE c3.business_id=r.id AND c3.category IN ('Coffee & Tea', 'Cafes', 'Tea Rooms', 'Juice Bars & Smoothies'))", "add_to_query", None]
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
			('peanut', 'butter'): [15, " AND EXISTS(SELECT 1 FROM categories as c3 WHERE c3.business_id=r.id AND c3.category IN ('Ice Cream & Frozen Yogurt', 'Gelato', 'Shaved Ice'))", "add_to_query"],
			('trick question', 'liar'): [15, " AND EXISTS(SELECT 1 FROM categories as c3 WHERE c3.business_id=r.id AND c3.category = 'Candy Stores')", "add_to_query"]
		}
	},
	7: {
		'return': 'question',
		'bot_statement': 'Eat in, doggie bag (woof woof!), or delivery?',
		'branches': {
			('eat in', 'in'): [8, None, None],
			('takeout', 'tk', 'out', 'pick up', 'doggie'): [8, " AND r.takeout=True", "add_to_query"],
			('delivery', 'deliver', 'delivered'): [8, " AND r.delivery=True", "add_to_query"],
			('lazy', 'tired'): [8, " AND r.drive_thru=True", "add_to_query"]
		}
	},
	8: {
		'return': 'question',
		'bot_statement': 'What about dietary concerns? Gluten? Soy? Vegan? Etc.?',
		'branches': {
			('nope', 'no', 'nah', 'none', 'negative'): [9, None, None],
			('vegetarian',): [9, " AND (r.vegetarian=True OR EXISTS(SELECT 1 FROM categories AS c7 WHERE c7.business_id=r.id AND c7.category='Vegetarian'))", "add_to_query"],
			('vegan',): [9, " AND r.vegan=True", "add_to_query"],
			('gf', 'gluten', 'gluten-free'): [9, " AND (r.gluten_free=True OR EXISTS(SELECT 1 FROM categories as c5 WHERE c5.business_id=r.id AND c5.category='Gluten-Free'))", "add_to_query"],
			('soy',): [9, " AND r.soy_free=True", "add_to_query"],
			('halal',): [9, " AND r.halal=True AND EXISTS(SELECT 1 FROM categories as c5 WHERE c5.business_id=r.id AND c5.category='Halal')", "add_to_query"],
			('kosher',): [9, " AND r.kosher=True AND EXISTS(SELECT 1 FROM categories as c5 WHERE c5.business_id=r.id AND c5.category='Kosher')", "add_to_query"]
		}
	},
	9: {
		'return': 'question',
		'bot_statement': "And last but not least, what's your price range?",
		'branches': {
			('poor', 'no money', 'feed me', 'please sir I want some more'): [15, " AND r.price_range=1", "add_to_query"],
			('cheap', 'not too bad', 'just got a job'): [15, " AND r.price_range=2", "add_to_query"],
			('going on a date', 'need to impress', 'pretend I haz money'): [15, " AND r.price_range=3", "add_to_query"],
			('no object', 'rich', 'wealthy', 'darling', 'mark zuckerberg'): [15, " AND r.price_range=4", "add_to_query"],
			('whatev',): [15]
		}
	},
	10: {
		'return': 'question',
		'bot_statement': 'Righto, bar it is! What kind of vibe were we thinkin? Chill? Intimate? Romantic...? Ooo! Are you going on a date?? Tell me, tell me!',
		'branches': {
			('intimate','quiet'): [12, " AND r.intimate=True", "add_to_query"],
			('romantic', 'hot date'): [20, " AND r.romantic=True", "end"],
			('chill', 'casual','yo'): [13, " AND (r.casual=True OR r.divey=True)", "add_to_query"],
			('whiskey', 'mixology', 'artisanal', 'craft', 'tapestry'): [20, " AND (r.hipster=True OR EXISTS(SELECT 1 FROM categories as c5 WHERE c5.business_id=r.id AND c5.category = 'Cocktail Bars'))", "end"]
		}
	},
	11: {
		'return': 'question',
		'bot_statement': 'Do you have a preference for coffee or tea?\nTea, right? You know you like tea! (Tea.)',
		'branches': {
			('lovely cucumber sandwiches', 'high society', 'darling'): [20, " AND EXISTS(SELECT 1 FROM categories AS c4 WHERE c4.business_id=r.id AND c4.category IN ('Tea Rooms')", "end"],
			('nah', 'nope', 'no preference', "don't care", 'negative'): [20, '', "end"],
			('caffeine free', 'juice', 'cleanse'): [20, " AND EXISTS(SELECT 1 FROM categories AS c4 WHERE c4.business_id=r.id AND c4.category IN ('Juice Bars & Smoothies'))", "end"]
		}

	},
	12: {
		'return': 'question',
		'bot_statement': "You just want wine, don't you?",
		'branches': {
			('yes sir', 'yup', "that's correct", 'shush', 'ya'): [20, " AND EXISTS(SELECT 1 FROM categories AS c4 WHERE c4.business_id=r.id AND c4.category IN ('Wine Bars'))", "end"]
		}
	},
	13: {
		'return': 'question',
		'bot_statement': 'Mirror mirror on the wall, tell me the one that just wants to watch sports and drink beers of them all...',
		'branches': {
			('hey now', 'fine'): [20, " AND EXISTS(SELECT 1 FROM categories as c4 WHERE c4.business_id=r.id AND c4.category IN ('Dive Bars', 'Sports Bars')", "end"]
		}
	}, 
	# the following 3 queries exist to represent next states, but have different
	# protocol and are handled differently
	15: {

	},
	17: {

	},
	20: {

	}

}



