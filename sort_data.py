def main():
	f = open("yelp_academic_dataset (1).json")
	user_file = open("users_data.json", 'w')
	business_file = open("businesses_data.json", 'w')
	rating_file = open("ratings_data.json", 'w')

	u = []
	b = []
	r = []

	for line in f:
		if '"type": "user"' in line:
			u.append(line)
		elif '"review_id"' in line:
			r.append(line)
		elif '"full_address"' in line:
			b.append(line)

	user_file.write("".join(u))
	business_file.write("".join(b))
	rating_file.write("".join(r))
	
if __name__ == "__main__":
	main()