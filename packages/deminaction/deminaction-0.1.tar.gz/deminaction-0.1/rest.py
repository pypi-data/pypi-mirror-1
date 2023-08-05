"""Wrapper around the DIA REST API. Could I possibly use any more acronyms?

Provides named methods for the different functions. It would be easy to have only
a single method for each get or set (passing in a constant) but there are a few
special cases that justify specific methods.

See:
  http://data.demaction.org/wiki/space/Developer+Documentation/APIs/Getting+Data
"""
from config import API_GET_URL, API_SET_URL, API_DEL_URL

import httplib, urllib, urlparse
from xml.parsers.expat import ExpatError
from xml.dom import minidom

TABLE_SUPPORTER = "supporter"
TABLE_SUPPORTER_CUSTOM = "supporter_custom"
TABLE_CUSTOM_FIELDS = "custom_field"
TABLE_CAMPAIGN = "campaign"
TABLE_DONATION = "donation"
TABLE_EVENT = "event"

class DIARest:
    """Using appropriate GETs and POSTs, interacts with the DIA system.
    This system is stateless, so you may instantiate as many as you want;
    however, you should not need more than one.
    """

    def __init__(self, userid, passwd):
        """Construct an instance; you must provide your username and password.
        There is the potential that the external key could work as well, but this
        is not supported.
        """
        self.username = userid
        self.password = passwd

    def _doGet(self, table, url=API_GET_URL, **kw):
        """Private helper to do a get against a specific URL. (Defaults to global 'get' url.)
        If you pass 'user' or 'password' as keyword params, they will over-ride the defaults,
        which come from the instance.

        Returns the content of the RESPONSE.
        """
        if not kw.get('user'): kw['user'] = self.username
        if not kw.get('password'): kw['password'] = self.password
        kw['table'] = table
        for key, value in kw.items():
            if value is None: del kw[key]

        loc, host, path, params, query, frag = urlparse.urlparse(url)
        query = urllib.urlencode(kw)
        getPath = "%s?%s" % (path, query)

        #f = open("/tmp/urllog", 'a')
        #f.write(getPath+"\n")
        #f.close()

        headers = {'Accept': ('text/plain', 'text/html', 'text/xml')}

        conn = httplib.HTTPConnection(host)
        conn.request('GET', getPath)
        response = conn.getresponse()
	retval = response.read()
        if conn is not None:
            conn.close()

	if response.status == 301:
		location = [header for header in response.msg.headers 
		               if header.startswith('Location: ')][0]
		newloc = location.split('Location: ')[1]
		raise NotImplementedError, "Redirects not implemented, %s" % newloc

        return retval

    def _cleanKW(self, key, column, order, limit, where, kw):
        """For the predefined kw args, don't include them if they're not supplied.
        Returns 'kw' with all the non-false args included.
        Helper method.
        """
        if key: kw["key"] = key
        if column: kw["column"] = column
        if order: kw["order"] = order
        if limit: kw["limit"] = limit
        if where: kw["where"] = where
        return kw

    def getOrgKey(self):
        """Return the organization_KEY value for the organization connected to this login."""
        # Kind of a strange method, but it works until I figure out a more normal way
        error = self.getCampaigns(key="asdffggsdfg")
        try:
            dom = minidom.parseString(error)
        except ExpatError:
            dom = minidom.parseString(error + "</data>")   # currently returns a broken doc, but don't rely on that
        data = dom.getElementsByTagName("data")[0]
        retval = data.getAttribute("organization_KEY")
        dom.unlink()
        return retval

    def getSupporters(self, key=None, column=None, order=None, limit=None, where=None, **kw):
        """Return a list of supporters. Provide parameters for tighter search. Empty parameters for all.
        Param 'key' takes a supporter key or multiple keys, comma-separated, of supporters to return.
        Param 'column' also takes comma-separated values.

        Columns for use with 'column' are any of the fields in an 'item' in the return, and can
        also be described with passing a 'desc' argument.
        http://api.demaction.org/dia/api/get.jsp?user=demo&password=demo&table=supporter&desc

        Returns an XML list of supporters, suitable for parsing. Each supporter is inside an 'item'.
        If you don't want to work directly with the xml, use 'pythonize'.
        """
        kw = self._cleanKW(key, column, order, limit, where, kw)
        return self._doGet(TABLE_SUPPORTER, **kw)

    def getCampaigns(self, key=None, column=None, order=None, limit=None, where=None, **kw):
        """Return a list of campaigns. Provide parameters for tighter search. Empty parameters for all.
        Param 'key' takes a campaign key or multiple keys, comma-separated, of supporters to return.
        Param 'column' also takes comma-separated values.

        Columns for use with 'column' are any of the fields in an 'item' in the return, and can
        also be described with passing a 'desc' argument.
        http://api.demaction.org/dia/api/get.jsp?user=demo&password=demo&table=campaign&desc

        Returns an XML list of campaigns, suitable for parsing. Each supporter is inside an 'item'.
        If you don't want to work directly with the xml, use 'pythonize'.
        """
        kw = self._cleanKW(key, column, order, limit, where, kw)
        return self._doGet(TABLE_CAMPAIGN, **kw)

    def getDonations(self, key=None, column=None, order=None, limit=None, where=None, **kw):
        """Return a list of donations. Provide parameters for tighter search. Empty parameters for all.
        Param 'key' takes a donation key or multiple keys, comma-separated, of supporters to return.
        Param 'column' also takes comma-separated values.

        Columns for use with 'column' are any of the fields in an 'item' in the return, and can
        also be described with passing a 'desc' argument.
        http://api.demaction.org/dia/api/get.jsp?user=demo&password=demo&table=donation&desc

        Returns an XML list of campaigns, suitable for parsing. Each supporter is inside an 'item'.
        If you don't want to work directly with the xml, use 'pythonize'.
        """
        kw = self._cleanKW(key, column, order, limit, where, kw)
        return self._doGet(TABLE_DONATION, **kw)

    def donationsReport(self, type, which):
        """UI supports several different reports. This is a placeholder in case we want to do that, too."""
        return NotImplementedException

    def getEvents(self, key=None, column=None, order=None, limit=None, where=None, **kw):
        """Return a list of events. Provide parameters for tighter search. Empty parameters for all.
        Param 'key' takes a donation key or multiple keys, comma-separated, of events to return.
        Param 'column' also takes comma-separated values.

        Columns for use with 'column' are any of the fields in an 'item' in the return, and can
        also be described with passing a 'desc' argument.
        http://api.demaction.org/dia/api/get.jsp?user=demo&password=demo&table=event&desc

        Returns an XML list of events, suitable for parsing. Each event is inside an 'item'.
        If you don't want to work directly with the xml, use 'pythonize'.
        """
        kw = self._cleanKW(key, column, order, limit, where, kw)
        return self._doGet(TABLE_EVENT, **kw)



    def setCustomFieldMapping(self, column, name, key=None, **kw):
        """Add or change the setting for mapping a readable name to a custom field column.

        See http://trac.democracyinaction.org/wiki/API/CustomFields
        """
        kw["simple"] = "yes"
        kw["READONLY_Database_Field"] = column
        kw["Name"] = name
        if key: kw["key"] = key
        else: kw["organization_KEY"] = self.getOrgKey()
        return self._doGet(TABLE_CUSTOM_FIELDS, API_SET_URL, **kw).strip()

    def delCustomFieldMapping(self, key):
        """Remove a custom field by key.
        Returns the value of the response directly from the service, which isn't generally helpful.
        (At least on success.)
        """
        return self._doGet(TABLE_CUSTOM_FIELDS, API_DEL_URL, key=key)

    def getCustomFieldMappings(self, key=None, column=None, order=None, limit=None, where=None, **kw):
        """Provide a list of all the named custom fields, as shown in the UI. Each one will map
        to a particular column name in the custom fields table based on the 'READONLY_Database_Field'
        column.

        Returns an XML list of items, suitable for parsing. Custom fields are each 'item'.
        If you don't want to work directly with the xml, use 'pythonize'.
        """
        kw = self._cleanKW(key, column, order, limit, where, kw)
        return self._doGet(TABLE_CUSTOM_FIELDS, **kw)

    def lookupCustomFieldMapping(self, name):
        """Custom fields can be named as they are in the custom table (like VARCHAR2) or can have a
        friendly name mapped through the action of the 'custom_field' table. Look up the column name
        from said table. If no results, return the name as given.
        """
        kw = {"where": 'Name="%s"' % name, "column": "READONLY_Database_Field"}
        field = pythonize(self._doGet(TABLE_CUSTOM_FIELDS, **kw))
        if field: name = field[0]['READONLY_Database_Field']
        return name

    def getSupporterCustomFields(self, key, desc=None, debug=None):
        """Get the custom fields on the supporter with supporter_KEY 'key'.
        The column names are the raw names. You can look up the raw column name
        associated with a named custom field with the 'lookupCustomFields' method.

        Returns an XML list of 1 item, suitable for parsing. Custom fields are inside the 'item'.
        If you don't want to work directly with the xml, use 'pythonize'.

        See http://trac.democracyinaction.org/wiki/API/CustomFields
        """
        if desc:
            kw = {"desc":"1"}
        else:
            kw = {"where": 'supporter_KEY=%s' % key}
        if debug: kw['debug'] = 1
        return self._doGet(TABLE_SUPPORTER_CUSTOM, **kw).strip()

    def setSupporterCustomField(self, key, name, value, debug=None):
        """Set the custom field 'name' on the supporter with supporter_KEY 'key' to 'value'.
        The name can be the name of the field as defined in the 'custom_field' table (as through the
        web ui) or a direct column name (like VARCHAR0). Caller is responsible for making sure the
        name is either in the table or mapped from the 'custom_field' table.
        """
        col = str(self.lookupCustomFieldMapping(name))   # 'col' comes as unicode, and can't be passed as kw arg
        cust_field = {col:value}
        orgkey = self.getOrgKey()
        if debug: cust_field["debug"] = 1
        return self.setSupporter(key=key, link="custom", linkKey="0", organization_KEY=orgkey, **cust_field)        



    def setSupporter(self, key=None, **kw):
        """
        Modify or create a supporter. If a 'key' is provided, edit that supporter. Else, create a new.
        Other keyword parameters will specify a column and value to set.

        Supporter defaults to using the email address as a unique key. If you supply an email address and
        a supporter already has it, you'll end up editing that supporter.

        Supporters can also use "linking". Not supported here explicitly at the moment, though it's just another
        parameter, so you can do it.

        There is a debug mode, with the 'debug' kw.

        See http://data.demaction.org/wiki/space/Developer+Documentation/APIs/Creating+a+Supporter

        Returns the key of the created item.
        """ 
        kw["simple"] = "yes"
        if key: kw["key"] = key
        else: kw["organization_KEY"] = self.getOrgKey()
        return self._doGet(TABLE_SUPPORTER, API_SET_URL, **kw).strip()

    def delSupporter(self, key, debug=None):
        """Remove a supporter by key.
        Returns the value of the response directly from the service, which isn't generally helpful.
        (At least on success.)
        """
        kw = {}
        if debug: kw["debug"] = 1
        return self._doGet(TABLE_SUPPORTER, API_DEL_URL, key=key, **kw)

    def setCampaign(self, key=None, **kw):
        """
        Modify or create a campaign. If a 'key' is provided, edit that one. Else, create a new.
        Other keyword parameters will specify a column and value to set.

        For creation, campaigns require 'organization_KEY' to be provided. This method calculates
        it automatically.

        There is a debug mode, with the 'debug' kw.

        See http://data.demaction.org/wiki/space/Developer+Documentation/APIs/Setting+Data

        Returns the key of the created item.
        """ 
        kw["simple"] = "yes"
        if key: kw["key"] = key
        else: kw["organization_KEY"] = self.getOrgKey()
        return self._doGet(TABLE_CAMPAIGN, API_SET_URL, **kw).strip()

    def delCampaign(self, key, debug=None):
        """Remove a campaign by key.
        Returns the value of the response directly from the service, which isn't generally helpful.
        (At least on success.)
        """
        kw = {}
        if debug: kw["debug"] = 1
        return self._doGet(TABLE_CAMPAIGN, API_DEL_URL, key=key, **kw)
        
    def setDonation(self, key=None, **kw):
        """
        Modify or create a donation. If a 'key' is provided, edit that one. Else, create a new.
        Other keyword parameters will specify a column and value to set.

        There is a debug mode, with the 'debug' kw.

        For creation, donations require 'organization_KEY' to be provided. This method calculates
        it automatically.

        See http://data.demaction.org/wiki/space/Developer+Documentation/APIs/Setting+Data

        Returns the key of the created item.

        Warning: I don't know if using this tries to process an actual donation!
        """ 
        kw["simple"] = "yes"
        if key: kw["key"] = key
        else: kw["organization_KEY"] = self.getOrgKey()
        return self._doGet(TABLE_DONATION, API_SET_URL, **kw).strip()

    def delDonation(self, key, debug=None):
        """Remove a donation by key.
        Returns the value of the response directly from the service, which isn't generally helpful.
        (At least on success.)
        """
        kw = {}
        if debug: kw["debug"] = 1
        return self._doGet(TABLE_DONATION, API_DEL_URL, key=key, **kw)
        
    def setEvent(self, key=None, **kw):
        """
        Modify or create a event. If a 'key' is provided, edit that one. Else, create a new.
        Other keyword parameters will specify a column and value to set.

        There is a debug mode, with the 'debug' kw.

        For creation, events require 'organization_KEY' to be provided. This method calculates
        it automatically.

        See http://data.demaction.org/wiki/space/Developer+Documentation/APIs/Setting+Data

        Returns the key of the created item.
        """ 
        kw["simple"] = "yes"
        if key: kw["key"] = key
        else: kw["organization_KEY"] = self.getOrgKey()
        return self._doGet(TABLE_EVENT, API_SET_URL, **kw).strip()

    def delEvent(self, key, debug=None):
        """Remove a event by key.
        Returns the value of the response directly from the service, which isn't generally helpful.
        (At least on success.)
        """
        kw = {}
        if debug: kw["debug"] = 1
        return self._doGet(TABLE_EVENT, API_DEL_URL, key=key, **kw)
        

def pythonize(xml):
    """Takes a returned XML statement and turns it into a list of dictionaries, where each dict in
    the list is an 'item' and each entry in the dict is a field. Elements with no value will be present
    but have value of None.

    Note: Assumes the xml is fairly simple: if the format starts growning more than one level of elements
    per item, this will only work marginally. But since they're *very* thinly wrapping SQL, I'm not
    afraid of that.

    Also note: remote system can sometimes produce non-valid XML! (Mostly HTML, like 'br' from fields.)
    This will blow up parsing. We will have to tidy or do some pre-processing CDATA insertion to be robust.
    """
    retval = []
    try:
        dom = minidom.parseString(xml)
        items = dom.getElementsByTagName("item")
        for item in items:
            dict = {}
            children = item.childNodes
            for child in children:
                if child.nodeType == child.ELEMENT_NODE:
                    valu = child.childNodes and child.childNodes[0].nodeValue or None
                    dict[child.nodeName] = valu
            retval.append(dict)
        dom.unlink()
    except ExpatError, e:
        print e
        pass   # invalid XML!
    return retval