import string
from turbogears import controllers, expose, flash, redirect
# from model import *
# import logging
# log = logging.getLogger("fosswallproxy.controllers")


LETTERS = string.ascii_uppercase
BASE_DIR = '/opt/falb/res'


class Base(controllers.RootController):
    pass


