# Copyright (c) 2004 gocept. All rights reserved.
# See also LICENSE.txt
# $Id: validators.py 29254 2009-02-21 19:14:24Z ctheune $

from Products.validation.interfaces.IValidator import IValidator
from config import COUNTRIES
import re

class CountryValidator:
    """country validator, checks if given value is in list
    of valid iso country codes.
    """
    __implements__ = (IValidator,)
    def __init__(self, name):
        self.name = name
    def __call__(self, value, *args, **kwargs):
        
        if value == '' or value in COUNTRIES.keys():
            return 1
        else:
            return """This is not a valid country ISO-Code."""


