deminaction - Python binding for "Democracy In Action" API
author: J Cameron Cooper
Copyright (c) 2005, Enfold Systems, LLC

Description
=============

A thin pure Python wrapper over the demaction.org ("Democracy in Action") web site, using
their simple RESTful interface, which is itself a very thin wrapper over an SQL database.

Note that since this is a very thin wrapper, you cannot just learn how the wrapper works
to deal successfully with the system. You will also have to understand how the remote system
works, which at the very least will require figuring out the columns on the database tables
(which is easy: read the comments for the get methods. Also, the column names are used almost
directly in the UI, with _ converted to a space, and maybe some capitalization.)

Should handle Supporters, Donations, Campaigns, and Events. Will provide the DIA XML directly,
or, optionally, convery to Python structures.

See tests/ for examples of usage.