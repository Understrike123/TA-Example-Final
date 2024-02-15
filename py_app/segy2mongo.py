from bokeh.models.widgets import PreText, Slider, Panel, Tabs, Button, Select, TextInput
import textwrap
from os import walk
from bokeh.layouts import layout, row
import re
import os
import pymongo
import _pickle as cPickle
from bson.binary import Binary
import numpy as np
from bokeh.layouts import grid
from readsegy import read_ebcdic, read_bheader, StructIBM32, num_traces
import panel as pn
from panel.widgets import StaticText
import pandas as pd

import logging
logger = logging.getLogger('panel.callbacks')


MONGODB_ADDRESS = 'seismic_mongo'

css = '''
body {
    overflow-y: hidden !important;
}
#header {
  height: 35px !important;
  font-size: 0.75em;
}
#sidebar {
    overflow-y: auto !important;
}
#main {
    padding-top: 20px !important;
}
'''

pn.extension(raw_css=[css])
webtemplate = pn.template.BootstrapTemplate(title='Segy2MongoDB', favicon='pgn.png',header_background='#000000')
pn.config.sizing_mode = 'stretch_both'


######################################## TAB 1 SEGYIN ##################################################################
def list_files(directory, extension1, extension2, extension3):
    for (dirpath, dirnames, filenames) in walk(directory):
        return (f for f in filenames if
                f.endswith('.' + extension1) or f.endswith('.' + extension2) or f.endswith('.' + extension3))

files1 = list_files('SEGY', 'sgy', 'segy', 'SGY')  #need to be modified
namafile = []
for name in files1:
    namafile.append(name)
def atoi(text):
    return int(text) if text.isdigit() else text
def natural_keys(text):
    return [atoi(c) for c in re.split(r'(\d+)', text)]
namafile.sort(key=natural_keys)

selectsegy = Select(value=namafile[0], options=namafile,  sizing_mode="stretch_width")
slidertraces = Slider(value=1, start=1, end=100, step=1,  sizing_mode="stretch_width")
selectproject = Select(value="New Project", options=['New Project','Existing Project'], sizing_mode="stretch_width")
projectname = TextInput(value='New_Project_Name', sizing_mode="stretch_width")
selectline = Select(value="", options=[''],  sizing_mode="stretch_width")
selectline.disabled = True
setprojects = Button(label='Set Project',  sizing_mode="stretch_width")
noofsamples = TextInput(value='0', title='nsamp',  sizing_mode="stretch_width")
selectampformat = Select(value="IBM32BITS", options=['IBM32BITS','IEEE32BITS'], sizing_mode="stretch_width")
seissamprate = TextInput(value='0', title='sampling rate (ms)',  sizing_mode="stretch_width")
progresstext = StaticText(value='',style={'color': "white"})

mongo_client = pymongo.MongoClient(f'mongodb://{MONGODB_ADDRESS}:27017')

def projectopt(attrname, old, new):
    if selectproject.value =='Existing Project':
        projectname.disabled = True
        selectline.disabled = False
        existingprojects = mongo_client.list_database_names()
        existingprojects[:] = [x for x in existingprojects if "admin" not in x]
        existingprojects[:] = [x for x in existingprojects if "config" not in x]
        existingprojects[:] = [x for x in existingprojects if "local" not in x]
        selectline.options = existingprojects
        selectline.value = existingprojects[0]
    elif selectproject.value =='New Project':
        projectname.disabled = False
        selectline.disabled = True

selectproject.on_change('value', projectopt)

def setproject():
    if selectproject.value == 'New Project':
        tempname = projectname.value
        path = 'TEMP_%s' %tempname #relative path full path
        try:
            os.mkdir(path)
        except:
            pass

setprojects.on_click(setproject)


widget_01_10 = Button(label='SEGYIN', sizing_mode="stretch_width")
minmaxtext = PreText(text="", width=300, height=600)


namalit = ['TRACE_SEQ_NO', 'FIELD_RECORD_NO', 'SHOT_POINT_NO', 'CHANNEL_NO', 'CMP_NO', 'OFFSET_SH_REC', 'ELEV_REC',
           'ELEV_SHOT', 'DEPTH_SHOT', 'ELEV_FLOATDAT_RCV', 'ELEV_FLOATDAT_SRC', 'XSHOT', 'YSHOT', 'XREC', 'YREC',
           'STATIC_SRC', 'STATIC_REC', 'STATIC_TOTAL', 'XCMP', 'YCMP', 'CMPDAT', 'FOLD', 'INLINE', 'XLINE',
           'UNASSIGNED']

literal01 = Select(value="TRACE_SEQ_NO", options=namalit,  sizing_mode="stretch_width")
literal02 = Select(value="FIELD_RECORD_NO", options=namalit,  sizing_mode="stretch_width")
literal03 = Select(value="SHOT_POINT_NO", options=namalit,  sizing_mode="stretch_width")
literal04 = Select(value="CHANNEL_NO", options=namalit,  sizing_mode="stretch_width")
literal05 = Select(value="CMP_NO", options=namalit,  sizing_mode="stretch_width")
literal06 = Select(value="OFFSET_SH_REC", options=namalit,  sizing_mode="stretch_width")
literal07 = Select(value="ELEV_REC", options=namalit,  sizing_mode="stretch_width")
literal08 = Select(value="ELEV_SHOT", options=namalit,  sizing_mode="stretch_width")
literal09 = Select(value="DEPTH_SHOT", options=namalit,  sizing_mode="stretch_width")
literal10 = Select(value="ELEV_FLOATDAT_RCV", options=namalit,  sizing_mode="stretch_width")
literal11 = Select(value="ELEV_FLOATDAT_SRC", options=namalit,  sizing_mode="stretch_width")
literal12 = Select(value="XSHOT", options=namalit,  sizing_mode="stretch_width")
literal13 = Select(value="YSHOT", options=namalit,  sizing_mode="stretch_width")
literal14 = Select(value="XREC", options=namalit,  sizing_mode="stretch_width")
literal15 = Select(value="YREC", options=namalit,  sizing_mode="stretch_width")
literal16 = Select(value="STATIC_SRC", options=namalit,  sizing_mode="stretch_width")
literal17 = Select(value="STATIC_REC", options=namalit,  sizing_mode="stretch_width")
literal18 = Select(value="STATIC_TOTAL", options=namalit,  sizing_mode="stretch_width")
literal19 = Select(value="XCMP", options=namalit,  sizing_mode="stretch_width")
literal20 = Select(value="YCMP", options=namalit,  sizing_mode="stretch_width")
literal21 = Select(value="CMPDAT", options=namalit,  sizing_mode="stretch_width")
literal22 = Select(value="FOLD", options=namalit,  sizing_mode="stretch_width")
literal23 = Select(value="INLINE", options=namalit,  sizing_mode="stretch_width")
literal24 = Select(value="XLINE", options=namalit,  sizing_mode="stretch_width")
literal25 = Select(value="UNASSIGNED", options=namalit,  sizing_mode="stretch_width")

byteloc01 = TextInput(value='1',  sizing_mode="stretch_width")
byteloc02 = TextInput(value='5',  sizing_mode="stretch_width")
byteloc03 = TextInput(value='9',  sizing_mode="stretch_width")
byteloc04 = TextInput(value='17',  sizing_mode="stretch_width")
byteloc05 = TextInput(value='21',  sizing_mode="stretch_width")
byteloc06 = TextInput(value='37',  sizing_mode="stretch_width")
byteloc07 = TextInput(value='41',  sizing_mode="stretch_width")
byteloc08 = TextInput(value='45',  sizing_mode="stretch_width")
byteloc09 = TextInput(value='49',  sizing_mode="stretch_width")
byteloc10 = TextInput(value='53',  sizing_mode="stretch_width")
byteloc11 = TextInput(value='57',  sizing_mode="stretch_width")
byteloc12 = TextInput(value='73',  sizing_mode="stretch_width")
byteloc13 = TextInput(value='77',  sizing_mode="stretch_width")
byteloc14 = TextInput(value='81',  sizing_mode="stretch_width")
byteloc15 = TextInput(value='85',  sizing_mode="stretch_width")
byteloc16 = TextInput(value='99',  sizing_mode="stretch_width")
byteloc17 = TextInput(value='101',  sizing_mode="stretch_width")
byteloc18 = TextInput(value='103',  sizing_mode="stretch_width")
byteloc19 = TextInput(value='73',  sizing_mode="stretch_width")
byteloc20 = TextInput(value='77',  sizing_mode="stretch_width")
byteloc21 = TextInput(value='201',  sizing_mode="stretch_width")
byteloc22 = TextInput(value='113',  sizing_mode="stretch_width")
byteloc23 = TextInput(value='115',  sizing_mode="stretch_width")
byteloc24 = TextInput(value='117',  sizing_mode="stretch_width")
byteloc25 = TextInput(value='141',  sizing_mode="stretch_width")

namafmt = ['INT32BITS', 'INT16BITS', 'IBM32BITS', 'IEEE32BITS']
format01 = Select(value="INT32BITS", options=namafmt,  sizing_mode="stretch_width")
format02 = Select(value="INT32BITS", options=namafmt,  sizing_mode="stretch_width")
format03 = Select(value="INT32BITS", options=namafmt,  sizing_mode="stretch_width")
format04 = Select(value="INT32BITS", options=namafmt,  sizing_mode="stretch_width")
format05 = Select(value="INT32BITS", options=namafmt,  sizing_mode="stretch_width")
format06 = Select(value="INT32BITS", options=namafmt,  sizing_mode="stretch_width")
format07 = Select(value="INT32BITS", options=namafmt,  sizing_mode="stretch_width")
format08 = Select(value="INT32BITS", options=namafmt,  sizing_mode="stretch_width")
format09 = Select(value="INT32BITS", options=namafmt,  sizing_mode="stretch_width")
format10 = Select(value="INT32BITS", options=namafmt,  sizing_mode="stretch_width")
format11 = Select(value="INT32BITS", options=namafmt,  sizing_mode="stretch_width")
format12 = Select(value="INT32BITS", options=namafmt,  sizing_mode="stretch_width")
format13 = Select(value="INT32BITS", options=namafmt,  sizing_mode="stretch_width")
format14 = Select(value="INT32BITS", options=namafmt,  sizing_mode="stretch_width")
format15 = Select(value="INT32BITS", options=namafmt,  sizing_mode="stretch_width")
format16 = Select(value="INT32BITS", options=namafmt,  sizing_mode="stretch_width")
format17 = Select(value="INT32BITS", options=namafmt,  sizing_mode="stretch_width")
format18 = Select(value="INT32BITS", options=namafmt,  sizing_mode="stretch_width")
format19 = Select(value="INT32BITS", options=namafmt,  sizing_mode="stretch_width")
format20 = Select(value="INT32BITS", options=namafmt,  sizing_mode="stretch_width")
format21 = Select(value="INT32BITS", options=namafmt,  sizing_mode="stretch_width")
format22 = Select(value="INT32BITS", options=namafmt,  sizing_mode="stretch_width")
format23 = Select(value="INT32BITS", options=namafmt,  sizing_mode="stretch_width")
format24 = Select(value="INT32BITS", options=namafmt,  sizing_mode="stretch_width")
format25 = Select(value="INT32BITS", options=namafmt,  sizing_mode="stretch_width")

value01 = TextInput(value='0',  sizing_mode="stretch_width")
value02 = TextInput(value='0',  sizing_mode="stretch_width")
value03 = TextInput(value='0',  sizing_mode="stretch_width")
value04 = TextInput(value='0',  sizing_mode="stretch_width")
value05 = TextInput(value='0',  sizing_mode="stretch_width")
value06 = TextInput(value='0',  sizing_mode="stretch_width")
value07 = TextInput(value='0',  sizing_mode="stretch_width")
value08 = TextInput(value='0',  sizing_mode="stretch_width")
value09 = TextInput(value='0',  sizing_mode="stretch_width")
value10 = TextInput(value='0',  sizing_mode="stretch_width")
value11 = TextInput(value='0',  sizing_mode="stretch_width")
value12 = TextInput(value='0',  sizing_mode="stretch_width")
value13 = TextInput(value='0',  sizing_mode="stretch_width")
value14 = TextInput(value='0',  sizing_mode="stretch_width")
value15 = TextInput(value='0',  sizing_mode="stretch_width")
value16 = TextInput(value='0',  sizing_mode="stretch_width")
value17 = TextInput(value='0',  sizing_mode="stretch_width")
value18 = TextInput(value='0',  sizing_mode="stretch_width")
value19 = TextInput(value='0',  sizing_mode="stretch_width")
value20 = TextInput(value='0',  sizing_mode="stretch_width")
value21 = TextInput(value='0',  sizing_mode="stretch_width")
value22 = TextInput(value='0',  sizing_mode="stretch_width")
value23 = TextInput(value='0',  sizing_mode="stretch_width")
value24 = TextInput(value='0',  sizing_mode="stretch_width")
value25 = TextInput(value='0',  sizing_mode="stretch_width")

scaling01 = TextInput(value='1',  sizing_mode="stretch_width")
scaling02 = TextInput(value='1',  sizing_mode="stretch_width")
scaling03 = TextInput(value='1',  sizing_mode="stretch_width")
scaling04 = TextInput(value='1',  sizing_mode="stretch_width")
scaling05 = TextInput(value='1',  sizing_mode="stretch_width")
scaling06 = TextInput(value='1',  sizing_mode="stretch_width")
scaling07 = TextInput(value='1',  sizing_mode="stretch_width")
scaling08 = TextInput(value='1',  sizing_mode="stretch_width")
scaling09 = TextInput(value='1',  sizing_mode="stretch_width")
scaling10 = TextInput(value='1',  sizing_mode="stretch_width")
scaling11 = TextInput(value='1',  sizing_mode="stretch_width")
scaling12 = TextInput(value='1',  sizing_mode="stretch_width")
scaling13 = TextInput(value='1',  sizing_mode="stretch_width")
scaling14 = TextInput(value='1',  sizing_mode="stretch_width")
scaling15 = TextInput(value='1',  sizing_mode="stretch_width")
scaling16 = TextInput(value='1',  sizing_mode="stretch_width")
scaling17 = TextInput(value='1',  sizing_mode="stretch_width")
scaling18 = TextInput(value='1',  sizing_mode="stretch_width")
scaling19 = TextInput(value='1',  sizing_mode="stretch_width")
scaling20 = TextInput(value='1',  sizing_mode="stretch_width")
scaling21 = TextInput(value='1',  sizing_mode="stretch_width")
scaling22 = TextInput(value='1',  sizing_mode="stretch_width")
scaling23 = TextInput(value='1',  sizing_mode="stretch_width")
scaling24 = TextInput(value='1',  sizing_mode="stretch_width")
scaling25 = TextInput(value='1',  sizing_mode="stretch_width")

ebcdictext = PreText(text="", width=720, height=600)
binarytext = PreText(text="", width=200, height=300)



def updatefile(attrname, old, new):
    filename = str(selectsegy.value)
    filename = 'SEGY/' + filename
    aadf = os.path.isfile(filename)
    if aadf == True:
        ebcdic = read_ebcdic(filename)
        ebcdic = textwrap.fill(str(ebcdic, 'utf-8'), 80)  # utf-8 remove b' character
        ebcdictext.text = ebcdic

        try:
            linename = str(selectsegy.value)
            linename = linename.split('.')  # remove point
            linename.pop()
            linename = str(linename[0])
            if selectproject.value == 'Existing Project':
                tempname = selectline.value
            else:
                tempname = projectname.value

            np.save('./TEMP_%s/ebcdic_%s' % (tempname, linename), ebcdic)
        except:
            pass
        # binary header
        binhead = read_bheader(filename)
        hbdr = (
            'jobid', 'lino', 'reno', 'ntrpr', 'nart', 'sr(micsec)', 'dto', 'nsamp', 'nso', 'format', 'fold', 'tsort',
            'vscode',
            'hsfs', 'hsfe', 'hslen', 'hstyp', 'schn', 'hstas', 'hstae', 'htatyp', 'hcorr', 'bgrcv', 'rcvm', 'mfeet',
            'polyv',
            'vpol', 'unassig1', 'unassig2', 'unassig3', 'unassig4', 'unassig5', 'unassig6', 'unassig7', 'unassig8',
            'unassig9')

        text = []
        for i, item in enumerate(hbdr):
            text.append('%s%s%d' % (item, ':', binhead[0][i]))
        text = np.reshape(np.array(text), (-1, 1))
        text = str(text).replace('[', '').replace(']', '').replace("'", '').replace(" ", '')
        binarytext.text = str(text)

        def litval(data, byteloc, fmt):
            if fmt == 'INT16BITS':
                text = np.fromstring(data[byteloc:byteloc + 2], np.dtype('>i2'))
            elif fmt == 'INT32BITS':
                text = np.fromstring(data[byteloc:byteloc + 4], np.dtype('>i4'))
            elif fmt == 'IBM32BITS':
                text = StructIBM32(1).unpackibm(data[byteloc:byteloc + 4])
            else:
                text = StructIBM32(1).unpackieee(data[byteloc:byteloc + 4])
            return list(text)

        ns = binhead[0][7]  # no of sample per trace
        noofsamples.value = str(ns)
        ns = int(noofsamples.value)
        ntraces = int(num_traces(filename, ns))  # no of traces in file
        sra = binhead[0][5]  # sampling rate
        seissamprate.value = str(int(sra / 1000))

        slidertraces.end = ntraces
        f = open(filename, "rb")
        traceno = int(slidertraces.value)
        f.seek(3600 + (traceno * 240) - 240 + (traceno * (ns * 4)) - (ns * 4))
        data = f.read(240)
        value01.value = str(litval(data, int(byteloc01.value) - 1, str(format01.value))[0])
        value02.value = str(litval(data, int(byteloc02.value) - 1, str(format02.value))[0])
        value03.value = str(litval(data, int(byteloc03.value) - 1, str(format03.value))[0])
        value04.value = str(litval(data, int(byteloc04.value) - 1, str(format04.value))[0])
        value05.value = str(litval(data, int(byteloc05.value) - 1, str(format05.value))[0])
        value06.value = str(litval(data, int(byteloc06.value) - 1, str(format06.value))[0])
        value07.value = str(litval(data, int(byteloc07.value) - 1, str(format07.value))[0])
        value08.value = str(litval(data, int(byteloc08.value) - 1, str(format08.value))[0])
        value09.value = str(litval(data, int(byteloc09.value) - 1, str(format09.value))[0])
        value10.value = str(litval(data, int(byteloc10.value) - 1, str(format10.value))[0])
        value11.value = str(litval(data, int(byteloc11.value) - 1, str(format11.value))[0])
        value12.value = str(litval(data, int(byteloc12.value) - 1, str(format12.value))[0])
        value13.value = str(litval(data, int(byteloc13.value) - 1, str(format13.value))[0])
        value14.value = str(litval(data, int(byteloc14.value) - 1, str(format14.value))[0])
        value15.value = str(litval(data, int(byteloc15.value) - 1, str(format15.value))[0])
        value16.value = str(litval(data, int(byteloc16.value) - 1, str(format16.value))[0])
        value17.value = str(litval(data, int(byteloc17.value) - 1, str(format17.value))[0])
        value18.value = str(litval(data, int(byteloc18.value) - 1, str(format18.value))[0])
        value19.value = str(litval(data, int(byteloc19.value) - 1, str(format19.value))[0])
        value20.value = str(litval(data, int(byteloc20.value) - 1, str(format20.value))[0])
        value21.value = str(litval(data, int(byteloc21.value) - 1, str(format21.value))[0])
        value22.value = str(litval(data, int(byteloc22.value) - 1, str(format22.value))[0])
        value23.value = str(litval(data, int(byteloc23.value) - 1, str(format23.value))[0])
        value24.value = str(litval(data, int(byteloc24.value) - 1, str(format24.value))[0])
        value25.value = str(litval(data, int(byteloc25.value) - 1, str(format25.value))[0])

for w in [selectsegy, slidertraces]:
    w.on_change('value', updatefile)



def segy2seis():
    progresstext.value = 'Fetching Data...Be patient!'
    filename = str(selectsegy.value)
    filename = 'SEGY/' + filename
    ntraces = int(slidertraces.end)
    ns = int(noofsamples.value)
    chunks = 132
    nsdb = ns

    # header reading and  amplitude conversion
    byteloc_slc = [int(byteloc01.value), int(byteloc02.value),
                   int(byteloc03.value), int(byteloc04.value),
                   int(byteloc05.value), int(byteloc06.value),
                   int(byteloc07.value), int(byteloc08.value),
                   int(byteloc09.value), int(byteloc10.value),
                   int(byteloc11.value), int(byteloc12.value),
                   int(byteloc13.value), int(byteloc14.value),
                   int(byteloc15.value), int(byteloc16.value),
                   int(byteloc17.value), int(byteloc18.value),
                   int(byteloc19.value), int(byteloc20.value),
                   int(byteloc21.value), int(byteloc22.value),
                   int(byteloc23.value), int(byteloc24.value),
                   int(byteloc25.value)]

    format_slc = [format01.value, format02.value,
                  format03.value, format04.value,
                  format05.value, format06.value,
                  format07.value, format08.value,
                  format09.value, format10.value,
                  format11.value, format12.value,
                  format13.value, format14.value,
                  format15.value, format16.value,
                  format17.value, format18.value,
                  format19.value, format20.value,
                  format21.value, format22.value,
                  format23.value, format24.value,
                  format25.value]

    scaling_slc = [float(scaling01.value), float(scaling02.value),
                   float(scaling03.value), float(scaling04.value),
                   float(scaling05.value), float(scaling06.value),
                   float(scaling07.value), float(scaling08.value),
                   float(scaling09.value), float(scaling10.value),
                   float(scaling11.value), float(scaling12.value),
                   float(scaling13.value), float(scaling14.value),
                   float(scaling15.value), float(scaling16.value),
                   float(scaling17.value), float(scaling18.value),
                   float(scaling19.value), float(scaling20.value),
                   float(scaling21.value), float(scaling22.value),
                   float(scaling23.value), float(scaling24.value),
                   float(scaling25.value)]

    head = [literal01.value, literal02.value, literal03.value,
            literal04.value, literal05.value, literal06.value,
            literal07.value, literal08.value, literal09.value,
            literal10.value, literal11.value, literal12.value,
            literal13.value, literal14.value, literal15.value,
            literal16.value, literal17.value, literal18.value,
            literal19.value, literal20.value, literal21.value,
            literal22.value, literal23.value, literal24.value, literal25.value]

    linename = str(selectsegy.value)
    linename = linename.split('.')  # remove point
    linename.pop()
    linename = str(linename[0])

    if selectproject.value == 'Existing Project':
        tempname = selectline.value
    else:
        tempname = projectname.value


    np.save('./TEMP_%s/head_%s' % (tempname, linename), head)

    if selectproject.value=='Existing Project':
        dbname = selectline.value  #existing dbname
    else:
        dbname = projectname.value  #new dbname

    mydb = mongo_client[dbname]
    mycol = mydb[linename]
    mycol.drop()

    f = open(filename, "rb")
    f.seek(3600)

    rmdr = int(ntraces % chunks)
    rit = int(ntraces / chunks)

    a = np.arange(0, ((ns * 4) + 240) * chunks, ((ns * 4) + 240))  #
    b = np.arange(0, ((ns * 4) + 240) * rmdr, ((ns * 4) + 240))  #

    def litval(data, byteloc, fmt):
        if fmt == 'INT16BITS':
            text = np.fromstring(data[byteloc:byteloc + 2], np.dtype('>i2'))
        elif fmt == 'INT32BITS':
            text = np.fromstring(data[byteloc:byteloc + 4], np.dtype('>i4'))
        elif fmt == 'IBM32BITS':
            text = StructIBM32(1).unpackibm(data[byteloc:byteloc + 4])
        else:
            text = StructIBM32(1).unpackieee(data[byteloc:byteloc + 4])
        return list(text)

    prog = 0
    for m in range(1, rit + 2):
        if m <= rit:
            data = f.read((ns + 60) * chunks * 4)
            mylist = []
            for s in a:
                prog += 1
                unpackedhdr = []
                for k in range(len(byteloc_slc)):
                    unpackedhdr.extend(litval(data, s + byteloc_slc[k] - 1, format_slc[k]))
                if selectampformat.value == 'IBM32BITS':
                    unpackedtrc = StructIBM32(ns).unpackibm(data[s + 240:s + (ns * 4) + 240])  # IBM
                elif selectampformat.value == 'IEEE32BITS':
                    unpackedtrc = list(StructIBM32(ns).unpackieee(data[s + 240:s + (ns * 4) + 240]))  # IEEE
                unpackedhdr = list(np.array(unpackedhdr) * np.array(scaling_slc))
                progresstext.value = 'Loading SEGY...'+str(int(prog / ntraces * 100)) + '%'
                mylist.append({head[0]: float(unpackedhdr[0]),
                               head[1]: float(unpackedhdr[1]),
                               head[2]: float(unpackedhdr[2]),
                               head[3]: float(unpackedhdr[3]),
                               head[4]: float(unpackedhdr[4]),
                               head[5]: float(unpackedhdr[5]),
                               head[6]: float(unpackedhdr[6]),
                               head[7]: float(unpackedhdr[7]),
                               head[8]: float(unpackedhdr[8]),
                               head[9]: float(unpackedhdr[9]),
                               head[10]: float(unpackedhdr[10]),
                               head[11]: float(unpackedhdr[11]),
                               head[12]: float(unpackedhdr[12]),
                               head[13]: float(unpackedhdr[13]),
                               head[14]: float(unpackedhdr[14]),
                               head[15]: float(unpackedhdr[15]),
                               head[16]: float(unpackedhdr[16]),
                               head[17]: float(unpackedhdr[17]),
                               head[18]: float(unpackedhdr[18]),
                               head[19]: float(unpackedhdr[19]),
                               head[20]: float(unpackedhdr[20]),
                               head[21]: float(unpackedhdr[21]),
                               head[22]: float(unpackedhdr[22]),
                               head[23]: float(unpackedhdr[23]),
                               head[24]: float(unpackedhdr[24]),
                               "amp": Binary(cPickle.dumps(unpackedtrc, protocol=2))})  #no headers in amplitude
            mycol.insert_many(mylist)

        elif m > rit:
            data = f.read((ns + 60) * 4 * rmdr)
            mylist = []
            for v in b:
                prog += 1
                unpackedhdr = []
                for k in range(len(byteloc_slc)):
                    unpackedhdr.extend(litval(data, v + byteloc_slc[k] - 1, format_slc[k]))
                if selectampformat.value == 'IBM32BITS':
                    unpackedtrc = StructIBM32(ns).unpackibm(data[v + 240:v + (ns * 4) + 240])  # IBM
                elif selectampformat.value == 'IEEE32BITS':
                    unpackedtrc = list(StructIBM32(ns).unpackieee(data[v + 240:v + (ns * 4) + 240]))  # IEE
                unpackedhdr = list(np.array(unpackedhdr) * np.array(scaling_slc))
                progresstext.value = 'Loading SEGY...'+str(int(prog / ntraces * 100)) + '%'
                mylist.append({head[0]: float(unpackedhdr[0]),
                               head[1]: float(unpackedhdr[1]),
                               head[2]: float(unpackedhdr[2]),
                               head[3]: float(unpackedhdr[3]),
                               head[4]: float(unpackedhdr[4]),
                               head[5]: float(unpackedhdr[5]),
                               head[6]: float(unpackedhdr[6]),
                               head[7]: float(unpackedhdr[7]),
                               head[8]: float(unpackedhdr[8]),
                               head[9]: float(unpackedhdr[9]),
                               head[10]: float(unpackedhdr[10]),
                               head[11]: float(unpackedhdr[11]),
                               head[12]: float(unpackedhdr[12]),
                               head[13]: float(unpackedhdr[13]),
                               head[14]: float(unpackedhdr[14]),
                               head[15]: float(unpackedhdr[15]),
                               head[16]: float(unpackedhdr[16]),
                               head[17]: float(unpackedhdr[17]),
                               head[18]: float(unpackedhdr[18]),
                               head[19]: float(unpackedhdr[19]),
                               head[20]: float(unpackedhdr[20]),
                               head[21]: float(unpackedhdr[21]),
                               head[22]: float(unpackedhdr[22]),
                               head[23]: float(unpackedhdr[23]),
                               head[24]: float(unpackedhdr[24]),
                               "amp": Binary(cPickle.dumps(unpackedtrc, protocol=2))})
            mycol.insert_many(mylist)
        else:
            break

    para1 = [literal01.value, literal02.value, literal03.value,
             literal04.value, literal05.value, literal06.value,
             literal07.value, literal08.value, literal09.value,
             literal10.value, literal11.value, literal12.value,
             literal13.value, literal14.value, literal15.value,
             literal16.value, literal17.value, literal18.value,
             literal19.value, literal20.value, literal21.value,
             literal22.value, literal23.value, literal24.value, literal25.value]

    para2 = [byteloc01.value, byteloc02.value,
             byteloc03.value, byteloc04.value,
             byteloc05.value, byteloc06.value,
             byteloc07.value, byteloc08.value,
             byteloc09.value, byteloc10.value,
             byteloc11.value, byteloc12.value,
             byteloc13.value, byteloc14.value,
             byteloc15.value, byteloc16.value,
             byteloc17.value, byteloc18.value,
             byteloc19.value, byteloc20.value,
             byteloc21.value, byteloc22.value,
             byteloc23.value, byteloc24.value,
             byteloc25.value]

    para3 = [format01.value, format02.value,
             format03.value, format04.value,
             format05.value, format06.value,
             format07.value, format08.value,
             format09.value, format10.value,
             format11.value, format12.value,
             format13.value, format14.value,
             format15.value, format16.value,
             format17.value, format18.value,
             format19.value, format20.value,
             format21.value, format22.value,
             format23.value, format24.value,
             format25.value]

    para4 = np.vstack((list(para1), list(para2), list(para3))).T
    sr = seissamprate.value
    para5 = [nsdb, sr, ntraces]
    file = str(selectsegy.value)
    file = file.split('.')  # remove point
    file.pop()  # remove seis
    file = ''.join(map(str, file))



    if selectproject.value=='Existing Project':
        tempname = selectline.value
    else:
        tempname = projectname.value

    with open("./TEMP_%s/%s.convpar" % (tempname, str(file)), 'wb') as fileconv:
        np.save(fileconv, para4)
    with open("./TEMP_%s/%s.samsr" % (tempname, str(file)), 'wb') as filesamsr:
        np.save(filesamsr, para5)

    progresstext.value = ''
    ##basemap

    mydb = mongo_client[tempname]
    mycol = mydb[str(file)]
    cmpnos = np.sort(mycol.find().distinct('CMP_NO'))
    cmpnos = [int(i) for i in cmpnos]

    literal = list(np.load('./TEMP_%s/%s.convpar' % (tempname, str(file)))[:, 0])
    mydoc = mycol.aggregate(
        [
            {"$match": {'CMP_NO': {"$gte": cmpnos[0], "$lte": cmpnos[-1]}}},
        ])
    header = pd.DataFrame(mydoc)[literal]

    # xy selected line
    x1 = header['XCMP'].values
    y1 = header['YCMP'].values
    l1 = [tempname+'_'+str(file)] * len(x1)

    peta= np.vstack((x1,y1,l1)).T
    np.save('./BASEMAP/%s_SEISMIC2D_XYL_%s'%(tempname,str(file)),peta)


widget_01_10.on_click(segy2seis)

grid = grid([[selectsegy, literal01, byteloc01, format01, value01, scaling01],
             [selectproject, literal02, byteloc02, format02, value02, scaling02],
             [projectname, literal03, byteloc03, format03, value03, scaling03],
             [selectline, literal04, byteloc04, format04, value04, scaling04],
             [setprojects, literal05, byteloc05, format05, value05, scaling05],
             [selectampformat, literal06, byteloc06, format06, value06, scaling06],
             [widget_01_10, literal07, byteloc07, format07, value07, scaling07],
             [slidertraces, literal08, byteloc08, format08, value08, scaling08],
             [None, literal09, byteloc09, format09, value09, scaling09],
             [None, literal10, byteloc10, format10, value10, scaling10],
             [None, literal11, byteloc11, format11, value11, scaling11],
             [None, literal12, byteloc12, format12, value12, scaling12],
             [None, literal13, byteloc13, format13, value13, scaling13],
             [None, literal14, byteloc14, format14, value14, scaling14],
             [None, literal15, byteloc15, format15, value15, scaling15],
             [None, literal16, byteloc16, format16, value16, scaling16],
             [None, literal17, byteloc17, format17, value17, scaling17],
             [None, literal18, byteloc18, format18, value18, scaling18],
             [None, literal19, byteloc19, format19, value19, scaling19],
             [None, literal20, byteloc20, format20, value20, scaling20],
             [None, literal21, byteloc21, format21, value21, scaling21],
             [None, literal22, byteloc22, format22, value22, scaling22],
             [None, literal23, byteloc23, format23, value23, scaling23],
             [None, literal24, byteloc24, format24, value24, scaling24],
             [None, literal25, byteloc25, format25, value25, scaling25],
             ])

l1 = grid
l2 = layout(row(ebcdictext))
l3 = layout(row(binarytext))
###################################################
tab1 = Panel(child=l1, title="BYTELOC")
tab2 = Panel(child=l2, title="EBCDIC")
tab3 = Panel(child=l3, title="BINARY")
widgets = Tabs(tabs=[tab1, tab2, tab3])
webtemplate.header.append(progresstext)
webtemplate.main.append(widgets)
webtemplate.servable()

