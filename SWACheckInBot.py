#!/usr/bin/env python3
# SWACheckInBot.py - checks in for a SWA flight based on user input


from datetime import date, datetime, time
import os
import re
from time import sleep

import pyinputplus as pyip
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
import twilio.rest


def print_header():
    title = "* SOUTHWEST CHECK-IN *"
    bar = "*" * len(title)
    print(bar)
    print(title)
    print(bar)
    return


class Reservation:
    def get_checkin_date(self):
        while True:
            input_date = pyip.inputDate(
                prompt="\nCheck-in date (M/D/Y): ", formats=["%m/%d/%y", "%m/%d/%Y"]
            )
            if input_date < date.today():
                print("Check-in date cannot be in the past.")
            else:
                self.checkin_date = input_date
                return

    def get_checkin_time(self):
        while True:
            while True:
                input_time = input("\nCheck-in time: ").strip()
                try:
                    mo = re.search(r"(\d{,2}):?(\d{2}) ?(AM|PM)?", input_time)
                    if not mo:
                        print(f"'{input_time}' is not a valid time.")
                    elif mo:
                        hour, minute = int(mo.group(1)), int(mo.group(2))
                        period = mo.group(3)
                        if 0 <= hour <= 23 and 0 <= minute <= 59:
                            break
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

            checkin_time = time(hour, minute)
            checkin_datetime = datetime(
                self.checkin_date.year,
                self.checkin_date.month,
                self.checkin_date.day,
                hour,
                minute,
            )

            if checkin_datetime < datetime.now():
                print("Check-in time cannot be in the past.")
                continue
            else:
                self.checkin_time = checkin_time
                self.checkin_datetime = checkin_datetime
                return

    def get_confirmation_num(self):
        self.confirmation_num = pyip.inputStr(
            prompt="\nConfirmation #: ",
            blockRegexes=[r".*"],
            allowRegexes=[r"^(\w{6})$"],
        )
        return

    def get_passenger_name(self):
        passenger_name = (
            pyip.inputStr(
                prompt="\nPassenger name: ",
                blockRegexes=[r".*"],
                allowRegexes=[r"^([A-Za-z]+\s[A-Za-z]+)$"],
            )
            .title()
            .split()
        )
        self.firstname = passenger_name[0]
        self.lastname = passenger_name[1]
        return

    def get_reservation(self):
        self.get_checkin_date()
        self.get_checkin_time()
        self.get_confirmation_num()
        self.get_passenger_name()
        return

    def update_checkin_datetime(self):
        # updates self.checkin_datetime if the date or time
        #   is changed by confirm_reservation()
        self.checkin_datetime = datetime(
            self.checkin_date.year,
            self.checkin_date.month,
            self.checkin_date.day,
            self.checkin_time.hour,
            self.checkin_time.minute,
        )
        return

    def confirm_reservation(self):
        while True:
            checkin_datetime_as_string = self.checkin_datetime.strftime(
                "%I:%M %p on %a, %b %d, %Y"
            )

            print(
                (f"\nChecking in at {checkin_datetime_as_string}"),
                (f"for {self.firstname} {self.lastname}"),
                (f"({self.confirmation_num})."),
            )

            user_confirm = pyip.inputYesNo(prompt=("Is this correct (Y/N)? "))
            if user_confirm == "no":
                print("\nWhat would you like to fix?")
                detail = pyip.inputMenu(
                    [
                        "Check-in date",
                        "Check-in time",
                        "Confirmation #",
                        "Passenger name",
                    ],
                    numbered=True,
                )

                if detail == "Check-in date":
                    self.get_checkin_date()
                elif detail == "Check-in time":
                    self.get_checkin_time()
                elif detail == "Confirmation #":
                    self.get_confirmation_num()
                elif detail == "Passenger name":
                    self.get_passenger_name()

                self.update_checkin_datetime()

            else:
                return

    def check_in(self):
        try:
            browser = webdriver.Firefox()
            print("\nChecking in... do not close this window!")
            # TODO add animation here
            while datetime.now() < self.checkin_datetime:
                sleep(1)

            swa_url = "https://www.southwest.com/air/check-in/index.html"
            browser.get(swa_url)

            confirmation_num_field = browser.find_element_by_id("confirmationNumber")
            firstname_field = browser.find_element_by_id("passengerFirstName")
            lastname_field = browser.find_element_by_id("passengerLastName")
            check_in_button = browser.find_element_by_id("form-mixin--submit-button")

            confirmation_num_field.send_keys(self.confirmation_num)
            firstname_field.send_keys(self.firstname)
            lastname_field.send_keys(self.lastname)
            check_in_button.click()

            # 5s is the shortest wait time that works
            #   and XPATH is the only CSS selector that works
            WebDriverWait(browser, 5).until(
                expected_conditions.element_to_be_clickable(
                    (
                        By.XPATH,
                        "/html/body/div[2]/div/div/div/div[2]/div[2]/div/div[2]/div/section/div/div/div[3]/button",
                    )
                )
            ).click()

            boarding_pos = browser.find_element_by_class_name(
                "air-check-in-passenger-list"
            ).text.split("\n")
            boarding_pos = {
                passenger: pos
                for passenger, pos in zip(boarding_pos[::2], boarding_pos[1::2])
            }
            self.boarding_pos = boarding_pos

            print("\nSuccessfully checked in!")
            print("Boarding positions:")
            for passenger, pos in boarding_pos.items():
                print(f" * {pos} - {passenger}")

        except Exception as e:
            print(f"An exception occurred: {e}")
            print("Unable to check in.")
            self.boarding_pos = None

        return

    def text_boarding_info_or_check_in_link(self):
        # texts boarding position(s) or the check-in link only if the user has
        #   correctly configured a Twilio account in their environment vars
        try:
            TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
            TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
            TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
            MY_CELL_NUMBER = os.getenv("MY_CELL_NUMBER")
            TWILIO_CLIENT = twilio.rest.Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

            if self.boarding_pos:
                msg = (
                    f"SWACheckInBot: "
                    f"You're checked in for itinerary {self.confirmation_num}! "
                    f"Boarding position(s): {', '.join(pos for pos in self.boarding_pos.values())}"
                )
            else:
                msg = (
                    f"SWACheckInBot: "
                    f"Uh oh! Something went wrong. "
                    f"Check in for {self.confirmation_num} ASAP! "
                    f"https://southwest.com/check-in"
                )

            TWILIO_CLIENT.messages.create(
                body=msg, from_=TWILIO_PHONE_NUMBER, to=MY_CELL_NUMBER
            )

        except:
            pass

        return


def main():
    print_header()
    reservation = Reservation()
    reservation.get_reservation()
    reservation.confirm_reservation()
    reservation.check_in()
    reservation.text_boarding_info_or_check_in_link()
    input("\nPress ENTER or close this window to quit...")
    return


if __name__ == "__main__":
    main()
