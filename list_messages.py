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

messages = client.messages.list()
for m in messages:
  print('direction', 'to', 'from', 'body')
  print(m.direction, m.to, m.from_, m.body)
sys.exit(1)
