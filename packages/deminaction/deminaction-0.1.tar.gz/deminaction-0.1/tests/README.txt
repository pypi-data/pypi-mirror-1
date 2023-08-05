These are the tests (mostly doctests) for this module. You may run them as tests, or read as examples.
Note that these run against the live server, so don't run too many, jus to be nice.

Broken tests? This is an interactive module, and uses a publicly available demo account. If the data
there changes, some of the tests will break. It cannot really be avoided.

BUT: if you run a test and it creates something but doesn't delete it, please do so manually.


Since we're on Python 2.3 and don't have ZopeTestCase easily available, the non-docstring
doctests are simulated by creating empty modules with the contents being a module-level
docstring.

Converting to Python 2.4's doctest, with support for this, should be easy. Just remove the quotes
from around the files and change the API call in runalltests.
