import json

def clean_business_file():
	f = open("yelp_academic_dataset_business.json")
	fo = open("yelp_academic_dataset_business_clean.json", 'w')

	for line in f:
		line.replace("\n", " ")
		fo.write(line)

	f.close()
	fo.close()

def clean_rating_file():
	f = open("yelp_academic_dataset_review.json")
	fo = open("yelp_academic_dataset_review_clean.json", 'w')

	for line in f:
		jsonline = json.loads(line)
		jsonline["text"] = jsonline["text"].replace("\n", " ")
		new_line = json.dumps(jsonline)
		fo.write(new_line + "\n")

	f.close()
	fo.close()



if __name__ == "__main__":
	# clean_file()
	clean_rating_file()
