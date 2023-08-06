from base import Schema
import types

### Utility / Example Types ###
def lower(value):
    """ 
        A lower-case string
        
        >>> print lower('HeLp')
        help
    """
    return str(value).lower()
    
def upper(value):
    """ 
        An upper-case string
        
        >>> print upper('HeLp')
        HELP
    """
    return str(value).upper()
    
def any(value):
    """ Returns whatever it gets. """
    return value

def items(object):
    """ Gets the items of an object or treats it like items. """
    if hasattr(object, 'items'):
        return object.items()
    else:
        return tuples(object)

tuple2 = Schema((int, int))
tuples = Schema([(any, any)])
    
### Complex Types ###
import datetime
def date(value):
    """
        Returns a date.  It can accept strings in the format: Y-M-D and M/D/Y
        
        >>> date("2008-2-5")
        datetime.date(2008, 2, 5)
    """
    if isinstance(value, datetime.date):
        return value
    if isinstance(value, datetime.datetime):
        return datetime.date(value.year, value.month, value.day)
    if isinstance(value, basestring):
        if '-' in value:
            return datetime.date(*(int(x) for x in value.split('-')))
        if '/' in value:
            month, day, year = value.split('/')
            return datetime.date(int(year), int(month), int(day))
        raise TypeError("String does not match format: 'Y-M-D' or 'M/D/Y'")
    raise TypeError("Unable to convert to a date: %r" % value)

def a_z(_value):
    """ 
        A string of characters only between a and z, inclusively. 
    
        >>> print a_z("hElP-45")
        help
    """
    value = str(_value).lower()
    value = "".join([i for i in value if i >= 'a' and i <= 'z'])
    if value:
        return value
    else:
        raise TypeError("Unable to convert value to only letters between a and z: %r" % _value)

def slug(value):
    """ 
        A string with nothing but characters betwen a and z, 0 through 9, and '-' representing spaces. 
        
        >>> print slug("hElP #45")
        help-45
        >>> print slug("Oh, Hai!")
        oh-hai
    """
    ret = []
    for c in str(value).lower():
        if (c >= 'a' and c <='z') or (c >= '0' and c <= '9'):
            ret.append(c)
        if c.isspace() or c == '-' and ret and ret[-1] != '-':
            ret.append('-')
    while ret and ret[0] == '-':
        ret.pop(0)
    while ret and ret[-1] == '-':
        ret.pop(-1)
    if ret:
        return "".join(ret)
    else:
        raise TypeError("Unable to convert value to a slug: %r", value)


def full_name(value):
    """
        Takes a value and returns a first and last name based on the value.
        
        >>> full_name('Bill Curtis')
        ('Bill', 'Curtis')
        >>> full_name('Curtis, Bill')
        ('Bill', 'Curtis')
        >>> full_name('Bill X. Curtis')
        ('Bill', 'Curtis')
        >>> full_name('Curtis, Bill X.')
        ('Bill', 'Curtis')
        >>> full_name('Curtis')
        (None, 'Curtis')
    """
    if isinstance(value, tuple):
        return tuple2(value)
    if ',' in value:
        names = value.split(',')
        names = [n.split()[0] for n in names]
        return names[-1], names[0]
    elif ' ' in value:
        names = value.split()
        return names[0], names[-1]
    else:
        return (None, value)
