# this is a cheap way of emulating file-type doctests (in Python 2.4 or ZopeTestCase)
"""
We will demonstrate usage of custom fields through the API. This is done in brief in
the supporters test.

First, set up::

 >>> from deminaction.rest import DIARest
 >>> from deminaction.rest import pythonize
 >>> rest = DIARest("enfoldsystems", "python")

We need a supporter upon which to set fields:

 >>> key_alice   = rest.setSupporter(Email="alice@enfoldssystems.com", First_Name="Alice", Last_Name="Liddell")

You can see that this is a demonstration of setting the standard fields; each keyword
param sets a field. We can see the standard fields that are available::

 >>> supporters = rest.getSupporters()
 >>> s = pythonize(supporters)
 >>> s[0].keys()
 [u'City', u'Last_Name', u'uid', u'Zip', u'Title', u'Web_Page', u'Department', u'State', u'Latitude', u'Other_Data_3', u'Source_Tracking_Code', u'Receive_Phone_Blasts', u'Email', u'Status', u'organization_KEY', u'Work_Phone', u'chapter_KEY', u'Instant_Messenger_Name', u'Phone', u'Source_Details', u'Other_Data_2', u'Soft_Bounce_Count', u'Cell_Phone', u'Pager', u'Notes', u'Work_Fax', u'Country', u'Region', u'Last_Bounce', u'Longitude', u'Tracking_Code', u'Last_Modified', u'key', u'Date_Created', u'Organization', u'Receive_Email', u'Other_Data_1', u'Phone_Provider', u'Alternative_Email', u'Home_Fax', u'First_Name', u'Password', u'Suffix', u'PRIVATE_Zip_Plus_4', u'Source', u'Timezone', u'MI', u'Hard_Bounce_Count', u'County', u'Instant_Messenger_Service', u'Street', u'Email_Preference', u'Email_Status', u'Street_2', u'Street_3', u'supporter_KEY', u'Occupation']

We can get even more info (like type, etc) with::

 rest.getSupporters(desc=1)

but that's not what we're lookin at yet.

The above call to 'setSupporter' created the supporter. Notice that the email addess above is wrong.
We will edit the existing record like so::

 >>> key_alice = rest.setSupporter(key=key_alice, Email="alice@enfoldsystems.com")

Let's take a look to be sure::

 >>> supporters = rest.getSupporters(column="Email")
 >>> s = pythonize(supporters)
 >>> [name["Email"] for name in s]
 [u'alice@enfoldsystems.com']

There is also another table that we can use for non-standard info. This table has a bunch of
general-purpose columns, like VARCHAR0..VARCHAR49, BOOL0..BOOL24, INTEGER0..INTEGER9 and so forth.
We can address these columns directly, or we can map them to a name.

Let's look at what mappings we have already (it should be empty)::

 >>> fields = rest.getCustomFieldMappings()
 >>> f = pythonize(fields)
 >>> f
 []

Let's add a mapping, and make sure that it's there::

 >>> varchar = rest.setCustomFieldMapping("VARCHAR0", "astring", Display_Name="A String")
 >>> fields = rest.getCustomFieldMappings()
 >>> f = pythonize(fields)
 >>> f.sort()
 >>> [(field['Name'], field['Display_Name'], field['READONLY_Database_Field']) for field in f]
 [(u'astring', u'A String', u'VARCHAR0')]

This one was a VARCHAR, a single line of text. We only set some of the fields about the mapping.
We can see the rest like::

  rest.getCustomFieldMappings(desc=1)

and also from the web UI.

Let's make an example of each of the different types of fields...

 * BOOL (boolean value)::

    >>> bool = rest.setCustomFieldMapping("BOOL0", "aboolean", Display_Name="A Boolean Value")

 * INTEGER (integer)::

    >>> integer = rest.setCustomFieldMapping("INTEGER0", "anint", Display_Name="An Integer")

 * BLOB (binary large object, probably a lot of text)::

    >>> blob = rest.setCustomFieldMapping("BLOB0", "ablob", Display_Name="A BLOB")

 * FL (floating point number, usually incl. currency)::

    >>> fl = rest.setCustomFieldMapping("FL0", "afloat", Display_Name="A Floating Point Number")

 * DATETIME (timestamp)::

    >>> dtime = rest.setCustomFieldMapping("DATETIME0", "adatetime", Display_Name="A Datetime value")

 * RADIO (multiple choice)::

    >>> radio = rest.setCustomFieldMapping("RADIO0", "aradio", Display_Name="A Radio Set", PRIVATE_Options="monkey,butter")

   The choices for the radio set are comma-separated in the PRIVATE_Options.

These entries describe pretty names for raw column names in a table that holds
our custom field data. We can pick this out from the 'READONLY_Database_Field'
entry, but we also have a method that does this for us::

 >>> col = rest.lookupCustomFieldMapping("astring")
 >>> col
 u'VARCHAR0'

But beware, since is also lets us ask for nonsense and doesn't provide an error::

 >>> rest.lookupCustomFieldMapping("nothing")
 'nothing'

This is for speed and flexibility, but it means you have to be sure of what you're
asking for.

Now let us look up the values of custom fields for our supporter::

 >>> pythonize(rest.getSupporterCustomFields(key_alice))
 []

It's empty, since we've never set any custom fields on this supporter before,
so let's set a value::

 >>> key = rest.setSupporterCustomField(key_alice, "astring", "I am the very model of a modern major general")

and see the change::

 >>> pythonize(rest.getSupporterCustomFields(key_alice))[0][col]
 u'I am the very model of a modern major general'

A few of the others are non-obvious. Booleans want either '0' or '1'::

 >>> col = rest.lookupCustomFieldMapping("aboolean")
 >>> key = rest.setSupporterCustomField(key_alice, "aboolean", 1)
 >>> pythonize(rest.getSupporterCustomFields(key_alice))[0][col]
 u'1'

DateTime is also non-obvious, but at this point, the web UI doesn't even set it, so I
can't say what the format should be.


This is the end, and we don't want to pollute the test environment,
so let's delete the custom fields::

 >>> xx = rest.delCustomFieldMapping(varchar)
 >>> xx = rest.delCustomFieldMapping(bool)
 >>> xx = rest.delCustomFieldMapping(integer)
 >>> xx = rest.delCustomFieldMapping(blob)
 >>> xx = rest.delCustomFieldMapping(fl)
 >>> xx = rest.delCustomFieldMapping(dtime)
 >>> xx = rest.delCustomFieldMapping(radio)
 >>> len(pythonize(rest.getCustomFieldMappings()))
 0

and supporter::

 >>> some_html = rest.delSupporter(key_alice)
 >>> len(pythonize(rest.getSupporters()))
 0

That's all folks.
"""
if __name__ == "__main__":
    import doctest
    doctest.testmod()