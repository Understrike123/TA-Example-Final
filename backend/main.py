from flask import request, render_template
from flask import Flask, request, jsonify
import panel as pn
import sys
import holoviews as hv
from holoviews.operation.datashader import regrid
import _pickle as cPickle
import numpy as np
import pymongo
from bokeh.io import curdoc
import pandas as pd
from curveintersect import intersection
from scipy.spatial import KDTree
from os import walk
from panel.layout import Column
from bokeh.models.widgets import PreText
import logging
from bokeh.embed import json_item
from flask_cors import CORS
import os
logger = logging.getLogger('panel.callbacks')

app = Flask(__name__)
CORS(app)

MONGODB_ADDRESS = "seismic_mongo"

colr = pn.widgets.Select(name='Select Color Scale', options=['gray', 'RdGy','BrBG','coolwarm','cwr','RdBu', 'spectral', 'fire', 'magma', 'seismic', 'bwr', 'jet'], max_height=50)
amp = pn.widgets.TextInput(name='Amplitude', value='1000', max_height=50)
cmpinc  = pn.widgets.TextInput(name='CMP Inc.', value='100', max_height=50)
xlaborient  = pn.widgets.TextInput(name='X-label Orientation', value='10', max_height=50)
textcanvas = pn.widgets.TextInput(name='Plot Height', value ='800', max_height=50)
ebcdictext = PreText(text="", width=720, height=600)
########################################################
mongo_client = pymongo.MongoClient(f'mongodb://{MONGODB_ADDRESS}:27017')
mongodb = mongo_client["test"]
mongoCollection = mongodb["LINE_EW_PERIHAKA_100"]

def hook(img, element):  # finalize_hooks.
    img.handles['glyph_renderer'].level = 'image'

def list_files(directory, extension):
    for (dirpath, dirnames, filenames) in walk(directory):
        return (f for f in filenames if f.endswith('.' + extension))
def get_url_param(param_name):
    try:
        param_value = sys.argv[1]  # Ambil argumen pertama dari baris perintah
        params = param_value.split('--')
        return params
    except IndexError:
        return []
    
params = get_url_param('params')

try:

    uniquelines = params[1:]

    if len(uniquelines) == 1:
        selectseismic = uniquelines[0]
        mydb = mongo_client["test"]
        mycol = mongoCollection  # Menggunakan koleksi yang sudah ditentukan
        cmpnos = np.sort(mycol.find().distinct('CMP_NO'))
        cmpnos = [int(i) for i in cmpnos]
        mydoc = mycol.aggregate(
            [
                {"$match": {'CMP_NO': {"$gte": cmpnos[0], "$lte": cmpnos[-1]}}},

            ])
        traces = np.array([cPickle.loads(x['amp']) for x in mydoc]).T

    else:
        tracesALL = []
        cmpnos = []
        for selectseismic in uniquelines:
            mydb = mongo_client["test"]
            mycol = mongoCollection  # Menggunakan koleksi yang sudah ditentukan
            composite = pd.read_csv('./BASEMAP/composite.csv')
            seismic = composite.loc[composite['z'] == selectseismic]
            XCMP = list(seismic.x)  # MANIPULASI

            literal = list(np.load(f'./TEMP_test/{selectseismic}.convpar')[:, 0])
            mydoc = mycol.aggregate(
                [
                    {"$match": {'XCMP': {"$gte": min(XCMP), "$lte": max(XCMP)}}},
                ])
            header = pd.DataFrame(mydoc)[literal]

            xshot = header['XCMP'].values
            cmpno = header['CMP_NO'].values
            cmpno = np.array(cmpno, dtype=int)
            cmpintersect = cmpno[0]

            mydoc = mycol.aggregate(
                [
                    {"$match": {'XCMP': {"$gte": min(XCMP), "$lte": max(XCMP)}}},
                ])
            traces = np.array([cPickle.loads(x['amp']) for x in mydoc])

            # checking sorting
            XCMP1 = seismic.x.values  # selected
            XCMP1 = np.array(XCMP1, dtype=int)
            XCMP1A = XCMP1[0]
            XCMP2 = np.array(xshot, dtype=int)  # from mongo
            XCMP2A = XCMP2[0]

            if XCMP1A != XCMP2A:
                traces = np.flipud(traces)
            tracesALL.extend(traces)
            cmpnos.extend(cmpno)
            cmpnos[cmpnos.index(cmpintersect)] = selectseismic
        traces = np.asarray(tracesALL).T

    rmstr = traces[:, int(traces.shape[1] / 3):int(traces.shape[1] / 2)]
    rms = int(np.std(rmstr - rmstr.mean(axis=0)))
    amp.value = str('%s' % rms)
except Exception as e:
    print(f"Error: {e}")
    pass

# @app.route("/hello", methods=['GET'])
# def get_image_data():
#     # Baca gambar dari file
#     with open('pgn.png', 'rb') as img_file:
#         img_data = img_file.read()

#     # Konversi gambar ke base64
#     encoded_image = base64.b64encode(img_data).decode('utf-8')

#     # Susun data JSON
#     json_data = {
#         'image': encoded_image,
#         'image_format': 'png'  # Format gambar (misalnya jpg, png, dll.)
#     }

#     return jsonify(json_data)

@app.route("/seisview2d", methods=['POST'])
def seismic():
    try: 
        
        # Mendapatkan data dari body permintaan POST
        data = request.json

        # Mendapatkan nilai-nilai dari data
        colr_value = data['colr']
        amp_value = data['amp']
        cmpinc_value = data['cmpinc']
        textcanvas_value = data['textcanvas']
        xlaborient_value = data['xlaborient']

        uniquelines = params[1:]
        ###agus
        uniqueline = []
        for line in uniquelines:
            a = line.split('_')
            selectproject = a[0]
            uniqueline.append('_'.join(a[1:None]))
        uniquelines = uniqueline   
        ###EBDIC
        ebcdic = np.load(f'./TEMP_test/ebcdic_LINE_EW_PERIHAKA_100.npy')
        ebcdictext.text = str(ebcdic)

        if len(uniquelines)==1:
            selectseismic = uniquelines[0]
            
            mydb = mongo_client[selectproject]
            mycol = mongoCollection
            
            cmpnos = np.sort(mycol.find().distinct('CMP_NO'))
            
            cmpnos = [int(i) for i in cmpnos]
            mydoc = mycol.aggregate(
                [
                    {"$match": {'CMP_NO': {"$gte": cmpnos[0], "$lte": cmpnos[-1]}}},

                ])
            traces = np.array([cPickle.loads(x['amp']) for x in mydoc]).T

            literal = list(np.load(f'./TEMP_test/LINE_EW_PERIHAKA_100.convpar')[:, 0])
            mydoc = mycol.aggregate(
                [
                    {"$match": {'CMP_NO': {"$gte": cmpnos[0], "$lte": cmpnos[-1]}}},
                ])
            header = pd.DataFrame(mydoc)[literal]

            # xy selected line
            x1 = header['XCMP'].values
            y1 = header['YCMP'].values

            files = list_files('./BASEMAP/', 'npy')
            cmpintersect = []
            lineintersect = []
            for name in files:
                if "SEISMIC2D" in name:
                    xyl = np.load('./BASEMAP/%s' % name)
                    x2 = np.array(xyl[:, 0], dtype=float)
                    y2 = np.array(xyl[:, 1], dtype=float)
                    l2 = xyl[0, 2]

                    x, y = intersection(x1, y1, x2, y2)  # line intersection
                    master1 = np.vstack((x1, y1)).T
                    if len(x) > 0:
                        slave = [x[0], y[0]]
                        tree = KDTree(master1, leafsize=master1.shape[0] + 1)  # master
                        dts, pt = tree.query(slave, k=2)  # no of nearest points
                        cmpintersect.extend([cmpnos[pt[0]]])
                        lineintersect.extend([l2])

            xtic = list(np.arange(0, len(cmpnos), 1))

            itic = []
            for k in cmpintersect:
                itic.extend([cmpnos.index(k)])

            xtic = xtic[::int(cmpinc_value)]
            cmpnos = cmpnos[::int(cmpinc_value)]
            xtic.extend(itic)
            cmpnos.extend(lineintersect)
            xticcmp = np.vstack((xtic, cmpnos)).T
            xticcmp = pd.DataFrame(xticcmp, columns=['A', 'B']).drop_duplicates(['A'], keep='last')
            xticcmp = xticcmp.loc[pd.to_numeric(xticcmp.A, errors='coerce').sort_values().index].values
            xtic = np.array(xticcmp[:, 0], dtype=int)
            cmptic = xticcmp[:, 1]
            cmptic = [item[:20] for item in cmptic]  # Limit character length
            xid = list(zip(map(int, xtic), map(str, cmptic)))

        else:
            tracesALL = []
            cmpnos = []
            for selectseismic in uniquelines:
                mydb = mongo_client[selectproject]
                composite = pd.read_csv('./BASEMAP/composite.csv')
                seismic = composite.loc[composite['z'] == selectproject+'_'+selectseismic]
                XCMP = list(seismic.x )  # MANPULATE
                mycol = mongoCollection
                literal = list(np.load(f'./TEMP_test/{selectseismic}.convpar')[:, 0])
                mydoc = mycol.aggregate(
                    [
                        {"$match": {'XCMP': {"$gte": min(XCMP), "$lte": max(XCMP)}}},
                    ])
                header = pd.DataFrame(mydoc)[literal]

                xshot = header['XCMP'].values
                cmpno = header['CMP_NO'].values
                cmpno = np.array(cmpno, dtype=int)
                cmpintersect = cmpno[0]

                mydoc = mycol.aggregate(
                    [
                        {"$match": {'XSHOT': {"$gte": min(XCMP), "$lte": max(XCMP)}}},
                    ])
                traces = np.array([cPickle.loads(x['amp']) for x in mydoc])

                # checking sorting
                XCMP1 = seismic.x.values  # selected
                XCMP1 = np.array(XCMP1, dtype=int)
                XCMP1A = XCMP1[0]
                XCMP2 = np.array(xshot, dtype=int)  # from mongo
                XCMP2A = XCMP2[0]

                if XCMP1A != XCMP2A:
                    # cmpno = np.flip(cmpno)
                    traces = np.flipud(traces)
                tracesALL.extend(traces)
                cmpnos.extend(cmpno)
                cmpnos[cmpnos.index(cmpintersect)] = selectseismic
            traces = np.asarray(tracesALL).T

        if len(uniquelines) > 1:
            xtic = list(np.arange(0, len(cmpnos), 1))
            cmpnos = np.array(cmpnos, dtype=str)
            cmpnos = [item[:20] for item in cmpnos]  # Limit character length
            xticA = []
            xticB = []
            cmpnoA = []
            cmpnoB = []
            for i, k in enumerate(cmpnos):
                try:
                    cmpnoA.extend([int(k)])
                    xticA.extend([xtic[i]])
                except:
                    xticB.extend([xtic[i]])
                    cmpnoB.extend([k])

            xticA = xticA[::int(cmpinc_value)]  # cmpinc
            cmpnoA = cmpnoA[::int(cmpinc_value)]  # cmpinc
            xticA.extend(xticB)
            cmpnoA.extend(cmpnoB)
            xtic = xticA
            cmpnos = cmpnoA
            xticcmp = np.vstack((xtic, cmpnos)).T
            xticcmp = pd.DataFrame(xticcmp, columns=['A', 'B']).drop_duplicates(['A'], keep='last')
            xticcmp = xticcmp.loc[pd.to_numeric(xticcmp.A, errors='coerce').sort_values().index].values
            xtic = np.array(xticcmp[:, 0], dtype=int)
            cmptic = xticcmp[:, 1]
            xid = list(zip(map(int, xtic), map(str, cmptic)))
        else:
            pass

        data = np.flipud(traces)
        vmin = -float(amp_value)
        vmax = float(amp_value)
        sr = (int(np.load('./TEMP_%s/%s.samsr' % (selectproject, selectseismic))[1]) )
        bounds = (0, 0, data.shape[1] - 1, data.shape[0] * sr)
        xrotation_value = min(max(0, int(xlaborient_value)), 360)

        plot_opts = {
            'colorbar': True,
            'clim': (vmin, vmax),
            'xlabel': 'CMP NO',
            'ylabel': 'TWT[ms]',
            'xlim': (0, data.shape[1]),
            'ylim': (0, data.shape[0] * sr),
            'xaxis': 'top',
            'invert_yaxis': True,
            'xticks': xid,
            'xrotation': xrotation_value,
            'fontscale': 0.75
        }
        style_opts = {'cmap': colr_value}
        hv.extension('bokeh')  # Memuat ekstensi plotting

        # Buat objek Holoviews di sini
        img = hv.Image(data, bounds=bounds).opts(responsive=True, min_height=int(textcanvas_value), min_width=800, show_grid=True).opts(style=style_opts, plot=plot_opts).opts(hooks=[hook], gridstyle=dict(grid_line_color='black',grid_line_width=1,xgrid_visible=False))
        img = regrid(img, upsample=True, interpolation='bilinear', precompute=True)
    
        layout = Column(img)  # Buat layout Panel dari objek Holoviews
        pn_panel = pn.panel(layout)  # Konversi layout Holoviews ke objek Panel
    
        result = json_item(pn_panel.get_root(), "myplot")  # Mengubah objek Panel ke JSON
    
        return jsonify(result), 200

    except Exception as e:
        # Tangani kesalahan dengan mencetak pesan kesalahan dan mengembalikan respons dengan status kode 500 jika terjadi kesalahan selama pemrosesan.
        print(f"Error: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)

