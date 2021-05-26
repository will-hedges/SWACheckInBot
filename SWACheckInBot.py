#!/usr/bin/env python3
# SWACheckInBot.py - checks in for a SWA flight based on user input


from datetime import date, datetime, time, timedelta
import os
import pathlib
import re
import sys
from time import sleep

import pyinputplus as pyip
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
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


def get_check_in_date():
    while True:
        input_date = pyip.inputDate(
            prompt="\nCheck-in date (M/D/Y): ", formats=["%m/%d/%y", "%m/%d/%Y"]
        )
        if input_date < date.today():
            print("Check-in date cannot be in the past.")
        else:
            return input_date


def get_check_in_time(check_in_date):
    valid_time = False
    while True:
        while not valid_time:
            input_time = input("\nCheck-in time: ").strip()
            try:
                mo = re.search(r"(\d{,2}):?(\d{2}) ?(AM|PM)?", input_time)
                if not mo:
                    print(f"'{input_time}' is not a valid time.")
                elif mo:
                    hour, minute = int(mo.group(1)), int(mo.group(2))
                    period = mo.group(3)
                    if 0 <= hour <= 23 and 0 <= minute <= 59:
                        valid_time = True
                    else:
                        print(f"'{input_time}' is not a valid time.")
            except ValueError:
                print(f"'{input_time}' is not a valid time.")

        if ":" in input_time and hour <= 12 and not period:
            period = pyip.inputChoice(["AM", "PM"])

        if period == "AM" and hour == 12:
            hour -= 12
        elif period == "PM" and hour != 12:
            hour += 12

        check_in_time = time(hour, minute)
        check_in_datetime = datetime(
            check_in_date.year,
            check_in_date.month,
            check_in_date.day,
            check_in_time.hour,
            check_in_time.minute,
        )
        if check_in_datetime < datetime.now():
            print("Check-in time cannot be in the past.")
        else:
            return check_in_time


def get_confirmation_num():
    confirmation_num = pyip.inputStr(
        prompt="\nConfirmation #: ",
        blockRegexes=[r".*"],
        allowRegexes=[r"^(\w{6})$"],
    )
    return confirmation_num


def get_passenger_name():
    passenger_name = (
        pyip.inputStr(
            prompt="\nPassenger name: ",
            blockRegexes=[r".*"],
            allowRegexes=[r"^([A-Za-z]+\s[A-Za-z]+)$"],
        )
        .title()
        .split()
    )
    return passenger_name


class Reservation:
    def __init__(self, check_in_date, check_in_time, confirmation_num, passenger_name):
        self.check_in_date = check_in_date
        self.check_in_time = check_in_time
        self.check_in_datetime = datetime(
            check_in_date.year,
            check_in_date.month,
            check_in_date.day,
            check_in_time.hour,
            check_in_time.minute,
        )
        self.confirmation_num = confirmation_num
        self.firstname, self.lastname = passenger_name

    def update_check_in_datetime(self):
        self.check_in_datetime = datetime(
            self.check_in_date.year,
            self.check_in_date.month,
            self.check_in_date.day,
            self.check_in_time.hour,
            self.check_in_date.minute,
        )

    def confirm_reservation(self):
        while True:
            check_in_datetime_as_string = self.check_in_datetime.strftime(
                "%I:%M %p on %a, %b %d, %Y"
            )

            print(
                (f"\nChecking in at {check_in_datetime_as_string}"),
                (f"for {self.firstname} {self.lastname}"),
                (f"({self.confirmation_num})."),
            )

            user_confirm = pyip.inputYesNo(prompt=("Is this correct (Y/N)? "))
            if user_confirm == "no":
                print("\nWhat would you like to fix?")
                detail_to_change = pyip.inputMenu(
                    (
                        "Check-in date",
                        "Check-in time",
                        "Confirmation #",
                        "Passenger name",
                    ),
                    numbered=True,
                )

                if detail_to_change == "Check-in date":
                    self.check_in_date = get_check_in_date()
                elif detail_to_change == "Check-in time":
                    self.check_in_time = get_check_in_time(self.check_in_date)
                elif detail_to_change == "Confirmation #":
                    self.confirmation_num = get_confirmation_num()
                elif detail_to_change == "Passenger name":
                    self.passenger_name = get_passenger_name()

                self.update_check_in_datetime()

            else:
                return


def check_in_and_return_boarding_pos(Reservation, driver):
    try:
        print("\nWaiting to check in... don't close these windows!")
        sixty_seconds = timedelta(seconds=60)
        while datetime.now() < Reservation.check_in_datetime - sixty_seconds:
            sleep(1)

        # TODO see if this will run headless
        if driver == "firefox":
            driver = webdriver.Firefox()
        elif driver == "chrome":
            driver = webdriver.Chrome()
        driver.get("https://www.southwest.com/air/check-in/index.html")

        confirmation_num_field = driver.find_element_by_id("confirmationNumber")
        firstname_field = driver.find_element_by_id("passengerFirstName")
        lastname_field = driver.find_element_by_id("passengerLastName")
        check_in_button = driver.find_element_by_id("form-mixin--submit-button")

        confirmation_num_field.send_keys(Reservation.confirmation_num)
        firstname_field.send_keys(Reservation.firstname)
        lastname_field.send_keys(Reservation.lastname)

        while datetime.now() < Reservation.check_in_datetime:
            sleep(1)
        check_in_button.click()

        # 5s is the shortest wait time that works here
        #   and XPATH is the only CSS selector that works here
        WebDriverWait(driver, 5).until(
            expected_conditions.element_to_be_clickable(
                (
                    By.XPATH,
                    "/html/body/div[2]/div/div/div/div[2]/div[2]/div/div[2]/div/section/div/div/div[3]/button",
                )
            )
        ).click()

        boarding_pos = driver.find_element_by_class_name(
            "air-check-in-passenger-list"
        ).text.split("\n")
        boarding_pos = {
            passenger: pos
            for passenger, pos in zip(boarding_pos[::2], boarding_pos[1::2])
        }

        print("\nSuccessfully checked in!")
        print("Boarding positions:")
        for passenger, pos in boarding_pos.items():
            print(f" * {pos} - {passenger}")

    except Exception as e:
        # FIXME no actual exception is thrown here
        print(f"An exception occurred: {e}")
        print("Unable to check in.")
        boarding_pos = None

    return boarding_pos


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

            if not recipient_phone_number:
                MY_CELL_NUMBER = os.getenv("MY_CELL_NUMBER")
                recipient_phone_number = MY_CELL_NUMBER

            TWILIO_CLIENT = twilio.rest.Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            TWILIO_CLIENT.messages.create(
                body=message,
                media_url=[media_url],
                from_=TWILIO_PHONE_NUMBER,
                to=recipient_phone_number,
            )

        except TwilioRestException:
            pass


def text_boarding_info_or_check_in_link(Reservation, boarding_pos):
    # will only send if twilio credentials are in env vars
    #   see docstring in cw.send_twilio_message()
    if boarding_pos:
        msg = (
            f"SWACheckInBot: "
            f"You're checked in for itinerary {Reservation.confirmation_num}! "
            f"Boarding position(s): {', '.join(pos for pos in boarding_pos.values())}"
        )
    else:
        msg = (
            f"SWACheckInBot: "
            f"Uh oh! Something went wrong. "
            f"Check in for {Reservation.confirmation_num} ASAP! "
            f"https://southwest.com/check-in"
        )

    print(msg)
    send_twilio_message(msg)


def main():
    show_header("SWA CHECK-IN BOT")
    browser = select_browser()

    check_in_date = get_check_in_date()
    check_in_time = get_check_in_time(check_in_date)
    confirmation_num = get_confirmation_num()
    passenger_name = get_passenger_name()

    reservation = Reservation(
        check_in_date, check_in_time, confirmation_num, passenger_name
    )
    reservation.confirm_reservation()

    boarding_pos = check_in_and_return_boarding_pos(reservation, browser)
    text_boarding_info_or_check_in_link(reservation, boarding_pos)

    input("\nPress ENTER or close this window to quit...")


if __name__ == "__main__":
    main()
