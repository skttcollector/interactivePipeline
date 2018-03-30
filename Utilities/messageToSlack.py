from urllib import request, parse
import json

# this is for slackapitesting-zbw account
# get the info from https://my.slack.com/services/new/incoming-webhook/ (you'll need to log in)
slackChannelURL = "https://hooks.slack.com/services/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" # this will be the url to the webhook ("https://hooks.slack.com/services/your/slack/URL")

def post_message_to_slack(text, *args):
	"""
		Example: post_message_to_slack("Posting this message from python!")
	"""
# maybe use profiles of users to determine who gets what? ie. rigging, animation, producer, etc
# add paths to files? 
	post = {"text": "{0}".format(text)} # links - add--> <url.com|linktext> in the quotes, "username":"someName", "icon_url":"https://slack.com/img/icons/app-57.png", "icon_emoji":":ghost", "channel":"#other-channel", "channel":"@username", icon, etc can be set from webpage that you get from new incoming webhooks
	
	try:
		json_data = json.dumps(post)
		req = request.Request(slackChannelURL, data=json_data.endode("ascii"), headers={"Content-Type:": "application/json"})
		resp = request.urlopen(req)
	except Exception as em:
		print("EXCEPTION: " + str(em))

