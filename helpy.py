import os
import pathlib
import sys

import pyinputplus as pyip
from twilio.base.exceptions import TwilioRestException
import twilio.rest


def show_header(title_string):
    """
    Prints an uppercase header with asterisks.

        Parameters:
            title_string (string): the program's name/title

        Example:
            show_header("some title")
            **************
            * SOME TITLE *
            **************
    """
    title = f"* {title_string.upper()} *"
    bar = "*" * len(title)
    print(bar)
    print(title)
    print(bar)


def select_browser():
    """
    Checks to see if geckodriver, chromedriver or both are in PATH.

    If both are present, asks the user to choose one.

    If neither are present, quits.
    """
    path_dirs = os.getenv("PATH").split(os.pathsep)
    webdrivers = []
    for path_dir in path_dirs:
        geckodriver = pathlib.Path(path_dir) / "geckodriver"
        chromedriver = pathlib.Path(path_dir) / "chromedriver"
        if geckodriver.is_file():
            webdrivers.append("firefox")
        if chromedriver.is_file():
            webdrivers.append("chrome")

    if not webdrivers:
        print("Neither geckodriver nor chromedriver were found in PATH")
        print("Please install a web driver to PATH and try again.")
        input("Press ENTER to quit...")
        sys.exit()

    if "firefox" in webdrivers and "chrome" in webdrivers:
        print(
            ("Multiple web drivers were found in PATH."),
            ("Which browser would you like to use?"),
        )
        choice = pyip.inputMenu(["Firefox", "Chrome"], numbered=True)
        return choice.lower()

    return webdrivers.pop()


def send_twilio_message(message=None, media_url=None, recipient=None):
    """
    Sends an SMS/MMS via twilio. Won't send unless either 'message' or 'media_url' is provided.
    See https://automatetheboringstuff.com/2e/chapter18/ for information on how to set up a free twilio account.
    Fails silently if environment variables are not set.

        Parameters:
            message (string): the text message body (defaults to None)
            media_url (string): the optional media/MMS url (defaults to None)
            recipient (string): recipient phone number, including country and area codes (ex. '+11238675309', defaults to None)

        These environment variables must be set:
            TWILIO_ACCOUNT_SID (string): twilio account SID
            TWILIO_AUTH_TOKEN (string): twilio auth token
            TWILIO_PHONE_NUMBER (string): twilio phone number, including country and area codes (ex. '+11238675309')
            MY_CELL_NUMBER (string): your cell number, including country and area codes (ex. '+11238675309')
                - if MY_CELL_NUMBER is set and no recipient is specified, will default to MY_CELL_NUMBER
    """

    if message or media_url:
        try:
            TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
            TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
            TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

            if not recipient:
                MY_CELL_NUMBER = os.getenv("MY_CELL_NUMBER")
                recipient = MY_CELL_NUMBER

            TWILIO_CLIENT = twilio.rest.Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            TWILIO_CLIENT.messages.create(
                body=message,
                media_url=[media_url],
                from_=TWILIO_PHONE_NUMBER,
                to=recipient,
            )

        except TwilioRestException:
            pass
