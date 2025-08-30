from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import file_html

plot = figure()
plot.scatter([1,2], [3,4])

html = file_html(plot, CDN, "my plot")

with open("export.html", "w") as f:
    f.write(html)