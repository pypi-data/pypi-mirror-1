====================================================================
This is StableDict - a dictionary class remembering insertion order.
====================================================================
(README.txt,v 1.1 2007/08/28 09:46:31 martin Exp)


Description
-----------

Order (i.e. the sequence) of insertions is remembered (internally
stored in a hidden list attribute) and replayed when iterating. A
StableDict does NOT sort or organize the keys in any other way.

Implemented as a subclass of the built in dict type.  Very compact
implementation (less than 150 lines of code).  Comes with a large
test suite derived from Python's test_dict.py in a separate test
module.


About the name
--------------

There is already an OrderedDict module/class at the Python Cheese
Shop.  It has similar goals but goes beyond StableDict in that it also
offers list-like methods.  Although OrderedDict is implemented as a
subclass of the built in dict type, it is not a proper subclass of dict
in the sense of Barbara Liskov's substitution principle - i.e. you
cannot always use a OrderdDict in place of a dict.

After I've made my own minimalistic ordered dictionary class I
obviously needed a new name.  OrderedDict was already taken and is
ambiguous anyway: One might also interpret "ordered" as the property
of having a total order relation defined on the keys (all keys are
_meaningful_ comparable with the "<" operator).

StableDict is ambiguous too (one might e.g. associate persistence) but
I hope that most people interpret it correctly as "resistant to change
of position" (cf. the stableness of sort algorithms).


Change History
--------------

2007-08-28  Martin Kammerhofer  <mkamm@gmx.net>

Release 0.2

	* Added README.txt (this file).
	* Changed capitalization of the module name from StableDict to
	  all lowercase stabledict (PEP 8).
	* Changed __repr__ so that x == eval(repr(x)).
	* Provided __str__ which is more concise than __repr__.
	* Made ``./setup test'' work (needs setuptools installed).
