# when execute plotting, will call for execution of motion_detector
from bokeh.models.annotations import Tooltip
from motion_detector import df

from bokeh.plotting import figure, output_file, show
# for the pop up window when hovered
from bokeh.models import HoverTool, ColumnDataSource

# convert all datetime to string first so that bokeh can read
df['Start_string'] = df['Start'].dt.strftime("%Y-%m-%d %H:%M:%S")
df['End_string'] = df['End'].dt.strftime("%Y-%m-%d %H:%M:%S")

cds = ColumnDataSource(df)  # convert the data to a column data source

p = figure(x_axis_type='datetime', height=100, width=500, sizing_mode='scale_width',
           title="Motion Graph")
p.yaxis.minor_tick_line_color = None
p.yaxis[0].ticker.desired_num_ticks = 1


# @Start means the column name = "Start"
hover = HoverTool(
    tooltips=[("Start", "@Start_string"), ("End", "@End_string")])
p.add_tools(hover)
q = p.quad(left='Start', right='End',  # here no need chg to start_string cause x_axis_type is datetime
           bottom=0, top=1, color="green", source=cds)
# tell bokeh to use this column data stores, dont point to the ori data

output_file("Graph.html")
show(p)
