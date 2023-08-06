
import logging
log = logging.getLogger('conversionkit')

class NoValue(object):
    """A class representing no value"""

def get_error(errors_str, conversion):
    if conversion.children:
        for child in conversion.children:
            if not hasattr(child, 'conversionkit_conversion_api'):
                return
            if child.error:
                errors_str += '\n'+child.error
            if child.children:
                get_error(errors_str, child)

class Conversion(object):
    conversionkit_conversion_api = '0.1'
    def __init__(self, value=NoValue(), state=None):
        self._value = value
        self.error = None
        self.children = None 

    def set_result(self, value):
        self._value = value

    def get_result(self):
        if self.error is not None:
            raise ConversionError(self, self.error)
        else:
            return self._value

    value = property(get_result, set_result)

    def get_all_errors(self):
        errors_str = self.error
        get_error(errors_str, self)
        return errors_str
        
class ConversionError(Exception):
    """\
    Raised if a result is accessed on a conversion when no result has been set.
    """
    def __init__(self, conversion, *k, **p):
        Exception.__init__(self, *k, **p)
        self.conversion = conversion

class Group(object):
    def __init__(
        self, 
        handlers, 
        default_source_encoding=None, 
        default_destination_encoding=None, 
        default_source_type=None, 
        default_destination_type=None
    ):
        self.handlers = handlers
        self.default_source_encoding = default_source_encoding
        self.default_destination_encoding = default_destination_encoding
        self.default_source_type = default_source_type
        self.default_destination_type = default_destination_type

    def filter(
        self, 
        source_encoding = None, 
        destination_encoding = None, 
        source_type = None, 
        destination_type = None,
        default_source_encoding=None, 
        default_destination_encoding=None, 
        default_source_type=None, 
        default_destination_type=None
    ):
        handlers = self.find_handlers(source_encoding, destination_encoding, source_type, destination_type)
        return Group(
            handlers, 
            default_source_encoding or source_encoding or self.default_source_encoding,
            default_destination_encoding or destination_encoding or self.default_destination_encoding,
            default_source_type or source_type or self.default_source_type,
            default_destination_type or destination_type or self.default_destination_type,
        )

    def find_handlers(
        self, 
        source_encoding = None,
        destination_encoding = None,
        source_type = None,   
        destination_type = None,
    ):
        handlers = self.handlers
        if handlers:
            parts = [source_encoding, destination_encoding, source_type, destination_type]
        
            for i, part in enumerate(parts):
                if part is not None:
                    filtered_handlers = {}
                    for spec, handler in handlers.items():
                        opts = spec[0][0], spec[1][0], spec[0][1], spec[1][1]
                        if opts[i] == part:
                            filtered_handlers[spec] = handler
                    handlers = filtered_handlers
        return handlers

    def perform(self,
        value,
        state=None,
        source_encoding = None,
        destination_encoding = None,
        source_type = None,
        destination_type = None,
    ):
        this_source_encoding = source_encoding or self.default_source_encoding
        this_destination_encoding = destination_encoding or self.default_destination_encoding
        this_source_type = source_type or self.default_source_type
        this_destination_type = destination_type or self.default_destination_type
        handlers = self.find_handlers(
            this_source_encoding,
            this_destination_encoding,
            this_source_type,
            this_destination_type
        )
        if len(handlers) > 1:
            raise Exception('Too many handlers matched %r'%handlers.keys())
        elif len(handlers) == 1:
            handler = handlers.values()[0]
            result = handler(conversion=Conversion(value), state=state)
            if not isinstance(result, Conversion):
                raise Exception('Handler %s failed to return a valid Conversion object, instead returning %r'%(handler, result))
            return result
        else:
            raise Exception('No such handler ((%r, %r), (%r, %r))'%(
                this_source_encoding,
                this_source_type,
                this_destination_encoding,
                this_destination_type,
            ))


def null_handler(conversion, state=None):
    return conversion 


# Form handling
class Schema(object):
    def __init__(
        self,
        handlers,
        types=None,
        pre_handlers=None,
        post_handlers=None,
        source_encoding='webform',
        destination_encoding='python',
    ):
        self.handlers = handlers
        if not isinstance(self.handlers, Group):
            raise Exception('Expected the handlers to be a Group object, not %r'%type(handlers))
        if types is None:
            # Assume the names of the fields also represent their type
            self.types = {}
            for key in self.handlers.handlers.keys():
                self.types[key[0][1]] = key[0][1]
        else:
            self.types = types
        self.pre_handlers = pre_handlers or []
        self.post_handlers = post_handlers or []
        self.source_encoding = source_encoding
        self.destination_encoding = destination_encoding

    def __call__(self, conversion, state=None):
        if conversion.error:
            raise Exception('Calling schema.__call__ with a conversion with an error')
        for handler in self.pre_handlers:
            log.debug('Calling %r with conversion object %r', handler, conversion)
            conversion = handler(conversion, state)
            if not isinstance(conversion, Conversion):
                raise Exception('Expected a conversion object from pre handler %s, not %r'%(handler, conversion))
            if conversion.error:
                return conversion
        conversion.children = {}
        for key, value in conversion.value.items():
            if not self.types.has_key(key):
                raise Exception('No type map was specified for %r in %r'%(key, self.types))
            type = self.types[key]
            conversion.children[key] = self.handlers.perform(
                value, 
                source_type=type, 
                destination_type=type, 
                source_encoding=self.source_encoding, 
                destination_encoding=self.destination_encoding,
                state=state,
            )
        value = {}
        error = None
        for key, conv in conversion.children.items():
            if conv.error:
                log.debug('Conversion error in child: %r, %r', conv.error, conv)
                if error is None:
                    error = ''
                error += ' '+conv.error#'Some of the child fields contain errors: %s'%conv.error
                if not error.strip():
                    raise Exception('The child field %r had an empty .error attribute'%conv)
            else:
                log.debug('Conversion error is %r %r', conv.error, conv)
                log.debug('Conversion success, adding the value. %r', conv.__dict__.items())
                value[key] = conv.value
        conversion.value = value
        conversion.error = error
        if conversion.error:
            return conversion
        for handler in self.post_handlers:
            conversion = handler(conversion, state)
            if not isinstance(conversion, Conversion):
                raise Exception('Expected a conversion object from post handler %s, not %r'%(handler, conversion))
            if conversion.error:
                return conversion
        return conversion

class PostHandler(object):
    pass
class PreHandler(object):
    pass

class MakeObject(PostHandler):
    def __init__(self, object):
        self.object = object

    def __call__(self, conversion, state=None):
        # Call the object with the conversion value in the MakeObject post validator.
        conversion.value = self.object(**conversion.value)
        return conversion

class AllFieldsPresent(PreHandler):
    def __init__(self, required=None, optional=None, allow_extra=True, filter_extra=False):
        self.required = required or []
        self.optional = optional or []
        self.allow_extra = allow_extra
        self.filter_extra = filter_extra

    def __call__(self, conversion, state=None):
        """\
        Check the conversion value is a dictionary then check each of the required keys
        is present. If ``allow_extra`` is ``False`` any fields not in the ``required``
        or ``optional`` list of fields causes an error to be returned. The
        ``filter_extra`` option is only used if ``allow_extra`` is True and results in
        all the extra fields being removed from the value dictionary.
        """
        required, optional, allow_extra, filter_extra = self.required, self.optional, self.allow_extra, self.filter_extra
        conversion = check_is_dict(conversion)
        allowed = required + optional
        for key in required:
            if not key in conversion.value.keys():
                conversion.error = 'The field %r was not submitted'%key
                return conversion
        filtered = {}
        to_filter = []
        for key in conversion.value.keys():
            if key in allowed:
                filtered[key] = conversion.value[key]
            else:
                to_filter.append(key)
        if allow_extra == False:
            if len(to_filter) == 1:
                conversion.error = 'The field %r was not expected'%to_filter[0]
                return conversion
            elif len(to_filter) > 1:
                conversion.error = 'The fields %r were not expected'%(', '.join(to_filter))
                return conversion
        if filter_extra == True:
            conversion.value = filtered
        return conversion

# These are effectively pre-filters they still put their result in result though.
def check_is_dict(conversion):
    """\
    Check the submitted conversion object holds a dictionary and raise a ``ConversionError`` if not.
    """
    if not isinstance(conversion.value, dict):
        raise ConversionError('Expected a dictionary, not %r'%conversion.value)
    return conversion
#
#def list_to_human(self, input, fn=repr):
#    # XXX What about internationalisation in the and ? _()
#    length = len(input)
#    if length == 1:
#        return fn(input[0])
#    elif length > 1:
#        return '%s and %s'%(', '.join([fn(x) for x in input[-(length+1):-1]]), fn(input[-1]))
#    return ''
#
#def form_to_python(self, to, converter):
#    # Check all the expected keys are there
#    conversion = check_keys_are_present(
#        to, 
#        required=['time', 'date', 'title'],
#        optional=[],
#        allow_extra=True,
#        filter_extra=True
#    )
#    if conversion.error:
#        return conversion
#    errors = []
#    for key in conversion.value.keys(): 
#        conversion.value[key] = convert.to('python'+key, conversion.value[key])
#        if conversion.value[key].error:
#            errors.append(key)
#    if len(errors) > 1:
#        conversion.error = 'The fields %s are not valid, please correct the errors'%list_to_human(errors)
#    elif len(errors) == 1:
#        conversion.error = 'The field %s is not valid, please correct the errors'%list_to_human(errors)
#
#    # Check required fields have values - or handle in the valid within the converter???
#    return conversion

