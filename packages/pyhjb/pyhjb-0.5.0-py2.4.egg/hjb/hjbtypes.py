"""
Provides

  - extensions to the normal python types that automatically convert
  HJB-encoded values.

  - functions that convert between python types and their HJB-encoded
    equivalents.
   
"""
import types
import re
from base64 import b64decode, b64encode

codecs = {
    "boolean": {
        "decoder": lambda x : BooleanType("true" == x.groups()[0].lower()),
        "pattern": re.compile(r"^\s*\(boolean\s*(\S+)\)\s*$"),
        "formatter": "(boolean %s)",
    },
    "byte_array": {
        "decoder": lambda x : ByteArrayType(b64decode(x.groups()[0])),
        "pattern": re.compile(r"^\s*\(base64\s*?(.*?)\)\s*$"),
        "formatter": "(base64 %s)",
        "encoder": b64encode
    },            
    "byte": {
        "decoder": lambda x : ByteType(x.groups()[0]),
        "pattern": re.compile(r"^\s*\(byte\s*([-+]?\d+)\)\s*$"),
        "formatter": "(byte %d)",
    },
    "char": {
        "decoder": lambda x : CharType(int(x.groups()[1], 16)),
        "pattern": re.compile(r"^\s*\(char\s*(\\u([0123456789aAbBcCdDeEfF]{1,4}))\)\s*$"),
        "formatter": "(char \\u%04X)",
        "encoder": ord,
    },
    "double": {
        "decoder": lambda x : DoubleType(x.groups()[0]),
        "pattern": re.compile(r"^\s*\(double\s*([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?)[fFdD]?\)\s*$"),
        "formatter": "(double %.9G)",
    },
    "float": {
        "decoder": lambda x : FloatType(x.groups()[0]),
        "pattern": re.compile(r"^\s*\(float\s*([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?)[fFdD]?\)\s*$"),
        "formatter": "(float %.9G)",
    },
    "int": {
        "decoder": lambda x : IntType(x.groups()[0]),
        "pattern": re.compile(r"^\s*\(int\s*([-+]?\d+)\)\s*$"),
        "formatter": "(int %d)",
    },
    "long": {
        "decoder": lambda x : LongType(x.groups()[0]),
        "pattern": re.compile(r"^\s*\(long\s*([-+]?\d+[lL]?)\)\s*$"),
        "formatter": "(long %d)",
    },
    "short": {
        "decoder": lambda x : ShortType(x.groups()[0]),
        "pattern": re.compile(r"^\s*\(short\s*([-+]?\d+)\)\s*$"),
        "formatter": "(short %d)",
    },
}

ordered_codec_types = [
    "byte",
    "char",
    "short",
    "int",
    "long",
    "double",
    "float",
    "boolean",
    "byte_array"]

def hjbencode(type_, input_):
    """Encode input values using the specified type"""
    if type_ in codecs:
        if "encoder" in codecs[type_]:
            input_ = codecs[type_]["encoder"](input_)
        return codecs[type_]["formatter"] % (input_,)
    else:
        return input_
    
def hjbdecode(input_):
    """Decode encoded values into an equivalent python type"""
    for type_ in ordered_codec_types:
        p = codecs[type_]["pattern"].match(input_)
        if p:
            return codecs[type_]["decoder"](p)
    return input_
    
class hjbtype(type):
    
    def __init__(cls, name, bases, dict):
        
        def attr_value(name):
            value = dict.get(name, None)
            if not value:
                for b in bases:
                    if name in b.__dict__:
                        value = b.__dict__.get(name)
            return value
        
        hjb_type_name = attr_value("__hjbtype__")
        if not hjb_type_name:
            raise ValueError("No __hjbtype__ attribute has been assigned")
        if (hjb_type_name not in ordered_codec_types):
            raise ValueError("Unrecognised hjb type name [%s]" % (hjb_type_name,))
        
        hjb_overrides = attr_value("__hjb_overrides__")
        if not hjb_overrides:
            raise ValueError("No __hjb_overrides__ attribute has been assigned")
        #dict["__new__"] = new_hjb_type
        super(hjbtype, cls).__init__(name, bases, dict)

def new_hjb_type(cls, value):

    overrides = cls.__hjb_overrides__
    if type(value) != types.StringType:
        return overrides.__new__(cls, value)
    else:
        p = codecs[cls.__hjbtype__]["pattern"].match(value)
        if (p):
            return overrides.__new__(cls, codecs[cls.__hjbtype__]["decoder"](p))
        else:
            return overrides.__new__(cls, value)
        

class CharType(types.UnicodeType):
    """I represent an HJB-encoded Java char"""

    __metaclass__ = hjbtype
    __hjbtype__ = "char"
    __hjb_overrides__ = types.UnicodeType

    def __new__(cls, value):
        
        # There's always one special case ;-)
        # CharType can't use new_hjb_type because we want to
        # create single characters, but there is no single
        # unicode character class
        overrides = cls.__hjb_overrides__
        if type(value) != types.StringType:
            return overrides.__new__(cls, unichr(value))
        else:
            p = codecs[cls.__hjbtype__]["pattern"].match(value)
            if (p):
                return overrides.__new__(cls, codecs[cls.__hjbtype__]["decoder"](p))
            else:
                if len(value) > 1:
                    raise ValueError("Invalid literal for type %s: %s" % (cls, value))
                return overrides.__new__(cls, unichr(value))
        
    def __str__(self):
        return hjbencode(self.__hjbtype__, self)

def hjb_char(value):
    return CharType(value)
        
class IntType(types.IntType):

    __metaclass__ = hjbtype
    __hjbtype__ = "int"
    __hjb_overrides__ = types.IntType
    __new__ = new_hjb_type
                
    def __str__(self):
        return hjbencode(self.__hjbtype__, self)


def hjb_int(value):
    return IntType(value)

class BooleanType(IntType):
    """I represent an HJB-encoded Java boolean"""

    __hjbtype__ = "boolean"

    def __str__(self):
        return hjbencode(self.__hjbtype__, bool(self))


def hjb_bool(value):
    return BooleanType(value)

            
class ByteType(IntType):
    """I represent an HJB-encoded Java byte"""

    __hjbtype__ = "byte"


def hjb_byte(value):
    return ByteType(value)
                
            
class ShortType(IntType):
    """I represent an HJB-encoded Java short"""

    __hjbtype__ = "short"


def hjb_short(value):
    return ShortType(value)
                
            
class LongType(types.LongType):
    """I represent an HJB-encoded Java long"""

    __hjbtype__ = "long"
    __hjb_overrides__ = types.LongType
    __metaclass__ = hjbtype
    __new__ = new_hjb_type
                
    def __str__(self):
        return hjbencode(self.__hjbtype__, long(self))


def hjb_long(value):
    return LongType(value)


class FloatType(types.FloatType):
    """I represent an HJB-encoded Java float"""

    __hjbtype__ = "float"
    __hjb_overrides__ = types.FloatType
    __metaclass__ = hjbtype
    __new__ = new_hjb_type

def hjb_float(value):
    return FloatType(value)

class DoubleType(FloatType):
    """I represent an HJB-encoded Java double"""

    __hjbtype__ = "double"

def hjb_double(value):
    return DoubleType(value)
    
class ByteArrayType(types.StringType):
    """I represent an HJB-encoded byte array"""

    __hjbtype__ = "byte_array"
    __hjb_overrides__ = types.StringType
    __metaclass__ = hjbtype
    __new__ = new_hjb_type

    def __str__(self):
        return hjbencode(self.__hjbtype__, self)

def hjb_byte_array(value):
    return ByteArrayType(value)
