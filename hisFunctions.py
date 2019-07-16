"""Reads and writes SOBEK HIS files.
Martijn Visser, Deltares, 2014-06, python 2
Updated to Python 3.6 by Peter Gijsbers
"""

from struct import unpack, pack
import numpy as np
from datetime import datetime, timedelta
from os.path import getsize
import pandas as pd
import configparser

def read_his(hisfile):
    '''Read a hisfile to a Pandas panel with extra attributes.'''
    filesize = getsize(hisfile)
    with open(hisfile, 'rb') as f:
        header = f.read(120).decode("ISO-8859-1")
        timeinfo = f.read(40).decode("ISO-8859-1")
        datestr = timeinfo[4:14].replace(' ', '0') + timeinfo[14:23]
        startdate = datetime.strptime(datestr, '%Y.%m.%d %H:%M:%S')
        try: 
            dt = int(timeinfo[30:-2]) # assumes unit is seconds
            filetype = "month"
        except: 
            dt = int(timeinfo[30:-3])
            filetype = "year"
        noout, noseg = unpack('ii', f.read(8))
        notim = int((filesize - 168 - noout*20 - noseg*24) / (4 * (noout * noseg + 1)))
        bpars, params, locnrs, locs = [], [], [], []
        if filetype == "year": f.read(1)
        for i in range(noout):
            if (filetype == "year" and i == (noout-1)): 
                params.append(f.read(19).decode("ISO-8859-1").rstrip())
            else:
                params.append(f.read(20).decode("ISO-8859-1").rstrip())
        for i in range(noseg):
            locnrs.append(unpack('i', f.read(4))[0])
            locs.append(f.read(20).decode("ISO-8859-1").rstrip())
        dates = []
        data = np.zeros((noout, notim, noseg), np.float32)
        for t in range(notim):
            ts = unpack('i', f.read(4))[0]
            date = startdate + timedelta(seconds=ts*dt)
            dates.append(date)
            for s in range(noseg):
                data[:, t, s] = np.fromfile(f, np.float32, noout)
    
    pn = pd.Panel(data, items=params, major_axis=dates, minor_axis=locs, dtype=np.float32, copy=True)
    pn.meta = dict(header=header, scu=dt, t0=startdate)
    return params, locs, dates, data, filetype

def read_hishia(hisfile):
    '''Read a hisfile to a Pandas panel with extra attributes.'''
    
    hiafile = hisfile[:-3] + 'hia'
    hia = configparser.ConfigParser()
    hia.read(hiafile)
    his_pos2hia_id = {}
    for section in hia.sections():
        if section == 'Long Locations':
            options = hia.options(section)
            for option in options:
                his_pos2hia_id[option] = hia.get(section,option)
                
    filesize = getsize(hisfile)
    with open(hisfile, 'rb') as f:
        header = f.read(120).decode("ISO-8859-1")
        timeinfo = f.read(40).decode("ISO-8859-1")
        datestr = timeinfo[4:14].replace(' ', '0') + timeinfo[14:23]
        startdate = datetime.strptime(datestr, '%Y.%m.%d %H:%M:%S')
        try: 
            dt = int(timeinfo[30:-2]) # assumes unit is seconds
            filetype = "month"
        except: 
            dt = int(timeinfo[30:-3])
            filetype = "year"
        noout, noseg = unpack('ii', f.read(8))
        notim = int((filesize - 168 - noout*20 - noseg*24) / (4 * (noout * noseg + 1)))
        bpars, params, locnrs, locs = [], [], [], []
        if filetype == "year": f.read(1)
        for i in range(noout):
            if (filetype == "year" and i == (noout-1)): 
                params.append(f.read(19).decode("ISO-8859-1").rstrip())
            else:
                params.append(f.read(20).decode("ISO-8859-1").rstrip())
        for i in range(noseg):
            locnrs.append(unpack('i', f.read(4))[0])
            loc = f.read(20).decode("ISO-8859-1").rstrip()
            if str(len(locs)+1) in his_pos2hia_id:
                loc = his_pos2hia_id[str(len(locs)+1)]
            locs.append(loc)
        dates = []
        data = np.zeros((noout, notim, noseg), np.float32)
        for t in range(notim):
            ts = unpack('i', f.read(4))[0]
            date = startdate + timedelta(seconds=ts*dt)
            dates.append(date)
            for s in range(noseg):
                data[:, t, s] = np.fromfile(f, np.float32, noout)
    
    pn = pd.Panel(data, items=params, major_axis=dates, minor_axis=locs, dtype=np.float32, copy=True)
    pn.meta = dict(header=header, scu=dt, t0=startdate)
    return params, locs, dates, data, filetype

#def read_hishia(hisfile):
#    '''Read a hisfile + hia file to a Pandas panel with extra attributes.
#    Returns the long location names as listed in the hia file
#    '''
#    hiafile = hisfile[:-3] + 'hia'
#    hia = configparser.ConfigParser()
#    hia.read(hiafile)
#    his_pos2hia_id = {}
#    for section in hia.sections():
#        if section == 'Long Locations':
#            options = hia.options(section)
#            for option in options:
#                his_pos2hia_id[option] = hia.get(section,option)
#
#    filesize = getsize(hisfile)
#    position = 0
#    with open(hisfile, 'rb') as f:
#        header = f.read(120).decode("ISO-8859-1")
#        timeinfo = f.read(40).decode("ISO-8859-1")
#        datestr = timeinfo[4:14].replace(' ', '0') + timeinfo[14:23]
#        startdate = datetime.strptime(datestr, '%Y.%m.%d %H:%M:%S')
#        dt = int(timeinfo[30:-2]) # assumes unit is seconds
#        noout, noseg = unpack('ii', f.read(8))
#        notim = int((filesize - 168 - noout * 20 - noseg * 24) / (4 * (noout * noseg + 1)))
#        bpars, params, locnrs, locs = [], [], [], []
#        for i in range(noout):
#            params.append(f.read(20).decode("ISO-8859-1").rstrip())
#        for i in range(noseg):
#            locnrs.append(unpack('i', f.read(4))[0])
#            loc = f.read(20).decode("ISO-8859-1").rstrip()
#            if str(len(locs)+1) in his_pos2hia_id:
#                loc = his_pos2hia_id[str(len(locs)+1)]
#            locs.append(loc)
#        dates = []
#        data = np.zeros((noout, notim, noseg), np.float32)
#        for t in range(notim):
#            ts = unpack('i', f.read(4))[0]
#            position += 4
#            date = startdate + timedelta(seconds=ts * dt)
#            dates.append(date)
#            for s in range(noseg):
#                data[:, t, s] = np.fromfile(f, np.float32, noout)
#
#    pn = pd.Panel(data, items=params, major_axis=dates, minor_axis=locs, dtype=np.float32, copy=True)
#    pn.meta = dict(header=header, scu=dt, t0=startdate)
#    return pn, params

def write_his(hisfile, pn):
    '''Writes a Pandas panel with extra attributes to a hisfile.'''
    # TODO: testing if the encoding works properly in python3
    with open(hisfile, 'wb') as f:
        header = pn.meta['header']
        scu = pn.meta['scu']
        t0 = pn.meta['t0']
        f.write((header.ljust(120)[:120]).encode('iso-8859-1')) # enforce length
        t0str = t0.strftime('%Y.%m.%d %H:%M:%S')
        timeinfo = 'T0: {}  (scu={:8d}s)'.format(t0str, scu)
        f.write((timeinfo).encode('iso-8859-1'))
        noout, notim, noseg = pn.shape
        f.write((pack('ii', noout, noseg)).encode('iso-8859-1'))
        params = np.array(pn.items, dtype='S20')
        params = np.char.ljust(params, 20)
        params.tofile(f)
        locs = np.array(pn.minor_axis, dtype='S20')
        locs = np.char.ljust(locs, 20)
        for locnr, loc in enumerate(locs):
            f.write((pack('i', locnr)).encode('iso-8859-1'))
            f.write((loc).encode('iso-8859-1'))
        data = pn.values.astype(np.float32)
        for t, date in enumerate(pn.major_axis):
            ts = int((date - t0).total_seconds() / scu)
            f.write((pack('i', ts)).encode('iso-8859-1'))
            for s in range(noseg):
                data[:, t, s].tofile(f)
        countmsg = 'hisfile written is not the correct length'
        assert f.tell() == 160 + 8 + 20 * noout + (4 + 20) * noseg + notim * (4 + noout * noseg * 4), countmsg

