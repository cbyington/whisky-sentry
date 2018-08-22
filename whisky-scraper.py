import urllib
from urllib.request import urlopen
from bs4 import BeautifulSoup
from twilio.rest import Client
import datetime
import pytz

# Twilio API credentials
twilio_sid = 'AC7852bc7c5f9a918607ab6353a64624b9'
twilio_token = 'ef0159ff649b8e3b46a142dac7b7945c'
twilio_phone_number = '+18317038528'
destination_phone_number = '+16508042890'


####################
## Whisky Parsing ##
####################

# set the URL we're going to scrape, and read its HTML contents into a BS object
page = 'https://www.klwines.com/productfeed?&productTypeCD=10&regionCD=&minprice=&maxprice=&page=1'
page_open = urlopen(page)
soup = BeautifulSoup(page_open,'html.parser')

# grab the data table from within the HTML object.  this is the info we're interested in inspecting
table_body = soup.find('tbody')
rows = table_body.find_all('tr')

# empty dictionaries to hold spirit info; list of spirit names for insertion into SMS
#new_spirits = {}
spirits_to_alert = {}
list_of_spirits = []

# localize timezones omg lol
now = datetime.datetime.now()
timezone = pytz.timezone("America/Los_Angeles")
now_timezone = timezone.localize(now) # here we have the wild current time in its natural PT habitat

# loop through each row in the table, cut out whitespace, and save relevant columns into dictionary
for row in rows:
	cols = row.find_all('td')
	cols = [x.text.strip() for x in cols]

	# save date added, price, quantity, allocation columns
	#new_spirits[cols[3]] = [cols[0],cols[4],cols[5],cols[6]]
	
	# choose whether to write spirits into spirits to alert dictionary
	#if "Sold Out" not in cols[5] and ("limit" in cols[3] or cols[6] == '1' or cols[6] == '2' or cols[6] == '3'):
	if "Sold Out" not in cols[5] and ("limit" in cols[3] or "Sazerac" in cols[3] or "Larue" in cols[3] or "Stagg" in cols[3] or "Handy" in cols[3] or cols[6] == '1' or cols[6] == '2' or cols[6] == '3'):
		spirits_to_alert[cols[3]] = [cols[0],cols[4],cols[5],cols[6]]
		list_of_spirits.append(cols[3] + " -- " + cols[4])

# compose SMS message body
message = "New spirits to check out @ K&L! \n\nhttps://www.klwines.com/productfeed?&productTypeCD=10&regionCD=&minprice=&maxprice=&page=1 \n\n" 
for spirit in range(len(list_of_spirits)):
	message = message + str(list_of_spirits[spirit]) + "\n"

# only send if there is something to send
if len(list_of_spirits) > 0:
	print(message)

####################
## SMS Generation ##
####################

	#client = Client(twilio_sid,twilio_token)
	#client.messages.create(to=destination_phone_number,from_=twilio_phone_number,body=message)
	print("Sent SMS")

if len(list_of_spirits) == 0:
	print(" ")
	print("Nothing to see here!")
