#! python3
# southwest_checkin.py - DESCRIPTION


from datetime import date, datetime, time
import logging
from time import sleep

import pyinputplus as pyip
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait


class Reservation:
    def print_header(): # TODO
        pass

    def get_checkin_date(self):
        while True:
            checkin_date = pyip.inputDate(
                prompt="\nCheck-in date (MM/DD/YYYY): ",
                formats=["%m/%d/%Y"]
            )

            logging.debug(f"checkin_date == {checkin_date}")

            if checkin_date < date.today():
                print("Check-in date cannot be in the past.")
            else:
                self.checkin_date = checkin_date
                return

    def get_checkin_time(self):
        while True:
            checkin_time = pyip.inputTime(
                prompt="\nCheck-in time: ", formats=["%H%M", "%H:%M"]
            )

            # FIXME I'm fairly certain I had a better way of doing this before
            #   should skip if you put PM, or if you put 0730, 1930 etc.
            if checkin_time.hour <= 12:
                period = pyip.inputChoice(["AM", "PM"])
                if period == "AM" and checkin_time.hour == 12:
                    checkin_time = time(checkin_time.hour - 12, checkin_time.minute)
                elif period == "PM" and checkin_time != 12:
                    checkin_time = time(checkin_time.hour + 12, checkin_time.minute)

            logging.debug(f"checkin_time == {checkin_time}")

            checkin_datetime = datetime(
                self.checkin_date.year,
                self.checkin_date.month,
                self.checkin_date.day,
                checkin_time.hour,
                checkin_time.minute,
            )

            if checkin_datetime < datetime.now():
                print("Check-in time cannot be in the past.")
            else:
                self.checkin_datetime = checkin_datetime
                self.checkin_time = checkin_time
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
        logging.debug(f"self.checkin_datetime == {self.checkin_datetime}")
        return

    def confirm_reservation(self):
        while True:
            print(
                (f"\nChecking in at {self.checkin_time.strftime('%I:%M %p')}"),
                (f"on {self.checkin_date.strftime('%a, %b %d, %Y')}"),
                (f"for {self.firstname} {self.lastname} ({self.confirmation_num})."),
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
        print("\nChecking in... do not close this window!")  # FIXME
        while datetime.now() < self.checkin_datetime:
            sleep(1)

        browser = webdriver.Firefox()
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

        WebDriverWait(browser, 20).until(
            expected_conditions.element_to_be_clickable(
                (
                    By.XPATH,
                    "/html/body/div[2]/div/div/div/div[2]/div[2]/div/div[2]/div/section/div/div/div[3]/button",
                )
            )
        ).click()

        # TODO make this a try/except block
        # TODO send message via Twilio if an exception occurs?

        return


def main():
    reservation = Reservation()
    reservation.get_reservation()
    reservation.confirm_reservation()
    reservation.check_in()
    input("\nPress ENTER or close this window to quit...")
    return


logging.basicConfig(level=logging.DEBUG, format=" %(levelname)s - %(message)s")
# logging.disable(logging.CRITICAL)

if __name__ == "__main__":
    main()
