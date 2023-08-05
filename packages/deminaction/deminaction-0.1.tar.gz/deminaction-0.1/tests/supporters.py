# this is a cheap way of emulating file-type doctests (in Python 2.4 or ZopeTestCase)
"""
To work with the "Supporters" section, first we must have a PythonDIA 'DIARest' object.
We have an account called 'enfoldsystems' for our unit tests, which should start out empty.
If the tests fail, take a look, and if it is not empty, make it so.

First, we make the connection object::

 >>> from deminaction.rest import DIARest
 >>> rest = DIARest("enfoldsystems", "python")

Once we have it, we can start asking it about supporters. Here we get a list of all::

 >>> supporters = rest.getSupporters()

We expect back some XML telling us that it's empty (but it doesn't really matter just what.)

We can use 'pythonize' to get more reasonable data structures. If we run it on this,
it will tell us no records were returned by returning an empty list::

 >>> from deminaction.rest import pythonize
 >>> s = pythonize(supporters)
 >>> s
 []

We need some supporters to work with. We can say::

 >>> key_alice   = rest.setSupporter(Email="alice@enfoldsystems.com", First_Name="Alice", Last_Name="Liddell")
 >>> key_bob     = rest.setSupporter(Email="bob@enfoldsystems.com", First_Name="Bob", Last_Name="Bobster")
 >>> key_charlie = rest.setSupporter(Email="charlie@enfoldsystems.com", First_Name="Charlie", Last_Name="Daniels")

We can pass as parameters any of the standard fields for this table. You can see these by saying::

 rest.getSupporters(desc=1)

but we'll just stick to the basics for the moment. Let's take a look at the supporters we created::

 >>> supporters = rest.getSupporters()

This returns XML, so we can look at it with XML tools::

 >>> from xml.dom import minidom
 >>> dom = minidom.parseString(supporters)
 >>> len(dom.getElementsByTagName("item"))
 3
 >>> names = [supporter.getElementsByTagName("First_Name")[0].childNodes for supporter in dom.getElementsByTagName("item")]
 >>> [name[0].nodeValue for name in names if name]
 [u'Alice', u'Bob', u'Charlie']

But the DOM interface is a pain. We can use 'pythonize' to get Python standard data structures::

 >>> s = pythonize(supporters)
 >>> [name["First_Name"] for name in s]
 [u'Alice', u'Bob', u'Charlie']

Here's another way to see the available fields::

 >>> s[0].keys()
 [u'City', u'Last_Name', u'uid', u'Zip', u'Title', u'Web_Page', u'Department', u'State', u'Latitude', u'Other_Data_3', u'Source_Tracking_Code', u'Receive_Phone_Blasts', u'Email', u'Status', u'organization_KEY', u'Work_Phone', u'chapter_KEY', u'Instant_Messenger_Name', u'Phone', u'Source_Details', u'Other_Data_2', u'Soft_Bounce_Count', u'Cell_Phone', u'Pager', u'Notes', u'Work_Fax', u'Country', u'Region', u'Last_Bounce', u'Longitude', u'Tracking_Code', u'Last_Modified', u'key', u'Date_Created', u'Organization', u'Receive_Email', u'Other_Data_1', u'Phone_Provider', u'Alternative_Email', u'Home_Fax', u'First_Name', u'Password', u'Suffix', u'PRIVATE_Zip_Plus_4', u'Source', u'Timezone', u'MI', u'Hard_Bounce_Count', u'County', u'Instant_Messenger_Service', u'Street', u'Email_Preference', u'Email_Status', u'Street_2', u'Street_3', u'supporter_KEY', u'Occupation']

When we do a set on an existing user, we just pass in the key, and the values from the params are changed::

 >>> key_bob = rest.setSupporter(key=key_bob, Email="bobster@enfoldsystems.com")

Let's do a search that returns only email addresses::

 >>> supporters = rest.getSupporters(column="Email")
 >>> s = pythonize(supporters)
 >>> s[0].keys()
 [u'supporter_KEY', u'key', u'Email']
 >>> [name["Email"] for name in s]
 [u'alice@enfoldsystems.com', u'bobster@enfoldsystems.com', u'charlie@enfoldsystems.com']

We can also do other queries, like look for a specific key::

 >>> supporters = rest.getSupporters(key=key_alice)
 >>> s = pythonize(supporters)
 >>> s[0]["First_Name"], s[0]["Last_Name"]
 (u'Alice', u'Liddell')

We can ask for several keys with comma separation::

 >>> supporters = rest.getSupporters(key=",".join((key_alice,key_bob)))
 >>> s = pythonize(supporters)
 >>> [name["Last_Name"] for name in s]
 [u'Liddell', u'Bobster']

We can limit::

 >>> supporters = rest.getSupporters(key=",".join((key_alice,key_bob)), limit=1)
 >>> s = pythonize(supporters)
 >>> [name["Last_Name"] for name in s]
 [u'Liddell']

And change order::

 >>> supporters = rest.getSupporters(key=",".join((key_alice,key_bob)), order="Last_Name")
 >>> s = pythonize(supporters)
 >>> [name["Last_Name"] for name in s]
 [u'Bobster', u'Liddell']

You can do other things with the 'where' param, which basically takes SQL::

 >>> supporters = rest.getSupporters(where='Email="alice@enfoldsystems.com"')
 >>> s = pythonize(supporters)
 >>> s[0]["First_Name"], s[0]["Last_Name"], s[0]["Email"]
 (u'Alice', u'Liddell', u'alice@enfoldsystems.com')

We can also use custom fields. In the 'supporter_custom' table we have a great many
generic columns available to use. See http://trac.democracyinaction.org/wiki/API/CustomFields
We can map these generic names (like VARCHAR21) to pretty names that we can use in a UI.

Let's look at what mappings we have already (it should be empty)::

 >>> fields = rest.getCustomFieldMappings()
 >>> f = pythonize(fields)
 >>> f
 []

Let's add a mapping, and make sure that it's there::

 >>> x = rest.setCustomFieldMapping("VARCHAR21", "acustomfield", Display_Name="A Custom Field")
 >>> w = rest.setCustomFieldMapping("VARCHAR20", "anotherfield", Display_Name="Another Custom Field")
 >>> fields = rest.getCustomFieldMappings()
 >>> f = pythonize(fields)
 >>> f.sort()
 >>> [(field['Name'], field['Display_Name'], field['READONLY_Database_Field']) for field in f]
 [(u'acustomfield', u'A Custom Field', u'VARCHAR21'), (u'anotherfield', u'Another Custom Field', u'VARCHAR20')]

We can delete as usual::

 >>> xx = rest.delCustomFieldMapping(x)
 >>> pythonize(rest.getCustomFieldMappings(key=x))
 []

These entries describe pretty names for raw column names in a table that holds
our custom field data. We can pick this out from the 'READONLY_Database_Field'
entry, but we also have a method that does this for us::

 >>> col = rest.lookupCustomFieldMapping("anotherfield")
 >>> col
 u'VARCHAR20'


This tells us that when we want to work with the custom field 'Nmber of friends'
we're actually dealing with the 'INTEGER6' column. Now, if we give this method
any value that it can't map, it'll give it right back to us. This lets us ask
for the actual column names::

 >>> rest.lookupCustomFieldMapping("VARCHAR0")
 'VARCHAR0'

But beware, since is also lets us ask for nonsense and doesn't provide an error::

 >>> rest.lookupCustomFieldMapping("nothing")
 'nothing'

This is for speed and flexibility, but it means you have to be sure of what you're
asking for.

Now that we have a column name, we can look up the value for our supporter::

 >>> pythonize(rest.getSupporterCustomFields(key_alice))
 []

It's empty, since we've never set any custom fields on this supporter before,
so let's set a value::

 >>> res = rest.setSupporterCustomField(key_alice, "anotherfield", "I am the very model of a modern major general")
 

and see the change::

 >>> pythonize(rest.getSupporterCustomFields(key_alice))[0][col]
 u'I am the very model of a modern major general'

This is the end of the test, and we don't want to pollute the test environment,
so let's delete the custom field::

 >>> xx = rest.delCustomFieldMapping(w)
 >>> len(pythonize(rest.getCustomFieldMappings()))
 0

and supporters::

 >>> some_html = rest.delSupporter(key_alice)
 >>> some_html = rest.delSupporter(key_bob)
 >>> some_html = rest.delSupporter(key_charlie)
 >>> len(pythonize(rest.getSupporters()))
 0

That's it!
"""
if __name__ == "__main__":
    import doctest
    doctest.testmod()