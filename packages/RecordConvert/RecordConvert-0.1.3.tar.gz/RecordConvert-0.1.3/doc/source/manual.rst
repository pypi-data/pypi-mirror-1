++++++++++++++++++++
RecordConvert Manual
++++++++++++++++++++

RecordConvert is a set of tools for dealing with the sorts of data structures
you commonly encounter when working with relational databases.

The premis is this: 

    Many applications, web applications in particular, use very complex internal
    models for their data consisting of complex classes, methods and lots of 
    ad-hoc conversions. Rather than trying to bend the data model to fit every
    use case as it comes up, wouldn't it be nicer to rigidly enforce a very simple
    data model and then choose tools which are designed to work with it?

To that end I've come up with a data model I call *KERNS*. RecordConvert is 
simply a package which provides a set of tools for working with KERNS data
structures.

Working with a KERNS data model is just like having a sensible naming
convention - it isn't strictly necessary but it makes a lot of problems much
easier if you do have it.

.. tip ::

   If you really don't like the restrictions of KERNS but still want the
   conversion capabilities of RecordConvert you should use ConversionKit 
   which works with ordinary Python dictionaries and lists. You'll be 
   missing out though. Sticking ridgidly to KERNS makes your life a lot
   easier.

Chapter 1: RecordConvert Principles and Practice
++++++++++++++++++++++++++++++++++++++++++++++++

Understanding the KERNS Data Model
==================================

RecordConvert revolves around a very simple data model I'm calling KERNS.  A
KERNS data structure consists of records, lists of records and any object which
can easily be represented by a UTF-8 encoded string (for example integers,
dates etc). A record is just like a dictionary but the keys must be valid
Python identifiers and must not be a keyword likely to conflict with any names
in Python, JavaScript, SQL or any other language you are likely to want to work
with.  Lists of records can't exist on their own although you can have a record
with a single key which has a value which is a list of records.

This data format is readily encoded into XML, JSON or DOSDEK (described later)
and can easily be represented in an SQL database by rows in tables related by
foreign keys. It is also easy to represent as objects in code in most languages
including Python. These features make KERNS an ideal basis for a data model to
use in your application.

Because a strict KERNS format only defines the string type you would usually
want to use a superset of KERNS for your actual data model, one which defines
things like integers, dates and times. You can write ConversionKit converters
using the StringConvert package to convert between strict KERNS and your own
KERNS-like data model.  RecordConvert provides tools to convert strict KERNS to
and from JSON, XML and DOSDEK (currently a work in progress).

KERNS in Python
---------------

KERNS data structures are represented in Python code with two classes: ``Record``
and ``ListOfRecords``.

.. sourcecode :: pycon

    >>> from recordconvert import Record, ListOfRecords

The ``Record`` class is just like an ordinary Python dictionary apart from the
following:

* The values can be read as attributes of the record as well as keys but can 
  only be added as keys
* All the keys have to be valid Python identifiers and can't start with an 
  ``_`` character
* The keys should not be keywords or reserved words used in SQL 92, Python or
  JavaScript

The restriction on the key names is necessary to be able to access the keys as
attributes but also makes it more likely you will be able to use the same data
with other programming languges or in other contexts in ways which you might
not anticipate when you start writing your code. 

Just to prove that there is very little magic going on behind the scenes you
are encouraged to look at the definition of the ``Record`` class in the
``recordconvert`` module.

The idea behind the ``Record`` class is that you'll use it as the main basis
for all data you work with. Since there is no restriction on the values of
a record, you can use records for lots of different things.

.. sourcecode :: pycon

    >>> event = Record(title="New Event", guests=3)
    >>> event['location'] = 'London'
    >>> event.location
    'London'
    >>> event.guests
    3

The ``ListOfRecords`` class is just like an ordinary Python list except that it
should only contain ``Record`` instances and that the keys
of the first record can be accessed as attributes of the list itself so that in
the case when the list only contains one record, the ``ListOfRecords`` instance
actually behaves just like the ``Record`` instance it contains.

.. sourcecode :: pycon

    >>> events = ListOfRecords([event])
    >>> events.location
    'London'
    >>> events[0].location
    'London'
    >>> events[0:1] = dict(title='Not a Record')
    Traceback (most recent call last):
      File ...
    TypeError: Item at index 0 is not a Record

The only time you should use the fact that ``ListOfEvents`` member behaves like
its first member is if you are modelling a one-to-one mapping. You'll see more
about this later.

Working with RecordConvert
==========================

To demonstrate how RecordConvert works, let's consider a data model with people
and addresses where each person can have zero or more addresses. A person has a
firstname and a lastname. An address has a number, city and a country.

Here's the data structure we want to work with in our application.

.. sourcecode :: pycon

    >>> person = Record(
    ...     firstname='James',
    ...     lastname='Gardner',
    ...     addresses=ListOfRecords([
    ...         Record(
    ...             number=12,
    ...             city='UK',
    ...             country='Bedford',
    ...         ),
    ...         Record(
    ...             number=5,
    ...             city='UK',
    ...             country='London',
    ...         )
    ...     ])
    ... )


RecordConvert comes with two converter factories for converting dictionaries of
strings to ``Record`` objects and lists of dictionaries of strings to
``ListOfRecord`` objects: ``toRecord()`` and ``toListOfRecords()``.

The ``toRecord()`` Converter
----------------------------

The ``toRecord()`` converter behaves in exactly the same way as
ConversionKit's ``toDictionary()`` converter. The only difference is
that it returns a ``Record`` instance rather than a Python dictionary and as a
result the restrictions that apply to records also apply to the keys of the
values that ``toRecord()`` converts.

Let's create a converter for converting an address dictionary to an 
address record. First we'll import the converters:

.. sourcecode :: pycon

    >>> from conversionkit import Conversion
    >>> from conversionkit import noConversion
    >>> from recordconvert import toRecord, toListOfRecords
    >>> from stringconvert import unicodeToInteger

Now we'll use them:

.. sourcecode :: pycon

    >>> address_converter = toRecord(
    ...     converters = dict(
    ...        number=unicodeToInteger(),
    ...        city=noConversion(),
    ...        country=noConversion(),
    ...    )
    ... )
    >>> from stringconvert import unicodeToInteger
    >>> address_1 = dict(
    ...     number=u'5',
    ...     city=u'UK',
    ...     country=u'London',
    ... )
    >>> result = Conversion(address_1).perform(address_converter).result
    >>> result
    {u'country': u'London', u'number': 5, u'city': u'UK'}
    >>> type(result)
    <class 'recordconvert.Record'>
    >>> address_2 = dict(
    ...     number=u'12',
    ...     city=u'UK',
    ...     country=u'Bedford',
    ... )
    >>> print Conversion(address_2).perform(address_converter).result
    {u'country': u'Bedford', u'number': 12, u'city': u'UK'}

See the ``toDictionary()`` converter for more information.

The ``toListOfRecords()`` Converter
-----------------------------------

As well as helping to representing and convert table records, RecordConvert can
also model relationships between records. For example, if the database has a
one-to-many mapping you can model that as a Record with one key which has a
``ListOfRecords()`` value. The ``ListOfRecords`` class is derived from and
behaves just like a ``list`` except that the only items the list can contain
are ``Record`` instances and that each item in the list should have the same
keys (not enforced).

A ``ListOfRecords`` instance can be created from an ordinary list of
dictionaries using the ``toListOfRecords()`` converter which takes
a converter representing the type of record to be created as its only argument.
The RecordConvert data model doesn't allow standalone lists of items (and
netither does the XML model) so any lists of records have to be associated with
a key as part of another record. This represents a one-to-many mapping. 

In this case we'll convert a person together with the two addresses associated
with it all in one go. First let's create the converter for a list of address:

.. sourcecode :: pycon

    >>> person_data = dict(
    ...     firstname=u'James',
    ...     lastname=u'Gardner',
    ...     addresses=[
    ...         dict(
    ...             number=u'12',
    ...             city=u'UK',
    ...             country=u'Bedford',
    ...         ),
    ...         dict(
    ...             number=u'5',
    ...             city=u'UK',
    ...             country=u'London',
    ...         )
    ...     ]
    ... )
    >>> addresses_converter = toListOfRecords(address_converter)
    >>> person = toRecord(
    ...     converters = dict(
    ...         firstname = noConversion(),
    ...         lastname = noConversion(),
    ...         addresses = addresses_converter,
    ...     )
    ... )
    >>> from pprint import pprint # To nicely format the data
    >>> pprint(Conversion(person_data).perform(person).result)
    {u'addresses': [{u'city': u'UK', u'country': u'Bedford', u'number': 12},
                    {u'city': u'UK', u'country': u'London', u'number': 5}],
     u'firstname': u'James',
     u'lastname': u'Gardner'}

As you can see the ``person`` converter makes use of the ``address_converter``
to produce the list of records.

See the ``toListOf()`` converter for more information.

Restrictions of RecordConvert
-----------------------------

Here are some data structures which you can easily convert using the ConversionKit
``toDictionary()`` and ``toListOf()`` converters but which aren't valid
KERNS and which shouldn't be used when using RecordConvert:

.. sourcecode :: pycon

    >>> # The items in the list are strings, not records
    >>> v = [
    ...     'James',
    ...     'Tom',
    ... ]
    >>> # The outer list contains different types of items
    >>> v = [
    ...     {
    ...         'city': 'London',
    ...         'country': 'UK',
    ...     },
    ...     [
    ...         {
    ...             'city': 'London',
    ...             'country': 'UK',
    ...         }
    ... 
    ...     ]
    ... ]
    >>> # The outer list contains different types of record
    >>> v = [
    ...     {
    ...         'city': 'London',
    ...         'country': 'UK',
    ...     },
    ...     {
    ...         'firstname': 'James',
    ...         'lastname': 'Gardner',
    ...     }
    ... ]
    >>> # The outer list contains other lists, not records.
    >>> v = [
    ...     [
    ...         {
    ...             'city': 'London',
    ...             'country': 'UK',
    ...         }
    ...     ],
    ...     [
    ...         {
    ...             'city': 'London',
    ...             'country': 'UK',
    ...         }
    ...     ]
    ... ]

Although there appear to be a lot of restrictions, any compatible data
structures are very easily used in virtually any situation and so the effort
involved in creating a model that fits the restrictions is more than paid for
by the simplifications you get in the conversion code you need.

Attribute Access in a ``ListOfRecords`` instance
------------------------------------------------

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

An Example: Creating Records From DB-API 2.0 Queries
-----------------------------------------------------

When you use the Python DB-API 2.0 to execute a query the result is
returned as a tuple of tuples. Each of the tuples represents a record of
results and can be used to instanciate a ``Record`` instance. The names of the
columns can be extracted from the ``.description`` attribute of the cursor.

Let's create a database and add some tables and data:

.. sourcecode :: pycon

    >>> import sqlite3
    >>> connection = sqlite3.connect(':memory:')
    >>> cursor = connection.cursor()
    >>> cursor.execute('''
    ...     CREATE TABLE person (
    ...         person_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ...         firstname VARCHAR(20),
    ...         lastname VARCHAR(40)
    ...     )
    ... ''')
    <sqlite3.Cursor object at ...>
    >>> cursor.execute('''
    ...     CREATE TABLE address (
    ...         address_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ...         person_id REFERENCES person(person_id),
    ...         number INTEGER,
    ...         country VARCHAR(20),
    ...         city VARCHAR(40)
    ...     )
    ... ''')
    <sqlite3.Cursor object at ...>
    >>> cursor.execute(
    ...     'INSERT INTO person (firstname, lastname) VALUES (?, ?)',
    ...     ('James', 'Gardner')
    ... )
    <sqlite3.Cursor object at ...>
    >>> cursor.execute(
    ...     'INSERT INTO address (person_id, number, country, city) VALUES (?, ?, ?, ?)',
    ...     (1, 5, 'UK', 'London')
    ... )
    <sqlite3.Cursor object at ...>
    >>> cursor.execute(
    ...     'INSERT INTO address (person_id, number, country, city) VALUES (?, ?, ?, ?)',
    ...     (1, 12, 'UK', 'Bedford')
    ... )
    <sqlite3.Cursor object at ...>

Now let's select all the addresses and create ``Record`` objects from the rows:

.. sourcecode :: pycon

    >>> cursor.execute('SELECT * FROM address')
    <sqlite3.Cursor object at ...>
    >>> rows = cursor.fetchall()
    >>> addresses = []
    >>> for row in rows:
    ...     record = Record()
    ...     for i in range(len(row)): 
    ...         record[cursor.description[i][0]] = row[i]
    ...     addresses.append(record)
    >>> addresses = ListOfRecords(addresses)
    >>> print addresses
    [{u'person_id': 1, u'country': u'UK', u'address_id': 1, u'number': 5, u'city': u'London'}, {u'person_id': 1, u'country': u'UK', u'address_id': 2, u'number': 12, u'city': u'Bedford'}]

Now let's get a person ``Record``:

.. sourcecode :: pycon

    >>> cursor.execute('SELECT * FROM person WHERE person_id=1')
    <sqlite3.Cursor object at ...>
    >>> rows = cursor.fetchall()
    >>> person = Record()
    >>> row = rows[0]
    >>> for i in range(len(row)):
    ...     person[cursor.description[i][0]] = row[i]
    >>> print person
    {u'person_id': 1, u'lastname': u'Gardner', u'firstname': u'James'}

We now have a ``person`` record and in many situations having one variable to
represent the person record and one to represent the person's addresses will be
perfectly adequate but you can also add the addresses to the person record:
 
.. sourcecode :: pycon

    >>> person['address'] = addresses
    >>> print person
    {u'person_id': 1, u'lastname': u'Gardner', u'firstname': u'James', u'address': [{u'person_id': 1, u'country': u'UK', u'address_id': 1, u'number': 5, u'city': u'London'}, {u'person_id': 1, u'country': u'UK', u'address_id': 2, u'number': 12, u'city': u'Bedford'}]}

.. note ::

    There is an argument that it makes more sense to call the person attribute
    represent the addresses ``addresses`` but I prefer to always use the singular
    for everything. Introducing plurals complicates the naming convention and also
    makes it less obvious when you access a variable. I prefer
    ``person.address[0].number`` to ``person.addresses[0].number``.

You can now access the attributes of the records:

.. sourcecode :: pycon

    >>> person.address[1].city
    u'Bedford'

.. note ::

    If you are used to using an object relational mapper such as SQLAlchemy or
    the Django ORM, this manaul approach to assembling object might seem a bit
    archaic. In a way it is but it also puts you completely in control of the
    objects you build and that can be very useful.

Notice that the data types returned from the database are already in the
correct Python types without having had any conversions applied. This is
because most DB-API drivers automatically handle conversions themselves so you
only need to introduce ConversionKit if the you aren't happy with the default
conversions the DB-API driver performs.

Designing an application with RecordConvert
===========================================

Now you've seen the mechanics of how to use the ``toRecord()`` and
``toListOf()`` converters and can assemble data structures using ``Record`` and
``ListOfRecords``, let's think about the best way to structure an application. 

If you've ever worked with Unicode you'll recall the advice that decoding to
Unicode objects and encoding to something like UTF-8 should always be done
right at the boundary of your application so that your entire application has
the benefit of working with Unicode and you never have to worry about whether
you are dealing with an encoded string or a proper Unicode object. 

Exactly the same advice applies to your data model. You should always convert
your data to records and lists of records as soon as it enters your application
and convert to a different format at the very last moment before your data
leaves your application. That way you are able to benefit from using records 
and lists of records in the correct format thoughout your application.

One point to be aware of is that many of the tools and utilities at the edge of
your application are likely to do at least some conversion automatically.
Database drivers, for example, often convert values to basic Python types for
you. This can appear helpful because it allows you to skip a conversion.
Despite this I'd strongly recommend you get into the habit of introducing a
conversion step anyway. There are a few reasons for this:

* The data format returned might not be exactly the same as the data types 
  you expect
* The data formats returned might change in a future version
* Applying a seemingly superfluous converter doesn't take very long, 
  debugging an obscure data problem or refactoring a whole application does
* You'll start seeing patterns for reuse which weren't obvious with your
  spaghetti data approach

The basic rule is:

    No external data or objects, whether from a data store, user input, a web
    service or anywhere else should ever enter your application without being
    converted (and hence validated) into records and lists of records

By being totally pedantic about using RecordConvert absolutely everywhere you
ensure that your application is isolated from its inputs and outputs. 

* This makes migration to different components very simple, you just need to
  re-write the converters, not the application.
* Your objects don't leak though your application implictly adding 
  dependencies you didn't know you had.
* You will be happy!

I strongly recommend pedantic and rigourous applications of these principles.
If you half do it, RecordConvert will start getting in your way because you'll
start having to use it all over the place to fix problems where you didn't
convert data properly at the edges and each case is likely to be slightly
different to the last, hindering re-use. If you do it properly your life will
be easier.


