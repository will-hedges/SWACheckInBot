#! python3
# southwest_checkin.py - DESCRIPTION


from datetime import date, datetime, time
import logging
from time import sleep

import pyinputplus as pyip
from selenium import webdriver


class Reservation:
    def get_checkin_date(self):
        while True:
            checkin_date = pyip.inputDate(
                prompt="\nCheck-in date: ",
                formats=[
                    "%m/%d",
                    "%m/%d/%y",
                    "%m/%d/%Y",
                    "%m.%d",
                    "%m.%d.%y",
                    "%m.%d.%Y",
                    "%m-%d",
                    "%m-%d-%y",
                    "%m.%d.%Y",
                    "%d-%m",
                    "%d-%m-%y",
                    "%d-%m-%Y",
                    # TODO add more formats, esp. international
                    #   will need to check if they are parsed correctly
                    #       for example, internat'l 3/1 vs. NA 3/1
                ],
            )
            # if no year is input, set the year to the current year
            #   since inputDate will default to 1900
            if checkin_date < date.today():
                checkin_date = date(
                    date.today().year, checkin_date.month, checkin_date.day
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
            if checkin_time.hour <= 12:
                period = pyip.inputChoice(["AM", "PM"])
                if period == "PM":
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
        # updates the check-in datetime if date or time is changed in confirmation
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
                    self.update_checkin_datetime()
                elif detail == "Check-in time":
                    self.get_checkin_time()
                    self.update_checkin_datetime()
                elif detail == "Confirmation #":
                    self.get_confirmation_num()
                elif detail == "Passenger name":
                    self.get_passenger_name()

            else:
                return

    def check_in(self):

        print("\nChecking in... do not close this window!")
        while datetime.now() < self.checkin_datetime:
            sleep(1)

        swa_url = "https://www.southwest.com/air/check-in/index.html"
        browser = webdriver.Firefox()
        browser.get(swa_url)

        try:
            confirmation_num_field = browser.find_element_by_id("confirmationNumber")
            firstname_field = browser.find_element_by_id("passengerFirstName")
            lastname_field = browser.find_element_by_id("passengerLastName")
            check_in_button = browser.find_element_by_id("form-mixin--submit-button")

            confirmation_num_field.send_keys(self.confirmation_num)
            firstname_field.send_keys(self.firstname)
            lastname_field.send_keys(self.lastname)
            check_in_button.click()

        # TODO send message via Twilio if an exception occurs?
        except Exception as e:
            print(f"Exception: {e}")

        # TODO click through the radio buttons and through the next page

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


main()
