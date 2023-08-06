from widgets import FusionChartsWidget 
from widgets import SingleSeriesChart, MultiSeriesChart
from widgets import GanttChart, MultiAxisChart
from elements import vLine, Line, DataPoint, DataSet, Style
from elements import Gantt, MultiAxis, Scatter, Waterfall


chart_types = [
# Single Series
    "FCF_Column2D", "FCF_Column3D", "FCF_Line", "FCF_Area2D", "FCF_Bar2D", "FCF_Pie2D", "FCF_Pie3D",
    "FCF_Doughnut2D", "FCF_Funnel",
# Multi Series
    "FCF_MSColumn2D", "FCF_MSColumn3D", "FCF_MSLine", "FCF_MSArea2D", 
    "FCF_MSBar2D", "FCF_MSColumn2DLineDY", "FCF_MSColumn3DLineDY",
    "FCF_Candlestick",
# Stacked
    "FCF_StackedColumn3D", "FCF_StackedColumn2D", "FCF_StackedBar2D", "FCF_StackedArea2D",
# Gantt
    "FCF_Gantt",
    ]

chart_class_names = [chart_type[4:]+'ChartWidget' for chart_type in chart_types]
for chart_type, chart_class_name in zip(chart_types, chart_class_names):
    globals()[chart_class_name] = type(chart_class_name, 
            (FusionChartsWidget,), 
            dict(chart_type=chart_type))

__all__ = ["FusionChartsWidget",
           "SingleSeriesChart", "MultiSeriesChart", "GanttChart", "MultiAxisChart", 
           "vLine", "Line", "DataPoint", "DataSet", "Style",
           'Gantt', 'MultiAxis', 'Scatter', "Waterfall",
           ] +chart_class_names

