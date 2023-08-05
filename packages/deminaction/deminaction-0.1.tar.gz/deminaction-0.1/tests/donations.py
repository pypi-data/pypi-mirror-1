# this is a cheap way of emulating file-type doctests (in Python 2.4 or ZopeTestCase)
"""
To work with the "Donations" section, first we must have a PythonDIA 'DIARest' object.
We have an account called 'enfoldsystems' for our unit tests, which should start out empty,
but we can't delete donations, so we have to expect some handing around.

First, we make the connection object::

 >>> from deminaction.rest import DIARest
 >>> rest = DIARest("enfoldsystems", "python")

Once we have it, we can start asking it about donations. Here we get a list of all::

 >>> donations = rest.getDonations()

We can use 'pythonize' to get more reasonable data structures. If we run it on this,
it will sort and make into a list of dicts for the records returned. We'll count them
so we can see it increase later.

 >>> from deminaction.rest import pythonize
 >>> c = pythonize(donations)
 >>> v = len(c)

Let's create some donations to work with. We can say::

 >>> key200 = rest.setDonation(Transaction_Type="Donation", amount="200", Form_Of_Payment="Check", Donation_Tracking_Code="asd")
 >>> key20  = rest.setDonation(Transaction_Type="Donation", amount="20", Form_Of_Payment="Cash", Donation_Tracking_Code="2345")
 >>> key1   = rest.setDonation(Transaction_Type="Donation", amount="1", Form_Of_Payment="Check", Donation_Tracking_Code="FFRE")

We can pass as parameters any of the standard fields for this table. You can see these by saying::

 rest.getDonations(desc=1)

but we'll just stick to the basics for the moment. Let's take a look at the donations we created::

 >>> donations = rest.getDonations()

This returns XML, so we can look at it with XML tools::

 >>> from xml.dom import minidom
 >>> dom = minidom.parseString(donations)
 >>> len(dom.getElementsByTagName("item")) - 3 == v
 True
 >>> items = [item.getElementsByTagName("amount")[0].childNodes for item in dom.getElementsByTagName("item")]
 >>> [item[0].nodeValue for item in items if item][:3]
 [u'200.00', u'20.00', u'10.00']

But the DOM interface is a pain. We can use 'pythonize' to get Python standard data structures::

 >>> i = pythonize(donations)
 >>> len(i) - 3 == v
 True
 >>> [elt["amount"] for elt in i][:3]
 [u'200.00', u'20.00', u'10.00']

Here's another way to see the available fields::

 >>> i[0].keys()
 [u'In_Honor_Address', u'Credit_Card_Expiration', u'Last_Name', u'uid', u'recurring_donation_KEY', u'Note', u'VARCHAR0', u'donation_KEY', u'VARCHAR2', u'Responsible_Party', u'Transaction_Type', u'chapter_KEY', u'event_KEY', u'Status', u'Date_Entered', u'organization_KEY', u'Thank_Date', u'AUTHCODE', u'membership_invoice_KEY', u'RESPMSG', u'Email', u'Donation_Tracking_Code', u'Tax_Status', u'Transaction_Date', u'merchant_account_KEY', u'PRIVATE_Complete_Summary', u'Designation_Code', u'Date_Fulfilled', u'referral_supporter_KEY', u'In_Honor_Name', u'Batch_Code', u'Order_Info', u'cc_type', u'Tracking_Code', u'Last_Modified', u'RESULT', u'key', u'Thank_You_Sent', u'VARCHAR1', u'Form_Of_Payment', u'IP_Address', u'Credit_Card_Digits', u'First_Name', u'AVS', u'amount', u'In_Honor_Email', u'PNREF', u'PRIVATE_Donation_Source', u'supporter_KEY']

When we do a set on an existing campaign, we just pass in the key, and the values from the params are changed::

 >>> key1 = rest.setDonation(key=key1, amount="10")

Let's do a search that returns only amounts::

 >>> donations = rest.getDonations(column="amount")
 >>> i = pythonize(donations)
 >>> i[0].keys()
 [u'donation_KEY', u'amount', u'key']
 >>> l = [elt["amount"] for elt in i]
 >>> l[:3]
 [u'200.00', u'20.00', u'10.00']

We can also do other queries, like look for a specific key::

 >>> donations = rest.getDonations(key=key20)
 >>> i = pythonize(donations)
 >>> i[0]["amount"], i[0]["Transaction_Type"]
 (u'20.00', u'Donation')

We can ask for several keys with comma separation::

 >>> donations = rest.getDonations(key=",".join((key1,key20)))
 >>> i = pythonize(donations)
 >>> l = [elt["amount"] for elt in i]
 >>> l.sort()
 >>> l
 [u'10.00', u'20.00']

We can limit::

 >>> donations = rest.getDonations(key=",".join((key1,key20)), limit=1)
 >>> i = pythonize(donations)
 >>> len([elt["amount"] for elt in i])
 1

And change order::

 >>> donations = rest.getDonations(key=",".join((key20,key1)), order="Donation_Tracking_Code")
 >>> i = pythonize(donations)
 >>> [(elt["amount"],elt["Donation_Tracking_Code"]) for elt in i]
 [(u'20.00', u'2345'), (u'10.00', u'FFRE')]

You can do other things with the 'where' param, which basically takes SQL::

 >>> donations = rest.getDonations(where='Donation_Tracking_Code="asd"')
 >>> i = pythonize(donations)
 >>> l = [(elt["amount"],elt["Donation_Tracking_Code"]) for elt in i]
 >>> len(l) > 1
 True

Normally we wouldn't want to pollute the test environment, and delete the donations::

 some_html = rest.delCampaign(key1)
 some_html = rest.delCampaign(key20)
 some_html = rest.delCampaign(key200)
 len(pythonize(rest.getDonations()))
 0

but donation deletion doesn't work. Oh well.

That's it!
"""
if __name__ == "__main__":
    import doctest
    doctest.testmod()