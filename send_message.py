from twilio.rest import TwilioRestClient
import os

def send_text(message, phone_num):
	ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
	AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
	TWILIO_NUMBER = os.environ.get('TWILIO_NUMBER')

	client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)

	client.messages.create(
		to=phone_num,
		from_=TWILIO_NUMBER,
		body=message,)