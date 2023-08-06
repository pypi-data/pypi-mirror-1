Overview
========

Cdblib contains classes to read and write cdb ("constant database") files.

Cdb files map string keys to string values with very fast record lookups.
Cdblib also allows for in-memory indexes to enable even faster lookups.

See http://cr.yp.to/cdb.html on D. J. Bernstein's site for the original
specification.

Installation
============

Cdblib requires Python 2.5.

The cdblib package contains a C extension module for speedups, but its use
is not required and makes no difference to the interfaces exposed (except of
course for speed).

To install with the C extension module for speed, run::

    # python setup.py install
    
Alternatively, you can simply copy the file cdblib.py to somewhere in your
PYTHONPATH (but this will not include the speedups from the C extension).

Example Usage
=============

Create a new CDB (or update an existing one):

>>> from cdblib import CDB, CDBWriter
>>> wcdb = CDBWriter("presidents.cdb") # Create a new CDB file.
>>> wcdb["Reagan"] = "1981 - 1988"
>>> wcdb["Bush"] = "1989 - 1992"
>>> wcdb["Clinton"] = "1993 - 2000"
>>> wcdb["Bush"] = "2001 - 2008" # Creates a second record with the key "Bush".
>>> wcdb["Bush"] # Return the first record with key "Bush".
'1989 - 1992'
>>> wcdb.getall("Bush") # Return all records with the key "Bush".
['1989 - 1992', '2001 - 2008']
>>> wcdb["Clinton"]
'1993 - 2000'
>>> wcdb.getall("Clinton")
['1993 - 2000']
>>> wcdb["Gore"] # Oops, the CDB doesn't contain the key "Gore".
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "cdblib.py", line 135, in __getitem__
    raise KeyError(key)
KeyError: 'Gore'
>>> wcdb.get("Gore", "Bush") # Return "Bush" if the key "Gore" doesn't exist.
'Bush'
>>> wcdb.close() # Close the CDB file and prevent any more writes.
    
Open an existing CDB read-only:

>>> rcdb = CDB("presidents.cdb") # Re-open the saved CDB file read-only.
>>> rcdb["Clinton"]
'1993 - 2000'
>>> rcdb.close()
>>> rcdb = CDB("presidents.cdb", load_index=True) # Load the CDB index into memory for faster lookups.
