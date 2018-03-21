from urllib import request, parse
import json

slackURL = None # this will be the url to the webhook ("https://hooks.slack.com/services/your/slack/URL")

def post_message_to_slack(text, *args):
	"""
		Example: post_message_to_slack("Posting this message from python!")
	"""
	post = {"text": "{0}".format(text)}

	try:
		json_data = json.dumps(post)
		req = request.Request(slackURL, data=json_data.endode("ascii"), headers={"Content-Type:": "application/json"})
		resp = request.urlopen(req)
	except Exception as em:
		print("EXCEPTION: " + str(em))

