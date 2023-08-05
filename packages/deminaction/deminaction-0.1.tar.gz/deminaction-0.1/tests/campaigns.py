# this is a cheap way of emulating file-type doctests (in Python 2.4 or ZopeTestCase)
"""
To work with the "Campaigns" section, first we must have a PythonDIA 'DIARest' object.
We have an account called 'enfoldsystems' for our unit tests, which should start out empty.
If the tests fail, take a look, and if it is not empty, make it so.

First, we make the connection object::

 >>> from deminaction.rest import DIARest
 >>> rest = DIARest("enfoldsystems", "python")

Once we have it, we can start asking it about campaigns. Here we get a list of all::

 >>> campaigns = rest.getCampaigns()

We expect back some XML telling us that it's empty (but it doesn't really matter just what.)

We can use 'pythonize' to get more reasonable data structures. If we run it on this,
it will tell us no records were returned by returning an empty list::

 >>> from deminaction.rest import pythonize
 >>> c = pythonize(campaigns)
 >>> c
 []

We need some campaigns to work with. We can say::

 >>> key_winter  = rest.setCampaign(Campaign_Title="Winter", Description="Do you understand?")
 >>> key_pacific = rest.setCampaign(Campaign_Title="Pacific", Description="Island Hopping")
 >>> key_repeal  = rest.setCampaign(Campaign_Title="Repeal 1st", Description="Repeal the 1st Amendment")

We can pass as parameters any of the standard fields for this table. You can see these by saying::

 rest.getCampaigns(desc=1)

but we'll just stick to the basics for the moment. Let's take a look at the campaigns we created::

 >>> campaigns = rest.getCampaigns()

This returns XML, so we can look at it with XML tools::

 >>> from xml.dom import minidom
 >>> dom = minidom.parseString(campaigns)
 >>> len(dom.getElementsByTagName("item"))
 3
 >>> items = [item.getElementsByTagName("Campaign_Title")[0].childNodes for item in dom.getElementsByTagName("item")]
 >>> l = [item[0].nodeValue for item in items if item]
 >>> l.sort()
 >>> l
 [u'Pacific', u'Repeal 1st', u'Winter']

But the DOM interface is a pain. We can use 'pythonize' to get Python standard data structures::

 >>> c = pythonize(campaigns)
 >>> l = [camp["Campaign_Title"] for camp in c]
 >>> l.sort()
 >>> l
 [u'Pacific', u'Repeal 1st', u'Winter']

Here's another way to see the available fields::

 >>> c[0].keys()
 [u'Suppress_Automatic_Response_Email', u'Reference_Name', u'Max_Number_Of_Emails', u'groups_KEYS', u'Suggested_Subject', u'photo_KEY', u'Learn_More_Link', u'roll_call_ID', u'Letter_Salutation', u'Thank_You_Page_Text_or_HTML', u'Status', u'recipient_KEYS', u'exclude_person_legislator_IDS', u'organization_KEY', u'Excluded_Recipient_Text', u'chapter_KEY', u'Sponsorship_Link', u'Alternate_Description', u'Success_Message', u'Hide_Keep_Me_Informed', u'Campaign_Title', u'Restricted_Districts', u'redirect_path', u'person_legislator_IDS', u'READONLY_Hit_Count', u'campaign_KEY', u'Restricted_Regions', u'rep_KEYS', u'Allow_Emails', u'Alternate_Content', u'Default_Tracking_Code', u'Footer', u'PRIVATE_trigger', u'Alternate_Subject', u'No_Recipient_Text', u'Suggested_Content', u'exclude_rep_KEYS', u'Roll_Call_Vote', u'Last_Modified', u'key', u'Restricted_Text', u'Letter_cannot_be_Edited', u'Description', u'Allow_Faxes', u'email_trigger_KEYS', u'Subject_cannot_be_Edited', u'Spread_The_Word_Redirect_Path', u'Enable_Preview', u'PRIVATE_Emails_Sent', u'PRIVATE_Faxes_Sent', u'Spread_The_Word_Text', u'recipient_group_KEYS', u'Max_Number_Of_Faxes', u'PRIVATE_Recent_Update', u'Archive', u'Date_Created', u'Preview_Text', u'Brief_Summary', u'Hide_Message_Type_Options', u'More_Info']

When we do a set on an existing campaign, we just pass in the key, and the values from the params are changed::

 >>> key_winter = rest.setCampaign(key=key_winter, Description="Napoleon, right?")

Let's do a search that returns only descriptions::

 >>> campaigns = rest.getCampaigns(column="Description")
 >>> c = pythonize(campaigns)
 >>> c[0].keys()
 [u'campaign_KEY', u'key', u'Description']
 >>> l = [name["Description"] for name in c]
 >>> l.sort()
 >>> l
 [u'Island Hopping', u'Napoleon, right?', u'Repeal the 1st Amendment']

We can also do other queries, like look for a specific key::

 >>> campaigns = rest.getCampaigns(key=key_winter)
 >>> c = pythonize(campaigns)
 >>> c[0]["Campaign_Title"], c[0]["Description"]
 (u'Winter', u'Napoleon, right?')

We can ask for several keys with comma separation::

 >>> campaigns = rest.getCampaigns(key=",".join((key_winter,key_pacific)))
 >>> c = pythonize(campaigns)
 >>> [camp["Campaign_Title"] for camp in c]
 [u'Winter', u'Pacific']

We can limit::

 >>> campaigns = rest.getCampaigns(key=",".join((key_winter,key_pacific)), limit=1)
 >>> c = pythonize(campaigns)
 >>> [camp["Campaign_Title"] for camp in c]
 [u'Winter']

And change order::

 >>> campaigns = rest.getCampaigns(key=",".join((key_winter,key_pacific)), order="Campaign_Title")
 >>> c = pythonize(campaigns)
 >>> [camp["Campaign_Title"] for camp in c]
 [u'Pacific', u'Winter']

You can do other things with the 'where' param, which basically takes SQL::

 >>> campaigns = rest.getCampaigns(where='Campaign_Title="Repeal 1st"')
 >>> c = pythonize(campaigns)
 >>> [camp["Campaign_Title"] for camp in c]
 [u'Repeal 1st']

We don't want to pollute the test environment, so let's delete the campaigns::

 >>> some_html = rest.delCampaign(key_winter)
 >>> some_html = rest.delCampaign(key_pacific)
 >>> some_html = rest.delCampaign(key_repeal)
 >>> pythonize(rest.getCampaigns())
 []

That's it!
"""
if __name__ == "__main__":
    import doctest
    doctest.testmod()