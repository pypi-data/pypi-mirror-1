"""\
Conversion Toolkit

See the docs/manual.txt for an explanation of what these classes do.
"""

import logging
log = logging.getLogger(__name__)

from formbuild import ValidationState, errors_to_dict

def message_handler(level, message):
    """\
    Triggered when an error, warning or other message has been set so that you 
    can provide additional handling. By default messages other than ``error``
    are simply logged to the ConversionKit logger.
    """
    log.level(level, message)

#
# Exceptions
#

class ConverterBug(Exception):
    pass

# Formencode compatibility of exceptions
formencode_present = False
try:
    import formencode
except ImportError:
    class ConversionError(Exception):
        pass
else:
    formencode_present = True
    # Derive the exception from a formencode.Invalid exception for
    # compatibility with existing code.
    class ConversionError(formencode.Invalid):
        def __init__(self, message):
            formencode.Invalid.__init__(self, message, {}, None)

class ConversionError(Exception):
    pass

class _Conversion(object):
    """\
    When writing handlers for this conversion object you should ensure that
    handlers designed to work with single values set the .result attribute
    directly whereas handlers which operate on nested data structures set
    the .children attribute and leave this object to calculate the result 
    from the child conversions.
    """
    def __init__(self, value, message_handler=message_handler):
        self._value = value
        self.dirty = True
        # This will get recalculated on first access because ``.dirty`` above
        # is ``True``
        self._valid = None
        # We store the result in a list to distinguish between a result which 
        # hasn't been set and one that has
        self._result = []
        self._error = []
        self.overall_error = None
        self.children = self
        self.child_type = None

    def perform(self, handler, state=None, formencode_method=None):
        if formencode_method is not None:
            # Use formencode compatibility mode 
            try:
                validation_state = ValidationState(state)
                result = getattr(handler, formencode_method)(
                    self.value, 
                    validation_state
                )
            except formencode.Invalid, e:
                self.error = errors_to_dict(e)
            else:
                self.result = result
        else:
            handler(self, state)
        return self

    def _calculate_key_properties(self):
        """
        This function simultaneously calculates the .result, .error and .valid 
        attributes.
        """
        if self.dirty:
            #. The child fields have changed, better update the results
            #. Conversion objects are designed to handle three cases:
            #  * A single value is being converted
            #  * A struct of key value pairs is being converted
            #  * A list of structs of key value pairs is being converted
            #  They can also handle the case where a nested data structure 
            #  composed of structs and lists of structs is made. 
            #. The three core cases are handled in the three ways coded for 
            #  below
            if isinstance(self.children, list):
                # This is a repeating list of structs
                result = []
                error = {}
                for i, child in enumerate(self.children):
                    if child.valid is False:
                        self._valid = False
                        error[i] = child.error
                    elif child.valid is True:
                        result.append(child.get_result(internal_call=True))
                    else:
                        raise Exception('No result or error has been set')
                if self._valid is None:
                    self._valid = True
                self._result = [result]
                if self.overall_error:
                    self._error = [self.overall_error]
                else:
                    self._error = [self.overall_error]#str(error)]
            elif isinstance(self.children, dict):
                # This is a struct
                result = {}
                error = {}
                for k, child in self.children.items():
                    if child.valid is False:
                        self._valid = False
                        error[k] = child.error
                    elif child.valid is True:
                        result[k] = child.result
                    else:
                        raise Exception(
                            'No result or error has been set for %r with '
                            'value %r'%(self, self._value)
                        )
                if self._valid is None:
                    self._valid = True
                if self.child_type:
                    result = self.child_type(result)
                    error = self.child_type(error)
                self._result = [result]
                if self.overall_error:
                    self._error = [self.overall_error]
                else:
                    self._error = [str(error)]
            else:
                # It is a single value so either it refers to self or is an
                # overall value for a nested conversion
                if self is not self.children:
                    self._error = self.children._error
                    self._valid = self.children._valid
                    self._result = self.children._result
                else:
                    # The correct attributes are already set so we don't need
                    # to do anything
                    pass

    def get_error(self):
        #. Calculate the values if necessary
        self._calculate_key_properties()
        if self._valid is False and not len(self._error):
            raise ConverterBug(
                'This conversion is marked as invalid but no error has been '
                'set. Please check that the handler used actually sets '
                '.error'
            )
        # raise an Exception if valid isn't set.
        elif self._valid is None:
            raise Exception(
                'No errors or result has been set. It is possible you have '
                'forgotten to perform a conversion by calling .perform() or '
                'that the handler you used has failed to behave correctly.'
            )
        # Now return the value:
        return self._error[0]

    def set_error(self, error):
        if not isinstance(self, SingleConversion):
            raise Exception(
                "The handler should not set the result of a NestedConversion "
                "directly. Instead it should build up a structure of child "
                "conversions"
            )
        if len(self._result):
            raise Exception(
                'You cannot set an error while an result is present'
            )
        # Set dirty in case this is a NestedConversion
        self.dirty = True
        self._valid = False
        self._error = [error]

    def get_result(self, internal_call=False):
        #. Calculate the values if necessary
        self._calculate_key_properties()
        #. If this isn't an internal call we need to raise an exception if 
        #  the value isn't valid
        if not internal_call and self._valid is False:
            raise ConversionError(self._error[0])
        # raise an Exception if valid isn't set.
        if self._valid is None:
            raise Exception(
                'No errors or result has been set. It is possible you have '
                'forgotten to perform a conversion by calling .perform() or '
                'that the handler you used has failed to behave correctly.'
            )
        # Now return the value:
        if not self._result:
            raise ConverterBug(
                'This conversion is marked as valid but no result has been '
                'set. Please check that the handler used actually sets '
                '.result'
            )
        return self._result[0]

    def set_result(self, result):
        if not isinstance(self, SingleConversion):
            raise Exception(
                "The handler should not set the result of a NestedConversion "
                "directly. Instead it should build up a structure of child "
                "conversions"
            )
        if len(self._error):
            raise Exception(
                'You cannot set a result while an error is present'
            )
        # No need to set dirty because this is only used in SingleConversions
        self._valid = True
        self._result = [result]

    def get_value(self):
        return self._value

    def set_value(self, value):
        raise Exception(
            'You cannot set the value direclty. Please create a new '
            'conversion object'
        )

    def get_valid(self):
        """\
        Can return ``True``, ``False`` or ``None`` if no conversion has yet
        been performed.
        """
        return self._valid

    def set_valid(self, value):
        raise Exception(
            'You cannot set whether a conversion is valid or not direclty.'
        )

    # Properties (available since Python 2.2)
    result = property(get_result, set_result)
    error = property(get_error, set_error)
    value = property(get_value, set_value)
    valid = property(get_valid, set_valid)

class SingleConversion(_Conversion):
    pass

class NestedConversion(_Conversion):
    pass

import datetime
def make_string_to_date(format='%d/%m/%Y'):
    def string_to_date(conversion, state=None):
        try:
            conversion.result = datetime.datetime.strptime(
                conversion.value, 
                format
            )
        except ValueError, e:
            conversion.error = str(e)
    return string_to_date

class EmptyState(object):
    """\
    An empty class whose instances can be used as a basis for a state to 
    be passed to ConversionKit handlers.

    Can be used like this::

        state = EmptyState()
        state.some_var = 'This will be accessible in the handler'

    You can use the state for passing around database connections or other
    more complex Python objects too.
    """
    pass


class Struct(object):
    def __init__(self, pre_handlers=None, handlers=None, post_handlers=None):
        self.pre_handlers = pre_handlers or []
        self.post_handlers = post_handlers or []
        self.handlers = handlers or {}

    def __call__(self, conversion, state=None):
        result = conversion.value
        # Loop over each of the pre_handlers, aborting if there is an error
        pre_handler_conversions = []
        for pre_handler in self.pre_handlers:
            pre_conversion = SingleConversion(result)
            pre_conversion.perform(pre_handler, state)
            if not pre_conversion.valid:
                # Set the main conversion error and return, rather than 
                # setting overall_error
                conversion.children = pre_conversion
                conversion.dirty = True
                conversion._calculate_key_properties()
                return
            pre_handler_conversions.append(pre_conversion)
            result = pre_conversion.result
        # Loop over the handlers, setting up a child conversion for each one
        # fields without a corresponding handler are removed
        conversion.children = {}
        errors = []
        for key, handler in self.handlers.items():
            if result.has_key(key):
                child_conversion = SingleConversion(result[key])
                child_conversion.perform(handler, state)
                if not child_conversion.valid:
                    errors.append(key)
                conversion.children[key] = child_conversion
        # Now update the conversion
        conversion._calculate_key_properties()
        if conversion.valid is False:
            if len(errors) > 2:
                conversion.overall_error = 'Some of the fields were not valid'
            elif len(errors) == 1:
                conversion.overall_error = 'The %s field is invalid'%errors[0]
            return 
        for post_handler in self.post_handlers:
            conversion.perform(post_handler, state)
            conversion.dirty = True
            conversion._calculate_key_properties()
            if not conversion.valid:
                return
        return conversion

        ##result = conversion.result
        ##children = conversion.children
        ##child_type = conversion.child_type
        ### Now run the conversion with the child conversions through each of 
        ### the post handlers
        ##post_handler_conversions = []
        ##for post_handler in self.post_handlers:
        ##    post_conversion = NestedConversion(result)
        ##    # Set the child conversions, manually
        ##    post_conversion.children = children
        ##    post_conversion.child_type = child_type
        ##    post_conversion.perform(post_handler, state)
        ##    if not post_conversion.valid:
        ##        # Set the main conversion error and return
        ##        conversion.children = post_conversion.children
        ##        conversion.overall_error = post_conversion.overall_error
        ##        conversion.child_type = post_conversion.child_type
        ##        conversion.dirty = True
        ##        return
        ##    post_handler_conversions.append(post_conversion)
        ##    result = post_conversion.result
        ##    children = post_conversion.children
        ##    child_type = post_conversion.child_type
        ##conversion.children = children
        ##conversion.child_type = child_type
        ##conversion.dirty = True
        ##conversion._calculate_key_properties()
        ##return conversion

def chain(*k):
    def handle_each_part_of_chain(conversion, state=None):
        result = conversion.value
        for handler in k:
            new_conversion = SingleConversion(result)
            handler(new_conversion, state)
            if not new_conversion.valid:
                conversion.error = new_conversion.error
                break
            else:
                result = new_conversion.result
        conversion.result = result
    return handle_each_part_of_chain

# Pre, handler, post

#def make_present(keys, raise_on_error=False):
#    def present(conversion, state=None):
#        for key in keys:
#            if not key in conversion.result.keys():
#                conversion.error = 'Missing key named %r'%(key)
#                if raise_on_error:
#                    raise Exception(conversion.error)
#                return
#        return conversion
#    return present

def if_missing(field, value):
    def if_missing_post_handler(conversion, state=None):
        if not conversion.result.has_key(field):
            conversion.children[field] = SingleConversion(value)
            conversion.children[field].perform(null)
            conversion.children[field]._calculate_key_properties()
    return if_missing_post_handler

def if_empty(field, value):
    def if_empty_post_handler(conversion, state=None):
        if not conversion.result.get(field):
            conversion.children[field] = SingleConversion(value)
            conversion.children[field].perform(null)
            conversion.children[field]._calculate_key_properties()
    return if_empty_post_handler

def exclude(fields):
    def exclude_handler(conversion, state=None):
        failed = []
        for field in fields:
            if field in conversion.value.keys():
                failed.append(field)
        if len(failed) == 1:
            conversion.error = 'The field %r is not allowed'%failed[0]
        elif len(failed) > 1:
            conversion.error = "The fields '%s' and %r are not allowed"%(
                "', '".join(fields[0:-1]), 
                fields[-1],
            )
        else:
            conversion.result = conversion.value
    return exclude_handler

def require(fields):
    def require_handler(conversion, state=None):
        failed = []
        for field in fields:
            if not field in conversion.value.keys():
                failed.append(field)
        if len(failed) == 1:
            conversion.error = 'The field %r was not present'%failed[0]
        elif len(failed) > 1:
            conversion.error = "The fields '%s' and %r were not present"%(
                "', '".join(fields[0:-1]), 
                fields[-1],
            )
        else:
            conversion.result = conversion.value
    return require_handler

def allow_empty(fields):
    """
    In ConversionKit, all fields which are submitted and have a handler
    have to have a value otherwise an error will be raised saying something
    along the lines of "Please enter a value". If an empty value is
    acceptable, the field can be explicity removed from the input so that it
    won't be valid. If you want to set a different value afterwards you can
    use an ``if_empty()`` post validator.

    The ``allow_empty()`` converter first checks the fields are present,
    then removes them if they are ``None`` or ``''``.
    """
    def allow_empty_handler(conversion, state=None):
        require(fields)(conversion, state)
        if conversion.valid:
            # Hack the conversion to remove the result
            conversion._result = []
            conversion._valid = None
            failed = []
            for field in fields:
                if conversion.value[field] in (None, ""):
                    del conversion.value[field]
            if not failed:
                conversion.result = conversion.value
    return not_allow_handler


def one_of(values):
    def one_of_handler(conversion, state=None):
        if not conversion.value in values:
            conversion.error = (
                'The value submitted is not one of the allowed values'
            )
        conversion.result = conversion.value
    return one_of_handler

def null(conversion, state=None):
    conversion.result = conversion.value
    return conversion

def require_if_present(present, fields):
    def require_if_present_handler(conversion, state):
        if not isinstance(fields, (list, tuple)):
            fields = [fields]
        if present in conversion.children.keys():
            for field in fields:
                if not field in conversion.chilren.keys():
                    # We need to replace the children with an overall error
                    conversion.children = SimpleConversion()
                    conversion.children.perform(null)
                    conversion.children.error = (
                        'The field %r, required if %r is present, could not '
                        'be found'%(field, present)
                    )
    return require_if_present_handler

def exactly_one_of(fields):
    def exactly_one_of_handler(conversion, state):
        found = []
        for k in conversion.children.keys():
            if k in fields:
                found.append(k)
            if len(found) == 2:
                # We need to replace the children with an overall error
                conversion.children = SimpleConversion()
                conversion.children.perform(null)
                conversion.children.error = (
                    'You should only specify %r or %r, not both'%(
                        found[0], 
                        found[1],
                    )
                )
                break
    return exactly_one_of_handler

def string_present(conversion, state=None):
    if not conversion.value.strip():
        conversion.error = 'No value was entered'
    else:
        conversion.result = str(conversion.value)
    

def string_to_integer(conversion, state=None):
    value = conversion.value
    try:
        result = int(value)
    except Exception, e:
        conversion.error = str(e)
    else:
        conversion.result = result
    return conversion

class ListOf(object):
    def __init__(self, handler):
        self.handler = handler

    def __call__(self, conversion, state=None):
        children = []
        errors = []
        for k in conversion.value:
            child_conversion = NestedConversion(k)
            child_conversion.perform(self.handler)
            if not child_conversion.valid:
                errors.append(child_conversion.error)
            children.append(child_conversion)
        if len(errors) >= 2:
            conversion.overall_error = 'Some of the items were not valid'
        elif len(errors) == 1:
            conversion.overall_error = 'One of the items was not valid'
        conversion.children = children
        conversion.dirty = True
        conversion._calculate_key_properties()
        return conversion
        
"""



Understanding the nested structs idea vs other data structures:

person.name = 'James'
person.addresses-1 = '3'
person.addresses-2 = '17'

{
    'person': {
     	'name': 'James',
        'addresses': [3, 17],
    }
}



person.name = 'James'
person.addresses-1.address_id = '3'
person.addresses-2.address_id = '17'

{
    'person': {
     	'name': 'James',
        'addresses': [
            {address_id: 3},
            {address_id: 17},
        ]
    }
}

SortedDict(dict)
Is order important?

"""

def unnest(conversion, state=None, current_level=None):
    """\
    The key point to note here is that ListOf produces a
    SingleConversion when it should really produce something which
    distinguishes it from a normal conversion, we are assuming that all such
    conversions are nested when maybe they aren't
    """
    keys = {}
    if current_level is None: 
        current_level = ''
    if isinstance(conversion.children, dict):
        for name, child in conversion.children.items():
            if not child.valid:
                if isinstance(child, SingleConversion):
                    # It could be a single value, a list or a dictionary
                    keys[name] = child.error
                    if isinstance(child.children, list):
                        # For each item in the list, recurse
                        for i, sub_child in enumerate(child.children):
                            if not sub_child.valid:
                                keys[name+'-'+str(i)] = sub_child.error
                                for k, v in unnest(sub_child, state).items():
                                    keys[name+'-'+str(i)+'.'+k] = v
                    elif isinstance(child.children, dict):
                        # For each item in the dictionary, recurse
                        for key, sub_child in child.children.items():
                            if not sub_child.valid:
                                keys[name+'.'+key] = sub_child.error
                                for k, v in  unnest(sub_child, state).items():
                                    keys[name+'.'+key+'.'+k] = v
                    else:
                        keys[name] = child.children.error
                        #raise Exception(
                        #    'Querns format doesn\'t accept a dictionary of %r '
                        #    'objects'%type(child.children)
                        #)
                else: 
                    print "1Dealing with type %s" % type(child)
                    for k, v in unnest(child, state).items():
                        keys[name+k] = v
            else:
                raise Exception('Unexpected chid format %s'%child)
    elif isinstance(conversion.children, list):
        raise Exception('Standlone lists are not supported by kerns format')
    else:
        pass
    return keys

"""
Not allowed:

* A list of values
* A value
* A list of lists?? -> No, because surely that would imply no key being used.
[
    [
        {'key': 'value'}
    ],
]

Allowed Cases: The idea is that the cases below can be used to model any object
or sub object that can be modelled in a relational database and therefore any
relationship. Therefore to test our Schema we simply need to test these cases.
Ideally a list of lists, a single value or a list of values should raise an
exception as it is created but this isn't implemented yet. 
"""

