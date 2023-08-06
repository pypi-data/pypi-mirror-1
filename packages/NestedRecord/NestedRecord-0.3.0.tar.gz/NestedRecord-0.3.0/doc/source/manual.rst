NestedRecord Manual
+++++++++++++++++++

.. contents::

Tools for handling the NestedRecord encoding, a useful way of representing
nested structures of dictionaries and lists as flat key-value pairs by using a
convention for key names.

Relationship with RecordConvert
===============================

NestedRecord is part of the ConversionKit range of packages but is particularly
closely associated with RecordConvert. To understand why NestedRecord is useful
you need to understand what RecordConvert is for.

The key idea behind RecordConvert is that all data in your application is best
handled as a set of lists and dictionaries with the following restrictions:

* Lists can't exist on their own
* Dictionaries can only contain keys which are also valid variable names in
  Python, SQL, JavaScript and other language. Such dictionaries are called *records*.
* All items within a list must be records and they must be the same type of record

These restictions make it trivially easy to represent any data source in an SQL
database or pretty much any other sort of data store. They also make it easy to
work with the data in your applicaiton.

The idea is that literally all inputs to your application (from HTTP requests,
web services, user input or anything else), get converted to a RecordConvert
structure, your application works with it and then converts the RecordConvert
structure to the appropriate format at the edge of your application for output.

This means you work with RecordConvert structures throughout your application
and write converters everywhere you need them.

Frequently the means of input to some part of your application has to be
key-value pairs, but what if these key-value pairs actually represent a nested
data structure? Your application will have to do a lot of work converting the
input. NestedRecord makes this process much easier.

An Example: HTML Forms
======================

As an example, let's think about an HTML form. Of course, NestedRecord is
applicable to lot's of other situations too, but this is one I encouter a lot.

Let's say you want to display a single page with information about a person and
all their addresses. In a simple case where there is just one address the data
your application want's to work with looks like this:

.. sourcecode :: pycon

    >>> person = {
    ...     'firstname': 'James',
    ...     'lastname': 'Gardner',
    ...     'address': [
    ...         {
    ...             'city': 'London',
    ...             'country': 'UK',
    ...         }
    ...     ]
    ... }

Recap of RecordConvert
----------------------

With RecordConvert the dictionaries are actually instances of the
``recordconvert.Record`` class and the list is actually an instance of the
``recordconvert.ListOfRecords`` class.

.. sourcecode :: pycon

    >>> from recordconvert import Record, ListOfRecords
    >>> person = Record(
    ...     firstname = 'James',
    ...     lastname = 'Gardner',
    ...     address = ListOfRecords(
    ...         Record(
    ...             city = 'London',
    ...             country = 'UK',
    ...         )
    ...     )
    ... )

In Python code you can use this data structure like this:

.. sourcecode :: pycon

    >>> person.firstname
    'James'
    >>> person.address[0].city
    'London'

As a convenience for the case where you are representing a one-to-one mapping
(ie a person can only possibly have one address) you can also access the
address details like this:

.. sourcecode :: pycon

    >>> person.address.city
    'London'

This means that you use the same internal data structure for one-to-one and
one-to-many mappings, but that there is some syntactic sugar to allow your
Python code to express the relationship more cleanly.

Back to the example
-------------------

To arrange this data so that the field names on the form can all be unique you
need to flatten it to a single dictionary of key-value pairs.

Values in a record are just listed by their key. Values in a record within a list
are represented by the parent key followed by a ``-`` character, then by their
parent record's position in the list (starting at 1) and then by a ``.`` then
by the value's key.

This means the dictionary is flattened to this:

.. sourcecode :: pycon

    >>> result = {
    ...     'firstname': 'James',
    ...     'lastname': 'Gardner',
    ...     'address[0].city': 'London',
    ...     'address[0].country': 'UK',
    ... }

Now the four HTML fields required can be given the names of the keys in the
flattened data structure. When the form is submitted you can then decode the
data structure back to the structure you need to work with in the application.

Using NestedRecord
------------------

NestedRecord comes with a number of functions for working with nested data
structures and their encodings:

``decode(data, depth=None, dict_type=dict, list_type=list, start_list_part='[', end_list_part=']', strict=True)``
    
    Takes a flat dictionary with appropriately encoded keys and decodes it to a
    Python data structure of dictionaries and lists (not records and and lists of
    records).

``encode(data, partial=False, dict_type=dict, start_list_part='[', end_list_part=']', strict=True)``

    Encodes a data structure of nested records to a flat structure.

By specifying the optional arguments ``dict_type``, and ``list_type`` you can
alter the class the functions use to return the result. For example, it is
common to use  ``dict_type=recordconvert.Record`` and
``list_type=recordconvert.ListOfRecords`` when working with RecordConvert.

The ``decode()`` function also takes a ``depth`` argument. The default is
``None`` which means "decode the whole data structure", but there are times
when it is useful to decode just part of the data structure. You can specify
the ``depth`` argument as an integer to specify the number of levels to decode
from the right of the key.

The ``encode()`` function takes a ``partial`` argument.

Let's try these functions with the data structures we've been looking at so far:

.. sourcecode :: pycon

    >>> from nestedrecord import decode, encode
    >>> encode(person) == result
    True
    >>> decode(result) == person
    True

NestedRecord in More Detail
===========================

Here are some more examples of data structures which **cannot** be encoded using NestedRecord:

.. sourcecode :: pycon

    >>> case1 = {
    ...     'key': [
    ...         {
    ...             'key': 'value'
    ...         },
    ...         {
    ...             'differentkey': 'value'
    ...         }
    ...     ],
    ... }
    >>> case2 = {
    ...     'key': {
    ...         'key': 'value'
    ...     },
    ... }
    >>> simple_data = [{
    ...     'key': 'value'
    ... }]

All items at each level are dictionaries, lists don't affect the level. This
means each key either contains:

* A value
* A list of values so that the parent key gets an index attached to it and 
  then each is treated as a dictionary
* A dictionary where the decode loop can be looped again

Note that in NestedRecod it isn't possible to have a list on its own because you
wouldn't know what types the list items were. In this example since the key
associated with the list is ``address`` we know that the items are addresses.

Another restriction is that it is not possible to reference the ``person`` list
as a whole or James's first address for example since these items don't have
values directly associated with them. It is only the single values themselves
that can have identifiers, not nested structures.

Lists must contain only records and only records of the same type.

Converters
----------

If you are using NestedRecord as part of a series of ConversionKit conversions
you will find these two converters very useful:

``decodeNestedRecord()``

    Applies the ``decode()`` function to the value being converted and takes
    the same arguments as ``decode()`` apart from ``data`` which is obtained
    from the conversion's ``.value`` attribute. Also takes a 
    ``raise_on_error`` argument which defaults to ``True``.

``encodeNestedRecord()``

    Applies the ``encode()`` function to the value being converted and takes
    the same arguments as ``encode()`` apart from ``data`` which is obtained
    from the conversion's ``.value`` attribute. Also takes a 
    ``raise_on_error`` argument which defaults to ``True``.

Partial Encoding and Decoding
=============================

Sometimes it is useful to be able to decode or encode just part of a strucutre,
perhaps to pass one of those parts to a different converter.

To demonstrate this let's create a data structure with more than two level's of depth:

.. sourcecode :: pycon

    >>> encoded_data = encode({'group': [person]})
    >>> print encoded_data
    {'group[0].lastname': 'Gardner', 'group[0].address[0].city': 'London', 'group[0].address[0].country': 'UK', 'group[0].firstname': 'James'}

Let's decode each depth of the encoded data and check it corresponds to each
depth of the decoding.

.. sourcecode :: pycon

    >>> data = decode(encoded_data, depth=1)
    >>> print data
    {'group': [{'address[0].country': 'UK', 'lastname': 'Gardner', 'firstname': 'James', 'address[0].city': 'London'}]}
    >>> encoded_person_data = data['group'][0]
    >>> person = decode(encoded_person_data, depth=1)
    >>> print person
    {'lastname': 'Gardner', 'firstname': 'James', 'address': [{'country': 'UK', 'city': 'London'}]}

Now let's think about partial encoding, this encodes from the other end from the decoding so 

.. sourcecode :: pycon

    >>> encode(
    ...     data = {
    ...         'work': {
    ...             'contact[0].phone': '01234 567890',    
    ...             'contact[0].mobile': '07574 123456',    
    ...             'contact[1].phone': '43210 567890',    
    ...             'contact[1].mobile': '47570 123456',    
    ...             'project.name': 'Test Project',    
    ...         }
    ...     },
    ...     partial = True
    ... )
    {'work.contact[1].mobile': '47570 123456', 'work.contact[1].phone': '43210 567890', 'work.contact[0].phone': '01234 567890', 'work.project.name': 'Test Project', 'work.contact[0].mobile': '07574 123456'}

Encoding Errors
===============

When working with ConversionKit it can be useful to flatten an error structure
into a similar format as the one described so far for nested structures of
lists and records. 

The difference with an error structure is that there needs to be an error
message at *each* level of the structure in addition to the possibility of
there being an error message at any point a value can normally occur.

To assist with this, NestedRecord provides the following function:

``encode_error(conversion, )``

Notice that the function actually takes a ConversionKit ``Conversion`` object as its argument. 

Here's an example:

    >>> from nestedrecord import encode_error
    >>> from recordconvert import toRecord, toListOfRecords
    >>> from conversionkit import Conversion, noConversion
    >>> from stringconvert import unicodeToInteger
    >>> person = {
    ...     'firstname': 'James',
    ...     'lastname': 'Gardner',
    ...     'address': [
    ...         {
    ...             'building_number': u'this should be an integer',
    ...             'city': u'London',
    ...             'country': u'UK',
    ...         }
    ...     ]
    ... }
    >>> to_person = toRecord(
    ...     converters = dict(
    ...         firstname=noConversion(),
    ...         lastname=noConversion(),
    ...         address=toListOfRecords(
    ...             toRecord( 
    ...                 converters = dict(
    ...                     building_number=unicodeToInteger(),
    ...                     city=noConversion(),
    ...                     country=noConversion(),
    ...                 )
    ...             )
    ...         )
    ...     ),
    ... )
    >>> conversion = Conversion(person).perform(to_person)
    >>> conversion.successful
    False
    >>> from pprint import pprint
    >>> pprint(encode_error(conversion))
    {u'address': 'One of the items was not valid',
     u'address[0]': 'The building_number field is invalid',
     u'address[0].building_number': "invalid literal for int() with base 10: 'this should be an integer'"}

As you can see we now have three levels of errors one for each level in the
chain. These errors can now be easily referenced in application code.

