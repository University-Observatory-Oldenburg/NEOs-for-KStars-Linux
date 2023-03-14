#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V1: 09.03.2023 TH

@author: Tobias Hoffmann
tobias.hoffmann3[at]uol.de

**Pre-Capture Script for NEOs for KStars Schedule (Linux) V1**

Description:
    ...  
Ideas:
    ...
"""
import sys
import datetime as dt
import base64
import math
import ephem
import os

import NEO_toolbox as NEO
from Input_parameters import load_parameters

dire = os.path.dirname(os.path.realpath(__file__))
params = load_parameters(dire,"parameters.json")

dir_data = params['Directory of Data/Code']
mount = params["Mount"]
dome = params["Dome"]
loc_mpccode = params['MPC Code']
loc_lat = float(params['Latitude [deg]'])
loc_long = float(params['Longitude [deg]'])
loc_elev = float(params['Elevation [m]'])
    
#%%
t = dt.datetime.utcnow()
# Create an observer object
observer = ephem.Observer()
observer.lat = loc_lat/180*math.pi
observer.lon = loc_long/180*math.pi
observer.elevation = loc_elev
observer.pressure = 0
observer.date = t

objects=NEO.read_list(dir_data+"objectslist_coordinates.json")
    
#%%
out_parked=NEO.mount_do(mount,"isparked",[])
if out_parked[0]=="Off":
    [tel_ra,tel_dec]=NEO.mount_do(mount,"coord",[])
    tel_ra=float(tel_ra)
    tel_dec=float(tel_dec)
    #[tel_ra_2000,tel_dec_2000]=jnow_to_j2000(tel_ra,tel_dec,t)
    [neo,val]=NEO.find_object(objects,tel_ra,tel_dec)
    #if val<1/120:
    #    print("Object already close enough, no correction needed...")
    print("Correction of coordinates needed! Moving telescope to "+neo[0]+" ...")
    sys.stdout.flush()
    data=NEO.get_mpcdata([neo[0]],neo[1],"mpc1line",t,loc_mpccode,loc_lat,loc_long)
    [mpc_ra,mpc_dec]=NEO.current_coordinate(data[0],observer)
    NEO.mount_do(mount,"move",[mpc_ra,mpc_dec])

exit(0)
