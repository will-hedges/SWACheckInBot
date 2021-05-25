import os
import pathlib
import random
import sys

import praw
import pyinputplus as pyip
from twilio.base.exceptions import TwilioRestException
import twilio.rest


def get_random_hot_image_post(subreddit):
    """
    Scrapes the top 10 "hot" posts in a given subreddit and picks one at random

        Parameters:
            subreddit (string): the subreddit to scrape from

        Returns:
            (post.title, post.url)
            post.title (string): the text title of the randomly selected post
            post.url (string): the url of the randomly selected post's image
    """
    PRAW_CLIENT_ID = os.getenv("PRAW_CLIENT_ID")
    PRAW_CLIENT_SECRET = os.getenv("PRAW_CLIENT_SECRET")
    PRAW_USER_AGENT = os.getenv("PRAW_USER_AGENT")

    REDDIT = praw.Reddit(
        client_id=PRAW_CLIENT_ID,
        client_secret=PRAW_CLIENT_SECRET,
        user_agent=PRAW_USER_AGENT,
    )

    while True:
        post = random.choice(
            [post for post in REDDIT.subreddit(subreddit).hot(limit=10)]
        )
        if post.url.endswith((".jpg", ".png", ".gif")):
            return (post.title, post.url)


def enter_to_quit():
    """
    Prompts the user to press Enter/Return and exits the terminal
    """
    input("\nPress ENTER to quit...")
    sys.exit()


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


def send_twilio_message(message=None, media_url=None, recipient_phone_number=None):
    """
    Sends an SMS/MMS via twilio. Won't send unless either 'message' or 'media_url' is provided.
    See https://automatetheboringstuff.com/2e/chapter18/ for information on how to set up a free twilio account.
    Fails silently if environment variables are not set.

        Parameters:
            message (string): the text message body (defaults to None)
            media_url (string): the optional media/MMS url (defaults to None)
            recipient_phone_number (string): recipient phone number, including country and area codes (ex. '+11238675309', defaults to None)

        These environment variables must be set:
            TWILIO_ACCOUNT_SID (string): twilio account SID
            TWILIO_AUTH_TOKEN (string): twilio auth token
            TWILIO_PHONE_NUMBER (string): twilio phone number, including country and area codes (ex. '+11238675309')
            MY_CELL_NUMBER (string): your cell number, including country and area codes (ex. '+11238675309')
                - if MY_CELL_NUMBER is set and no recipient is specified, param recipient_phone_number will default to MY_CELL_NUMBER
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
