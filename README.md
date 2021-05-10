# SWACheckInBot - a Selenium bot for flight check in

Set and forget terminal app to check in at the earliest time for an SWA flight.

## Introduction

Or southwest chicken, if you prefer.

If you're like me and you like to get an early boarding for an SWA flight, it's nerve-wracking to try and beat everyone else, and no one wants to pay extra just to get a good seat. At the 24-hour mark prior to your flight, you might be:
* at work
* driving
* sleeping
* generally living life

This bot aims to check you in when you say with all your input information. No more waiting for the clock to change.

## Technologies
* [Python 3](https://www.python.org/downloads/) (fully tested on 3.8)
* [Mozilla Firefox](https://www.mozilla.org/en-US/firefox/new/) or [Google Chrome](https://www.google.com/chrome/)
* [geckodriver](https://github.com/mozilla/geckodriver/releases) or [chromedriver](https://chromedriver.chromium.org/downloads) (respectively) in your PATH
* [PyInputPlus](https://pyinputplus.readthedocs.io/en/latest/)
* [Selenium](https://selenium-python.readthedocs.io/)
### Optional
* [Twilio](https://pypi.org/project/twilio/) (for SMS notifications)

## Setup
To run this project:
* Download the release archive
* Install packages in [requirements.txt](https://github.com/chemicalwill/SWACheckInBot/blob/main/requirements.txt)
* Run [SWACheckInBot.py](https://github.com/chemicalwill/SWACheckInBot/blob/main/SWACheckInBot.py) from wherever you want

In order to use the **optional** Twilio SMS functionality to text yourself alerts, you'll need to set up a free Twilio account. [Automate the Boring Stuff With Python 2e Chapter 18](https://automatetheboringstuff.com/2e/chapter18/) has a good walkthrough on how to do this.
You'll also need to set the following environment variables:
* TWILIO_ACCOUNT_SID
* TWILIO_AUTH_TOKEN
* TWILIO_PHONE_NUMBER
* MY_PHONE_NUMBER (the cell number you want to receive the text)

**NOTE: set your PC to *NEVER* sleep/hibernate/etc. while you are running this program. Screensaver/lock is fine.**

## Example Notifications

![alt tag](https://i.imgur.com/cXlrKMu.png?1) ![alt tag](
https://i.imgur.com/4kIoJlb.png?1)
