# Copyright (c) 2004 gocept. All rights reserved.
# See also LICENSE.txt
# $Id: TestWidget.py 29254 2009-02-21 19:14:24Z ctheune $

from Products.Archetypes.public import BaseSchema, Schema
from Products.Archetypes.public import StringField
from Products.Archetypes.public import BaseContent, registerType
from Products.CMFCore import CMFCorePermissions
#from Products.ATCountryWidget.config import PROJECTNAME


from Products.ATCountryWidget.Widget import CountryWidget


schema =  BaseSchema + Schema ((
    StringField(
        'country',
        required=1,
        widget=CountryWidget(label='Country',
                             description='Select a country.')
    ),
))



class TestCountryWidget(BaseContent):
    """blah
    """
    schema = schema
    archetypes_name = portal_type = meta_type='TestCountryWidget'

    
registerType(TestCountryWidget)


