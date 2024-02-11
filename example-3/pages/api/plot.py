from flask import Flask, jsonify
from bokeh.plotting import figure
from bokeh.embed import json_item
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})


@app.route('/api/plot')
def get_plot():
    # Buat plot menggunakan Bokeh
    plot = figure(title='Contoh Plot', x_axis_label='X', y_axis_label='Y')
    plot.line([1, 2, 3, 4, 5], [6, 7, 2, 4, 5])

    # Konversi plot menjadi format JSON yang dapat disematkan
    plot_json = json_item(plot, 'myplot')

    return jsonify(plot_json)


if __name__ == '__main__':
    app.run()
