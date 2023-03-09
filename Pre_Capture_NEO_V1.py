#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V1: 09.03.2023 TH

@author: Tobias Hoffmann
tobias.hoffmann3[at]uol.de

**Pre-Capture Script for NEOs for KStars Schedule (Linux)**

Description:
    ...  
Ideas:
    ...
"""
import sys
import datetime as dt
import math
import ephem

import NEO_toolbox_V1 as NEO

dir_data = "/home/stellarmate/Robotic/KStars_NEOs/"
mount = "LX200 10micron"
dome = "Dome Simulator"

# Location
loc_mpccode="G01" # MPC Code of observatory, if not available put ""
loc_lat=53.152847 # Latitude of observatory / deg N
loc_long=8.165280 # Longitude of observatory / deg E
loc_elev=54 # Elevation of observatory / m
    
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
