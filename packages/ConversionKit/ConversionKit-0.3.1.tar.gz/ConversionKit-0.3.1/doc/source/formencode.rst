Appendix C: FormEncode Compatibility
++++++++++++++++++++++++++++++++++++

At the time of writing the dominant validation and conversion library for
Python is called FormEncode. In order to facilitate re-use of existing code
ConversionKit has been written to be compatible with FormEncode.

ConversionKit is also designed as an alternative/replacement for FormEncode
which aims to:

* Designed around one-way conversions rather than two-way conversions
* Provide better state information about the conversion taking place by 
  using a conversion object for each conversion
* Remove the need for ``Invalid`` exceptions to provide a more natural API for
  accessing errors
* Use no complex Python code in any of the implementation, making it much more
  straightforward to extend or customise
* Supports deeply-nested sets of conversions based on lists and ordered 
  dictionaries

ConversionKit supports FormEncode validators and schema as well its own
converters. ConversionKit will automatically handle FormEncode ``Invalid``
exceptions and set the conversion object's ``.error`` attribute with an
appropriate value.

Here's an example:

.. sourcecode :: pycon

    >>> class State(object): pass
    >>> state = State()
    >>>
    >>> from conversionkit import Conversion
    >>> import formencode
    >>>
    >>> validator = formencode.validators.DateConverter()
    >>> Conversion('12/12/2009').perform(
    ...     validator, 
    ...     state, 
    ...     formencode_method='to_python'
    ... ).result
    datetime.date(2009, 12, 12)

All FromEncode validators and converters have two conversion functions, one
to convert to Python and one designed to convert from Python. This means
FormEncode validators can perform two types of conversion whereas a
ConversionKit converter only performs *one* conversion. To use FormEncode
validators and schema with ConversionKit you need to tell ConversionKit
which converter you wish to use. Notice that the ``perform()`` method takes
an extra argument named ``formenocde_method``. This can take the string
value ``'to_python'`` or ``'from_python'`` depending on which of the
FormEncode validator's methods you wish to use. This allows you to use
existing validators with ConversionKit.

If you have FormEncode installed, ConversionKit will derive it's ``Invalid``
exception class from the ``formencode.Invalid`` class. This means that you can
use ConversionKit in existing FormEncode code. Here's an example:

.. sourcecode :: pycon

    >>> import formencode
    >>> class EmptyState(object): pass
    >>> state = EmptyState()
    >>> try:
    ...     result = Conversion('12/02/2009').perform(
    ...         formencode.validators.DateConverter(),
    ...         state,
    ...         formencode_method='to_python',
    ...     ).result
    ... except formencode.Invalid, e:
    ...     print "Failed, %r"%e
    ... else:
    ...     print "Success: %r"%result
    ...
    Success: datetime.date(2009, 12, 2)

In its internal handling of FormEncode validators, ConversionKit uses two
tools which make FormEncode behave in a more standard way. You are free
to use them in your own code too. They are:

``ValidationState``
    A class which takes the ``state`` you wish to use as its only argument.
    During certain validation operations FormEncode sets certain attributes on
    the ``state`` object it receives. If you are using a custom state object
    you probably don't want these to actually be set on your object. This class
    intercepts the operations FromEncode uses and stores them internally so
    your state is not affected.

``error_to_dict()``
    This function takes a FormEncode exception object and converts it to a 
    dictionary of errors, raising an exception if there are any errors not
    associated with a field. 

In addition, if you are using a ``webob.Request`` object such as the one
used in Pylons you might want to use this function:

``params_to_dict()``
    This takes the ``request.params`` object and converts it into a normal
    dictionary, taking account of multiple values for the same key. If you 
    just called ``dict()`` on the object you'd only get the first value for
    each key.


