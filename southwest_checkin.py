#! python3
# southwest_checkin.py - DESCRIPTION


from datetime import date, datetime, time
import logging

import pyinputplus as pyip
from selenium import webdriver


logging.basicConfig(
    level=logging.DEBUG,
    format=' %(levelname)s - %(message)s'
    )
# logging.disable(logging.CRITICAL)

class Reservation():

    def get_checkin_date(self):
        while True:
            self.checkin_date = pyip.inputDate(
                prompt='Check-in date: ',
                formats=[
                    '%m/%d', '%m/%d/%y', '%m/%d/%Y',
                    '%m.%d', '%m.%d.%y', '%m.%d.%Y',
                    '%m-%d', '%m-%d-%y', '%m.%d.%Y',
                    '%d-%m', '%d-%m-%y', '%d-%m-%Y',

                    # TODO add more formats, ISO, etc.

                    ]
                )

            # TODO default to current year if none provided

            if self.checkin_date < date.today():
                print('Check-in date cannot be in the past.')
            else:
                return


    def get_checkin_time(self):
        checkin_time = pyip.inputTime(
            prompt='Check-in time: ',
            formats=[
                '%H%M', '%H:%M',
                '%I:%M', '%I:%M%p', '%I:%M %p'
                ]
            )

        # TODO validate input for AM/PM (period)
        # TODO validate that checkin datetime is not in the past

        self.checkin_time = checkin_time
        return


    def get_confirmation_num(self):
        self.confirmation_num = pyip.inputStr(
            prompt='Confirmation #: ',
            blockRegexes=[r'.*'],
            allowRegexes=[r'^(\w{6})$']
            )
        return


    def get_ticket_name(self):
        name = pyip.inputStr(
            prompt='Reservation name: ',
            blockRegexes=[r'.*'],
            allowRegexes=[r'^[A-Za-z]+\s[A-Za-z]$']
            ).split()
        self.firstname = name[0]
        self.lastname = name[1]
        return


    def get_reservation(self):
        self.get_checkin_date()
        self.get_checkin_time()
        self.get_confirmation_num()
        self.get_ticket_name()


    def confirm_reservation(self):
        pass


def main():
    reservation = Reservation()
    reservation.get_reservation()
    reservation.confirm_reservation()
    return


main()
