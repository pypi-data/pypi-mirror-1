# this is a cheap way of emulating file-type doctests (in Python 2.4 or ZopeTestCase)
"""
To work with the "Events" section, first we must have a PythonDIA 'DIARest' object.
We have an account called 'enfoldsystems' for our unit tests, which should start out empty.
If the tests fail, take a look, and if it is not empty, make it so.

First, we make the connection object::

 >>> from deminaction.rest import DIARest
 >>> rest = DIARest("enfoldsystems", "python")

Once we have it, we can start asking it about events. Here we get a list of all::

 >>> events = rest.getEvents()

We expect back some XML telling us that it's empty (but it doesn't really matter just what.)

We can use 'pythonize' to get more reasonable data structures. If we run it on this,
it will tell us no records were returned by returning an empty list::

 >>> from deminaction.rest import pythonize
 >>> c = pythonize(events)
 >>> c
 []

We need some events to work with. We can say::

 >>> key_python = rest.setEvent(Address="6100 Main St", City="Houston", State="TX", Event_Name="Python meetup")
 >>> key_moon   = rest.setEvent(Address="Mare Tranquilatus", City="Light Side", State="LU", Event_Name="Moon landing")
 >>> key_boring = rest.setEvent(Address="1230 Elm St", City="Nowheresville", State="AI", Event_Name="Boring fundraiser")

We can pass as parameters any of the standard fields for this table. You can see these by saying::

 rest.getEvents(desc=1)

but we'll just stick to the basics for the moment. Let's take a look at the events we created::

 >>> events = rest.getEvents()

This returns XML, so we can look at it with XML tools::

 >>> from xml.dom import minidom
 >>> dom = minidom.parseString(events)
 >>> len(dom.getElementsByTagName("item"))
 3
 >>> items = [item.getElementsByTagName("Event_Name")[0].childNodes for item in dom.getElementsByTagName("item")]
 >>> l = [item[0].nodeValue for item in items if item]
 >>> l.sort()
 >>> l
 [u'Boring fundraiser', u'Moon landing', u'Python meetup']

But the DOM interface is a pain. We can use 'pythonize' to get Python standard data structures::

 >>> i = pythonize(events)
 >>> l = [elt["Event_Name"] for elt in i]
 >>> l.sort()
 >>> l
 [u'Boring fundraiser', u'Moon landing', u'Python meetup']

Here's another way to see the available fields::

 >>> i[0].keys()
 [u'City', u'Request_Additional_Attendees', u'End', u'Zip', u'One_Column_Layout', u'Event_Name', u'groups_KEYS', u'Start', u'State', u'Contact_Email', u'Maximum_Attendees', u'chapter_KEY', u'event_KEY', u'PRIVATE_trigger', u'Status', u'email_trigger_KEYS', u'organization_KEY', u'Header', u'Footer', u'Automatically_add_to_Groups', u'merchant_account_KEY', u'This_Event_Costs_Money', u'Address', u'Directions', u'redirect_path', u'Recurrence_Interval', u'Ticket_Price', u'Class', u'Default_Tracking_Code', u'distributed_event_KEY', u'PRIVATE_Required_Custom_Fields', u'Required', u'Request', u'Last_Modified', u'Display_to_Chapters', u'key', u'Description', u'Guests_allowed', u'PRIVATE_Zip_Plus_4', u'Recurrence_Frequency', u'national_event_KEY', u'PRIVATE_Custom_Fields', u'Map_URL', u'Date_Created', u'supporter_KEY']

When we do a set on an existing campaign, we just pass in the key, and the values from the params are changed::

 >>> key_boring = rest.setEvent(key=key_boring, Event_Name="REALLY boring fundraiser")

Let's do a search that returns only names::

 >>> events = rest.getEvents(column="Event_Name")
 >>> i = pythonize(events)
 >>> i[0].keys()
 [u'Event_Name', u'event_KEY', u'key']
 >>> l = [name["Event_Name"] for name in i]
 >>> l.sort()
 >>> l
 [u'Moon landing', u'Python meetup', u'REALLY boring fundraiser']

We can also do other queries, like look for a specific key::

 >>> events = rest.getEvents(key=key_python)
 >>> i = pythonize(events)
 >>> i[0]["State"], i[0]["City"]
 (u'TX', u'Houston')

We can ask for several keys with comma separation::

 >>> events = rest.getEvents(key=",".join((key_python,key_boring)))
 >>> i = pythonize(events)
 >>> l = [elt["Event_Name"] for elt in i]
 >>> l.sort()
 >>> l
 [u'Python meetup', u'REALLY boring fundraiser']

We can limit::

 >>> events = rest.getEvents(key=",".join((key_python,key_boring)), limit=1)
 >>> i = pythonize(events)
 >>> len([elt["Event_Name"] for elt in i])
 1

And change order::

 >>> events = rest.getEvents(key=",".join((key_python,key_boring)), order="State")
 >>> i = pythonize(events)
 >>> [(elt["Event_Name"],elt["State"]) for elt in i]
 [(u'REALLY boring fundraiser', u'AI'), (u'Python meetup', u'TX')]

You can do other things with the 'where' param, which basically takes SQL::

 >>> events = rest.getEvents(where='Event_Name="Moon landing"')
 >>> i = pythonize(events)
 >>> [(elt["Event_Name"],elt["State"]) for elt in i]
 [(u'Moon landing', u'LU')]

We don't want to pollute the test environment, so let's delete the events::

 >>> some_html = rest.delEvent(key_python)
 >>> some_html = rest.delEvent(key_moon)
 >>> some_html = rest.delEvent(key_boring)
 >>> len(pythonize(rest.getEvents()))
 0

That's it!
"""
if __name__ == "__main__":
    import doctest
    doctest.testmod()