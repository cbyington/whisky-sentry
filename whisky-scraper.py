import datetime 
import pytz
from urllib.request import urlopen
from bs4 import BeautifulSoup
from twilio.rest import Client

# Twilio API credentials
twilio_sid = 'AC7852bc7c5f9a918607ab6353a64624b9'
twilio_token = 'ef0159ff649b8e3b46a142dac7b7945c'
client = Client(twilio_sid,twilio_token)
twilio_phone_number = '+18317038528'
destination_phone_number = '+16508042890'

# URL of page to scrape
page = 'https://www.klwines.com/productfeed?&productTypeCD=10&regionCD=&minprice=&maxprice=&page=1'

####################
## Whisky Parsing ##
####################

# read page HTML contents into a BS object
soup = BeautifulSoup(urlopen(page),'html.parser')

# grab the data table from within the HTML object.  this is the info we're interested in inspecting
rows = soup.find('tbody').find_all('tr')

# instantiate empty dictionaries to hold spirit info; list of spirit names for insertion into SMS
#new_spirits = {}
spirits_to_alert = {}
list_of_spirits = []

# calculate current time in UTC for comparison later to the time products were uploaded
utc_tz = pytz.timezone("UTC")
now_aware = utc_tz.localize(datetime.datetime.utcnow()) 

# loop through each row in the table, cut out whitespace for each column
for row in rows:
	cols = row.find_all('td')
	cols = [x.text.strip() for x in cols]

	# cast scraped datetimes from naive to aware (UTC). datetimes are rendered (in browser) in PT but scraped in UTC :shrug:
	cols[0] = utc_tz.localize(datetime.datetime.strptime(cols[0],'%m/%d/%Y %I:%M %p'))

	# save date added, price, quantity, allocation columns in dict
	#new_spirits[cols[3]] = [cols[0],cols[4],cols[5],cols[6]]
	
	# choose whether to write spirits into spirits to alert dictionary
	#if "Sold Out" not in cols[5] and ("limit" in cols[3] or "Sazerac" in cols[3] or "Larue" in cols[3] or "Stagg" in cols[3] or "Handy" in cols[3] or cols[6] == '1' or cols[6] == '2' or cols[6] == '3'):
	if ("limit" in cols[3] or "Sazerac" in cols[3] or "Larue" in cols[3] or "Stagg" in cols[3] or "Handy" in cols[3] or cols[6] == '1' or cols[6] == '2' or cols[6] == '3'):
		if cols[0] >= now_aware + datetime.timedelta(hours = -48):
			spirits_to_alert[cols[3]] = [cols[0],cols[4],cols[5],cols[6]]
			list_of_spirits.append(cols[3] + " -- " + cols[4])

# compose SMS message body
message = "New spirits to check out @ K&L! \n\nhttps://www.klwines.com/productfeed?&productTypeCD=10&regionCD=&minprice=&maxprice=&page=1 \n\n" 
for spirit in range(len(list_of_spirits)):
	message = message + str(list_of_spirits[spirit]) + "\n"

# only send if there is something to send
print(" ")
if len(list_of_spirits) > 0:
	print(message)

####################
## SMS Generation ##
####################

	# indentation here means SMS will fire only if the list is non empty
	client.messages.create(to=destination_phone_number,from_=twilio_phone_number,body=message)
	print("Sent SMS")

if len(list_of_spirits) == 0:
	print(" ")
	print("Nothing to see here!")
