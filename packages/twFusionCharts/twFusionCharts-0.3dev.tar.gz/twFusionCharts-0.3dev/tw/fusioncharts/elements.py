try:
    from xml.etree.ElementTree import Element
except ImportError:
    from cElementTree import Element

def stringify_dict(d):
    """Coverts all values of the given dictionary to strings inplace"""
    for key in d.keys():
        value = d[key]
        if isinstance(value, basestring):
            d[key]=value
        else:
            d[key]=str(value)
    return d

from meta import parse_set

class DataSet(object):
    def __init__(self, data, **attrs):
        self.data = [parse_set(d) for d in data]
        self.attrs = attrs

def DataPoint(**kwargs):
    stringify_dict(kwargs)
    return Element('set', kwargs)

def vLine(**kwargs):
    stringify_dict(kwargs)
    return Element('vLine',kwargs)

def Line(**kwargs):
    stringify_dict(kwargs)
    return Element('line',kwargs)

def Style(name, style_type, **kwargs):
    stringify_dict(kwargs)
    kwargs['name']=name
    kwargs['type']=style_type
    return Element('style', kwargs)

class XElem(object):
    '''A nice convenience wrapper for building up large ElementTrees

    Use like this: (assuming the use of the Gantt class below)
    chart=GanttChart()
    chart.add(G.categories([
        G.category(start="1/1/2001", end="12/31/2001"),
        G.category(start="1/1/2002", end="12/31/2002"),
        G.category(start="1/1/2003", end="12/31/2003")],
                           align="center",
                           isBold="0"))
    '''
    valid_elems=None
    valid_attrs=None
    name=None

    def __init__(self, elems=None, **attrs):
        if elems is None: elems = []
        if not hasattr(elems, '__len__') or isinstance(elems, basestring):
            self.elems = [ elems ]
        else:
            self.elems = list(elems)
        self.attrs = attrs
        if self.name is None:
            self.name = self.__class__.__name__

    def __validate(self):
        if self.valid_attrs:
            for a in self.attrs:
                assert a in self.valid_attrs, \
                       'Invalid attribute %s on element %s' % (a, self.name)
        if self.valid_elems:
            for e in self.elems:
                assert e.name in self.valid_elems, \
                       'Invalid element name %s in %s' % (e.name, self.name)
        for e in self.elems:
            e.__validate()

    def to_element(self):
        name = self.name
        if name is None: name = self.__class__.__name__
        elem = Element(self.name, **stringify_dict(self.attrs))
        for e in self.elems:
            try:
                elem.append(e.to_element())
            except AttributeError, ae:
                raise
        return elem

    def add(self, elem):
        self.elems.append(elem)

class Gantt(object):
    '''Elements available for Gantt charts'''
    class categories(XElem):
        name='categories'

    class category(XElem):
        name='category'

    class processes(XElem):
        name='processes'

    class process(XElem):
        name='process'

    class tasks(XElem):
        name='tasks'

    class task(XElem):
        name='task'

    class item(XElem):
        name='item'

    class legend(XElem):
        name='legend'

    class trendlines(XElem):
        name='trendlines'

    class line(XElem):
        name='line'

    class datatable(XElem): pass

    class datacolumn(XElem): pass

    class text(XElem): pass

class MultiAxis(object):
    class categories(XElem):
        name='categories'

    class category(XElem):
        name='category'

    class axis(XElem):
        name='axis'

    class dataset(XElem):
        name='dataset'

    class set(XElem):
        name='set'

    class styles(XElem):
        name='styles'

    class definition(XElem):
        name='definition'

    class style(XElem):
        name='style'
        
    class application(XElem):
        name='application'

    class apply(XElem):
        name='apply'

class Scatter(object):
    class categories(XElem):
        name='categories'

    class category(XElem):
        name='category'

    class dataset(XElem):
        name='dataset'

    class set(XElem):
        name='set'

class Waterfall(object):
    class set(XElem):
        name='set'
