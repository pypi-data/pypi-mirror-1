ConversionKit Manual
++++++++++++++++++++

ConversionKit is a general purpose toolkit designed from the ground up to:

* Allow you to encapsulate conversion functionality into reusable components
* Provide a unified API to perform a conversion, no matter how complex
* Simplify the process of performing conversions

The ConversionKit package provides a low-level API on which other packages can
build. ConversionKit includes support for compound and nested types and can be
used for:

* Unit conversions
* HTML form handling
* URL parsing and generation
* Encoding to and from SQL data types
* Much, much more...

The ConversionKit package contains the core code, other packages such as a
`URLConvert <http://jimmyg.org/work/code/urlconvert/index.html>`_, `FormConvert
<http://jimmyg.org/work/code/formconvert/index.html>`_ and `ConfigConvert
<http://jimmyg.org/work/code/configconvert/index.html>`_ provide
domain-specific APIs on top of ConversionKit.

Chapter 1: Getting Started
++++++++++++++++++++++++++

Before you learn how to use ConversionKit it is important you are aware of how
a closure works in Python because ConversionKit uses them extensively as a
slightly safer way of working with converters than using Python classes.
Although "closure" is a fancy name, it just describes what happens to local
variables when a function returns another function defined within it; it's a
really simple technique. ConversionKit doesn't use any of the magic you might
have seen in other conversion packages. There are no decorators, generators,
meta-classes, inheritance or complex code.

If you haven't heard the word "closure" before take a look at 
`Appendix A: Primer on Functional Python Programming`_ before continuing otherwise 
the techniques described in this manual may appear unfamiliar.

Writing Converters
==================

Now that you've read the functional Python primer let's see look at how to
write a ConversionKit *converter*. Although you might never need to write your
own converter if you are simply using existing ones it is still helpful to
know how they are implemented and how they work.

Here is a converter which converts a Python string to an integer. A production
implementation of a string-to-integer converter can be found in the FormConvert
package which also contains many other converters for converting Python values
to and from strings.

::

    >>> def stringToInteger():
    ...     def stringToInteger_converter(conversion, state=None):
    ...         try:
    ...             result = int(conversion.value)
    ...         except Exception, e:
    ...             conversion.error = str(e)
    ...         else:
    ...             conversion.result = result
    ...     return stringToInteger_converter

There is quite a lot going on in this example so before we look at how to use
it to perform a conversion let's look at the conventions which it meets:

1. The converter is implemented as a function which returns a function

    The outer function sets up the inner function which it returns. The inner
    ``stringToInteger_converter()`` function is what is actually responsible for
    performing the conversion.

2. The outer function is named in camelCase but starting with a lowercase letter 
   so that it still conforms to `PEP 8 <http://www.python.org/dev/peps/pep-0008/>`_

    As you learned in the functional Python primer the outer function behaves
    as if it is a Python class with a ``__call__()`` method so it is useful to
    distiguish between this type of function and functions which don't behave like
    classes. ConversionKit (and the packages which rely on it) follow a convention
    where functions which return functions (and thus behave a bit like classes) are
    named in camelCase with a lower case first letter and all other functions are
    named with underscores.

    .. caution :: 

        Not all Python packages obey this naming convention. Modules in the
        Standard Library for example use a combination of underscores and
        camelCase without any meaning implied by either.

3. The inner and outer function names are related

    Inner functions should have the same name as their corresponding outer function
    but with the string ``_converter`` appended to their name. 

    It is important to stick to this convention because if an exception occurs
    somewhere in your code, the name of the inner function is the only thing which
    will help you identify it. This is because Python doesn't print a full module
    path for functions returned from other functions, it only uses their name:
    
    .. sourcecode :: pycon
    
        >>> stringToInteger()
        <function stringToInteger_converter at ...>
    
    If you had just named the inner function something like ``converter`` it
    would still work correctly but it would be harder to debug in the
    event of an unexpected exception.

4. The outer function can take any number of arguments

    The arguments passed to the outer function are used to configure the inner
    function. In this case the ``stringToInteger_converter()`` function needs
    no configuration so the outer ``stringToInteger()`` function takes no 
    arguments.

5. The inner function takes exactly two arguments, ``conversion`` which is required 
   and ``state`` which is optional

    The first argument is always an instance of a ``Conversion`` object which is used
    to keep track of the state of the conversion itself. The ``Conversion``
    instance contains the value to be converted as its ``.value`` attribute. The
    second argument is an optional ``state`` object which can contain any objects,
    functions or other data necessary to perform the conversion. You'll learn more
    about the state in the "Understanding State" section so let's concentrate on
    the ``conversion`` argument.

6. The inner function is responsible for actually performing the conversion

    The value to be converted is available as the ``.value`` attribute of the
    object passed as the ``conversion`` argument.

7. The inner function must set an error or a result on the object passed as 
   the ``conversion`` argument

    If the conversion could not be performed, the inner function must set a
    ``.error`` attribute which must be a string describing the error which
    occurred. Otherwise it must set a ``.result`` attribute containing the result
    of the conversion. The inner function must not set both an ``.error`` 
    attribute and a ``.result`` attribute. If a result is set it is assumed
    the conversion was successful.

8. The inner function must not modify the ``.value`` attribute of the object
   passed as the ``conversion`` argument

    conversion objects should always provide access to the
    original value before the conversion took place via their ``.value`` attribute
    so you should be careful not to change this value when writing your own
    converters.
    
    One case where it is easy to accidentally change the original value is when you
    are converting a dictionary of values such as this one:

    .. sourcecode :: python
    
        {'key1': '1', 'key2': '2'}
    
    Then in the converter you might write this by mistake:
    
    .. sourcecode :: pycon 
    
        result = conversion.value
        result['key1'] = 1
        result['key2'] = 2
        conversion.result = result
    
    In this situation modifying the ``result`` dictionary also modifies the
    ``conversion.value`` dictionary becasue the first line makes ``result`` and
    ``conversion.value`` point to the same dictionary, it doesn't make ``result`` a
    copy of ``conversion.value``. You can see that ``conversion.value`` is no
    longer the same as the original value, the values are now integers:
    
    .. sourcecode :: python
    
        {'key2': 2, 'key1': 1}
    
    Instead you should create a copy of the original values like this:
    
    .. sourcecode :: pycon 
    
        result = conversion.value.copy()
        result['key1'] = 1
        result['key2'] = 2
        conversion.result = result

    The value of ``conversion.value`` would now be 
    ``{'key2': '2', 'key1': '1'}`` and the value of ``conversion.result`` 
    would be ``{'key2': 2, 'key1': 1}``.
    
    Of course, this is just standard Python behaviour but it might catch you out
    if you aren't expecting it.

9. The inner function should be designed in such a way that it can be used
    more than once

    This means it shouldn't set any variables the first time it is used which 
    would adversely affect its behaviour on subsequent calls.

Now that you've seen the main rules that a converter must meet, take another
look at the example and satisfy for yourself that it meets them.

Configuring Converters
----------------------

Some converters you will write will need configuration. This can be done by
passing arguments to the outer function. 

If you want to write a converter which requires some configuration you need to
write an outer function which accpets arguments which are then accessible from
the returned inner function. All the previous rules about converters apply in
the new case but there is one additional rule:

10. The inner function should not directly modify the arguments passed to the outer function

    Otherwise if the outer function contains default arguments the second time
    you called the outer function the defaults might have changed which would
    result in different behaviour of the inner function.

As an example consider the ``stringToDate`` converter below. The ``format``
argument to the outer function is used to determine how the string should be
parsed in the inner function.

.. sourcecode :: pycon

    >>> import datetime
    >>> def stringToDate(format='%d/%m/%Y'):
    ...     def stringToDate_converter(conversion, state=None):
    ...         try:
    ...             result = datetime.datetime.strptime(
    ...                 conversion.value, 
    ...                 format
    ...             )
    ...         except ValueError, e:
    ...             conversion.error = str(e)
    ...         else:
    ...             conversion.result = datetime.date(
    ...                 result.year, 
    ...                 result.month,
    ...                 result.day 
    ...             )
    ...     return stringToDate_converter

Performing Single Conversions
=============================

Now that you've seen some simple converters, let's look at how you would use them.

Each conversion you perform with ConversionKit requires two things:

* A converter such as the ``stringToInteger()`` converter above
* A ``Conversion`` object to provide the value being converted and keep track of the error or result

You might be surprised to hear that you never actually use a converter
directly. Instead you use the ``Conversion`` object's ``perform()`` method to
perform the conversion using the converter.

First import the ``Conversion`` class from the ``ConversionKit`` module.

.. sourcecode :: pycon

    >>> from conversionkit import Conversion

Now perform the conversion with a converter, specifying the value to be
converted as the argument to ``Conversion``. Internally, the argument gets set
as the ``.value`` attribute of the ``conversion`` instance:

.. sourcecode :: pycon

    >>> conversion = Conversion('2009')
    >>> conversion.perform(stringToInteger())
    <conversionkit.Conversion object at ...>
    >>> print conversion.result
    2009

As you can see, after the conversion the result can be accessed via the
conversion's ``.result`` attribute. The original value is still available via
the ``.value`` attribute:

.. sourcecode :: pycon

    >>> conversion.value
    '2009'

The idea is that you'll create a different ``Conversion`` object for each
conversion you wish to perform. They are very lightweight so there isn't a
large performance impact for this. You can't perform another conversion on the
same ``conversion`` object or you will get an exception:

.. sourcecode :: pycon

    >>> conversion.perform(stringToInteger())
    Traceback (most recent call last):
      ...
    ConversionKitError: A converter has already been applied to this conversion object

.. note ::

    This might all seem like a lot of effort to go to for such a simple
    conversion but the power of ConversionKit is that the infrastructure you use
    for simple examples such as this is exactly the same as the infrastructure used
    for very complex conversions so you only need to learn one set of techniques to
    enable you to deal with the vast majority of cases you'll encounter.

When Errors Occur
-----------------

Not all conversions will be possible because sometimes the value being
converted might not be valid. In such circumstances an exception will be raised
with a description of the error. Here we are trying to convert the string
``'_33_'`` to an integer:

.. sourcecode :: pycon

    >>> conversion = Conversion('_33_')
    >>> conversion.perform(stringToInteger())
    <conversionkit.Conversion object at ...>
    >>> print conversion.result
    Traceback (most recent call last):
      ...
    ConversionError: invalid literal for int() with base 10: '_33_'

You can test for this exception and handle the error like this:

.. sourcecode :: pycon

    >>> import conversionkit
    >>> conversion = conversionkit.Conversion('_33_')
    >>> conversion.perform(stringToInteger())
    <conversionkit.Conversion object at ...>
    >>> try:
    ...     result = conversion.result
    ... except conversionkit.ConversionError, e:
    ...     error = str(e)
    ...     print "The conversion failed: %r"%(error)
    ... else:
    ...     print "The conversion succeeded: %r"%(result)
    The conversion failed: "invalid literal for int() with base 10: '_33_'"

This is rather cumbersome so ConversionKit provides an alternative API which is
more commonly used. After a conversion has been applied the ``conversion``
instance has a ``.successful`` attribute which is set to either ``True`` or
``False``. If it is ``True`` then the ``.result`` attribute will contain the
result, otherwise the ``.error`` attribute will contain a string describing the
error. The error description accessed at ``.error`` is the same as the one
which would be raised in the ``ConversionError`` if you tried to access the
``.result`` attribute when ``.successful`` is ``False``.

.. sourcecode :: pycon

    >>> conversion = Conversion('_33_')
    >>> conversion.perform(stringToInteger())
    <conversionkit.Conversion object at ...>
    >>> if conversion.successful:
    ...     print "The conversion succeded: %r"%conversion.result
    ... else:
    ...     print "The conversion failed: %r"%conversion.error
    The conversion failed: "invalid literal for int() with base 10: '_33_'"

Exceptions You Might See
------------------------

If you try to access the ``.successful`` attribute before a result or an error
has been set on the conversion, an exception is raised:

.. sourcecode :: pycon

    >>> conversion = Conversion('Some value')
    >>> conversion.successful
    Traceback (most recent call last):
       ...
    ConversionKitError: No conversion has been performed yet

If the converter you are using isn't written properly and fails to set an error
or a result you will get an excetion when you call its ``perform()`` method. To
demonstrate this we need a faulty converter such as the one below.

.. sourcecode :: pycon

    >>> def toFaulty():
    ...     def toFaulty_converter(converison, state=None):
    ...         return conversion
    ...     return toFaulty_converter

Let's see what happens when we try to use it:

.. sourcecode :: pycon

    >>> conversion = Conversion('Some value')
    >>> conversion.perform(toFaulty())
    Traceback (most recent call last):
       ...
    ConversionKitError: The converter <function toFaulty_converter at 0x...> doesn't work correctly, it failed to set a result or an error.

It's worth being aware that you can't set an error or a result twice on the
same conversion either.

Configuring Converters
----------------------

If the converter requires configuration (like the ``stringToDate`` converter
you've already seen) you would set up the conversion like this:

.. sourcecode :: pycon

    >>> conversion = Conversion('2009-02-21')
    >>> conversion.perform(stringToDate('%Y-%m-%d'))
    <conversionkit.Conversion object at ...>
    >>> if conversion.successful:
    ...     print "The conversion succeeded: %r"%conversion.result
    ... else:
    ...     print "The conversion failed: %r"%conversion.error
    The conversion succeeded: datetime.date(2009, 2, 21)

Performing Conversions in One Step
----------------------------------

You can shorten the process like this:

.. sourcecode :: pycon

    >>> Conversion('2009-02-21').perform(stringToDate('%Y-%m-%d')).result
    datetime.date(2009, 2, 21)

This works because the ``perform()`` method returns the ``conversion`` object it
is acting on so accessing ``.result`` on the result of calling the method is
the same as accessing it directly on the conversion.

Re-Using Converters
-------------------

Although you can't apply a second converter to the same conversion, converters
themselves are desgined to be used on multiple different conversions so you can
do this:

.. sourcecode :: pycon

    >>> string_to_date_converter = stringToDate('%Y-%m-%d')
    >>> Conversion('2009-02-21').perform(string_to_date_converter).result
    datetime.date(2009, 2, 21)
    >>> Conversion('2009-02-20').perform(string_to_date_converter).result
    datetime.date(2009, 2, 20)

Notice that the same ``string_to_date_converter`` function is used in both
conversions but that two instances of the ``Conversion`` class are needed, one
conversion instance per conversion. 

.. tip :::

    Notice that the ``string_to_date_converter`` variable representing the
    ``stringToDate_converter()`` inner function returned by ``stringToDate()`` is
    named with underscore characters rather than camelCase to make it clear that it
    does not behave like a class.

Using the ``oneOf()`` Converter
-------------------------------

Sometimes you might want to confirm that a value is one of an allowed number of
values. You can do this with the ``oneOf`` converter. It works like this:

.. sourcecode :: pycon
    
    >>> from conversionkit import oneOf
    >>>
    >>> allowed_values = oneOf([1,2,3])
    >>> print Conversion(2).perform(allowed_values).result
    2
    >>> print Conversion(4).perform(allowed_values).error
    The value submitted is not one of the allowed values

.. note ::

    The ``oneOf`` converter isn't really a converter at all because it doesn't
    perform any conversion. Instead it mearly *validates* that a value is one of a
    set of allowed values. ConversionKit doesn't make a distinction between
    validators and converters because they both have the exactly the same APIs,
    taking a value and producing a result or an error.

    Some developers have suggested that ConversionKit could be improved by
    separating the roles of converters and validators and if your particular
    application would benefit from this approach you are free to implement your 
    own converters and validators separately. I've always found it most useful 
    to combine these roles so that converters attempt to perform a conversion, 
    displaying appropriate error messages if a conversion is not possible. This
    is the approach taken by ConversionKit.

The ``tryEach()`` Converter
-----------------------------

Another useful converter is the ``tryEach()`` converter which takes a series of
converters as arguments and tries each in turn until one successfully handles
the conversion without an error.

.. sourcecode :: pycon

    >>> from conversionkit import tryEach
    >>> each = tryEach(
    ...     [
    ...         stringToInteger(),
    ...         stringToDate('%Y-%m-%d'),
    ...     ]
    ... )
    >>>
    >>> Conversion('2009-07-31').perform(each).result
    datetime.date(2009, 7, 31)

There are options to allow you to stop on the first error, stop on the first
good result, try all of them regardless, have the result and children as a
dictionary instead of a list and also to set the error message if no results
are found.

Performing Multiple Conversions on the Same Value
=================================================

As you've already learned, each conversion can only use one converter. What if
you want to apply multiple converters to a conversion? The answer is that you
have to create multiple conversion objects and copy the ``.result`` attribute
from the first to the ``.value`` attribute of the second before the conversion.

The ``noConversion()`` Converter
--------------------------------

There's a converter called the ``noConversion`` converter which simply sets the
result of a conversion to be a *copy* of the input value. This isn't
particularly useful on its own but as you'll see in Chapter 3, it can be handy
when dealing with *compound conversions* when one part of a compound data type
doesn't actually need converting.

When used on its own it looks like this:

.. sourcecode :: pycon

    >>> from conversionkit import noConversion
    >>>
    >>> value = 'Any value'
    >>> conversion = Conversion(value)
    >>> conversion.perform(noConversion()).result
    'Any value'
    >>> value == conversion.value == conversion.result
    True

A conversion using ``noConversion`` never results in an error being set.

Performing Multiple Conversions on the Same Value
=================================================

As you've already learned, each conversion can only use one converter. What if
you want to apply multiple converters to a conversion? The answer is that you
have to create multiple conversion objects and copy the ``.result`` attribute
from the first to the ``.value`` attribute of the second before the conversion.
Here's a hard coded example, I'll show you the easier method in the next
section, but it is useful to understand this technique for when you are coding
more complex converters later on. Here I'm converting a string to an integer and
then chceking it is one of the allowed values:

.. sourcecode :: pycon

    >>> input = '2'
    >>> first_conversion = Conversion(input)
    >>> first_conversion.perform(stringToInteger())
    <conversionkit.Conversion object at ...>
    >>> second_conversion = Conversion(first_conversion.result)
    >>> second_conversion.perform(oneOf([1, 2, 3]))
    <conversionkit.Conversion object at ...>
    >>> second_conversion.result
    2

Chaining Using the ``chainConverters()`` Tool
---------------------------------------------

The ``chainConverters()`` tool is a function which produces a converter from the
combination of all the converters passed to it. The value is passed through
each converter in turn from left to right in the argument list and the result
of the last converter is set as the ``.result`` attribute of the conversion. 

Here's an example which uses ``chainConverters``:

.. sourcecode :: pycon

    >>> from conversionkit import chainConverters
    >>> 
    >>> conversion = Conversion('2')
    >>> chain = chainConverters(
    ...     stringToInteger(), 
    ...     oneOf([1, 2, 3]),
    ... )
    >>> conversion.perform(chain)
    <conversionkit.Conversion object at ...>
    >>> if conversion.successful:
    ...     print conversion.value
    2

This approach is called *chaining*. If an error occurs in one of the
converters, the error that occurred is set as the ``.error`` attribute of the
conversion and no more converters are applied.

.. sourcecode :: pycon

    >>> conversion = Conversion('4')
    >>> chain = chainConverters(
    ...     stringToInteger(), 
    ...     oneOf([1, 2, 3]),
    ... )
    >>> conversion.perform(chain)
    <conversionkit.Conversion object at ...>
    >>> if not conversion.successful:
    ...     print conversion.error
    The value submitted is not one of the allowed values

.. note ::

   Later on when you look at compound conversions you'll learn about a slightly
   different tool for changing called ``chainPostConverters()``. Post converters
   are special converters which operate on a conversion instance which has already
   had a conversion applied. Don't get the two types of converters or the two
   types of chaining tools confused.

Understanding State
===================

In the certain circumstances it can be useful to be able to pass extra objects
to a converter to enable it to perform the conversion. For example, a converter
which also needs to validate that the username entered on a "Create Account"
form on a website might need to be able to access a database to perform a check
that the username isn't already taken. Let's set up an SQLite in-memory
database for an example and create a ``users`` table:

.. sourcecode :: pycon

    >>> import sqlite3
    >>> connection = sqlite3.connect(':memory:')
    >>> cursor = connection.cursor()
    >>> cursor.execute('CREATE TABLE users (username VARCHAR(20))')
    <sqlite3.Cursor object at ...>
    >>> cursor.close()

Consider the converter below which uses a database connection to check that a
username is still available. Notice that this time, the ``state`` argument
to the inner function is not optional:

.. sourcecode :: pycon

    >>> def usernameAvailable():
    ...     def usernameAvailable_converter(conversion, state):
    ...         cursor = state.connection.cursor()
    ...         cursor.execute(
    ...             'SELECT 1 FROM users WHERE username=?', 
    ...             (conversion.value,)
    ...         )
    ...         rows = cursor.fetchall()
    ...         if len(rows) and rows[0][0] == 1:
    ...             conversion.error = 'This username is not available'
    ...         else:
    ...             conversion.result = conversion.value
    ...         cursor.close()
    ...     return usernameAvailable_converter

To use this converter you can create a ``state`` object, set up a database
connection on it and then pass the object as the second argument to the
conversion's ``perform()`` method:

.. sourcecode :: pycon

    >>> from bn import AttributeDict
    >>> state = AttributeDict()
    >>> state['connection'] = connection
    >>> Conversion('james').perform(usernameAvailable(), state).result
    'james'

Here we are using an ``AttributeDict`` from the ``bn`` module provided by the
BareNecessities package. It is just a dictionary which allows keys to be
accessed as attributes but only allows them to be set like a normal dictionary.

You don't have to use an ``AttributeDict`` object as the state, you can use any
object you like.

The ``state`` argument, passed as the second argument to ``perfom()`` gets
passed as the second argument to the ``usernameAvailable_converter()`` inner
function when the conversion is performed. A ``cursor`` object is then created
from the ``connection`` object accessed from the ``state``. The SQL query is
executed and a result or error is set based on the result of the query, just as
is the case with a normal converter.

Using the ``state`` argument in this way lets you encapsulate some quite
complex logic in ConversionKit converters and then use them in the same way as
any other ConversionKit converter.

Summary
=======

In this chapter you have learned everything there is to know about how to
convert values from an input to a result. You have also seen how to write your
own converters and how to avoid common pitfalls. 

In the next chapter you'll learn how to deal with converting compound values
where, in the event of a failure, you want to know which sub-component couldn't
be converted. 

Before you can work with compound conversions you'll need a thorough
understanding of the topics covered in this chapter. Make sure you understand
the examples and can write your own converters as functions which return
functions before continuing.

Chapter 2: Compound Conversions
+++++++++++++++++++++++++++++++

In the previous chapter you saw how to perform single conversions such as
converting a string to an integer or a string to a date but let's think about
what happens if the data structure you wish to convert is more complex. 

As an example consider a dictionary of values representing an event which looks
like this:

.. sourcecode :: pycon

    >>> event = {
    ...     'name': 'Party',
    ...     'guests': '23',
    ...     'time': '2009-02-15',
    ...     'place': 'London',
    ... }

Imagine you want to convert this dictionary into a Python object. One way of
doing so would be to write a converter which takes a dictionary as its input
and then to write custom code to convert each of the values, before assembling
and returning the result as a new dictionary. Here's some code that just that:

.. sourcecode :: pycon

    >>> def eventToPython():
    ...     def eventToPython_converter(conversion, state=None):
    ...         event = conversion.value
    ...         child_conversions = {
    ...             'name': Conversion(event['name']).perform(noConversion()),
    ...             'guests': Conversion(event['guests']).perform(stringToInteger()),
    ...             'time': Conversion(event['time']).perform(stringToDate('%d/%m/%Y')),
    ...             'place': Conversion(event['place']).perform(noConversion()),
    ...         }
    ...         errors = []
    ...         for child in child_conversions.values():
    ...             if not child.successful:
    ...                 errors.append(child.error)
    ...         if errors:
    ...             conversion.error = 'Some of the fields were invalid'
    ...         else:
    ...             result = {}
    ...             for k, v in child_conversions.items():
    ...                 result[k] = v.result
    ...             conversion.result = result
    ...     return eventToPython_converter

.. note ::

    Notice the use of the ``noConversion()`` converter for handling the name and place.
    Since these are strings anyway, no conversion needs to be performed.

The compound converter can now be used like other converters:

.. sourcecode :: pycon

    >>> conversion = Conversion(event).perform(eventToPython())
    >>> print conversion.error
    Some of the fields were invalid

Although this approach works well there is one problem in particular
which needs addressing:

* Any errors which are occur when converting the individual fields are
  associated with the overall dictionary, not the field which contained the
  error. If the error is as undescriptive as ``Some of the fields were invalid``,
  which was the error above, it is very hard to know in which field the 
  problem occurred.

Whilst this might not be a problem in some circumstances it certainly is in
others so ConversionKit needs to provide a facility for accessing any error
associated with each of the fields. It does this by requiring that compound
converters also set a ``.children`` attribute on the conversion object
containing a data structure of all the child conversions which have taken
place. This allows any code using the conversion object to access the
individual errors by accessing the ``.error`` attribute of the child conversion
which contained the error.

Here's that rule again:

11. Compound converters must set a ``.children`` attribute on the object
    passed to the compound converter as the ``conversion``` argument

    After the conversion the ``.children`` attribute should therefore contain a
    data structure which contains every other conversion which was necessary for
    the compound conversion to be performed and any child error can therefore be
    extracted from the ``.children`` attribute.

Here's an updated version of the ``eventToPython()`` compound converter which
also sets the ``.children`` attribute (only the last line has changed):

.. sourcecode :: pycon

    >>> def eventToPython():
    ...     def eventToPython_converter(conversion, state=None):
    ...         event = conversion.value
    ...         child_conversions = {
    ...             'name': Conversion(event['name']).perform(noConversion()),
    ...             'guests': Conversion(event['guests']).perform(stringToInteger()),
    ...             'time': Conversion(event['time']).perform(stringToDate('%d/%m/%Y')),
    ...             'place': Conversion(event['place']).perform(noConversion()),
    ...         }
    ...         errors = []
    ...         for child_name, child_conversion in child_conversions.items():
    ...             if not child_conversion.successful:
    ...                 errors.append(child_conversion.error)
    ...         if errors:
    ...             conversion.error = 'Some of the fields were invalid'
    ...         else:
    ...             result = {}
    ...             for k, v in child_conversions.items():
    ...                 result[k] = v.result
    ...             conversion.result = result
    ...         conversion.children = child_conversions
    ...     return eventToPython_converter

Here's an example where the updated converter above is used on an event with an
invalid time value:

.. sourcecode :: pycon

    >>> event_with_error = {
    ...     'name': 'Party',
    ...     'guests': '23',
    ...     'time': '2009/02/15',
    ...     'place': 'London',
    ... }
    >>> conversion = Conversion(event_with_error)
    >>> conversion.perform(eventToPython())
    <conversionkit.Conversion object at ...>
    >>> print conversion.error
    Some of the fields were invalid
    >>> print conversion.children['time'].error
    time data did not match format:  data=2009/02/15  fmt=%d/%m/%Y

The important thing to note here is that although the ``conversion`` instance
contains child conversions with their own errors it still has a ``.error``
attribute of its own and so will still behave in the same way as a normal
single conversion *in addition* to the extra information it provides.

As an example of where an overall error and a child errors are useful consider
the case of form conversion in a web application. The conversion error string
can be used as part of an overall error message, or perhaps a flash message or
alert popup and any child conversion errors could be displayed next to the
fields containing the invalid values.

When you use even more deeply nested conversions, setting an appropriate 
error message at each level becomes even more important.

Now you've seen both single and compound conversions you might be wondering
when it is appropriate to write converters of each type. The simple rules are:

* If you want individual errors to be associated with sub-components of an
  input value, use a compound converter, otherwise use a single converter.

* If you aren't sure, write a compound converter because compound conversions
  behave like single conversions anyway in that they have a ``.error``,
  ``.result`` and ``.successful`` attributes, but they also provide more
  flexibility if you need it.

Using the ``toDictionary()`` Tool
=================================

The description of compound converters you've read so far in this chapter can
apply to any data types, not just dictionaries. You could work on lists,
objects or anything else you want to convert.

If you do need to convert a dictionary though, ConversionKit provides a tool
which can create a suitable converter for you. It is called ``toDictionary()``
and to use it you simply specify the converters to be used for each key and let
ConversionKit handle the conversions for you.  Internally, ConversionKit will
set up a separate ``Conversion`` object for each key value pair and set the
``.children`` attribute for you too.

Here's an example:

.. sourcecode :: pycon

    >>> from conversionkit import toDictionary
    >>> 
    >>> event_converter = toDictionary(
    ...     converters = {
    ...         'name': noConversion(),
    ...         'guests': stringToInteger(),
    ...         'time': stringToDate(format='%Y-%m-%d'),
    ...         'place': noConversion(),
    ...     }
    ... )

The ``event_converter`` object is actually a configured inner
function so it can be used directly in a conversion's ``perform()`` method
without needing to be called again. This is no different from the example in
the `Re-Using Converters`_ section where the ``string_to_date_converter`` was
used directly without being called again.

Here's how it is used (we are using the ``pprint()`` function to print the dictionary nicely with the keys in alphaetical order):

.. sourcecode :: pycon

    >>> from pprint import pprint
    >>> event = {
    ...     'name': 'Party',
    ...     'guests': '23',
    ...     'time': '2009-02-15',
    ...     'place': 'London',
    ... }
    >>> conversion = Conversion(event).perform(event_converter)
    >>> pprint(conversion.result)
    {u'guests': 23,
     u'name': 'Party',
     u'place': 'London',
     u'time': datetime.date(2009, 2, 15)}

As you can see, this produces the expected result. You can still access the
child conversions of both successful and unsuccessful conversions via the
``.children`` attribute:

.. sourcecode :: pycon

    >>> pprint(conversion.children)
    {u'guests': <conversionkit.Conversion object at 0x...>,
     u'name': <conversionkit.Conversion object at 0x...>,
     u'place': <conversionkit.Conversion object at 0x...>,
     u'time': <conversionkit.Conversion object at 0x...>}

If you need to work with dictionaries, using the ``toDictionary`` converter can
save you some time. In the next sections we'll look at some more advanced
functionality of the ``toDictionary()`` converter.

Extra Fields are Filtered, Missing Fields are Ignored
-----------------------------------------------------

In real life, you might not have complete control over the input value which is
passed to a dictionary converter. There might be extra fields you weren't
expecting or some of the fields you were expecting might be missing.

Rather than setting an error for missing or extra fields, the
``toDictionary`` implementation simply ignores things it can't validate.
This means that:

* missing fields won't be present in the result and no error will be produced
* extra fields will be filtered out and not appear in the result

To demonstrate this let's look at a valid event dictionary which needs
converting:

.. sourcecode :: pycon

    >>> event = {
    ...     'name': 'Party',
    ...     'guests': '23',
    ...     'time': '2009-02-15',
    ...     'place': 'London',
    ... }

Consider this version of an ``event_converter``. The event data has a
``place`` field which the converter isn't expecting and the converter expects a
``location`` field which isn't present in the event data:

.. sourcecode :: pycon

    >>> event_converter = toDictionary(
    ...     converters = {
    ...         'name': noConversion(),
    ...         'guests': stringToInteger(),
    ...         'time': stringToDate(format='%Y-%m-%d'),
    ...         'location': noConversion(),
    ...     }
    ... )

Let's perform the conversion:

.. sourcecode :: pycon

    >>> conversion = Conversion(event).perform(event_converter)
    >>> pprint(conversion.result)
    {u'guests': 23, u'name': 'Party', u'time': datetime.date(2009, 2, 15)}

Notice that the time and the number of guests have been successfully converted
to Python objects but that the result has no ``'place'`` key and no error was
raised about the fact no ``'location'`` key was present in the event.

The ``allow_extra_fields`` and ``filter_extra_fields`` Arguments
----------------------------------------------------------------

If you want an exception to be raised if the generated converter recieves too
many arguments you can specify ``allow_extra_fields=False`` as an argument to
``toDictionary()``. If you don't want extra fields to be filtered you can
specify ``filter_extra_fields=False`` to have a ``noConversion()`` conversion
performed on each extra field and have it added to the result. Generally
speaking, using the defaults of ``allow_extra_fields=True`` and
``filter_extra_fields=True`` is fine.

Setting ``allow_extra_fields=False`` in the example below causes an exception
to be raised due to the presence of the place key in the event data dictionary:

.. sourcecode :: pycon

    >>> event = {
    ...     'name': 'Party',
    ...     'guests': '23',
    ...     'time': '2009-02-15',
    ...     'place': 'London',
    ... }

.. sourcecode :: pycon

    >>> event_converter = toDictionary(
    ...     converters = {
    ...         'name': noConversion(),
    ...         'guests': stringToInteger(),
    ...         'time': stringToDate(format='%Y-%m-%d'),
    ...         'location': noConversion(),
    ...     },
    ...     allow_extra_fields=False
    ... )
    >>> conversion = Conversion(event).perform(event_converter)
    Traceback (most recent call last):
      ...
    ConversionKitError: The field u'place' is not allowed

If you want to have extra fields set an error on the conversion instead of
raising an exception you should set ``allow_extra_fields`` to ``False`` and set
``raise_on_extra_fields`` to ``False`` too:

.. sourcecode :: pycon

    >>> event_converter = toDictionary(
    ...     converters = {
    ...         'name': noConversion(),
    ...         'guests': stringToInteger(),
    ...         'time': stringToDate(format='%Y-%m-%d'),
    ...         'location': noConversion(),
    ...     },
    ...     allow_extra_fields=False,
    ...     raise_on_extra_fields=False
    ... )
    >>> conversion = Conversion(event).perform(event_converter)
    >>> print conversion.error
    The field u'place' is not allowed

Here's another example. This time notice that setting
``filter_extra_fields=False`` results in the place being present in the result:

.. sourcecode :: pycon

    >>> event_converter = toDictionary(
    ...     converters = {
    ...         'name': noConversion(),
    ...         'guests': stringToInteger(),
    ...         'time': stringToDate(format='%Y-%m-%d'),
    ...         'location': noConversion(),
    ...     },
    ...     filter_extra_fields=False
    ... )
    >>> conversion = Conversion(event).perform(event_converter)
    >>> pprint(conversion.result)
    {u'guests': 23,
     u'name': 'Party',
     u'place': 'London',
     u'time': datetime.date(2009, 2, 15)}

.. note :: 

    If you are coming from a FromEncode background the ``allow_extra_fields``
    and ``filter_extra_fields`` options behave the same way they would then working
    with a FormEncode ``Schema``, ConversionKit just sets the defaults to ``True``
    rather than ``False``.

Setting Default Values
======================

If a key is missing or empty you might want to set a default value for it. The
``toDictionary()`` tool takes a ``missing_or_empty_defaults`` argument to allow you to specify
the default values for missing or empty fields.

Here's an event which is missing a ``location`` field and has an empty number
of guests.

.. sourcecode :: pycon

    >>> event = {
    ...     'name': 'Party',
    ...     'guests': '',
    ...     'time': '2009-02-15',
    ... }

Here's an ``event_converter`` which is set to 

.. sourcecode :: pycon

    >>> event_converter = toDictionary(
    ...     converters = {
    ...         'name': noConversion(),
    ...         'guests': stringToInteger(),
    ...         'time': stringToDate(format='%Y-%m-%d'),
    ...         'location': noConversion(),
    ...     },
    ...     missing_or_empty_defaults = {
    ...         'location': 'London',
    ...         'guests': 10,
    ...     },
    ... )
    >>> conversion = Conversion(event).perform(event_converter)
    >>> pprint(conversion.result)
    {u'guests': 10,
     u'location': 'London',
     u'name': 'Party',
     u'time': datetime.date(2009, 2, 15)}

As you can see both the missing ``location`` key and empty ``guests`` key were
given the default value specified. Notice that the defaults get applied *after*
the conversions so the default value you specify does not get converted. You
cannot specify defaults for fields which don't have an associated converter.

.. note ::

   One design decision which I pondered for quite a while was whether it was 
   better for a default to be processed through the child converter as though
   it had actually been passed as the original value for that field or 
   whether it should be a short-cut which just gets set as a result. At the 
   moment it is just a short-cut so you specify the result you want as the 
   default, not the input.

The ``missing_defaults`` and ``empty_defaults`` arguments
---------------------------------------------------------

Sometimes you might want to be more specific and specify a that a default
should only be applied if the field is present but empty or only if the field
is missing rather than having the same default applied regardless of the error.
To achive this the ``toDictionary()`` tool takes two more arguments:
``missing_defaults`` and ``empty_defaults``.

``missing_defaults``
    A dictionary of field names and values which should only be applied if the
    fields specified are missing

``empty_defaults``
    A dictionary of field names and values which should only be applied if the
    fields specified are present but have empty values

If you specify a ``missing_or_empty_defaults`` value as well as a
``missing_defaults`` or ``empty_defaults`` value, the ``missing_defaults`` or
``empty_defaults`` value is used in preference. 

Here's an example:

.. sourcecode :: pycon

    >>> event = {
    ...     'name': 'Party',
    ...     'guests': '',
    ...     'title': '',
    ...     'time': '2009-02-15',
    ... }
    >>> event_converter = toDictionary(
    ...     converters = {
    ...         'name': noConversion(),
    ...         'guests': stringToInteger(),
    ...         'time': stringToDate(format='%Y-%m-%d'),
    ...         'location': noConversion(),
    ...         'title': noConversion(),
    ...     },
    ...     missing_or_empty_defaults = {
    ...         'location': 'This will never be used because an empty_defaults and missing_defaults value is present',
    ...         'guests': 10,
    ...     },
    ...     empty_defaults = {
    ...         'location': 'London',
    ...         'title': 'No Title',
    ...     },
    ...     missing_defaults = {
    ...         'location': 'Paris',
    ...     },
    ... )
    >>> conversion = Conversion(event).perform(event_converter)
    >>> pprint(conversion.result)
    {u'guests': 10,
     u'location': 'Paris',
     u'name': 'Party',
     u'time': datetime.date(2009, 2, 15),
     u'title': 'No Title'}

As you can see the default for the missing location ``Paris`` was used in
preference to the long string provided in ``defaults`` but the value of
``guests`` was picked from ``defaults`` as nothing more specific was specified
and the value of ``title`` was chosen from ``empty_defaults``.

.. tip ::

   Internally, ConversionKit creates a new ``Conversion`` instance for any
   defaults and applies a ``noConversion()`` to them so that from that they can be
   treated as if they had been converted as normal from that point on.

Setting Errors
==============

In the same way that you can set default values for missing and empty fields
you can also set errors. If you set an error, any default specified is not
used.

Just as with defaults there are three parameters to ``toDictionary()`` which
you can use:

``missing_or_empty_errors``
    Sets an error if the field is missing or empty

``missing_errors``
    Sets an error if the field is missing

``empty_errors``
    Sets an error if the field is present but empty

Here's an example:

.. sourcecode :: pycon

    >>> event = {
    ...     'name': 'Party',
    ...     'guests': '',
    ...     'title': '',
    ...     'time': '2009-02-15',
    ... }
    >>> event_converter = toDictionary(
    ...     converters = {
    ...         'name': noConversion(),
    ...         'guests': stringToInteger(),
    ...         'time': stringToDate(format='%Y-%m-%d'),
    ...         'location': noConversion(),
    ...         'title': noConversion(),
    ...     },
    ...     missing_or_empty_errors = {
    ...         'location': 'This will never be used because an empty_defaults and missing_defaults value is present',
    ...         'guests': 'The guests value is missing or invalid',
    ...     },
    ...     empty_errors = {
    ...         'location': 'Please enter a value',
    ...         'title': 'Please enter a value for the title',
    ...     },
    ...     missing_errors = {
    ...         'location': 'Please specify a location',
    ...     },
    ... )
    >>> conversion = Conversion(event).perform(event_converter)
    >>> print conversion.error
    The 'location', 'title' and 'guests' fields were invalid
    >>> for child in conversion.children.values():
    ...     if not child.successful:
    ...         print child.error
    Please enter a value for the title
    Please specify a location
    The guests value is missing or invalid

Of course, you can use the ``errors``, ``missing_errors`` and ``empty_errors``
parameters at the same time as the ``defaults``, ``missing_defaults`` and
``empty_defaults`` parameters but you should not configure a situation where an
error and a default are set at the same time.

Alternative Ways of Specifing Error Messages
--------------------------------------------

There are occasions when you want to set the same (or similar) error message
for each field. In that case it can be tadious to set up the dictionaries for
``missing_or_empty_errors``, ``missing_errors`` and ``empty_errors``. Instead
ConversionKit provides two more options:

* Specify a string to be used for each of the converters
* Specify a ``(message, field_names)`` tuple to set the message for the list 
  of fields described by ``field_names``.

Either way the messages you set should be escaped with any ``%`` characters
written as ``%%`` because the messages have Python string formatting applied so
that the messages can include the name of the field they are applying to.

Here's are the event and the converters for the examples:

.. sourcecode :: pycon

    >>> event = {
    ...     'name': 'Party',
    ...     'guests': '',
    ... }
    >>> converters = {
    ...     'name': noConversion(),
    ...     'guests': stringToInteger(),
    ...     'location': noConversion(),
    ... }

Here's the first example:

.. sourcecode :: pycon

    >>> event_converter1 = toDictionary(
    ...     converters = converters,
    ...     empty_errors = ('Please specify a value for %(key)s', ['guests', 'time']),
    ...     missing_errors = u'The field %(key)s is missing'
    ... )
    >>> conversion = Conversion(event).perform(event_converter1)
    >>> print conversion.error
    The 'location' and 'guests' fields were invalid
    >>> for child in conversion.children.values():
    ...     if not child.successful:
    ...         print child.error
    Please specify a value for guests
    The field location is missing

Notice that we get an error for ``location`` and ``guests`` but not ``time``
since that field is not part of the event.

Here's the second example:

    >>> event_converter2 = toDictionary(
    ...     converters = converters,
    ...     missing_or_empty_errors = ('Please specify a value for %(key)s', ['guests', 'time']),
    ... )
    >>> conversion = Conversion(event).perform(event_converter2)
    >>> print conversion.error
    The 'time' and 'guests' fields were invalid
    >>> for child in conversion.children.values():
    ...     if not child.successful:
    ...         print child.error
    Please specify a value for time
    Please specify a value for guests

This time we get errors for ``guests`` and ``time`` because they are stated
explicitly but no error for ``location`` becuase it isn't part of the list of
fields specified for the ``missing_or_empty_errors`` argument.

And the third example:

.. sourcecode :: pycon

    >>> event_converter3 = toDictionary(
    ...     converters = converters,
    ...     missing_or_empty_errors = 'Please specify a value for %(key)s'
    ... )
    >>> conversion = Conversion(event).perform(event_converter3)
    >>> print conversion.error
    The 'location' and 'guests' fields were invalid
    >>> for child in conversion.children.values():
    ...     if not child.successful:
    ...         print child.error
    Please specify a value for guests
    Please specify a value for location

This time, since a string is specified for ``missing_or_empty_errors``, all the
field names for the converters are used so the errors appear for ``location``
and ``guests``.

Thinking in terms of fields
===========================

Although the methods described so far for working with missing and empty values
work well, some people find it easier to think in terms of individual fields
being empty or missing. To support this way of thinking ConversionKit comes
with a ``Field`` class which allows you to specify any defaults or errors to be
associated with a particular field so that you don't have to specify them
directly as arguments to ``toDictionary()``. Internally ``toDictionary()``
inspects the fields and assembles the appropriate objects for you from the
values you passed to ``Field``. 

Here's an example demonstrating this:

.. sourcecode :: pycon

    >>> event = {
    ...     'name': 'Party',
    ...     'guests': '',
    ...     'title': '',
    ...     'time': '2009-02-15',
    ... }

    >>> from conversionkit import Field
    >>> event_converter = toDictionary(
    ...     converters = {
    ...         'name': noConversion(),
    ...         'guests': Field(
    ...             stringToInteger(), 
    ...             missing_or_empty_default=10,
    ...         ),
    ...         'time': stringToDate(format='%Y-%m-%d'),
    ...         'location': Field(
    ...             noConversion(),
    ...             empty_error='Please enter a value', 
    ...             missing_error='Please specify a location',
    ...         ),
    ...         'title': noConversion(),
    ...     },
    ... )
    >>> conversion = Conversion(event).perform(event_converter)
    >>> print conversion.error
    The location field is invalid
    >>> for name, child in conversion.children.items():
    ...     if not child.successful:
    ...         print name, 'error: %r' % child.error
    ...     else:
    ...         print name, 'result: %r' % child.result
    title result: ''
    guests result: 10
    location error: 'Please specify a location'
    name result: 'Party'
    time result: datetime.date(2009, 2, 15)

Using ``Field()`` objects isn't considered better than using plain converters
and parameters to ``toDictionary()`` but it is an approach some people prefer,
particularly if they are used to using FormEncode.

Sometimes the values in the dictionary might have complex inter-relations which
need further validation or conversion beyond the conversion of the individual
key value pairs (fields) it contains. To handle this case you need to know
about a new component called a *post-converter*. Let's look at these in the
next chapter.

Summary
=======

You've learned a lot in this chapter. You have seen how compound conversions
can be performed and how errors can be associated with the data structure as a
whole as well as with individual sub-components and you've seen how child
conversions are stored in a conversion's ``.children`` attribute when compound
conversions are performed on them. You've also seen how the ``toDictionary()``
tool can make working with dictionaries much easier.

Chapter 3: Post-Converters
++++++++++++++++++++++++++

Once you've performed a conversion on a dictionary you end up with a conversion
object with either its ``.error`` or ``.result`` attribute set and a
``.children`` attribute containing a structure representing all the individudal
conversions necessary to calculate the result.

If you now want to perform some more analysis or conversions on the
``conversion``, according to the rules from Chapter 1 you would need to create
new conversions for each of the conversions which have already occurred and
assemble a new conversion object. As you can imagine that would quickly get
tedious so instead ConversionKit supports the concept of a *post converter*.

A post converter is just like an ordinary converter except that:

* the ``Conversion`` instance it recieves has already been used.
* the inner function name ends with ``_post_converter`` instead of ``_converter``
* you are allowed to set results or errors on the conversion or any child 
  conversions even though a result or error may already have been set

This behaviour makes post converters very useful. They can be used for:

* Setting an error on a child conversion
* Replacing the result of a child conversion
* Removing an error from a child conversion and setting a result instead
* Setting an error on the conversion
* Add, remove or rename child conversions

Of course, as you saw in Chapter 1, if you set an error on result on a
conversion which has already been used, you get an error. ConversionKit
therefore provides two functions, ``set_error()`` and ``set_result()`` which
are only to be used in post-converters and which change the error or result on
a used conversion. We'll look at these in a minute but first let's look at
how you can chain together conversions to be able to use a post-converter

Chaining Post-Converters
========================

To chain post-converters you use the ``chainPostConverters()`` tool:

.. sourcecode :: pycon

    >>> from conversionkit import chainPostConverters

The ``chainPostConverters()`` tool is different from ``chainConverters()`` in
that the *same* ``Conversion`` instance is passed to each post-converter in the
cahin after the first one. At each point the ``Conversion`` instance is
expected to be in a consistent state with either a ``.error`` or ``.result``
attribute set, not both. Of course the first item in the chain has to be an
ordinary converter because until it is performed, the ``Conversion`` instance
won't have been used. You'll see an example of ``chainPostConverters()`` in the
next section.

The ``set_error()`` and ``set_result()`` functions
==================================================

One problem you will face when writing post-converters is how to set an error
or a result on a child conversion. After all each conversion instance is only
designed to be used once so you can't just set its ``.error`` or ``.result``
attribute again. 

The answer is that you need to use ConversionKit's ``set_error()`` and
``set_result()`` functions to reset the conversion and apply the new error or
result. 

.. sourcecode :: pycon

    >>> from conversionkit import set_error, set_result

.. caution::

    Because Python is a dynamic language with powerful introspection features
    you can easily access the ``conversion`` instance's private variables to hack
    an error or result on an existing conversion. This is considered extremely bad
    practice for two reasons:

    * You might not hack the ``Conversion`` object very well and end up 
      leaving it in an inconsistent state
    * The API could change at any time so even if your hack does work 
      correctly at the moment it might not in the future

    The ``set_error()`` and ``set_result()`` functions provided by
    ConversionKit will always do the right thing so it is important you use them.

Here's an example of a post-converter making use of ``set_error()`` which
checks that two fields have the same input value and which sets an error on the
second of the two fields if it doesn't. You could easily write a similar
post-converter to check the results of both the fields are the same after
having passed through the converters.

.. sourcecode :: pycon

    >>> def sameValue(field1, field2):
    ...     def sameValue_post_converter(conversion, state=None):
    ...         value = conversion.value.copy()
    ...         if value[field1] != value[field2]:
    ...             set_error(
    ...                 conversion.children[field2],
    ...                 'The fields %s and %s have different values' % (
    ...                     field1,
    ...                     field2,
    ...                 )
    ...             )
    ...             set_error(conversion, 'The fields are not valid')
    ...         # We don't need to set a result because one should already be present
    ...     return sameValue_post_converter

Let's test this post-converter:

.. sourcecode :: pycon

    >>> registration = {
    ...     'password': '123456',
    ...     'password_confirm': '654321',
    ... }
    >>> registration_converter = chainPostConverters(
    ...     toDictionary(
    ...         empty_errors = {
    ...             'password': "Please enter a password",
    ...             'password_confirm': "Please confirm your password",
    ...         },
    ...         converters = {
    ...             'password': noConversion(),
    ...             'password_confirm': noConversion(),
    ...         },
    ...     ),
    ...     sameValue('password', 'password_confirm'),
    ... )
    >>> conversion = Conversion(registration).perform(registration_converter)
    >>> conversion.error
    'The fields are not valid'
    >>> conversion.children['password_confirm'].error
    'The fields password and password_confirm have different values'

When you use the ``set_error()`` function any result associated with the
conversion is removed because a conversion can't have a result and an error at
the same time.

Using ``set_result()`` to change the result of a conversion is very similar but
you specify the new result as the second argument instead of an error. When
using ``set_result()`` any error assoicated with the conversion is removed.

An implementation of the ``sameValue()`` converter is also available in the
``formconvert`` module:

.. sourcecode :: pycon

    >>> from formconvert import sameValue

The ConversionKit, RecordConvert and FormConvert packages already have a range
of post-converters implemented which you can re-use. Look at their API
documentation for details.

The Effect of Missing Fields in ``toDictionary()``
==================================================

You might be wondering how ``toDictionary()`` handles setting the ``.children``
attribute of a conversion if a default value or error is set for a missing
filed. The reason this is problematic is that there is no initial value to set
for the ``.value`` attribute so how can ``toDictionary()`` create a child
conversion on which to set the default value or the error?

The answer is that ConversionKit provides a special object called ``Missing``
which should only be used internally by ConversionKit and is only used when a
field is missing and a default value or an error needs to be set for it.

.. sourcecode :: pycon

    >>> from conversionkit import Missing

I don't personally like having to create an artificual value to have a specific
meaning but the alternatives are to:

* Halt all processing and set an *overall* error when any missing field is
  encountered so you don't set the ``.children`` attribute of a conversion at
  all. The drawback of this approach is that useful error and conversion
  information information which could be passed on would be discarded and this
  isn't helpful in many cases (eg processing HTML forms where you want to show
  all error messages at once for a user to correct problems).

* Have another attribute on conversions called ``.missing`` to contain the
  information about the default value or errors. This avoids having to create a
  ``Missing`` class but results in all other post-converters having to do
  further processing, looking in two places rather than one.

Clearly the ``Missing`` object is the least of the three evils.

Pre-Converters
==============

Now we've looked a post-converters you might wonder if there is such a thing as
a *pre-converter*. It turns out there is but that it isn't very exciting. 

You might want to use a pre-converter for:

* Converting the value from its present (non-dictionary) form into a
  dictionary so that the individual values can be converted
* Modifying the input dictionary to add or remove keys 
* All manner of other things

The reason pre-converters aren't particularly exciting is that they are just
ordinary converters which take a value from a ``Conversion`` instance's
``.value`` attribute and set a different value as the instance's ``.result``
attribute if there aren't any errors. This means pre-converters can be applied
just by using the ordinary ``chainConverter`` tool.

If the input value is a dictionary, pre-converters have to operate on the
*entire* dictionary as if it is a single value and cannot set errors on the
individual child conversions to convey an error in a particular field. To do
that you would have to use the ``toDictionary()`` tool or a post-converter.
Pre-converters can therefore only set an overall error.

Pre-converters are very easy to write, they are just normal converters which
happen to operate on is a dictionary.

Here's a pre-converter which replaces a key called ``name`` with one called
``firstname`` and one called ``lastname``:

.. sourcecode :: pycon

    >>> def splitName(key='name'):
    ...     def splitName_converter(conversion, state=None):
    ...         value = conversion.value.copy()
    ...         if value.has_key(key):
    ...             parts = value[key].split(' ')
    ...             if not len(parts) >= 2:
    ...                 conversion.error = 'A name should contain at least two parts'
    ...             else:
    ...                 value['firstname'] = parts[0]
    ...                 value['lastname'] = parts[-1]
    ...         conversion.result = value
    ...     return splitName_converter

Notice that we create a copy of the conversion's value. You'll recall that the
idea is that no converters (whether pre-converters, post-converters or any
other sort) will modify the original value of a conversion.

Here's the pre-converter in action, we're using the string to email converter
from FormConvert just to demonstrate that most of the converters you could want
already exist. Notice that we specify converters for ``firstname`` and
``lastname`` even though the input dictionary only has a ``name`` key. The
pre-converter will convert the input dictionary for us.

.. sourcecode :: pycon

    >>> from stringconvert.email import unicodeToEmail
    >>>
    >>> contact = {'name': u'James Gardner', 'email': u'james@example.com'}
    >>> contact_to_dictionary = chainConverters(
    ...     splitName('name'),
    ...     toDictionary(
    ...         converters={
    ...             'firstname': noConversion(),
    ...             'lastname': noConversion(),
    ...             'email': unicodeToEmail(),
    ...         }
    ...     ),
    ... )
    >>> pprint(Conversion(contact).perform(contact_to_dictionary).result)
    {u'email': u'james@example.com',
     u'firstname': u'James',
     u'lastname': u'Gardner'}

As you can see the ``splitName()`` converter has been applied first to change
the input dictionary so that the ``name`` key is replaced by ``firstname`` and
``lastname`` keys and then the ``toDictionary()`` converter has converted the
individual fields.

Summary
=======

In this chapter you've seen how to use post-converters to perform further
processing on ``Conversion`` instances which have already been used. You've
also seen how the special ``chainPostConverters()`` tool is used to chain a
normal converter and a series of post-converters.

Since post-converters are such a powerful tool you may be tempted to use them a
lot. In many situations it is better to create duplicate ``Conversion``
instances in a normal converter rather than using a post-converter otherwise
your code can quickly become over-complex.

Chapter 4: List Conversions
+++++++++++++++++++++++++++

Using the ``toListOf()`` Converter
==================================

We've spent quite a lot of time discussing dictionaries as an example of
compound conversions and how the ``toDictionary()`` converter factory can help
simpify the task of writing compound conversions for dictionaries, but there
are other data structures which you often need to convert. A common situation
in a variety of programming fields is to validate a repeatable set of fields.
ConversionKit helps with this use case too by providing the ``toListOf``
tool.

The ``toListOf()`` tool takes a dictonary converter (of the type produced by
calling ``toDictionary()``) as its only argument. It will convert a list made
up entirely of dictionaries which can be converted by the dictionary converter
you specify.

To demonstrate this let's create two events and an event converter:

.. sourcecode :: pycon

    >>> event1 = {'place': 'London', 'name': 'Party', 'guests': '23', 'time': '2009-02-15'} 
    >>> event2 = {'place': 'London', 'name': 'Dinner', 'guests': '8', 'time': '2009-02-15'}
    >>> event_converter = toDictionary(
    ...     converters = {
    ...         'name': noConversion(),
    ...         'guests': stringToInteger(),
    ...         'time': stringToDate(format='%Y-%m-%d'),
    ...         'place': noConversion(),
    ...     },
    ... )

Here's an example which converts a list of events:

.. sourcecode :: pycon

    >>> from conversionkit import toListOf
    >>>
    >>> list_of_events = toListOf(event_converter)
    >>> conversion = Conversion([event1, event2]).perform(list_of_events)
    >>> print type(conversion.result)
    <type 'list'>
    >>> pprint(conversion.result)
    [{u'guests': 23,
      u'name': 'Party',
      u'place': 'London',
      u'time': datetime.date(2009, 2, 15)},
     {u'guests': 8,
      u'name': 'Dinner',
      u'place': 'London',
      u'time': datetime.date(2009, 2, 15)}]

Dealing With Errors
-------------------

Just like with dictionaries, if an error occurs during the conversion the
``.error`` attribute will be set on the conversion but the child conversion
where the error occurred will also have an error associated with it. In this
case the conversion's ``.children`` attribute is a list of child conversions.

Here's an example which has an error, the time field uses ``/`` characters
instead of the expected ``-`` characters.

.. sourcecode :: pycon

    >>> event_with_error = {'place': 'London', 'name': 'Party', 'guests': '23', 'time': '2009/02/15'} 

.. sourcecode :: pycon

    >>> conversion = Conversion([event_with_error, event2])
    >>> conversion.perform(list_of_events)
    <conversionkit.Conversion object at ...>
    >>> print conversion.error
    One of the items was not valid

And here are the child conversions:

.. sourcecode :: pycon
    
    >>> conversion.children
    [<conversionkit.Conversion object at ...>, <conversionkit.Conversion object at ...>]
    >>> conversion.children[0].error
    'The time field is invalid'

Specifying the Allowed Number of Items in the List
--------------------------------------------------

When working with lists you might want to specify the number of repetitions of
items which are allowed. You can do this with the ``min`` and ``max`` arguments
to ``toListOf()``. 

.. sourcecode :: pycon

    >>> list_of_events = toListOf(event_converter, min=1, max=3)
    >>> conversion = Conversion([event1, event2]).perform(list_of_events)
    >>> pprint(conversion.result)
    [{u'guests': 23,
      u'name': 'Party',
      u'place': 'London',
      u'time': datetime.date(2009, 2, 15)},
     {u'guests': 8,
      u'name': 'Dinner',
      u'place': 'London',
      u'time': datetime.date(2009, 2, 15)}]
    >>> conversion = Conversion([]).perform(list_of_events)
    >>> print conversion.error
    No items were specified
    >>> conversion = Conversion([event1, event1, event1, event1]).perform(list_of_events)
    >>> print conversion.error
    There are too many items in the list. The maximum number is 3.

Summary
=======

You've now learned how to write compound converters, and how the
``toDictionary()`` and ``toListOf()`` tools can make creating converters for
converting dictionaries and list of dictionaries much easier. You've seen how
pre-converters and post-converters work and the different types of conversion
they each operate on. You've also seen how to reset conversions in
post-converters.

In the next chapter we'll take the concept of converting dictionaries and lists
one step further and describe how to convert complex data structures comprised
of nested lists of dictionaries.

Chapter 5: Nested Conversions
+++++++++++++++++++++++++++++

In the last chapter you saw how to work with dictionaries and lists of
dictionaries but since the ``toListOf()`` tool is still an ordinary converter
and a ``toDictionaryOf()`` tool is still an ordinary converter there is no
reason why you can't use these compound converters in other ``toListOf()`` or
``toDictionary()`` calls. This allows you to easily write converters capable of
converting complex data structures consisting of nested lists and dictionaries.
Conversions involving such data structures are called *nested conversions* in
ConversionKit terminology.

Learning by Example
===================

First let's create a converter for a simple dictionary which we'll use in the
nested conversions:

.. sourcecode :: pycon

    >>> simple = toDictionary(
    ...     converters = {
    ...         'key': noConversion(),
    ...     }
    ... )
    >>> simple_data = {
    ...     'key': 'value'
    ... }
    >>> simple_result = Conversion(simple_data).perform(simple).result
    >>> print simple_result
    {u'key': 'value'}
    
Now let's try to convert a dictionary which has a list of simple dictionaries
as the value of the ``'key'`` key:

.. sourcecode :: pycon

    >>> case1 = {
    ...     'key': [
    ...         {
    ...             'key': 'value'
    ...         },
    ...         {
    ...             'key': 'value'
    ...         }
    ...     ],
    ... }
    >>> case1_converter = toDictionary(
    ...     converters = {
    ...         'key': toListOf(simple) 
    ...     }
    ... )
    >>> result1 = Conversion(case1).perform(case1_converter).result
    >>> pprint (result1)
    {u'key': [{u'key': 'value'}, {u'key': 'value'}]}

Now a dictionary which has another dictionary as the value of the ``'key'``
key:

.. sourcecode :: pycon

    >>> case2 = {
    ...     'key': {
    ...         'key': 'value'
    ...     },
    ... }
    >>> case2_converter = toDictionary(
    ...     converters = {
    ...         'key': simple 
    ...     }
    ... )
    >>> result2 = Conversion(case2).perform(case2_converter).result
    >>> pprint(result2)
    {u'key': {u'key': 'value'}}


How about a list of dictionaries:

.. sourcecode :: pycon

    >>> case3 = [
    ...     {
    ...         'key': 'value'
    ...     },
    ...     {
    ...         'key': 'value'
    ...     },
    ... ]
    >>> case3_converter = toListOf(simple)
    >>> result3 = Conversion(case3).perform(case3_converter).result
    >>> pprint(result3)
    [{u'key': 'value'}, {u'key': 'value'}]

What about a list of lists of simple dictionaries:

.. sourcecode :: pycon

    >>> case4 = [
    ...     [
    ...         {
    ...             'key': 'value'
    ...         },
    ...     ],
    ...     [
    ...         {
    ...             'key': 'value'
    ...         },
    ...     ]
    ... ]
    >>> case4_converter = toListOf(toListOf(simple))
    >>> result4 = Conversion(case4).perform(case4_converter).result
    >>> pprint(result4)
    [[{u'key': 'value'}], [{u'key': 'value'}]]

As you can imagine, you can nest any of these examples in the others to easily
create converters for very complex nested data structures.

Obtaining Errors From Nested Conversions
========================================

To demonstrate how error can be obtained from the conversions let's create new
converters which are not capable of converting the nested data structures from
the last section because they expect the dictionary values to be integers:

.. sourcecode :: pycon

    >>> simple = toDictionary(
    ...     converters = {
    ...         'key': stringToInteger(),
    ...     }
    ... )
    >>> case1_converter = toDictionary(
    ...     converters = {
    ...         'key': toListOf(simple) 
    ...     }
    ... )
    >>> case2_converter = toDictionary(
    ...     converters = {
    ...         'key': simple 
    ...     }
    ... )
    >>> case3_converter = toListOf(simple)
    >>> case4_converter = toListOf(toListOf(simple))

Now let's see the errors:

.. sourcecode :: pycon

    >>> error_simple = Conversion(simple_data).perform(simple)
    >>> error_simple.error
    'The key field is invalid'
    >>> error1 = Conversion(case1).perform(case1_converter)
    >>> error1.error
    'The key field is invalid'
    >>> error2 = Conversion(case2).perform(case2_converter)
    >>> error2.error
    'The key field is invalid'
    >>> error3 = Conversion(case3).perform(case3_converter)
    >>> error3.error
    'Some of the items were not valid'
    >>> error4 = Conversion(case4).perform(case4_converter)
    >>> error4.error
    'Some of the items were not valid'

As you can see, nested conversions have an ``.error`` attribute which returns a
single string representing the overall error, just as is the case with compoud
conversions.

Extracting Errors From a Nested Conversion
==========================================

Just as with compound conversions you extract errors from the individual fields
in a nested conversion from the ``.children`` attribute of the conversion. The
only difference is that this time, the child conversions themselves might be
compound or nested conversions and so might themselves have a ``.children``
attribute. 

Early versions of ConversionKit provided tools to automatically extract errors
from sets of nested conversions but in practice it is as hard to obtain the
relevant error message from the data structure ConversionKit produces as it is
to obtain the errors directly from the child conversions since in both cases
you need to have an understanding of what the data and errors actually mean in
order to choose the appropriate error messages to use.

Chapter 6: Applications of ConversionKit
++++++++++++++++++++++++++++++++++++++++

ConversionKit is being used as the basis for a number of other packages so
before you start writing complex validators you might like to investigate some
of these other packages:

RecordConvert

    A set of tools for handling nested sets of records of the type you might
    encounter frequently when dealing with relational database management systems.
    The package provides a ``make_record()`` converter factory, a ``Record`` class
    and a ``make_list_of_records()`` converter factory. RecordConvert is also an
    implementation of the KERNS data model and contains tools for representing
    KERNS in XML and JSON as well as a special encoding for representing nested
    data structures in a simple key-value structure which proves useful when
    working with HTML forms in particular.

URLConvert

    A set of tools for building *rules* which are used to convert a URL to a
    dictionary of *routing variables* and for converting a dictionary of routing
    variables back to a URL. The routing variables extracted from the URL can be
    used for application dispatch or as a simple state store. Being able to 
    convert routing variables back to a URL allows you to make application code
    agnostic of the URLs which it uses. By modifying the URLConvert rules you 
    can then change a URL structure without affecting the applicaiton. 

FormConvert

    A set of converters specifically designed to convert Unicode strings recieved
    from a form submission (HTML or otherwise) into Python objects. The package
    is designed specifically around the KERNS data model and can easily produce
    data structures consisting of nested records from a single HTML form. It also
    contains tools for extracting deeply nested error messages so to display on
    the GUI if data cannot be converted successfully.

ConfigConvert

    A set of converters specifically geared towards the sorts of conversions 
    commonly performed when parsing config file data. Also includes tools to
    parse a config file encoded directly using a variant of the KENRS encoding
    specifically for configuration files.

Appendix A: Primer on Functional Python Programming
+++++++++++++++++++++++++++++++++++++++++++++++++++

Before you learn about ConversionKit in detail it is useful to know about
Python's more functional features since they are used extensively in
ConversionKit itself and you will need to use a similar approach if you write
your own converters.

In traditional Python you might write a class like this:

.. sourcecode :: pycon

    >>> class DateToString(object):
    ...     def __init__(self, format):
    ...         self.format = format
    ...
    ...     def convert(self, date):
    ...         return date.strftime(self.format)

You could then use this class to convert a date like this:

.. sourcecode :: pycon

    >>> import datetime
    >>>
    >>> date_to_date_in_words = DateToString('%a, %d %b %Y')
    >>> print date_to_date_in_words.convert(datetime.date(2009, 3, 22))
    Sun, 22 Mar 2009

Here the ``'%a, %d %b %Y'`` string tells the ``DateToString`` class to convert
dates to a string representing the Locale's date format. As you can see the
``date_to_date_in_words`` object is an instance of the ``DateToString`` class
and when its ``convert()`` method is called, the date in the locale's
representation is returned. 

.. caution ::

     Although the examples in this chapter refer to a ``DateToString``
     converter, a real ConversionKit implementation of such a converter would be
     slightly more complex. See the next chapter for details and an example.

If we create a new instance of the ``DateToString`` class with a different
format string we can create an object for performing a slightly different
conversion:

.. sourcecode :: pycon

    >>> date_to_uk_format = DateToString('%d/%m/%Y')
    >>> print date_to_uk_format.convert(datetime.date(2009, 3, 22))
    22/03/2009

This time the same ``DateToString`` class is used to create a
``date_to_uk_format`` object which converts the same date to a UK
representation.

So far this is all typical Python behaviour you should already have
encountered.

The ``__call__()`` Method
=========================

All Python classes have a special method named ``__call__()`` which is executed
if the class instance is called without a method name. Let's change the
definition of the ``DateToString`` class so that it uses a ``__call__()``
method instead of a ``convert()`` method:

.. sourcecode :: pycon

    >>> class DateToString(object):
    ...     def __init__(self, format):
    ...         self.format = format
    ...
    ...     def __call__(self, date):
    ...         return date.strftime(self.format)

This time the class is used like this:

.. sourcecode :: pycon

    >>> date_to_date_in_words = DateToString('%a, %d %b %Y')
    >>> print date_to_date_in_words(datetime.date(2009, 3, 22))
    Sun, 22 Mar 2009
    >>> date_to_uk_format = DateToString('%d/%m/%Y')
    >>> print date_to_uk_format(datetime.date(2009, 3, 22))
    22/03/2009

On lines 2 and 4, no method name is specified when calling the class instance.
Instead the ``date_to_date_in_words`` and ``date_to_uk_format`` instances are
called in the same way functions are called which causes Python to execute
their ``__call__()`` methods. As you can see, the result is the same as before.

In effect the ``DateToString`` class is used for nothing more than specifying
information about how the conversion code in the ``__call__()`` method should
perform. In this case there is another way of writing the same code in Python
which avoids the need to have a class at all.

Using Nested Functions
======================

Consider this code:

.. sourcecode :: pycon

    >>> def DateToString(format):
    ...     def DateToString_converter(date):
    ...         return date.strftime(format)
    ...     return DateToString_converter

You can use it in exaclty the same way as before:

.. sourcecode :: pycon

    >>> date_to_date_in_words = DateToString('%a, %d %b %Y')
    >>> print date_to_date_in_words(datetime.date(2009, 3, 22))
    Sun, 22 Mar 2009

It can take a little bit of thinking to understand how this code works if you
haven't seen this approach before. When the ``DateToString`` function is
called with a ``format`` argument it returns the ``DateToString_converter()`` function. 

In this case the ``DateToString_converter()`` function is assigned to the
``date_to_date_in_words`` variable so that in the second line it is actually
the ``DateToString_converter()`` function which is called with the
``datetime.date(2009, 3, 22)`` argument. If that doesn't quite make sense read
this section again and look at the code. If it still doesn't make sense try
testing the above code at a Python prompt to check it works. You'll see that
``date_to_date_in_words`` really is the ``DateToString_converter()`` function:

.. sourcecode :: pycon

    >>> date_to_date_in_words
    <function DateToString_converter at 0x...>

If you aren’t used to this style of programming you might be wondering how the
``DateToString_converter()`` function can access the ``format`` variable
passed to the ``DateToString()`` function even when the function has returned.
This is a feature of Python called a *closure*. It simply means that Python
keeps track of any of the variables passed to the outer function for you. If
you call the ``DateToString()`` function again with different arguments the
change won’t affect the ``DateToString_converter()`` functions which have
already been returned since a new ``DateToString_converter()`` function is
created each time ``DateToString`` is called and each function keeps track of
the arguments the outer function was called with when it was created.

.. sourcecode :: pycon

   >>> date_to_date_in_words2 = DateToString('%a, %d %b %Y') 
   >>> date_to_date_in_words is date_to_date_in_words2
   False

Please make sure you understand this section before you move on to learning
about the rest of ConversionKit because you will have to use these techniques
to write your own validators.

Why Not Just Use Python Classes?
================================

In ConversionKit the same converter is designed to be used over and over again.
If converters were implemented as classes it would be possible for an
inexperienced developer set an instance variable:

.. sourcecode :: pycon

    >>> class DateToString(object):
    ...     def __init__(self, format):
    ...         self.format = format
    ...
    ...     def __call__(self, date):
    ...         return date.strftime(self.format)
    ... 
    >>> date_to_date_in_words = DateToString('%a, %d %b %Y')
    >>> print date_to_date_in_words(datetime.date(2009, 3, 22))
    Sun, 22 Mar 2009
    >>>
    >>> date_to_date_in_words.format = '%d/%m/%Y'
    >>> print date_to_date_in_words(datetime.date(2009, 3, 22))
    22/03/2009

Notice that in line 3 the ``.format`` attribute is set so that the
``date_to_date_in_words`` now doesn't return a date in words at all but instead
returns a string in a UK date format.

This might not seem like a big deal, but ConversionKit is also designed to deal
with horribly complex conversions involving nested lists and dictionaries, post
converters, chains and pre-converters, each operating on child conversions and
keeping track of errors. If one converter were to suddenly start behaving in
different way because a piece of code in a completely different part of the
application changed an attribute it could create a bug that was very difficult
to track down. To help prevent this possibility, ConversionKit uses a
functional approach so that the code using a converter can't access the
variables used to create the function.

.. note ::

    Technically you can access the variables in a closure from
    one of the "private" varibales attached to a function object, but you can't
    change them so this approach is genuinely more secure.

Extending PEP 8
===============

PEP 8 is a document which defines the recommended coding conventions which
should be used when writing Python. Amongst the recommendations are that
classes should always start with a capital letter and that functions should
always start with a lowercase letter. PEP 8 purists might be very unhappy with
the fact that in the functional examples so far, the ``DateToString`` function
has been named with an upper case letter to look like a class.

Rather than naming functions like classes, ConversionKit and the libraries
on which it is based follow this convention:

* Functions which return functions and which behave a little like classes with
  a ``__call__()`` method should be named in camelCase with a lowercase first
  letter. All other functions and variable names should be lowercase with words
  seprarated by underscore characters.

Following this convention, the ``DateToString()`` function we've been using as
an example in this appendix would actually be named ``dateToString()`` if it
were used in ConversionKit.

To make it easier to rename pairs of inner and outer functions it is
recommended that the inner function from such a class be named with the same
name as the outer function (in camelCase) but with ``_converter`` appended to
it. This is the convention you'll see used in ConversionKit and its
documentation.

Appendix B: Tips
++++++++++++++++

1. Think about how you want to represent the data in the interface
2. Think about all the places error messages will be displayed
3. Decide on the validation structure based on the error messages you want the conversions to produce
4. Design your Form class based on the kerns-encoded data structures (not the Python objects)

Most important: **Don't share converters between API and web interface**

.. include :: formencode.rst
