"""\
Tools for working with a relational data model
"""

from conversionkit import toDictionary, MSG_DICTIONARY, chainConverters
from conversionkit import toListOf
from bn import AttributeDict

#
# Exceptions
#

class RecordConvertError(Exception):
    """\
    Exceptions of this type can end up being visible to the end user so the 
    messages should use plain English and not reveal anything about the
    application.
    """

#
# Record and Reserved Words
#

case_sensitive_reserved_words = []
case_insensitive_reserved_words = []

def enable_reserved_word_checking():
    """\
    Set up a list of reserved keywords from SQL, Python and JavaScript.
    ``Record`` instances will be prevented from using these words as keys.
    """
    if not case_sensitive_reserved_words:
        from recordconvert.reserved import case_sensitive_reserved_words as cs
        case_sensitive_reserved_words = cs
    if not case_sensitive_reserved_words:
        from recordconvert.reserved import case_insensitive_reserved_words as ci
        case_insensitive_reserved_words = ci

class ListOfRecords(list):
    """\
    A list which only holds records of the same type and proxies attributes to
    keys of the first item in the list
    """
    def __init__(self, items=[]):
        if isinstance(items, list):
            counter = 0 
            for item in items:
                if not isinstance(item, Record):
                    raise TypeError('Item at index %s is not a Record'%counter)
                counter += 1
            list.__init__(self, items)
        else:
            if not isinstance(items, Record):
                raise TypeError('Item passed to ListOfRecords() is not a Record')
            list.__init__(self, [items])

    def append(self, item):
        if not isinstance(item, Record):
            raise TypeError('Item is not a Record')
        list.append(self, item)

    def insert(self, pos, item):
        if not isinstance(item, Record):
            raise TypeError('Item is not a Record')
        list.insert(self, pos, item)
        
    def extend(self, items):
        counter = 0
        for item in items:
            if not isinstance(item, Record):
                raise TypeError('Item at index %s is not a Record'%counter)
        list.extend(self, items)
        
    def __setitem__(self, key, value):
        if not isinstance(value, Record):
            raise TypeError('Item is not a Record')
        list.__setitem__(self, key, value)
       
    def __setslice__(self, i, j, value):
        counter = 0
        for item in value:
            if not isinstance(item, Record):
                raise TypeError('Item at index %s is not a Record'%counter)
        list.__setslice__(self, i, j, value)

    def __setattr__(self, name):
        if len(self) and isinstance(self[0], AttributeDict):
            # This will trigger a failure. Don't set attributes
            # of a ListOfRecords instance
            return setattr(self[0], name)

    def __getattr__(self, name):
        if len(self) and isinstance(self[0], AttributeDict) and \
           hasattr(self[0], name):
            return getattr(self[0], name)

class Record(AttributeDict):
    """\
    The main class for dealing with records, derived from ``dict``.
    """

    def __setitem__(self, name, value):
        # check the name isn't a reserved word
        if name in case_sensitive_reserved_words:
            raise KeyError('The key %s is a reserved word')
        elif name.upper() in case_insensitive_reserved_words:
            raise KeyError('The key %s is a reserved word')
        # Check that the name doesn't start with an underscore or a
        # number
        first_char_ord = ord(name[0])
        if first_char_ord == 95 or \
           (first_char_ord >= 48 and first_char_ord <= 57):
            raise RecordConvertError(
                'Key names cannot start with an underscore (_) '
                'character or a digit'
            )
        for char in name:
            if not(
                (ord(char) >= 97 and ord(char) <= 122) or \
                (ord(char) >= 65 and ord(char) <= 90) or \
                (ord(char) >= 48 and ord(char) <= 57) or \
                ord(char) == 95
            ):
                raise RecordConvertError(
                    'Record keys cannot contain the character %r'%char
                )
        # Treat the key as Unicode even though it can be encoded as
        # ASCII
        return dict.__setitem__(self, unicode(name), value)

#
# Converters
#

def listToListOfRecords():
    def listToListOfRecords_converter(conversion, state=None):
        new_list = ListOfRecords()
        for item in conversion.value:
            new_list.append(Record(item))
        conversion.result = new_list
    return listToListOfRecords_converter

def toListOfRecords(converter, *k, **p):
    if isinstance(converter, Record):
        raise RecordConvertError(
            'toListOfRecords() takes a converter such as toRecord() as its '
            'argument, not a Record instance'
        )
    return chainConverters(toListOf(converter, *k, **p), listToListOfRecords())
    
def dictionaryToRecord():
    def dictionaryToRecord_converter(conversion, state=None):
        conversion.result = Record(conversion.value)
    return dictionaryToRecord_converter

def toRecord(
    converters,
    missing_defaults = None,
    empty_defaults = None,
    missing_errors = None,
    empty_errors = None,
    missing_or_empty_errors = None,
    missing_or_empty_defaults = None,
    filter_extra_fields=True,
    allow_extra_fields=True,
    raise_on_extra_fields=True,
    use_many_message_after_failures=3,
    msg_many_invalid_fields=MSG_DICTIONARY['msg_many_invalid_fields'],
    msg_some_invalid_fields=MSG_DICTIONARY['msg_some_invalid_fields'],
    msg_single_invalid_field=MSG_DICTIONARY['msg_single_invalid_field'],
    msg_field_not_allowed=MSG_DICTIONARY['msg_field_not_allowed'],
    msg_fields_not_allowed=MSG_DICTIONARY['msg_fields_not_allowed'],

):
    # Use the make_dictionary converter with the arguments specified and
    # the extra post-converter to make the result a record.
    return chainConverters(toDictionary(**locals()), dictionaryToRecord())

