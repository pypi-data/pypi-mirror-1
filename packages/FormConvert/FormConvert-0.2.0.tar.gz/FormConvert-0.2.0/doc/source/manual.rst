Manual
++++++

What is FormConvert?
====================

* A set of ConversionKit converters for converting Unicode strings received
  from a form submission into Python objects

FormConvert can deal with the following types of form components:

* Form components which allow the user to input a single value per field name
  such as text fields, hidden fields and textareas 

* Form components which allow the user to select a single value per field name
  from a set of possilbe options. For example a select field or radio button
  group

* Form components which allow the user to input zero or more values for a
  particular form field. For example multiple-value selects fields or checkbox
  groups.

FormConvert also contains tools to allow you to represent any data structure
supported by the NestedRecords package. This
allows you to represent extremely complex nested data structures (such as the
ones you would naturally have to work with when using an SQL database) as HTML
forms and have them seamlessly converted to Python data structures on
submission.

FormConvert doesn't care how the forms are generated, or even whether you are
using an HTML form at all. It is really just a set of converters with a
specific application to decoding data submitted over HTTP, but can be used in
many other situations too. Many applications will install FormConvert just so
they can re-use the ConversionKit converters it already defines.

In this documentation I'll assume you are using FormConvert to handle HTML form
submission. The examples will use FormBuild 2.0 to generate the HTML required
but you could use any tool you preferred in your application.

Relationship to FormBuild
-------------------------

FormBuild is another tool I've written which let's you take dictionaries of
data and generate HTML fields and forms from them. Although FormBuild and
FormConvert were designed completely independently they work very well together
because FormBuild can take use the data structures FormConvert produces to
produce HTML forms with that data correctly populated. 

In this manual we'll be using FormBuild to demonstrate the HTML-side of the 
process but you could easily use any other library instead.

Getting Started
===============

Just so you can see the sorts of steps involved let's go through a really
trivial example.

To perform a conversion on a submitted form you use FormConvert which is based
on ConversionKit. ConversionKit is very generic and not much use on its own.
Instead packages such as FormConvert, URLConvert, ConfigConvert, RecordConvert
and NestedRecord build on ConversionKit to provide useful functionality in a
specific problem domain.

To perform a conversion with ConversionKit or any of the tools built upon it
involves four steps:

#. Create a ``Conversion`` object containing the value you wish to convert
#. Perform a conversion with a *converter*
#. Check if the conversion was successful
#. Read the result from the conversion object's ``.result`` attribute if it was
   successful or the error from its ``.error`` attribute if it was not.

FormConvert is also closely tied to the RecordConvert and NestedRecord packages
and is set up assuming you want to work with NestedRecord data structures in
your application. You'll see this later.

To generate our HTML fields we need some software. Install FormBuild (a tool
which works well with FormConvert to generate HTML forms). Your application
might use a different form building package. That's fine too, I just need one
for the examples so that's what I've chosen.

.. sourcecode :: bash

    $ easy_install FormBuild>=2.0.1

Then let's import some objects we need:

.. sourcecode :: pycon

    >>> from formbuild import Form
    >>> from conversionkit import Conversion
    >>> from stringconvert import unicodeToInteger
    >>> from recordconvert import Record

Now let's create an HTML field with the name ``age``:

.. sourcecode :: pycon

    >>> form = Form()
    >>> form.text(name='age')
    literal(u'<input id="age" name="age" type="text" />')

Imagine this form was submitted and you have to convert its value to to a
Python integer. The web framework you are using should provide some interface
to decode the HTTP post data or query string and provide a dictionary of
Unicode values, keyed by the field names. If it doesn't you can use a
``Request`` object provided by the WebOb package:

.. sourcecode :: bash

    $ easy_install WebOb

Now let's set up the object as if it is really handling a GET form submission
by setting up a fake environment with the ``QUERY_STRING`` set up as it would be in
a real example:

.. sourcecode :: pycon

    >>> from webob import Request
    >>> fake_environ = {
    ...     'QUERY_STRING': 'age=3',
    ... }
    >>> request = Request(fake_environ)
    >>> request.params['age']
    '3'

Now let's actually perform the conversion, this is where ConversionKit comes in:

.. sourcecode :: pycon

    >>> conversion = Conversion(unicode(request.params['age']))
    >>> conversion.perform(unicodeToInteger())
    <conversionkit.Conversion object at 0x...>
    >>> conversion.successful
    True
    >>> conversion.result
    3
    >>> result = Record(age = conversion.result)
    >>> print result
    {'age': 3}

As you can see the conversion was successful and the result was a Python
integer. We then assembled a record to represent the form data submitted.

.. tip ::

    Before you continue it is strongly recommended you read the all the
    ConversionKit documentation, particularly the manual.

If we wanted to populate the form with the new value you could do so like this:

.. sourcecode :: pycon

    >>> form = Form(values=result)
    >>> form.text(name='age')
    literal(u'<input id="age" name="age" type="text" value="3" />')

Notice that the FormBuild ``Form`` is this time passed the ``result``
dictionary as its ``values`` argument. When a text input field is created with
the ``age`` name, FormBuild correctly sets its value to 3.

How it could be more complex
----------------------------

In a more realistic example we'd need to be significantly more rigorous than this.
We might need to:

* Convert the request object's ``param`` structure to something more suitable
* Decode a nested data structure which might include:
  * Remove fields we don't need such as the ``.x`` and ``.y`` coordinates on an image submit button
  * Refactoring duplicate field names to better match our conventions
* Convert all the fields together
* Perform extra checks on fields, eg ensuring passwords match

Then to build a form from the result we might need to:

* Convert all the values to Unicode strings
* Encode the nested data structure to a flat dictionary for FormBuild to handle
* Pass FormBuild any errors

One of the reasons form processing is often difficult is that it is often easy
to skip some of these steps in certain cases but unless you learn a pattern
that can handle all of them you'll keep coming across situations you don't know
how to deal with.

You'll see how to do each of these things as you work through the manual.

The Simple Cases
================

Now that you've seen how a conversion works when you convert each field
manually and assemble the result into a record, let's look at some more
realistic cases.

Handling Complete Forms
-----------------------

FormConvert is designed to work on sets of fields. If you are just converting
one field you don't need FormConvert you can just follow the trivial example in
the previous section.

If you had to convert each field manually each time, using FormConvert
would barely be quicker than writing your conversion code from scratch. This
is where *records* come in.

In the simplest case FormConvert assumes that the form you are creating is
analogous to a row in a database table (although you don't have to be using a
relational database of course). One field name therefore corresponds to one
column in the row. FormConvert also assumes that you want to use the
NestedRecord data model in your application and are therefore happy to restrict
the field names you are using to those which are also valid Python variable
names and which do not start with an ``_`` character.

.. tip ::

    The beauty of FormConvert is that it is based on ConversionKit which means
    it can be used with any converters and not just the ones from RecordConvert.
    If you don't want to work with RecordConvert records, and would rather use
    simple Python dictionaries and lists you can use the ConversionKit
    ``toDictionary()`` and ``toListOf()`` conversion factories instead. You
    might want to do this if you are using FormConvert in a legacy application or
    if you are trying to replace existing FormEncode schema which don't have the
    same restrictions. 
    
    Having said that, if you are writing an application from scratch it is strongly
    recommended you use RecordConvert to deal with forms because it deliberately
    limits the combinations of data structures you can work with to just the ones
    which can be represented direclty in an SQL database and this in turn prevents
    you designing forms which are more complex than they need to be which in turn
    simplifies your application code and makes it more re-usable and maintainable
    because there are fewer combinations of cases to deal with.

To convert a set of fields you need to use a ``toRecord()`` converter. This is
just like the ``toDictionary()`` converter which is documented in detail in the
ConversionKit manual but it imposes restrictions on the names which can make up
the keys of the dictionary. Now would be a good time to read the RecordConvert
documentation if you haven't done so already.

Let's convert a form with fields for both name and age. You'll need to write a
converter capable of converting both of these fields. Luckily ``toRecord()``
can generate such a converter for you if you tell it how you want each field
converted. Here's how you would create a suitable converter:

.. sourcecode :: pycon

    >>> from recordconvert import toRecord
    >>> from stringconvert import unicodeToInteger, unicodeToUnicode
    >>>
    >>> form_converter = toRecord(
    ...     converters = dict(
    ...         name=unicodeToUnicode(min=3, max=30),
    ...         age=unicodeToInteger(),
    ...     )
    ... )

This creates a converter which will produce a ``Record`` object where the
``age`` field is an integer and the ``name`` field is a string with between 3
and 30 characters.

.. note :: 
    
    Because we are using records, all the field names have to be valid Python names
    which means it is safe to use ``dict()`` rather than ``{}`` to generate a
    dictionary for the ``converters`` argument because the keys won't contain
    values which can't be passed as Python arguments.

We can create an HTML form for this data with FormBuild like this:

.. sourcecode :: pycon

    >>> form = Form()
    >>> fields = [form.text(name='age'), form.text(name='name')]
    >>> initial_html = u'\n'.join(fields)
    >>> initial_html
    u'<input id="age" name="age" type="text" />\n<input id="name" name="name" type="text" />'

Here's a typical form submission from this form:

.. sourcecode :: pycon

    >>> fake_environ = {
    ...     'QUERY_STRING': 'age=28&name=James',
    ... }
    >>> request = Request(fake_environ)

The ``form_converter`` converter you've just created will expect a dictionary
as the conversion's value, not a WebOb ``request`` object so you need to use
FormConvert's ``multiDictToDict()`` converter to extract all the parameters to
a more suitable structure. The ``multiDictToDict()`` converter also decodes
parameters to Unicode objects if they aren't already Unicode. You can specify
the encoding to use for this, ``'utf8'`` is usually fine and by the nature of
UTF-8 will also decode ordinary 8-bit Python strings as well as Latin 1 and
ASCII character sets:

.. sourcecode :: pycon

    >>> from formconvert import multiDictToDict
    >>> 
    >>> conversion = Conversion(request.params).perform(multiDictToDict(encoding='utf8'))
    >>> conversion.successful
    True
    >>> params = conversion.result
    >>> params 
    {'age': u'28', 'name': u'James'}
    
Now we can perform the conversion:

.. sourcecode :: pycon

    >>> conversion = Conversion(params).perform(form_converter)
    >>> conversion.successful
    True
    >>> conversion.result
    {u'age': 28, u'name': u'James'}

Notice that the ``age`` field has been converted to an integer and the ``name``
field remains a string.

Because the result is actually a ``Record`` object you can access the keys
as attributes:

.. sourcecode :: pycon

    >>> person = conversion.result
    >>> person.name
    u'James'

You can generate a suitable form to redisplay this data like this (although in
a real example you might prefer to write another converter to convert the
``person`` object back to a plain dictionary containing unicode strings as
values before passing it to FormBuild):

.. sourcecode :: pycon

    >>> form = Form(values=person)
    >>> fields = [form.text(name='age'), form.text(name='name')]
    >>> initial_html = u'\n'.join(fields)
    >>> initial_html
    u'<input id="age" name="age" type="text" value="28" />\n<input id="name" name="name" type="text" value="James" />'

Handling Empty Fields
---------------------

If you have a field such as an HTML text input field and the user doesn't enter a
value, the browser will still submit the field but without a value. Most
libraries will then represent this as an empty string (``u''``). To handle this
in your conversion code you can either set a default value for the field or set
an error message so that the user knows they were supposed to enter a value.

You can set an error message for an empty field using the ``empty_errors``
argument to the ``toRecord()`` converter. For example, if the name is not
allowed to be empty you could set up the converter like this:

.. sourcecode :: pycon

    >>> form_converter = toRecord(
    ...     converters = dict(
    ...         name=unicodeToUnicode(min=3, max=30),
    ...         age=unicodeToInteger(),
    ...     ),
    ...     empty_errors = dict(
    ...         name = u'Please specify your name',
    ...     ),
    ... )

Let's test it:

.. sourcecode :: pycon

    >>> fake_environ = {
    ...     'QUERY_STRING': 'age=28&name=',
    ... }
    >>> request = Request(fake_environ)
    >>> conversion = Conversion(request.params).perform(multiDictToDict(encoding='utf-8'))
    >>> conversion.successful
    True
    >>> params = conversion.result
    >>> params 
    {'age': u'28', 'name': u''}
    >>> conversion = Conversion(params).perform(form_converter)
    >>> conversion.successful
    False
    >>> conversion.error
    u'The name field is invalid'
    >>> conversion.children
    {u'age': <conversionkit.Conversion object at 0x...>, u'name': <conversionkit.Conversion object at 0x...>}
    >>> conversion.children['name'].error
    u'Please specify your name'

The ``toRecord()`` converter has a ``empty_defaults`` argument which allows you
to specify default values for empty fields in a similar way. See the
RecordConvert documentation on ``toRecord()`` for details.

Handling Missing Fields (Checkboxes)
------------------------------------

Checkboxes submit no values if they aren't checked and multi-valued select
dropdowns submit no value if no values are selected. It turns out that
multi-valued select dropdowns are best handled as nested data as you'll see
later. As you'll also see later you should treat a checkbox group (multiple
checkboxes with the same name in the same form) in the same way as multi-valued
select boxes so we won't consider these here. That just leaves the case of a
single checkbox input field. Let's look at that.

Checkboxes are useful for yes/no answers such as people agreeing to terms and
conditions. Anything more complex like gender is best handled by either a
radio-group or a single select dropdown with the values ``Male`` and
``Female``, asking "Male? (True or False)" with a checkbox might be regarded as
rude.

You therefore often end up wanting to handle the checkbox in code as a boolean
value. The best way to do this is to give the checkbox a value of ``'yes'`` and
then use a ``unicodeToBoolean()`` converter to convert it to a ``True`` value if
the field is ticked and submitted. If the field isn't ticked, it won't be
submitted and will be missing. You can handle this case by using the
``toDictionary()`` converter's ``missing_defaults`` argument to set a value of
``False`` if the field is missing.

Let's imagine a form with a checkbox input field named ``agree`` which we want
to handle in code as a ``True`` value if it is ticked, and a ``False`` value
otherwise.

Here's the HTML:

.. sourcecode :: pycon

    >>> form = Form()
    >>> form.checkbox(name='agree', value='yes')
    literal(u'<input id="agree" name="agree" type="checkbox" value="yes" />')

.. note ::

    Checkboxes can behave differently from other FormBuild fields. If you don't
    specify a ``value`` argument to ``form.checkbox()`` the field will take the
    value from the values passed to the ``Form`` constructor but it won't be able
    to tell whether the checkbox should be ticked or not, leaving it up to you to
    explictly set the ``checked`` argument to determine whether or not the checkbox
    should be ticked.

    This isn't very satisfactory so the second mode of operation is to allow a
    ``value`` argument to be set explicitly. In this case if the value for the
    field in the ``values`` dictionary passed to the ``Form`` constructor matches the
    ``value`` argument to ``form.checkbox()`` the field will be checked. 

    As you've seen though, it is handy to think of checkboxes in terms of
    ``True`` and ``False`` values so as a further possibility, if you explicitly
    set the ``value`` argument to ``form.checkbox()`` and the value for the field
    in the ``values`` dictionary passed to ``Form`` is ``True``, the field will be
    checked. This is the technique we are using here.

Here's the converter:

.. sourcecode :: pycon

    >>> from stringconvert import unicodeToBoolean
    >>> form_converter = toRecord(
    ...     converters = dict(
    ...         agree = unicodeToBoolean()
    ...     ),
    ...     missing_defaults = dict(
    ...         agree = False,
    ...     ),
    ... )

Let's test it in the case a user ticks the box:

.. sourcecode :: pycon

    >>> agree_ticked_fake_environ = {
    ...     'QUERY_STRING': 'agree=yes',
    ... }
    >>> request = Request(agree_ticked_fake_environ)
    >>> params = Conversion(request.params).perform(multiDictToDict(encoding='utf-8')).result
    >>> conversion = Conversion(params).perform(form_converter)
    >>> conversion.successful
    True
    >>> conversion.result
    {u'agree': True}

Here's the HTML generated when you re-use this data in a form, notice that the checkbox is checked:

.. sourcecode :: pycon

    >>> form = Form(values=conversion.result)
    >>> form.checkbox(name='agree', value='yes')
    literal(u'<input checked="checked" id="agree" name="agree" type="checkbox" value="yes" />')

Now the case where the user doesn't tick the checkbox:

.. sourcecode :: pycon

    >>> agree_not_ticked_fake_environ = {
    ...     'QUERY_STRING': '',
    ... }
    >>> request = Request(agree_not_ticked_fake_environ)
    >>> params = Conversion(request.params).perform(multiDictToDict(encoding='utf-8')).result
    >>> conversion = Conversion(params).perform(form_converter)
    >>> conversion.successful
    True
    >>> conversion.result
    {u'agree': False}

As you can see we get the results we want. This time when the form is generated
the checkbox is unticked:

.. sourcecode :: pycon

    >>> form = Form(values=conversion.result)
    >>> form.checkbox(name='agree', value='yes')
    literal(u'<input id="agree" name="agree" type="checkbox" value="yes" />')

Select Dropdowns and Radio Button Groups (Enums)
------------------------------------------------

Form fields such as select dropdowns or radio groups allow a user to pick one
value from a set of possible values. Your converter needs to ensure that the
value submitted is one of the allowed values. You can do this with a
``oneOf()`` converter from ConversionKit:

.. sourcecode :: pycon

    >>> from conversionkit import oneOf

Here's an example, first the form:

.. sourcecode :: pycon

    >>> form = Form()
    >>> form.radio_group(name='eye_colour', options=[('blue', 'Blue'), ('brown', 'Brown'), ('green', 'Green')])
    literal(u'<input type="radio" name="eye_colour" value="blue" /> Blue\n<input type="radio" name="eye_colour" value="brown" /> Brown\n<input type="radio" name="eye_colour" value="green" /> Green')

Now an example request which submitting this form might produce:

.. sourcecode :: pycon

    >>> from webob import Request
    >>> fake_environ = {
    ...     'QUERY_STRING': 'eye_colour=blue',
    ... }

Let's write a converter:

.. sourcecode :: pycon

    >>> from stringconvert import unicodeToBoolean
    >>> form_converter = toRecord(
    ...     converters = dict(
    ...         eye_colour = oneOf(['blue', 'brown', 'green'])
    ...     ),
    ... )

Now let's try it:

.. sourcecode :: pycon

    >>> request = Request(fake_environ)
    >>> params = Conversion(request.params).perform(multiDictToDict(encoding='utf-8')).result
    >>> conversion = Conversion(params).perform(form_converter)
    >>> conversion.successful
    True
    >>> conversion.result
    {u'eye_colour': u'blue'}

Here's the form re-generated from the result:

.. sourcecode :: pycon

    >>> form = Form(values=conversion.result)
    >>> form.radio_group(name='eye_colour', options=[('blue', 'Blue'), ('brown', 'Brown'), ('green', 'Green')])
    literal(u'<input type="radio" name="eye_colour" value="blue" checked="checked" /> Blue\n<input type="radio" name="eye_colour" value="brown" /> Brown\n<input type="radio" name="eye_colour" value="green" /> Green')

If the use had submitted the value 'grey' the conversion would fail and you
would get an error:

.. sourcecode :: pycon

    >>> fake_environ = {
    ...     'QUERY_STRING': 'eye_colour=grey',
    ... }
    >>> request = Request(fake_environ)
    >>> params = Conversion(request.params).perform(multiDictToDict(encoding='utf-8')).result
    >>> conversion = Conversion(params).perform(form_converter)
    >>> conversion.successful
    False
    >>> conversion.error
    'The eye_colour field is invalid'
    >>> conversion.children['eye_colour'].error
    'The value submitted is not one of the allowed values'

Handling Nested Structures
==========================

Not all forms are made from simple field types all representing a
single dictionary of data. Real examples are much more complicated and yet very
few form conversion tools deal with the full complexities of the cases you are
likely to meet. Hopefully FormConvert will though. 

Before we go into the code let's have a quick recap of RecordConvert and
NestedRecord to put the later examples in context.

Quick Recap of RecordConvert and NestedRecord
---------------------------------------------

RecordConvert defines two classes: ``Record()``, which behaves like a Python
dictionary but supports attribute access to the values and places restricitons
on the names you can use as keys, and ``ListOfRecords()`` which behaves like a
Python lists but proxies attribute access to the first item in the list. The
idea is that you model *all* internal data strucutres using *only* records and
lists of records, no records with records as keys, no lists which don't contain
records and no lists which contain different types of records. Although this
appears to make certain types of problem much harder, once you get used to
writing the converters it actually makes everything tremendously simple.

In the NestedRecord data model there are no such thing as single values or
lists of single values. The simplest object is a record and the simplest record
is one with one key and one value:

.. sourcecode :: python

    {key: value}

The simplest list is an empty list:

.. sourcecode :: python

    []

but after that all keys must be records. This means the next simplest list
looks like this:

.. sourcecode :: python

    [{key: value}]

Records can have lists of records as their values so you can have data
structures like this:

.. sourcecode :: python

    [{key: [{key: value}]}]

You can't have any other data structure. No dictionaries with dictionaries for
keys for example.

NestedRecord provides a way to represent the nested data structures
of dictionaries and lists of dictionaries as a flattened data structure by
using a convention on the key names. It turns out this convention is very useful
when representing data as HTML forms because the HTTP protocol only supports
key-value pairs of data. 

Here's an example with three levels of depth:

.. sourcecode :: pycon
       
    >>> from nestedrecord import encode
    >>> example_data = {
    ...     'one': [
    ...          {
    ...              'two': [
    ...                  {
    ...                      'three': 'a'
    ...                  }
    ...              ],
    ...              'four': [
    ...                  {
    ...                      'five': 'b'
    ...                  },
    ...                  {
    ...                      'six': 'c'
    ...                  },
    ...              ]
    ...          }
    ...     ],
    ...     'seven': 'd',
    ... }
    >>> encoded_data = encode(example_data)
    >>> print encoded_data
    {'one[0].two[0].three': 'a', 'seven': 'd', 'one[0].four[0].five': 'b', 'one[0].four[1].six': 'c'}

As you can see the complex nested data structure has been flattened in a
dictionary. The values ``'a'``, ``'b'``, ``'c'`` and ``'d'`` could now be represented in
an HTML form by three fields with names that match the corresponding key in the
dictionary above.

When the form is submitted the data can then be automatically converted back to
the correct data structure without any work from you.

Let's decode the data:

.. sourcecode :: pycon

    >>> from nestedrecord import decode
    >>> print encoded_data
    {'one[0].two[0].three': 'a', 'seven': 'd', 'one[0].four[0].five': 'b', 'one[0].four[1].six': 'c'}
    >>> decoded_data = decode(encoded_data)
    >>> print decoded_data
    {'seven': 'd', 'one': [{'four': [{'five': 'b'}, {'six': 'c'}], 'two': [{'three': 'a'}]}]}
    >>> decoded_data == example_data
    True

As you can see the decoded version of the encoded original example data is the
same as the original example data as you'd expect.

Unfortunately there are a few edge cases where using a "pure" NestedRecord
structure like this doesn't work. In these cases FormConvert steps in to
perform the necessary conversions. In this manual you'll learn what the edge
cases are and how to use FormConvert to solve them.

If you aren't committed to use a NestedRecord data structure as the model for
your application, FormConvert is unlikely to be a great deal of use to you
though.

Relational Data Structures
--------------------------

FormConvert and the NestedRecord data structure model the sorts of
relationships you get when working with SQL relational databases. This means
that even if you aren't using an SQL back-end you'll need to understand the
relationships different objects can have in order to decide how to best handle
forms representing those relationships.

Let's imagine we have the following tables:

Stores sign in information

+--------------+
| authkit_user |
+==============+
| username     |
+--------------+
| password     |
+--------------+

Holds information about the user:

+------------+
| person     |
+============+
| person_id  |
+------------+
| firstname  |
+------------+
| lastname   |
+------------+
| age        |
+------------+
| address_id |
+------------+

Stores the person's address(es):

+------------+
| address    |
+============+
| address_id |
+------------+
| number     |
+------------+
| street     |
+------------+
| city       |
+------------+

There are three ways rows in one table can be related to rows in another:

#. They both represent the same thing in the real world
#. A row from one table is related to many rows from another table
#. One or more rows from one table can be related to one or more rows from another

Each of these cases needs dealing with by an application in different ways. The
terminology for each of these cases in order is:

#. One to one relationship
#. One to many relationship
#. Many to many relationship

It is also to have a row that isn't related to anything else at all but this
case is easy to handle because it just represents a single dictionary of data
so you can treat it in the same way as the examples in the previous section.

One-to-Many Relationships
-------------------------

One to many relationships are when one thing is related to zero or more
instances of another thing. For example a person can have no address
(homeless), one address or many addresses. This is an example of a one to many
mapping.

In NestedRecord, one to many mappings are represented as follows. The thing on
the one side of the mapping, in this case a person, is represented by a Record.
The zero or more instances of the thing on the many side are represented as a
list of records. Here's an example:

.. sourcecode :: pycon

    >>> from recordconvert import Record, ListOfRecords
    >>>
    >>> person = Record(
    ...     person_id = 1,
    ...     firstname = 'James',
    ...     lastname = 'Gardner',
    ...     age = 28,
    ...     address = ListOfRecords(
    ...         [
    ...             Record(
    ...                 address_id = 1,
    ...                 number = 12,
    ...                 street = 'Long Avenue',
    ...                 city = 'Oxford',
    ...             ),
    ...             Record(
    ...                 address_id = 2,
    ...                 number = 5,
    ...                 street = 'Shop Street',
    ...                 city = 'London',
    ...             ),
    ...         ]
    ...     )
    ... )

In this case the person has two addresses. 

If your HTML interface only ever let's a user modify the core person
information or one of the addresses at once you can treat this situation the
same way as all the examples in the previous chapter because each of the things
you are displaying can be easily represented as a single dictionary.

There are two approaches to displaying the address data alongside the person fields:

* As a data grid
* As a checkbox group

When using a data grid, all the address information for each of the person's
addresses is displayed in fields for them to edit. 

When using a checkbox group the IDs of all the addresses are displayed (or some
other identifying property) and the user can tick which addresses are theres.
In this case the boxes for 1 and 2 would be ticked but all the others (imagine
there are also addresses 3, 4 and 5 in the system) would be unticked. 

Let's look at each case, starting with the data grid.

Based on a data grid (or repeating fieldsets)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are cases where you'd like a user to be able to edit all this information
at the same time, possibly even adding or removing addresses as they go. To do
this you need a slightly more sophisticated approach. Each field will need its
own name so you can use NestedRecord to flatten the data structure:

.. sourcecode :: pycon

    >>> from nestedrecord import encode
    >>>
    >>> encoded_person = encode(person)
    >>> print encoded_person
    {'address[1].address_id': 2, 'address[0].address_id': 1, 'firstname': 'James', 'lastname': 'Gardner', 'age': 28, 'address[0].street': 'Long Avenue', 'address[1].city': 'London', 'address[0].number': 12, 'person_id': 1, 'address[1].number': 5, 'address[0].city': 'Oxford', 'address[1].street': 'Shop Street'}

We can use the encoded person as the ``values`` argument to a FormBuild
``Form`` but because there could be a varying number of addresses for each
person the form generation will need to create different numbers of sets of
address fields for displaying different people. For handling this it is easiest
to use the original ``person`` object and encode each address as you use it:

.. sourcecode :: pycon

    >>> form = Form(values=encoded_person)
    >>> output = []
    >>> output.append(form.hidden(name='person_id'))
    >>> output.append(form.text(name='firstname'))
    >>> output.append(form.text(name='lastname'))
    >>> output.append(form.text(name='age'))
    >>> counter = 0
    >>> for address in person.address:
    ...     output.append(form.hidden(name='address[%s].%s'%(counter, 'address_id')))
    ...     output.append(form.text(name='address[%s].%s'%(counter, 'number')))
    ...     output.append(form.text(name='address[%s].%s'%(counter, 'street')))
    ...     output.append(form.text(name='address[%s].%s'%(counter, 'city')))
    ...     counter += 1
    >>> print '\n'.join(output)
    <input name="person_id" type="hidden" value="1" />
    <input id="firstname" name="firstname" type="text" value="James" />
    <input id="lastname" name="lastname" type="text" value="Gardner" />
    <input id="age" name="age" type="text" value="28" />
    <input name="address[0].address_id" type="hidden" value="1" />
    <input id="address0number" name="address[0].number" type="text" value="12" />
    <input id="address0street" name="address[0].street" type="text" value="Long Avenue" />
    <input id="address0city" name="address[0].city" type="text" value="Oxford" />
    <input name="address[1].address_id" type="hidden" value="2" />
    <input id="address1number" name="address[1].number" type="text" value="5" />
    <input id="address1street" name="address[1].street" type="text" value="Shop Street" />
    <input id="address1city" name="address[1].city" type="text" value="London" />

Notice that since ``[`` and ``]`` aren't valid in the ``id`` attributes they
get stripped. Also notice that all fields got their correct values. This code
would work for any person now, regarless of the number of addresses they have.

Here's a validator for the person:

.. sourcecode :: pycon

    >>> from recordconvert import toRecord, toListOfRecords
    >>>
    >>> form_converter = toRecord(
    ...     converters = dict(
    ...         person_id = unicodeToInteger(),
    ...         firstname = unicodeToUnicode(),
    ...         lastname = unicodeToUnicode(),
    ...         age = unicodeToInteger(),
    ...         address = toListOfRecords(
    ...             toRecord(
    ...                 converters = dict(
    ...                     address_id = unicodeToInteger(),
    ...                     number = unicodeToInteger(),
    ...                     street = unicodeToUnicode(),
    ...                     city = unicodeToUnicode(),
    ...                 )
    ...             )
    ...         )
    ...     )
    ... )

Let's set up a fake request representing the form above being submitted.

.. sourcecode :: pycon

    >>> fake_environ = {
    ...     'QUERY_STRING': 'person_id=1&firstname=James&lastname=Gardner&age=28&address[0].address_id=1&address[0].number=12&address[0].street=Long+Avenue&address[0].city=Oxford&address[1].address_id=2&address[1].number=5&address[1].city=London&address[1].street=Shop+Street'
    ... }
    >>> request = Request(fake_environ)

Now let's try the conversion. There's an extra step we need to take after we've got hold of the ``params``. We need to decode the keys to turn them back into a nested structure suitable for the conversion. Here's how:

.. sourcecode :: pycon

    >>> from nestedrecord import decodeNestedRecord
    >>> params = Conversion(request.params).perform(multiDictToDict(encoding='utf-8')).result
    >>> person_params = Conversion(params).perform(decodeNestedRecord()).result
    >>> conversion = Conversion(person_params).perform(form_converter)
    >>> from pprint import pprint
    >>> pprint(conversion.result)
    {u'address': [{u'address_id': 1,
                   u'city': u'Oxford',
                   u'number': 12,
                   u'street': u'Long Avenue'},
                  {u'address_id': 2,
                   u'city': u'London',
                   u'number': 5,
                   u'street': u'Shop Street'}],
     u'age': 28,
     u'firstname': u'James',
     u'lastname': u'Gardner',
     u'person_id': 1}
    >>> conversion.result == person
    True

Ways of representing the relationship on a screen:

* By ID and label only (checkbox group or multiple select box)
* With all the data too

Based on ID only
~~~~~~~~~~~~~~~~

You might want a form with the person details and then a checkbox group for all
the possible addresses so that the user can select which addresses are
associated with the person.

In this case you can use a checkbox group but the usual pattern is to give each
checkbox the same name and a different ID, each representing a address. Then in
the application you simply have to deal with a list of IDs representing the
addresses.

Things might look like this:

.. sourcecode :: pycon

    >>> person = Record(
    ...     person_id = 1,
    ...     firstname = 'James',
    ...     lastname = 'Gardner',
    ...     age = 28,
    ...     address = [1, 2]
    ... )

You can generate such a checkbox group like this passing in the address list
manually but as you'll see in a minute there is a better approach:

.. sourcecode :: pycon

    >>> form = Form(
    ...     values=dict(
    ...         person_id=person.person_id, 
    ...         firstname=person.firstname, 
    ...         lastname=person.lastname, 
    ...         age=person.age, 
    ...         address=[1,2]
    ...     ), 
    ...     options=dict(address=[(1,1),(2,2),(3,3)])
    ... )
    >>> output = []
    >>> output.append(form.hidden(name='person_id'))
    >>> output.append(form.text(name='firstname'))
    >>> output.append(form.text(name='lastname'))
    >>> output.append(form.text(name='age'))
    >>> output.append(form.checkbox_group(name='address'))
    >>> print '\n'.join(output)
    <input name="person_id" type="hidden" value="1" />
    <input id="firstname" name="firstname" type="text" value="James" />
    <input id="lastname" name="lastname" type="text" value="Gardner" />
    <input id="age" name="age" type="text" value="28" />
    <input type="checkbox" name="address" value="1" checked="checked" /> 1
    <input type="checkbox" name="address" value="2" checked="checked" /> 2
    <input type="checkbox" name="address" value="3" /> 3

.. tip ::

   You might be wondering what the ``options`` argument is above. It is simply
   a list of (id, label) pairs of all the possilbe options for a checkbox group.
   The key should be the same as the name specified for the checkbox group. In
   this case this is ``address`` but in a more complex example it could be
   ``person[1].address`` or something similar. It is not the ``sub_name``, an
   argument to ``form.checkbox_group()`` which you'll learn about in a bit.

   You might also be wondering why the options are specified in the ``Form``
   constructor and not as an argument to ``form.checkbox_group()``. The answer is
   that the options for checkbox groups are often calculated from a database
   query. FormBuild encourages separation between templating code and database
   code. Structured this way, the database code can occur as the ``Form`` object
   is constructed and then the call to ``form.checkbox_group()`` can occur in
   template code without needing any access to a database to determine which
   options it should be producing checkboxes for.

This works fine, but there's a better way. You'll recall that single values
aren't allowed in the NestedRecord data model, this means that you'll want each
ID to represent a complete record. Rather than giving each item the same name
you give it the name of the ``address_id`` as though each is a separate
record. 

We want the data structure to look like this instead:

.. sourcecode :: pycon

    >>> person = Record(
    ...     person_id = 1,
    ...     firstname = 'James',
    ...     lastname = 'Gardner',
    ...     age = 28,
    ...     address = ListOfRecords(
    ...         [
    ...             Record(
    ...                 address_id = 1,
    ...             ),
    ...             Record(
    ...                 address_id = 2,
    ...             ),
    ...         ]
    ...     )
    ... )

Now we can encode this data as before and we don't have to specify any values manually:

.. sourcecode :: pycon

    >>> form = Form(
    ...     values=encode(person), 
    ...     options=dict(address=[(1,1),(2,2),(3,3)])
    ... )
    >>> output = []
    >>> output.append(form.hidden(name='person_id'))
    >>> output.append(form.text(name='firstname'))
    >>> output.append(form.text(name='lastname'))
    >>> output.append(form.text(name='age'))
    >>> output.append(form.checkbox_group(name='address', sub_name='address_id'))
    >>> print '\n'.join(output)
    <input name="person_id" type="hidden" value="1" />
    <input id="firstname" name="firstname" type="text" value="James" />
    <input id="lastname" name="lastname" type="text" value="Gardner" />
    <input id="age" name="age" type="text" value="28" />
    <input type="checkbox" name="address[0].address_id" value="1" checked="checked" /> 1
    <input type="checkbox" name="address[1].address_id" value="2" checked="checked" /> 2
    <input type="checkbox" name="address[2].address_id" value="3" /> 3

Let's set up a fake request representing the form above being submitted.

.. sourcecode :: pycon

    >>> fake_environ = {
    ...     'QUERY_STRING': 'person_id=1&firstname=James&lastname=Gardner&age=28&address[0].address_id=1&address[1].address_id=2'
    ... }
    >>> request = Request(fake_environ)

Let's see how this turns out when processed in the application:

.. sourcecode :: pycon

    >>> from recordconvert import toRecord, toListOfRecords
    >>>
    >>> form_converter = toRecord(
    ...     converters = dict(
    ...         person_id = unicodeToInteger(),
    ...         firstname = unicodeToUnicode(),
    ...         lastname = unicodeToUnicode(),
    ...         age = unicodeToInteger(),
    ...         address = toListOfRecords(
    ...             toRecord(
    ...                 converters = dict(
    ...                     address_id = unicodeToInteger(),
    ...                 )
    ...             )
    ...         )
    ...     )
    ... )

Now let's try the conversion. Again, there's an extra step we need to take after we've
got hold of the ``params``. We need to decode the keys to turn them back into a
nested structure suitable for the conversion. Here's how:

.. sourcecode :: pycon

    >>> from nestedrecord import decodeNestedRecord
    >>> params = Conversion(request.params).perform(multiDictToDict(encoding='utf-8')).result
    >>> person_params = Conversion(params).perform(decodeNestedRecord()).result
    >>> conversion = Conversion(person_params).perform(form_converter)
    >>> pprint(conversion.result)
    {u'address': [{u'address_id': 1}, {u'address_id': 2}],
     u'age': 28,
     u'firstname': u'James',
     u'lastname': u'Gardner',
     u'person_id': 1}
    >>> conversion.result == person
    True

If you want the list of ticked checkboxes you can easily do this:

.. sourcecode :: pycon

    >>> [address['address_id'] for address in conversion.result.address]
    [1, 2]

As you can see, by structuring your data properly you can make form processing much more automatic.

.. caution ::

   You might be tempted to deduce something from the order of the fields. For
   example the second checkbox will always come before the first in the decoded
   data structure's list of records for the addresses. It is best not to rely on
   this though and instead use the real ID as the value of each checkbox. Failing
   that you can always set hidden fields for other variables to be decoded to
   create more complete records on the server side.

Many-to-Many Relationships
--------------------------

A many-to-many relationship is when one or more instances of one entity are
related to zero or more instances of another. For example, in real life more
than one person often lives at an address this means that an address has zero
or more people associated with it and a person might have zero or more
addresses associated with him or her.

When dealing with forms though, you only ever deal with one entity at once. For
example you are either editing an address and changing the people known to be
living there or editing a person's record to adjust which addresses they are
known to live at so you never provide an interface showing both ways of
thinking about it at the same time.

If you think about how you would implement a many-to-many mapping in a
relational database, the reasoning becomes clear. You actually introduce a
third table and each entitiy has a one to many relationship with the third
table which is why a many-to-many mapping can be decomposed into two
one-to-many mappings for the purposes of form handling.

This means that handling a many to many mapping in a form is exaclty the same
as handling a one-to-many mapping from the point of view of the entity being
changed. The only differences wihh a many-to-many mapping are that:

* you will need two forms, one to handle each entity
* one end of each one-to-many mapping will be the link table, not the other entity

One-to-One Relationships
------------------------

There's one type of relationship we haven't thought of yet: the one-to-one
relationship. As an example think about a person again. In addition to the
name, age etc (stored in the ``person`` table) you might need to store signin
information for the user such as username and password.

The ideal way of modelling this situation is to keep the sign in information
with the person information (ie in the same table in the case of a relational
database) but this isn't always possible. You might want to use a third party
program for managing the sign in data for example. In these cases you have two
choices:

* Create a combined record with the keys for the person from both tables 
* Treat the situation as a one-to-many mapping

The first option might sound quite appealing but as soon as you do this there
is no easy way programatic way to determine which keys are from which table.
This results in your data being harder to work with than you might imagine.

The better approach is the second becasue it actually models the underlying
data structure better. To use it though you have to decide which of the two
tables is going to be modelled as the *one* side of the one-to-many mapping.
I'm going to choose the ``authkit_user`` table.

.. sourcecode :: pycon

    >>> from recordconvert import Record, ListOfRecords
    >>>
    >>> person = Record(
    ...     person_id = 1,
    ...     firstname = 'James',
    ...     lastname = 'Gardner',
    ...     age = 28,
    ...     address = ListOfRecords(
    ...         [
    ...             Record(
    ...                 address_id = 1,
    ...                 number = 12,
    ...                 street = 'Long Avenue',
    ...                 city = 'Oxford',
    ...             ),
    ...             Record(
    ...                 address_id = 2,
    ...                 number = 5,
    ...                 street = 'Shop Street',
    ...                 city = 'London',
    ...             ),
    ...         ]
    ...     ),
    ...     authkit_user = ListOfRecords(
    ...         [
    ...             Record(
    ...                 username = 'jim',
    ...                 password = '1234'
    ...             )
    ...         ]
    ...     ),
    ... )
    >>> person.authkit_user.username
    'jim'

Now you can deal with the ``person`` table and the ``authkit_user`` table the
same way as the relationship between ``person`` and ``address``. The only
difference is that there will never be more than one record for the list of
authkit_user records.

Handling Errors
===============

When errors occur during the conversion the ``conversion.successful`` attribute
will be ``False``. There will then be an error associated with each level of
the error hierachy. You can encode this hierachy using the ``encode_error()``
function from the ``nestedrecord`` module provided by the NestedError package.

Using the checkbox group example from earlier, we get this if there is an error in the data submitted

First let's import the ``encode_error()`` function:

.. sourcecode :: pycon

    >>> from nestedrecord import encode_error

.. sourcecode :: pycon

    >>> person = Record(
    ...     person_id = 1,
    ...     firstname = 'James',
    ...     lastname = 'Gardner',
    ...     age = 28,
    ...     address = ListOfRecords(
    ...         [
    ...             Record(
    ...                 address_id = 'this will cause an error',
    ...             ),
    ...             Record(
    ...                 address_id = 2,
    ...             ),
    ...         ]
    ...     )
    ... )
    >>> fake_environ = {
    ...     'QUERY_STRING': 'person_id=1&firstname=James&lastname=Gardner&age=28&address[0].address_id=this+will+cause+an+error&address[1].address_id=2'
    ... }
    >>> request = Request(fake_environ)
    >>> from nestedrecord import decodeNestedRecord
    >>> params = Conversion(request.params).perform(multiDictToDict(encoding='utf-8')).result
    >>> person_params = Conversion(params).perform(decodeNestedRecord()).result
    >>> conversion = Conversion(person_params).perform(form_converter)
    >>> conversion.successful
    False
    >>> errors = encode_error(conversion)
    >>> pprint(errors)
    {u'address': 'One of the items was not valid',
     u'address[0]': 'The address_id field is invalid',
     u'address[0].address_id': "invalid literal for int() with base 10: 'this will cause an error'"}

The error messages are now named in a similar fashion to the encoded field
names which makes working with them much easier. If you were using
``form.field()`` to create the HTML for each field you could use the ``errors``
dictionary above as the ``errors`` argument to ``Form`` to have the error
messages which are directly associated with fields displayed next to them
automatically. That's beyond the scope of this documentation though.

Handling the Difficult Cases
============================

There are a few situations where the NestedRecord approach can't easily be
used. We'll look at these problems in this section as well as their solutions.

Handling Image Buttons
----------------------

When you are using an image button to submit a form, the browser will add two
new field names made from the ``name`` attribute of the submit input image
button followed by ``.x`` and ``.y``. These contain the co-ordinates where the
image was clicked.

If you want to access this information you can do so by treating the x an y
coordinates as two values of a record contained in a list of records.

For example, here are the form fields:

.. sourcecode :: pycon

    >>> form = Form()
    >>> output = []
    >>> output.append(form.text(name='username'))
    >>> output.append(form.password(name='password'))
    >>> output.append(form.image_button(name='submit', value="Sign in"))
    >>> print '\n'.join(output)
    <input id="username" name="username" type="text" />
    <input id="password" name="password" type="password" />
    <input name="submit" type="image" value="Sign in" />

The resulting query string might look like this (note the extra submission):

.. sourcecode :: pycon

    >>> fake_environ = {
    ...     'QUERY_STRING': 'username=james&password=1234&submit.x=51&submit.y=13&submit=Sign+in'
    ... }

This is hard to process because the NestedRecord model doesn't allow the naming convention the fields happen to have. FormConvert provides two choices:

* Strip the fields completely and lose the information about where the user clicked and what the value of the button was
* Modify the ``params`` before they are passed to ``decodeNestedRecord()`` so that they are in a more appropriate format

Either way we use the ``handleSubmitImage()`` converter.

.. sourcecode :: pycon

    >>> from formconvert import handleSubmitImage

Stripping the Image Submit Data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's look at the case where you simply strip the data first:

.. sourcecode :: pycon

    >>> form_converter = toRecord(
    ...     converters = dict(
    ...         username = unicodeToUnicode(),
    ...         password = unicodeToUnicode(),
    ...     )
    ... )
    >>> request = Request(fake_environ)
    >>> params = Conversion(request.params).perform(multiDictToDict(encoding='utf-8')).result
    >>> modified_params = Conversion(params).perform(handleSubmitImage(name='submit', strip=True)).result
    >>> person_params = Conversion(modified_params).perform(decodeNestedRecord()).result
    >>> conversion = Conversion(person_params).perform(form_converter)
    >>> print conversion.result
    {u'username': u'james', u'password': u'1234'}

There are quite a lot of conversions going on here so it might be neater to use
the ConversionKit ``chainConverters()`` converter to make it neater. 

.. sourcecode :: pycon 

    >>> from conversionkit import chainConverters

Here's the same thing written in a more compact way: 

.. sourcecode :: pycon

    >>> combined_converter = chainConverters(
    ...     multiDictToDict(encoding='utf-8'), 
    ...     handleSubmitImage(name='submit', strip=True),
    ...     decodeNestedRecord(), 
    ...     form_converter
    ... )
    >>> conversion = Conversion(request.params).perform(combined_converter)
    >>> print conversion.result
    {u'username': u'james', u'password': u'1234'}

Modifying the Image Submit Data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is very similar but you use the ``submit_image_to_record`` converter to
convert the submit image data:

.. sourcecode :: pycon

    >>> from formconvert import submit_image_to_record

You then use ``handleSubmitImage()`` again, but pass it ``strip=False`` (the default):

.. sourcecode :: pycon

    >>> form_converter = toRecord(
    ...     converters = dict(   
    ...         username = unicodeToUnicode(),
    ...         password = unicodeToUnicode(),
    ...         submit = submit_image_to_record,
    ...     )
    ... )
    >>> request = Request(fake_environ)
    >>> combined_converter = chainConverters(
    ...     multiDictToDict(encoding='utf-8'),
    ...     handleSubmitImage(name='submit'),
    ...     decodeNestedRecord(),
    ...     form_converter
    ... )
    >>> conversion = Conversion(request.params).perform(combined_converter)
    >>> pprint(conversion.result)
    {u'password': u'1234',
     u'submit': [{u'x': 51, u'y': 13}],
     u'username': u'james'}
    >>> conversion.result.submit.x
    51

Handling Multiple Fields With The Same Name (Multi-Valued Select Boxes)
-----------------------------------------------------------------------

Sometimes the form you are converting has multiple fields with the same name.
The best way to handle this is to give the fields a different name becuase the
NestedRecord ``decode()`` function does not expect lists of values for the same
key. You've already seen how we solved this problem in the case of checkbox
groups earlier by using the ``sub_name`` argument to ``form.checkboc_group()``.

It turns out that all fields can be handled by giving them each a key
corresponding to their position in a nested record data structure flattened by
the ``encode()`` function except in the image button case just discussed and
one rare case: a select field with its ``multiple`` attribute set and with more
than one value selected by the user. In this case the browser submits each of
the values under the same field name so we have to be able to cope with this
behaviour.

Here's some sample HTML which demonstrates a problematic set up:

.. sourcecode :: pycon

    >>> form = Form(
    ...     values=dict(fruit=[1,2]), 
    ...     options=dict(fruit=[(1, 'Apples'), (2, 'Pears'), (3, 'Bananas')])
    ... )
    >>> form.combo(name='fruit')
    literal(u'<select id="fruit" multiple="multiple" name="fruit" size="4">\n<option selected="selected" value="1">Apples</option>\n<option selected="selected" value="2">Pears</option>\n<option value="3">Bananas</option>\n</select>')

When this form gets submitted the QUERY_STRING will look like this:

.. sourcecode :: pycon

    >>> fake_environ = {
    ...     'QUERY_STRING': 'fruit=1&fruit=2'
    ... }

We can't decode this using the NestedRecord data structure because there are
two values for the field ``fruit`` but once again we can envisage a ``fruit``
key with a ``ListOfRecords`` value containing records for different types of
fruit. For this to work we'll need a converter which removes the ``fruit`` keys
and replaces them with something like this:

::

    fruit[0].fruit_id=1
    fruit[1].fruit_id=2

The ``refactorDuplicateFields()`` converter does just this.

.. sourcecode :: pycon

    >>> from formconvert import refactorDuplicateFields

Let's create a converter for the submitted fields:

.. sourcecode :: pycon

    >>> fruit_converter = toRecord(
    ...     converters = dict(
    ...         fruit = toListOfRecords(
    ...             toRecord(
    ...                 converters = dict(
    ...                     fruit_id = unicodeToInteger(),
    ...                 )
    ...             )
    ...         )
    ...     )
    ... )

Now for the conversion:

.. sourcecode :: pycon

    >>> request = Request(fake_environ)
    >>> combined_converter = chainConverters(
    ...     multiDictToDict(encoding='utf-8'),
    ...     refactorDuplicateFields('fruit', 'fruit_id'),
    ...     decodeNestedRecord(),
    ...     fruit_converter
    ... )
    >>> conversion = Conversion(request.params).perform(combined_converter)
    >>> print conversion.result
    {u'fruit': [{u'fruit_id': 1}, {u'fruit_id': 2}]}
    >>> conversion.result.fruit[0].fruit_id
    1

Handling FieldSets
------------------

Sometimes you want a form with fields from more than one database table. If the
field names from each table were different you could get away with having them
all in the same form but if some of the columns have the same names you need a
more sophisticated approach.

In the application you will want to deal with two sets of records so the best
thing to do is give each record a name and encode them. The encoded field names
can then be used in the form and then decoded into the two records once the data
is submitted. Here's an example of encoding the data for use in the form. We
only show the field for the address firstname, but notice how the field name
for the input field uses the encoded key name:

.. sourcecode :: pycon

    >>> from recordconvert import Record, ListOfRecords
    >>> from nestedrecord import encode
    >>> account = Record(
    ...     username='jim',
    ...     password=123456,
    ... )
    >>> address1=Record(
    ...     number = 12,
    ...     city = 'London',
    ... )
    >>> data = Record(
    ...     address=ListOfRecords(address1),
    ...     account=ListOfRecords(account),
    ... )
    >>> encoded_data = encode(data)
    >>> print encoded_data
    {'address[0].number': 12, 'account[0].password': 123456, 'address[0].city': 'London', 'account[0].username': 'jim'}

Then let's create a dummy request using the WebOb pacakge:

.. sourcecode :: pycon

    >>> # Should really encode v below but the strings we've chosen are safe anyway
    >>> query_string = '&'.join(['%s=%s'%(k,v) for k, v in encoded_data.items()])
    >>> print query_string
    address[0].number=12&account[0].password=123456&address[0].city=London&account[0].username=jim
    >>> fake_environ = {
    ...     'QUERY_STRING': query_string,
    ... }

Now let's use the request in a pre-validator:

.. sourcecode :: pycon

    >>> from formconvert import multiDictToDict
    >>> from conversionkit import chainConverters
    >>> from stringconvert.email import unicodeToEmail
    >>> contact_to_dictionary = chainConverters(
    ...     multiDictToDict(encoding='utf-8'), 
    ...     decodeNestedRecord(),
    ...     toRecord(
    ...         converters = dict(
    ...             account=toListOfRecords(
    ...                 toRecord(
    ...                     converters = dict(
    ...                         username = unicodeToUnicode(),
    ...                         password = unicodeToUnicode(),
    ...                     )
    ...                 )    
    ...             ),
    ...             address=toListOfRecords(
    ...                 toRecord(
    ...                     dict(
    ...                         number = unicodeToInteger(),
    ...                         city = unicodeToUnicode(),
    ...                     )
    ...                 )
    ...             )
    ...         )
    ...     )
    ... )

Let's pass the entire request as the argument to convert:

.. sourcecode :: pycon

    >>> request = Request(fake_environ)
    >>> result = Conversion(request.params).perform(contact_to_dictionary).result
    >>> pprint(result)
    {u'account': [{u'password': u'123456', u'username': u'jim'}],
     u'address': [{u'city': u'London', u'number': 12}]}

Useful Converters
=================

FormConvert also provides some useful converters you might wish to use to help handle specific cases. These include:

.. sourcecode :: pycon

    >>> from formconvert import excludeFields, sameValue, removeFieldsIfOtherFieldResultIs, duplicateField, exacltyOneFieldFrom
    >>> raise NotImplementedError("The documentation for the above imports hasn't been written yet.")


