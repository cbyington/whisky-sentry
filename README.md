# whisky-sentry
Rare and Special Whisky Detection and Alerting as-a-Service (RaSWDaAaS). 

A simple web scraper of K&L Wine's new products page (link below).  Alerts user via text message when new whisky meets user-specified parameters, allowing you to quickly purchase low-inventory or high-interest items before they sell out.

https://www.klwines.com/productfeed?&productTypeCD=10&regionCD=&minprice=&maxprice=&page=1

## Overview
Retrieves new product list from the link above every 10 minutes and sends an alert text message if any products meet the following criteria:
* Not sold out AND
* Not vodka, rum, or armagnac AND
* Posted in the last 19m (to avoid sending multiple alerts on an item unnecessarily) AND 
* At least one of the following:
  * Product name contains "limit" (usually indicates a bottle limit and consequently a rare or special item)
  * Product allocation is three or fewer (same concept as bottle limit above)
  * Product name contains "Sazerac," "Stagg," "Handy," or "Larue"
 
## Requesting Changes
Submit a PR to add your phone # to the distribution list or to change the list of product names on which an alert is generated.

## Local Environment Dependencies
* python 3.7.0
* beautifulsoup4 4.6.3
* pytz 2018.5
* twilio 6.16.2
* A Twilio account, Twilio phone number, and API credentials (test account is free) 
* A deep, haunting thirst for whisky (must be installed in your local flesh prison environment)

## Known Issues
* Using Twilio free credits to send texts currently.  They will run out eventually.
* Product alerts may be duplicated once or twice in some cases.  This is because I've specified the alerts to send for products uploaded in the last 30 minutes, but the job runs every 10 minutes.  I've set this overlap period because Heroku Scheduler (used to run the job) is a bit sporadic in its job timing and there's sometimes a 15 or even 20 minute gap between job runs.  Setting the 30 minute lookback ensures we never miss a new whisky :100:.
