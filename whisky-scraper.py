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
import psycopg2

# Twilio API credentials
twilio_sid = os.environ.get('TWILIO_SID') # stored in config vars in Heroku
twilio_token = os.environ.get('TWILIO_SECRET')
client = Client(twilio_sid,twilio_token) # stage the Twilio API call

# DB credentials
DATABASE_URL = os.environ['DATABASE_URL']

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


########################
## Database Functions ##
########################

# functions to write to and read from a database of alerts we've already sent; this ensures we don't double-send notifications
def insert_alert(date,sku,name,price,quantity_on_hand,allocation):
	conn=psycopg2.connect(DATABASE_URL, sslmode='require')
	cur=conn.cursor()
	cur.execute("INSERT INTO alerts VALUES(%s,%s,%s,%s,%s,%s)",(date,sku,name,price,quantity_on_hand,allocation))
	conn.commit()
	conn.close()

def read_alerts(date):
	conn=psycopg2.connect(DATABASE_URL, sslmode='require')
	cur=conn.cursor()
	cur.execute("SELECT DISTINCT sku FROM alerts WHERE date >= %s",[date])
	rows=cur.fetchall()
	conn.close()
	return rows # returns a tuple object of all the rows


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

skus_recently_alerted_on = list(read_alerts(now_aware + datetime.timedelta(minutes = -60))) # don't alert on a product that was alerted on within the last 60m
sku_blacklist = [str(item) for sublist in skus_recently_alerted_on for item in sublist]

for row in rows: # loop through each row in the table, cut out whitespace for each cell
	cols = row.find_all('td')
	cols = [x.text.strip() for x in cols]

	# cast # on hand and allocation to None if they are empty string
	# TODO: there has got to be a better way to do this
	if cols[5] == '':
		cols[5] = '-47'

	if cols[6] == '':
		cols[6] = '-47'

	# cast scraped datetimes from naive to aware (UTC). datetimes are rendered (in browser) in PT but scraped in UTC :shrug:
	cols[0] = utc_tz.localize(datetime.datetime.strptime(cols[0],'%m/%d/%Y %I:%M %p'))

	# choose whether to write spirits into list of spirits to alert on based on selection criteria
	if 'Sold Out' not in cols[5]: # note to self on fields: 0 = time. 1 = sku. 3 = name. 4 = price. 5. q on hand. 6 = allocation.  
		if not any(b in cols[1] for b in sku_blacklist): # check if have alerted on the SKU in the last 60m.  if so, don't send another alert
			if cols[0] >= now_aware + datetime.timedelta(minutes = -30): # require the product was posted in last 30 mins
				if not any(j in cols[3] for j in blacklist_words): # exclude blacklisted spirits
					if 'limit' in cols[3] or any(i in cols[3] for i in search_words) or any(z in cols[6] for z in ['1','2','3']): # alert if has limit in the name, has any of the search words, or as <= 3 allocation
						list_of_spirits.append(cols[3] + " -- " + cols[4])
						insert_alert(cols[0],cols[1],cols[3],float(cols[4].strip('$')),cols[5],cols[6]) # insert into DB so we don't alert on it again

####################
## SMS Generation ##
####################

# compose SMS message body
message = "New spirits to check out @ K&L! (PG test!) \n\nhttps://www.klwines.com/productfeed?&productTypeCD=10&regionCD=&minprice=&maxprice=&page=1 \n\n" 
for spirit in list_of_spirits:
	message = message + str(spirit) + "\n"

if len(list_of_spirits) > 0: # only send if there is something to send
	print(message) 

	for phone_number in destination_phone_numbers:
		client.messages.create(to=phone_number,from_=twilio_phone_number,body=message)
		print("Sent SMS to " + str(phone_number))

if len(list_of_spirits) == 0:
	print("Nothing to see here!")
