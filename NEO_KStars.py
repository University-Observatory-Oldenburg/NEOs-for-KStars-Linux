# -*- coding: utf-8 -*-
"""
V0.1: 01.08.2021 TH
V0.2: 21.12.2021 TH
V0.3: 19.01.2022 TH
V0.4: 26.01.2022 TH
V0.5: 08.02.2022 TH
V1.0: 09.03.2023 TH
V1.1: 13.03.2023 TH

@author: Tobias Hoffmann
tobias.hoffmann3[at]uol.de

**NEO Import Script for KStars (Linux) V1.1**

Description:
    The script imports the current NEOs on the ESA Priority list, the MPC NEA Observation Aid, the MPC Confirmation Page and some own additional objects from a input prompt.
    It checks all objects for observability in the following night (magnitude, altitude, uncertainty, etc.)
    The final list of observable objets is put into KStars (asteroid file) and the Wishlist in order to quickly import the objects into the Scheduler
    It is necessary to run this script before starting KStars. An Internet connection is also needed.
    
Ideas:
    - Bring in athmospheric extinction: Use different altitude limites with different vis. mag
    - Create pretty form for input of Parameters and Location
"""
import datetime as dt
import ephem
import os
import math

import NEO_toolbox as NEO
from Input_parameters import load_parameters

dire = os.path.dirname(os.path.realpath(__file__))
params = load_parameters(dire,"parameters.json")

# Parameters
dir_kstars = params['Directory of KStars']
dir_data = params['Directory of Data/Code']
loc_mpccode = params['MPC Code']
loc_lat = float(params['Latitude [deg]'])
loc_long = float(params['Longitude [deg]'])
loc_elev = float(params['Elevation [m]'])
p_mag_max = float(params['Maximum Visual Magnitude [mag]'])
p_mag_min = float(params['Minimum Visual Magnitude [mag]'])
p_alt_min = float(params['Horizon Altitude [deg]'])
p_time_min = float(params['Minimum Time above Horizon [h]'])
p_alt_sun = float(params['Horizon of Sun [deg]'])
p_v_min = float(params['Minimum Velocity of NEO [arcsec/min]'])
p_v_max = float(params['Maximum Velocity of NEO [arcsec/min]'])
p_unc_min = float(params['Minimum Orbital Uncertainty [arcsec]'])
p_unc_max = float(params['Maximum Orbital Uncertainty [arcsec]'])

#%%
p_alt_min=p_alt_min/180*math.pi
p_alt_sun=p_alt_sun/180*math.pi
t = dt.datetime.utcnow()

# Create an observer object
observer = ephem.Observer()
observer.lat = loc_lat/180*math.pi
observer.lon = loc_long/180*math.pi
observer.elevation = loc_elev
observer.pressure = 0
observer.date = t
observer.horizon = p_alt_min

#%%
# Download Objects from ESA Priority List, MPC NEA Observation Aid, MPC Confirmation Page and own Additional Objects
namelist_ESAPL=NEO.get_objects("esa_prioritylist",dir_data,t,loc_mpccode,p_mag_max,p_mag_min,p_mag_max,p_v_min,p_v_max,p_unc_min,p_unc_max)
namelist_NEAObs=NEO.get_objects("mpc_neaobs",dir_data,t,loc_mpccode,p_mag_max,p_mag_min,p_mag_max,p_v_min,p_v_max,p_unc_min,p_unc_max)
namelist_NEOCP=NEO.get_objects("mpc_neocp",dir_data,t,loc_mpccode,p_mag_max,p_mag_min,p_mag_max,p_v_min,p_v_max,p_unc_min,p_unc_max)
namelist_addobj=NEO.get_addobj("addObjects",dir_data)
namelist=namelist_ESAPL+namelist_NEAObs+namelist_addobj
     
#%%
#Getting mpc1line data
data_list=NEO.get_mpcdata(namelist,False,"mpc1line",t,loc_mpccode,loc_lat,loc_long)
data_listcp=NEO.get_mpcdata(namelist_NEOCP,True,"mpc1line",t,loc_mpccode,loc_lat,loc_long)

#%%
# Parse the asteroid data and calculations for observability
[objects_observable,data_list]=NEO.remove_unobservable(data_list,False,observer,p_alt_min,p_alt_sun,p_time_min)
[objects_observablecp,data_listcp]=NEO.remove_unobservable(data_listcp,True,observer,p_alt_min,p_alt_sun,p_time_min)

#%%
# Covert everything for KStars
out=""
i=800000
for data in data_list:
    kstars_data=NEO.mpc1line_to_kstars(data,i)
    out=out+kstars_data
    i=i+1

i=900000
for data in data_listcp:
    kstars_data=NEO.mpc1line_to_kstars(data,i)
    out=out+kstars_data
    i=i+1
    
#%%
# Save data and replace asteroid file for KStars
if os.path.exists(dir_kstars+"asteroids.bin"):
    os.system('copy '+dir_kstars+'asteroids.dat '+dir_kstars+'asteroids_old.dat')
    os.remove(dir_kstars+"asteroids.bin")
if not os.path.exists(dir_kstars+"asteroids_old.dat"):
    os.system('copy '+dir_kstars+'asteroids.dat '+dir_kstars+'asteroids_old.dat')

NEO.edit_kstars(dir_kstars,'asteroids_old.dat',out,objects_observable+objects_observablecp)

NEO.save_coordinates(dir_data,objects_observable+objects_observablecp,data_list+data_listcp,observer)