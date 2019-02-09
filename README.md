# Whisky Sentry
Rare and Special Whisky Detection and Alerting as-a-Service (RaSWDaAaS). 

A simple web scraper of K&L Wine's new products page (link below).  Alerts user via text message when new whisky meets user-specified parameters, allowing you to quickly purchase low-inventory or high-interest items before they sell out.

https://www.klwines.com/productfeed?&productTypeCD=10&regionCD=&minprice=&maxprice=&page=1

## Overview
Retrieves new product list from the link above every 10 minutes and sends an alert text message if any new products meet the following criteria:
* Not sold out AND
* Not vodka, rum, or armagnac AND
* At least one of the following:
  * Product name contains "limit" (usually indicates a bottle limit and consequently a rare or special item)
  * Product allocation is three or fewer (same concept as bottle limit above)
  * Whisky: product name contains "Sazerac," "Stagg," "Handy," "Larue," "K&L Exclusive," or "Single Barrel"
  * Beer: product name comtains "Brouwerij Drie Fonteinen," "Brasserie Cantillon," "Bottle Logic," "Modern Times"
 
## Requesting Changes
Submit a PR to add your phone # to the distribution list or to change the list of product names on which an alert is generated.

## Local Environment Dependencies
* python 3.7.0
* beautifulsoup4 4.6.3
* pytz 2018.5
* twilio 6.16.2
* psycopg2 2.7.6.1
* a PostgreSQL database
* A Twilio account, Twilio phone number, and API credentials (test account is free) 
* A deep, haunting thirst for whisky (must be installed in your local flesh prison environment)

## Known Issues
* None right now
