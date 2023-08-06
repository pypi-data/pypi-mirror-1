A country widget for Archetypes

Adds a new tool, ``portal_countryutil`` to the Plone root, which lets
you manage a list of areas which may contain several countries from the
official ISO-country list via the ZMI.  A complete list of areas and
their countries is being created at install time.

Provides three widgets which you can use in your own Archetype:

CountryWidget
  the areas and countries defined in the country tool are then rendered as a dropdown (with <optgroup>).

AreaWidget
  provides a dropdown with all areas you have defined.
  
MultiCountryWidget
  for use with LinesField, lets you select multiple countries


Examples
--------

Here is some code that demonstrates how to use those widgets::

    ---- YourArcheType.py ----

    # Import the widget/s:
    from Products.ATCountryWidget.Widget import CountryWidget, AreaWidget

    # Define the field/s in your schema:
    [...]

     StringField(
        'country',
        validators=('isValidISOCountry',),
        widget=CountryWidget(label='Country',
                             provideNullValue=1,   # this is default
                             nullValueTitle='-',   # this is default
                             omitCountries=None,   # this is default, can be a 
                                                   # list of country codes which 
                                                   # are not displayed
                             description='Select a country')
     ),

    [... and/or ...]

     StringField(
        'area',
        widget=AreaWidget(label='Area',
                          provideNullValue=1,      # this is default
                          nullValueTitle='-',      # this is default
                          description='Select an area')
     ),

    [... and/or ...]

     LinesField(
        'countries',
        widget=MultiCountryWidget(label='Countries',
                             omitCountries=None,   # this is default, can be a 
                                                   # list of country codes which 
                                                   # are not displayed
                             description='Select countries')
     ),

    [...]


Use without Archetypes
----------------------

To use your countrylist in a custom page template outside of an
Archetype (e.g. in a search form) you can directly use the API the
country tool provides::

   <select tal:define="countrytool here/portal_countryutils">
     <option>Choose...</option>
     <optgroup
         label="Western Europe"
         tal:repeat="area countrytool/listAreas"
         tal:attributes="label area/name">
       <option
         value="DE"
         tal:repeat="country area/countries"
         tal:content="country/name"
         tal:attributes="value country/isocc">Germany
       </option>
     </optgroup>
   </select>

For more details on how to customize content-types, add custom fields to
content-types, see Martin's tutorial:
http://plone.org/documentation/how-to/adding-new-fields-to-smart-folders-search/documentation/tutorial/richdocument/extending-atct
