from dispatch import generic, strategy

@generic()
def transform_chart(data):
    pass

@generic()
def parse_set(data):
    """Parses a data set"""

@generic()
def parse_category(data):
    """Parse a category"""

from elements import *

@parse_set.when('isinstance(data, tuple)')
def _parse_set_from_tuple(data):
    if len(data)==1:
        return DataPoint(value=data[0])
    elif len(data)==2:
        return DataPoint(label=data[0], value=data[1])
    elif len(data)==3:
        return DataPoint(label=data[0], value=data[1], toolText=data[2])
    else:
        raise ValueError, "Invalid data tuple"

@parse_set.when('isinstance(data, (int, float))')
def _parse_set_from_int(data):
    return DataPoint(value=data)

@parse_set.when('isinstance(data, basestring) and data=="|"')
def _parse_set_from_pipe(data):
    return vLine()

@parse_set.when(strategy.default)
def _parse_default(data):
    return data

@parse_category.when('isinstance(data, basestring)')
def _parse_category_from_string(data):
    return {'label': data}

@parse_category.when('isinstance(data, dict)')
def _parse_category_from_dict(data):
    return data

