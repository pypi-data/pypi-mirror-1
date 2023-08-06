import pkg_resources
from pkg_resources import resource_filename
from tw.api import CSSLink, JSLink, JSSource, Widget, Link
#from turbogears.widgets.meta import load_kid_template

#from turbogears import startup, view, expose, url, config
#from pylons import config
#from turbojson import jsonify
#import cherrypy
from mako.template import Template
from mako.lookup import TemplateLookup
import simplejson

from meta import parse_category, parse_set, transform_chart
from elements import stringify_dict, XElem


__all__ = ["FusionChartsWidget"]

# declare your static resources here

## JS dependencies can be listed at 'javascript' so they'll get included
## before
my_js = JSLink(modname=__name__, 
                filename='static/FusionCharts.js', javascript=[])

# my_css = CSSLink(modname=__name__, filename='static/fusioncharts.css')

class FusionChartsWidget(Widget):
    #template = """<div id="${id}">${value}</div>"""
    ## You can also define the template in a separate package and refer to it
    ## using Buffet style uris
    template = "tw.fusioncharts.templates.fusioncharts"
    engine_name = "mako" 

    javascript = [my_js]
    #css = [my_css]
    params = ['chart_type', 'width', 'height', 'debug_mode',
              'register_with_js', 'swf_file', 'data_xml', 'chart_url', 'chart']
    width = 450
    height = 450
    debug_mode = False
    register_with_js = False
    swf_file = None
    data_xml = None
    chart = None
    chart_url = None

    def __init__(self, id=None, parent=None, children=[], **kw):
        """Initialize the widget here. The widget's initial state shall be
        determined solely by the arguments passed to this function; two
        widgets initialized with the same args. should behave in *exactly* the
        same way. You should *not* rely on any external source to determine
        initial state."""
        super(FusionChartsWidget, self).__init__(id, parent, children, **kw)
        flash_dir='/static/flash'
        self.swf_file = Link(modname=__name__, 
                             filename='static/flash/%s.swf' % self.chart_type).link
        

    def update_params(self, d):
        """This method is called every time the widget is displayed. It's task
        is to prepare all variables that are sent to the template. Those
        variables can accessed as attributes of d."""
        super(FusionChartsWidget, self).update_params(d)
        if d['value']:
            chart = d['value']
        elif d['chart']:
            chart = d['chart']
            if callable(chart):
                chart=chart()
        else:
            chart = None
        if chart:
            chart_dict = transform_chart(chart)
            data_xml = chart.template_c.render(**chart_dict)
            d['data_xml'] = data_xml.replace('"', "'")
        if d['data_xml']:
            d['data_xml'] = simplejson.encode(d['data_xml'])

            
template_lookup = TemplateLookup(directories=[resource_filename(__name__, '/')])

class BaseChart(object):
    template = None
    def __init__(self, template, trendlines, **attrs):
        if template is not None:
            self.template = template
        if self.template:
            f_name = 'templates/%s.mak'%self.template
            self.template_c = template_lookup.get_template(f_name)
        self.attrs = stringify_dict(attrs)
        self.trendlines = trendlines or []
        self.styles = set()
        self.applications = []

    def add_trendline(self, trendline):
        self.trendlines.append(trendline)

    def add_trendlines(self, *trendlines):
        self.trendlines.extend(trendlines)

class SingleSeriesChart(BaseChart):
    template = "single_series"
    def __init__(self, data=(), trendlines=None, template=None, **attrs):
        BaseChart.__init__(self, template, trendlines, **attrs)
        self.data = [parse_set(d) for d in data]

class MultiSeriesChart(BaseChart):
    template = "multi_series"
    def __init__(self, categories=(), datasets=(), trendlines=None,
                 template=None, categories_attrs=None, **attrs):
        BaseChart.__init__(self, template, trendlines, **attrs)
        self.set_categories(categories)
        self.datasets = list(datasets)
        self.categories_attrs = stringify_dict(categories_attrs or {})

    def set_categories(self, categories):
        self.categories = [parse_category(category) for category in categories]

    def add_dataset(self, dataset):
        self.datasets.append(dataset)

    def add_datasets(self, *datasets):
        self.datasets.extend(datasets)

class GanttChart(BaseChart, XElem):
    template="xml"
    name='chart'
    valid_elems=set(['categories', 'processes', 'tasks', 'connectors',
                     'legend', 'trendlines'])
    def __init__(self, elems=None, **attrs):
        BaseChart.__init__(self, template=None, trendlines=None, **attrs)
        XElem.__init__(self, elems, **attrs)

class ScatterChart(BaseChart, XElem):
    template="xml"
    name='graph'
    valid_elems=set(['categories', 'processes', 'tasks', 'connectors',
                     'legend', 'trendlines'])
    def __init__(self, elems=None, **attrs):
        BaseChart.__init__(self, template=None, trendlines=None, **attrs)
        XElem.__init__(self, elems, **attrs)

class MultiAxisChart(BaseChart, XElem):
    template="xml"
    name='chart'
    valid_elems=set(['categories', 'axis', 'dataset', 'set',
                     'styles', 'definition', 'application'])
    def __init__(self, elems=None, **attrs):
        BaseChart.__init__(self, template=None, trendlines=None, **attrs)
        XElem.__init__(self, elems, **attrs)

class WaterfallChart(BaseChart, XElem):
    template="xml"
    name='chart'
    valid_elems=set(['set'])
    def __init__(self, elems=None, **attrs):
        BaseChart.__init__(self, template=None, trendlines=None, **attrs)
        XElem.__init__(self, elems, **attrs)
        
@transform_chart.when("isinstance(data, SingleSeriesChart)")
def transform_single_series_chart(chart):
    return dict(attrs=chart.attrs, trendlines=chart.trendlines,
                data=chart.data, styles=chart.styles, applications=chart.applications)

@transform_chart.when("isinstance(data, MultiSeriesChart)")
def transform_multi_series_chart(chart):
    return dict(attrs=chart.attrs, categories=chart.categories,
                datasets=chart.datasets, trendlines=chart.trendlines,
                categories_attrs=chart.categories_attrs, styles=chart.styles,
                applications=chart.applications)

@transform_chart.when('isinstance(data, XElem)')
def transform_xelem(elem):
    elem = elem.to_element()
    return dict(elem=elem)


