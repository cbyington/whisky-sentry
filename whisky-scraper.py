####################################
## Libraries & Script Parameters ##
####################################

import os
import datetime 
import pytz
import requests
from bs4 import BeautifulSoup
from twilio.rest import Client
import random

# Twilio API credentials
twilio_sid = os.environ.get('TWILIO_SID') # stored in config vars in Heroku
twilio_token = os.environ.get('TWILIO_SECRET')
client = Client(twilio_sid,twilio_token) # stage the Twilio API call

# phone #s
twilio_phone_number = '+18317038528'
destination_phone_numbers = ['+16508042890'] # people to alert
error_phone_number = '+16508042890' # phone # to which to send runtime error notifications

# URL of page to scrape
page = 'https://www.klwines.com/productfeed?&productTypeCD=10&regionCD=&minprice=&maxprice=&page=1'

# list of keywords to be matched to product name.  any of these will trigger a text to be sent
search_words = ['Sazerac',
		'Larue',
		'Stagg',
		'Handy',
		'K&L Exclusive']

# any keyword in this list will result in the spirit not triggering an alert (even if it meets other criteria)
blacklist_words = ['Rum',
		   'Vodka',
		   'Armagnac']

# list of user agents to choose from randomly when opening the K&L website
user_agents = ['Mozilla/5.0',
			'Chrome/44.0',
			'Chrome/45.0',
			'Safari/537',
			'Safari/536'
			'Safari/535']


####################
## Whisky Parsing ##
####################

# choose a random user-agent and define header user-agent to send in the web scraping request to avoid bot blockers
random_user_agent = random.SystemRandom().choice(user_agents)
headers = {'user-agent': random_user_agent}

# read page HTML contents into a BS object.  send Chris an SMS if the app is blocked by K&L (happened before)
try: 
	soup = BeautifulSoup(requests.get(page, headers=headers).content,'html.parser')

except requests.exceptions.HTTPError as e:
	print("Request error!")

	# send an SMS to Chris' cell phone to let him know of the error
	error_message = "There has been an HTTP request error with whisky-sentry"
	client.messages.create(to=error_phone_number,from_=twilio_phone_number,body=error_message)

	exit()

# grab the data table from within the HTML object.  this is the info we're interested in inspecting
rows = soup.find('tbody').find_all('tr')

# empty list to hold spirit info.  This'll go into the SMS message
list_of_spirits = []

# calculate current time in UTC for comparison later to the time at which products were uploaded
utc_tz = pytz.timezone("UTC")
now_aware = utc_tz.localize(datetime.datetime.utcnow()) 

# loop through each row in the table, cut out whitespace for each cell
for row in rows:
	cols = row.find_all('td')
	cols = [x.text.strip() for x in cols]

	# cast scraped datetimes from naive to aware (UTC). datetimes are rendered (in browser) in PT but scraped in UTC :shrug:
	cols[0] = utc_tz.localize(datetime.datetime.strptime(cols[0],'%m/%d/%Y %I:%M %p'))

	# choose whether to write spirits into list of spirits to alert on based on selection criteria
	if cols[0] >= now_aware + datetime.timedelta(minutes = -19): # posted in last 20 mins
		if 'Sold Out' not in cols[5]:
			if not any(j in cols[3] for j in blacklist_words): # exclude blacklisted spirits
				if 'limit' in cols[3]: # "limit" is in the name - usually this is a bottle limit
					list_of_spirits.append(cols[3] + " -- " + cols[4])
				elif any(i in cols[3] for i in search_words): # if any of the search_words show up in the name
					list_of_spirits.append(cols[3] + " -- " + cols[4])
				elif any(x in cols[6] for x in ['1','2','3']): # if the allocation (bottle limit) is 1, 2, or 3
					list_of_spirits.append(cols[3] + " -- " + cols[4])


####################
## SMS Generation ##
####################

# compose SMS message body
message = "New spirits to check out @ K&L! \n\nhttps://www.klwines.com/productfeed?&productTypeCD=10&regionCD=&minprice=&maxprice=&page=1 \n\n" 
for spirit in list_of_spirits:
	message = message + str(spirit) + "\n"

# only send if there is something to send
if len(list_of_spirits) > 0:
	print(message) 

	for phone_number in destination_phone_numbers:
		client.messages.create(to=phone_number,from_=twilio_phone_number,body=message)
		print("Sent SMS to " + str(phone_number))

if len(list_of_spirits) == 0:
	print("Nothing to see here!")
