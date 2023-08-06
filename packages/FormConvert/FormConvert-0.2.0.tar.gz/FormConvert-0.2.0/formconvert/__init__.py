import datetime

from conversionkit import set_error, message, chainConverters
from conversionkit.exception import ConversionKitError
from nestedrecord import decodeNestedRecord
from recordconvert import toRecord, toListOfRecords
from stringconvert import unicodeToUnicode, unicodeToInteger

#
# Exceptions
#

class FormConvertError(ConversionKitError):
    pass

#
# Pre-converters
#

class ExcludedFieldPresentError(Exception):
    pass

def excludeFields(fields, raise_exception=False):
    """\
    A pre-validator which ensures that the specified fields don't exist and
    which sets an error if they do. If ``raise_exception`` is ``True`` an 
    exception is raised instead of setting an error.
    """
    def excludeFields_converter(conversion, state=None):
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
        if not raise_exception and not conversion.successful:
            raise ExcludedFieldPresentError(conversion.error)
    return excludeFields_converter

import cgi
def multiDictToDict(encoding='utf8'):
    def multiDictToDict_converter(conversion, state=None):
        result = {}
        if isinstance(conversion.value, cgi.FieldStorage):
            for k in conversion.value.keys():
                v = conversion.value.getlist(k)
                if len(v) == 1:
                    if isinstance(v[0], unicode):
                        result[k] = v[0]
                    else:
                        result[k] = v[0].decode(encoding)
                else:
                    res = []
                    for item in v:
                        if isinstance(item, unicode):
                            res.append(item)
                        else:
                            res.append(item.decode(encoding))
                    result[k] = res
        elif conversion.value.__class__.__name__ in ['NestedMultiDict', 'UnicodeMultiDict', 'MultiDict']:
            for k in conversion.value.keys():
                v = conversion.value.getall(k)
                if len(v) == 1:
                    if isinstance(v[0], unicode):
                        result[k] = v[0]
                    else:
                        result[k] = v[0].decode(encoding)
                else:
                    res = []
                    for item in v:
                        if isinstance(item, unicode):
                            res.append(item)
                        else:
                            res.append(item.decode(encoding))
                    result[k] = res
        else:
            raise FormConvertError(
                'Cannot convert a %r object'% (
                    conversion.value.__class__.__name__
                )
            )
        conversion.result = result
    return multiDictToDict_converter

submit_image_to_record = toListOfRecords(
    toRecord(
        converters = dict(
            x = unicodeToInteger(),
            y = unicodeToInteger(),
            name = unicodeToUnicode(),
        )
    )
)

def handleSubmitImage(name, strip=False, raise_on_error=False):
    def handleSubmitImage_converter(conversion, state=None):
        found=False
        result = {}
        for k, v in conversion.value.items():
            if k.startswith(name+'.'):
                found = True
                if not strip:
                    result[name+'[0].'+k[len(name)+1:]] = v
            elif k == name:
                found = True
                if not strip:
                    result[name+'[0].value'] = v
            else:
                result[k] = v
        if not found and raise_on_error:
            raise ConversionKitError(
                'The expected image button field %r was not submitted'%name
            )
        conversion.result = result
    return handleSubmitImage_converter

def refactorDuplicateFields(name, id_name):
    """\
    When an HTTP form submission uses multiple fields with the same name
    this converter can be used to refactor then into a structure which 
    when decoded by NestedRecord results in a list or records.
    """
    def refactorDuplicateFields_converter(conversion, state=None):
        result = {}
        counter = 0
        for k, v in conversion.value.items():
            if k == name:
                for item in v:
                    new_key = name+'['+str(counter)+'].'+id_name
                    if result.has_key(new_key):
                        raise Exception(
                            'Cannot refactor duplicate fields, key %r already '
                            'present'%new_key
                        )
                    result[new_key] = item
                    counter += 1
            else:
                if result.has_key(k):
                    raise Exception(
                        'Cannot refactor duplicate fields, key %r already '
                        'present'%k
                    )
                result[k] = v
        conversion.result = result
    return refactorDuplicateFields_converter

def duplicateField(from_field, to_field):
    """\
    Copy the input value from the required field ``from_field`` to create a
    new field named ``to_field`` which is a duplicate of the original.
    """
    def duplicateField_converter(conversion, state=None):
        if conversion.value.has_key(to_field):
            conversion.error = 'Unexpected field %r'%to_field
        elif not conversion.value.has_key(from_field):
            conversion.error = 'The required field to be duplicated %r is missing'%from_field
        else:
            # Shouldn't modify the input dictionary, so take a copy
            conversion.result = conversion.value.copy()
            conversion.result[to_field] = conversion.result[from_field]
    return duplicateField_converter


#
# Useful post-converters
#

def sameValue(field1, field2):
    """\
    A post-converter which ensures ``field1`` and ``field2`` had the same
    input value.
    """
    def sameValue_post_converter(conversion, state=None):
        value = conversion.value
        if value[field1] != value[field2]:
            set_error(
                conversion.children[field2],
                'The fields %s and %s have different values' % (
                    field1,
                    field2,
                )
            )
            set_error(conversion, 'The fields are not valid')
    return sameValue_post_converter

def removeFieldsIfOtherFieldResultIs(
    present, 
    value, 
    fields,
    raise_if_field_to_remove_is_not_present=True
):
    """\
    Removes all the fields listed in the list ``fields`` if the field 
    ``present`` is present and has the value ``value``.
    """
    def removeFieldsIfOtherFieldResultIs_post_converter(conversion, state=None):
        result = conversion.value.copy()
        our_fields = fields
        if not isinstance(fields, (list, tuple)):
            our_fields = [fields]
        if present in result.keys() and result[present] == value:
            for field in our_fields:
                if not field in conversion.children.keys():
                    if raise_if_field_to_remove_is_not_present: 
                        raise FormConvertError(
                            'Could not remove the key %r because it is not '
                            'present'%field
                        )
                else:
                    del conversion.children[field]
                    del result[field]
        conversion.result = result
    return removeFieldsIfOtherFieldResultIs_post_converter

def exacltyOneFieldFrom(*fields):
    def exacltyOneFieldFrom_post_converter(conversion, state=None):
        found = []
        for k in conversion.children.keys():
            if k in fields:
                found.append(k)
        if len(found) == 2:
            set_error(
                conversion,
                'You should only specify %r or %r, not both'%(
                    found[0],
                    found[1],
                )
            )
        elif not found:
            set_error(
                conversion,
                'You must specify one of the fields %r'%(
                    fields,
                )
            )
    return exacltyOneFieldFrom_post_converter

def requireIfPresent(present, fields):
    """\
    Sets an overall error is the field ``present`` is present and any of the 
    fields in the list ``fields`` is not.
    """
    if not isinstance(fields, (list, tuple)):
        raise ConversionKitError(
            'The ``fields`` argument should be a list or a tuple, not '
            '%r' % type(fields)
        ) 
    def requireIfPresent_post_converter(conversion, state=None):
        if present in conversion.children.keys():
            for field in fields:
                if not field in conversion.children.keys():
                    set_error(
                        conversion,
                        'The field %r, required if %r is present, could not '
                        'be found'%(field, present)
                    )
                    return
    return requireIfPresent_post_converter

