import json
import re
import sys
import time

from requests import get
from twilio.rest import Client

with open('config.json','r') as f:
  data = f.read()
#  print(data)
  config = json.loads(data)

# print(config)

client = Client(config["account_sid"], config["auth_token"])

# for message in client.messages.list():
# 	print(message)

print('Getting IP from home.azcwr.org')
r = get('http://home.azcwr.org/')
# assert "You currently do not have an active access pass."
if "You currently do not have an active access pass." not in r.text:
	  print('Already have an access pass!')
	  print(r.text)
	  sys.exit(1)
# You appear to me as: <ip>
ips = re.findall(r'[0-9]+(?:\.[0-9]+){3}', r.text)
if len(ips) > 1:
	print('got too many ips')
	print(ips)
	sys.exit(1)
if len(ips) == 0:
	print("didn't get any ips")
	print(r.text)
	sys.exit(1)
myip = ips[0]
print('got ip '+myip)

# get existing messages to ensure we don't get an old one
print('Getting list of existing messages')
messages = client.messages.list()
seen_ids = [x.sid for x in messages]

# send enroll message
print('Sending enroll message')
message = client.api.account.messages.create(to=config["target_number"],from_=config["from_number"],body="enroll beginner")

# verify reply, wait up to a minute
start_wait = int(time.time())
while True:
	if time.time()-start_wait < 60:
		time.sleep(5)

		# get latest message list
		messages = client.messages.list()

		# get a list of new messages
		new_messages = [x for x in messages if x.sid not in seen_ids]

		# add these new ones to seen_ids
		seen_ids = seen_ids+[x.sid for x in new_messages]

		valid_messages = [x for x in new_messages if x.direction == "inbound" and x.body.startswith('Thank you, you are now enrolled')]

		if len(valid_messages) != 0:
			print('Got valid reply for enrollment')
			break
		else:
			print('No valid reply yet for enrollment, waiting')

	else:
		print('Failed to get a proper enrollment reply after 60s')
		for m in messages:
		  print('direction', 'to', 'from', 'body')
		  print(m.direction, m.to, m.from_, m.body)
		sys.exit(1)

# send access message
print 'Sending access message'
message = client.api.account.messages.create(to=config["target_number"],from_=config["from_number"],body="access "+myip)

# check azcwr for correct access
print 'Waiting for verification of access'
time.sleep(20) # TODO: replace this with a periodic refresh with timeout

r = get('http://home.azcwr.org/')
if "Here is a list of target systems for this range" in r.text:
	print('Success!')
	sys.exit(0)
else:
	print("Didn't get access?")
	print(r.text)
	sys.exit(1)
# "Here is a list of target systems for this range"
