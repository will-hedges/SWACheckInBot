#! python3
# southwest_checkin.py - DESCRIPTION


from datetime import date
import logging
import time

import pyinputplus as pyip
from selenium import webdriver


logging.basicConfig(
    level=logging.DEBUG,
    format=' %(levelname)s - %(message)s'
    )
# logging.disable(logging.CRITICAL)

class Reservation():

    def __init__(self):
        self.current_year = date.today().year
        return


    def get_checkin_date(self):
        checkin_date = pyip.inputDate(
            prompt='Check-in date (MM/DD): ',
            formats=['%m/%d']
            )
        checkin_date = date(self.current_year, checkin_date.month, checkin_date.day)
        self.checkin_date = checkin_date
        return


    def get_checkin_time(self):
        checkin_time = pyip.inputTime(
            prompt='Check-in time (HH:MM AM/PM): ',
            formats=['%I:%M %p']
            )
        self.checkin_time = checkin_time
        return


    def get_confirmation(self):
        confirmation = pyip.inputStr(prompt='Confirmation number: ')
        self.confirmation = confirmation
        return


    def get_ticket_name(self):
        name = pyip.inputStr(prompt='Reservation name: ').split()
        self.firstname = name[0]
        self.lastname = name[1]
        return


    def get_reservation(self):
        self.get_checkin_date()
        self.get_checkin_time()
        self.get_confirmation()
        self.get_ticket_name()


    def confirm_reservation(self):
        # TODO review all stored variables
        pass


def main():
    reservation = Reservation()
    reservation.get_reservation()
    reservation.confirm_reservation()
    return


main()
