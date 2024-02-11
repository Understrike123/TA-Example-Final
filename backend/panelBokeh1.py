from flask import Flask, render_template
from bokeh.embed import server_document

app = Flask(__name__)


@app.route("/")
def hello_world():
    script = server_document('http://localhost:5006/seisview2d?params=SEISMIC2D--test_LINE_EW_PERIHAKA_100')

    print(script)

    return render_template("index.html", js_code=script)
