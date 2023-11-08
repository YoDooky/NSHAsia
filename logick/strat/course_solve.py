import time

from selenium.webdriver import ActionChains
import logging

from exceptions import QuizEnded, NoFoundedElement
from log import print_log
from aux_functions import AuxFunc
from driver_init import driver
from web.xpaths import XpathResolver

from logick import strat, question_solve


class CourseStrategy:

    def main(self):
