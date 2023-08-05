# this is a cheap way of emulating file-type doctests (in Python 2.4 or ZopeTestCase)
"""
This test is to deliberately provoke bad XML from the remote service. This was originally
a problem. It should pass now.

We'll set up as usual::

 >>> from deminaction.rest import DIARest
 >>> rest = DIARest("demo", "demo")

Broken XML: we will provoke mal-formed XML (because of HTML snippets not CDATA encoded or cleaned up).
This easily comes from the UI::

 >>> val = rest.setCampaign(Campaign_Title="Island Hopping", Description="<br>")
 >>> campaigns = rest.getCampaigns(where='Campaign_Title="Island Hopping"')
 >>>
 >>> from xml.dom import minidom
 >>> dom = None
 >>> dom = minidom.parseString(campaigns)

(We expect here a traceback for ExpatError.)

Output problem if exception occured::

 >>> if not dom: print campaigns
 ...

And clean up. We must have a query that leaves out the broken field in order to pythonize::

 >>> campaigns = rest.getCampaigns(where='Campaign_Title="Island Hopping"', column="Campaign_Title")
 >>> from deminaction.rest import pythonize
 >>> s = pythonize(campaigns)
 >>> key = s[0]["campaign_KEY"]
 >>> some_html = rest.delCampaign(key)

"""
if __name__ == "__main__":
    import doctest
    doctest.testmod()