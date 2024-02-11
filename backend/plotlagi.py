import json

from flask import Flask, jsonify
from gevent.pywsgi import WSGIServer
from bokeh.plotting import figure
from bokeh.plotting import Figure
from bokeh.resources import CDN
from bokeh.embed import json_item
from bokeh.layouts import column
from bokeh.models import CustomJS, ColumnDataSource, Slider
from bokeh.sampledata.autompg import autompg

app = Flask(__name__)

@app.route('/plot')
def plot():
    # Create a simple Bokeh plot
    x = [1, 2, 3, 4, 5]
    y = [6, 7, 2, 4, 8]

    plot = figure(title="Bokeh Plot", tools="pan,box_zoom,reset", plot_height=300, plot_width=400)
    plot.line(x, y, line_width=2)

    # Convert the plot to JSON
    plot_json = json.dumps(json_item(plot, "myplot"))

    return jsonify(plot=plot_json)

print("Listening on HTTP port 5000")
http_server = WSGIServer(('', 5000), app)
http_server.serve_forever()