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
import twilio.rest

import helpy


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

    def get_reservation_details(self):
        self.get_checkin_date()
        self.get_checkin_time()
        self.get_confirmation_num()
        self.get_passenger_name()

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

    def check_in(self, driver):
        try:
            print("\nChecking in... don't close these windows!")
            sixty_seconds = timedelta(seconds=60)
            while datetime.now() < self.checkin_datetime - sixty_seconds:
                sleep(1)

            # setting self.driver keeps Chrome from closing
            #   at the completion of this function
            if driver == "firefox":
                self.driver = webdriver.Firefox()
            elif driver == "chrome":
                self.driver = webdriver.Chrome()
            driver = self.driver
            driver.get("https://www.southwest.com/air/check-in/index.html")

            confirmation_num_field = driver.find_element_by_id("confirmationNumber")
            firstname_field = driver.find_element_by_id("passengerFirstName")
            lastname_field = driver.find_element_by_id("passengerLastName")
            check_in_button = driver.find_element_by_id("form-mixin--submit-button")

            confirmation_num_field.send_keys(self.confirmation_num)
            firstname_field.send_keys(self.firstname)
            lastname_field.send_keys(self.lastname)

            while datetime.now() < self.checkin_datetime:
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
            self.boarding_pos = boarding_pos

        except Exception as e:
            # FIXME no actual exception is thrown here
            print(f"An exception occurred: {e}")
            print("Unable to check in.")
            self.boarding_pos = None

    def text_boarding_info_or_check_in_link(self):
        # will only send if twilio credentials are in env vars
        #   see docstring in helpy.send_twilio_message()
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

        print(msg)
        helpy.send_twilio_message(msg)


def main():
    helpy.show_header("SWA CHECK-IN BOT")
    browser = helpy.select_browser()
    reservation = Reservation()
    reservation.get_reservation_details()
    reservation.confirm_reservation()
    reservation.check_in(browser)
    reservation.text_boarding_info_or_check_in_link()
    input("\nPress ENTER or close this window to quit...")


if __name__ == "__main__":
    main()
