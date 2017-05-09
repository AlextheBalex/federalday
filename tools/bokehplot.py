from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.embed import components
from bokeh.models import NumeralTickFormatter


def get_plot_markup_xy(title, label_x, label_y, x, y, width=800, height=200,
                       x_axis_type="linear", y_axis_type="linear"):
    '''p = figure(
        width=width, height=height,
        tools="resize,pan,box_zoom,reset,save",
        # y_axis_type="log", y_range=[0.001, 10**11],
        title=title,
        x_axis_label=label_x,
        y_axis_label=label_y,
        x_axis_type=x_axis_type,
        y_axis_type=y_axis_type,
    )
    p.left[0].formatter.use_scientific = False

    p.line(x, y)'''

    p = figure(plot_width=600, plot_height=400, x_axis_type=x_axis_type)

    # add a circle renderer with a size, color, and alpha
    # p.circle(x, y, size=1, color="navy", alpha=0.5)

    p.vbar(x=x, width=0.9, bottom=0,
           top=y, color="firebrick")

    return "\n".join(components(p))
