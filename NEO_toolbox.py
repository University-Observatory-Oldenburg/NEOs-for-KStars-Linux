# -*- coding: utf-8 -*-
"""
V1: 09.03.2023 TH

@author: Tobias Hoffmann
tobias.hoffmann3[at]uol.de

**Toolbox for functions for NEO Import for KStars (Linux) V1.1**

Description:
    ...  
Ideas:
    ...
"""
import requests as req
import os
import ephem
import math
import json
import sys
import subprocess
from astropy.coordinates import SkyCoord,FK5
from astropy import units as u

def jd_to_date(jd):
    jd = jd + 0.5
    F, I = math.modf(jd)
    I = int(I)
    A = math.trunc((I - 1867216.25)/36524.25)
    if I > 2299160: B = I + 1 + A - math.trunc(A / 4.)  
    else: B = I
    C = B + 1524
    D = math.trunc((C - 122.1) / 365.25)
    E = math.trunc(365.25 * D)
    G = math.trunc((C - E) / 30.6001)
    day = C - E + F - math.trunc(30.6001 * G)
    if G < 13.5: month = G - 1
    else: month = G - 13 
    if month > 2.5: year = D - 4716
    else: year = D - 4715 
    if month < 10: month = "0"+str(month)
    else: month = str(month)  
    if day<10: day= "0"+str(day)   
    else: day=str(day)   
    return str(year)+month+day

def delete_indices(list_object, indices):
    indices = sorted(indices, reverse=True)
    for idx in indices:
        if idx < len(list_object):
            list_object.pop(idx)
  
def delete_duplicates(y):         
    res=[]
    [res.append(x) for x in y if x not in res]
    return res

def epoch_conv(ep):
    T=ep[0]
    T=ord(T)-64+9
    Y=ep[1:3]
    Y=T*100+int(Y)
    M=ep[3]
    if ord(M)<64: M=int(M)   
    else: M=ord(M)-64+9  
    D=ep[4]
    if ord(D)<64: D=int(D)     
    else: D=ord(D)-64+9    
    return Y,M,D

def date_to_jd(year,month,day):
    if month == 1 or month == 2:
        yearp = year - 1
        monthp = month + 12
    else:
        yearp = year
        monthp = month
    if ((year < 1582) or
        (year == 1582 and month < 10) or
        (year == 1582 and month == 10 and day < 15)):
        B = 0
    else:
        A = math.trunc(yearp / 100.)
        B = 2 - A + math.trunc(A / 4.)   
    if yearp < 0: C = math.trunc((365.25 * yearp) - 0.75)  
    else: C = math.trunc(365.25 * yearp)           
    D = math.trunc(30.6001 * (monthp + 1)) 
    jd = B + C + D + day + 1720994.5
    return jd

def darkness(observer,sun_hor): # Calculate the darkness-time at which the sun rises and sets beyond certain horizon
    observer.horizon = sun_hor
    sun=ephem.Sun()
    sun.compute(observer)
    a=sun.alt
    if a<sun_hor: sunset = observer.previous_setting(sun)
    else: sunset = observer.next_setting(sun)
    sunrise = observer.next_rising(sun)
    # Calculate the time of nautical darkness as the time between
    # sunset and sunrise when the sun is below -12 degrees altitude
    nautical_darkness_start = ephem.Date(sunset)
    nautical_darkness_end = ephem.Date(sunrise)
    return [nautical_darkness_start,nautical_darkness_end]

def mpc1line_to_xephem(dataline):
    elements = dataline.strip().split() # Parse the MPC1-line string into its components
    name = elements[0]
    H = elements [1]
    G = elements [2]
    epoch = elements[3]
    [year,month,day]=epoch_conv(epoch)
    epoch=f'{month}/{day}/{year}'
    M= elements[4]
    peri = elements[5]
    node = elements[6]
    incl = elements[7]
    e = elements[8]
    n = elements[9]
    a = elements[10]
    xephem_string = f'{name},e,{incl},{node},{peri},{a},{n},{e},{M},{epoch},2000,H{H},{G}' # Build the xephem-format orbital elements string
    return xephem_string


def mpc1line_to_kstars(dataline,i):
    name=dataline[0:7].strip()
    [year,month,day]=epoch_conv(dataline[20:25])
    jdt=str(date_to_jd(year,month,day)-2400000.5).replace(".0", "")
    a=dataline[94:104].replace(" ", "")
    e=dataline[70:80].replace(" ", "")
    q=str(float(a)*(1-float(e)))[0:10]
    incl=dataline[60:69].replace(" ", "")
    peri=dataline[37:47].replace(" ", "")
    node=dataline[48:58].replace(" ", "")
    M=dataline[26:36].replace(" ", "")
    H=dataline[8:13].replace(" ", "")
    G=dataline[14:19].replace(" ", "")
    P=str(2*math.pi*math.sqrt((float(a)*149597870700)**3/(1.327124*(10**20)))/31557600)[0:5]
    emoid="null"
    #data=f',[\"{str(i)} {name}\"Y\",\"{H}\",\"{G}\",null,null,null,null,null,{jdt},\"{e}\",\"{a}\",\"{q}\",\"{incl}\",\"{node}\",\"{peri}\",\"{M}\",\"{P}\",{emoid},null]'
    data=',[\"'+str(i)+' '+name+'\",\"Y\",\"'+H+'\",\"'+G+'\",null,null,null,null,null,'+jdt+',\"'+e+'\",\"'+a+'\",\"'+q+'\",\"'+incl+'\",\"'+node+'\",\"'+peri+'\",\"'+M+'\",\"'+P+'\",'+emoid+',null]'
    return data

def remove_empty(mylist):
    result=[]
    for entry in mylist:
        if not entry.strip() == '':
            result.append(entry)
    return result
            
def get_objects(loc,dir_data,t,mpccode,mag_max,m_min,m_max,v_min,v_max,unc_min,unc_max):
    namelist=[]
    t2 = t.strftime("%Y%m%d")
    payload=""
    word="\n"
    begin=1
    end=-1
    if loc=="esa_prioritylist":
        link='https://neo.ssa.esa.int/PSDB-portlet/download?file=esa_priority_neo_list'
    elif loc=="mpc_neocp":
        link='https://www.minorplanetcenter.net/iau/NEO/neocp.txt'
        begin=0
    elif loc=="mpc_neaobs":
        link="https://cgi.minorplanetcenter.net/cgi-bin/neaobs_getlist.cgi"
        payload = "date="+t2+"&ralo=-120&rahi=%2B120&declo=-90&dechi=%2B90&magbr="+str(m_min)+"&magfa="+str(m_max)+"&motlo="+str(v_min)+"&mothi="+str(v_max)+"&mtype=m&elolo=60&elohi=180&gallat=0&unclo="+str(unc_min)+"&unchi="+str(unc_max)+"&uncsig=1&dayssince=0&typ1=V&typ2=P&typ3=t&typ4=p&typ5=m&stat1=N&stat2=M&stat3=1&stat4=P&bel=100&bmag=21.0&sort=1&dirsort=1&oc="+mpccode+"&ndate=&ephint=1&ephunit=h&raty=a&motty=t&motun=m"
        word="name=\"Obj\" VALUE=\""
        end=None
    
    f = open(os.path.join(dir_data,loc+".txt"), "w")
    resp = (req.get(link,params=payload)).text
    f.write(resp)
    f.close()
    resp = (resp.split(word))[begin:end]
    for obj in resp:
        if len(obj)>20:
            if loc=="esa_prioritylist": 
                name=(obj.split("\""))[1]
                mag=(obj[36:40])
                if float(mag)<=mag_max: namelist.append(name)
            elif loc=="mpc_neocp": 
                name=obj[0:7].strip()
                mag=obj[43:47]
                if float(mag)<=mag_max: namelist.append(name)
            elif loc=="mpc_neaobs":
                name=((obj.split(">"))[1].split("Pos"))[0].strip()
                namelist.append(name)       
    return namelist

def get_addobj(name,dir_data):
    namelist = []
    f = open(os.path.join(dir_data,name+".txt"),"r")
    addobj = f.readlines()
    f.close()
    for obj in addobj:
        obj=obj.replace("\n","")
        namelist.append(obj)
    return namelist
            
def get_mpcdata(namelist,unconfirmed,form,t,mpccode,lat,long): 
    if unconfirmed:
        data_list=[]
        for obj in namelist:
            resp_data = req.get('https://cgi.minorplanetcenter.net/cgi-bin/showobsorbs.cgi?Obj='+obj+'&orb=y')
            data_list.append(((resp_data.text).split("\n"))[2])
    else:   
        t2 = t.strftime("&d=%Y%%2F%m%%2F%d+%H%M")
        if form=="xephem": e="3"
        else: e="-1"
        if mpccode==None: mpccode=""
        elif len(mpccode)>3: mpccode=""
        else: 
            long=""
            lat=""  
        namelist_conv=""
        for obj in namelist:
            obj = obj.replace(" ","+")
            namelist_conv=namelist_conv+"%0D%0A"+obj  
        payload = "ty=e&TextArea="+namelist_conv+t2+"&l=1&i=&u=d&uto=0&c="+mpccode+"&long="+str(long)+"&lat="+str(lat)+"&alt=&raty=a&s=t&m=m&adir=S&oed=&e="+e+"&resoc=&tit=&bu=&ch=c&ce=f&js=f"
        resp_data = req.get("https://cgi.minorplanetcenter.net/cgi-bin/mpeph2.cgi", params=payload)
        data_list=((resp_data.text).split("\n"))
        if form=="xephem": data_list=data_list[1::2]
    data_list=remove_empty(data_list)
    return data_list 

def remove_unobservable(data_list,iscp,observer,hor,sun_hor,min_time):
    [darkness_start,darkness_end] = darkness(observer,sun_hor)
    observer.horizon = hor
    objects_observable = []
    objects_notobs=[]
    i=0
    for data in data_list:
        data=mpc1line_to_xephem(data)
        remove=False
        asteroid = ephem.readdb(data)
        asteroid.compute(observer) # Calculate the position of the asteroid at the current time
        altitude = asteroid.alt
        try: # Calcultate rise and set time 
            rise_time = observer.next_rising(asteroid)
            if altitude>hor: rise_time=observer.previous_rising(asteroid) # when already above horizon -> last rising
            if rise_time<darkness_start: rise_time=darkness_start # when last rising is above is before sunset, sunset ist rising time
            if rise_time>darkness_end: remove=True # asteroid rising after sunrise, no observation
            set_time = observer.next_setting(asteroid) 
            if set_time>darkness_end: set_time=darkness_end
        except: 
            if altitude>hor: # always above horizon
                rise_time=darkness_start 
                set_time=darkness_end
            else: remove=True # never above horizon
        if not remove:
            print(f"Asteroid {asteroid.name} is observable from {rise_time} to {set_time}")
            uptime=(set_time-rise_time)*24 # time of asteroid above horizon in hours
            if uptime>min_time: objects_observable.append([asteroid.name,iscp,uptime])
            else: objects_notobs.append(i)
        else: objects_notobs.append(i) 
        i=i+1
    delete_indices(data_list, objects_notobs)
    objects_observable=delete_duplicates(objects_observable) #Delete duplicates
    data_list=delete_duplicates(data_list)
    return [objects_observable,data_list]

def edit_kstars(dir_kstars,name,out,objects):
    numobj=len(objects)+len(objects)
    h=open(os.path.join(dir_kstars,name),'r')
    kstars_text=h.read()
    h.close()
    splitlist=["800000","800001","800002","800003","\"count\":"]
    for item in splitlist:
        text=kstars_text.split(',[\"'+item)
        if len(text)>1:
            if item==splitlist[-1]:
                count=(text[1].split("}"))[0]
            else:
                count=((text[1].split(splitlist[-1]))[1].split("}"))[0]
            count_new=int(count)+numobj
            kstars_text_new=text[0]+out+"],\"count\":"+str(count_new)+"}"
            g=open(os.path.join(dir_kstars,"asteroids.dat"),"w") 
            g.write(kstars_text_new)
            g.close()
            wl = open(os.path.join(dir_kstars,"wishlist.obslist"), "w") 
            wl.write("\n".join(str(x) for [x,y,z] in objects));
            wl.close();
            break
        
def save_coordinates(dir_data,objectlist,datalist,observer):
    if len(objectlist)!=len(datalist):
        print("Error! Data list and object list do not match dimensions!")
    for i in range(len(datalist)):
        data=mpc1line_to_xephem(datalist[i])
        asteroid = ephem.readdb(data)
        asteroid.compute(observer)
        ra = (asteroid.ra)*12/math.pi
        dec = (asteroid.dec)*180/math.pi
        (objectlist[i]).append(ra)
        (objectlist[i]).append(dec)
    write_list(objectlist,os.path.join(dir_data,"objectslist_coordinates.json"))
    
def current_coordinate(data,observer):
    data=mpc1line_to_xephem(data)
    asteroid = ephem.readdb(data)
    asteroid.compute(observer)
    ra = (asteroid.ra)*12/math.pi
    dec = (asteroid.dec)*180/math.pi
    return[ra,dec]
          
def write_list(a,name):
    with open(name, "w") as c:
        json.dump(a, c)

def read_list(name):
    with open(name, 'rb') as c:
        a = json.load(c)
        return a
   
def mount_do(instrument,task,param):
    num=1
    if task=="move":
        cmd = "indi_setprop \""+instrument+".EQUATORIAL_EOD_COORD.RA;DEC="+str(param[0])+";"+str(param[1])+"\""
    elif task=="coord":
        cmd = "indi_getprop \""+instrument+".EQUATORIAL_EOD_COORD.*\""
        num=2
    elif task=="isparked":
        cmd = "indi_getprop \""+instrument+".TELESCOPE_PARK.PARK\""
    elif task=="ismovingCW":
        cmd = "indi_getprop \""+instrument+".DOME_MOTION.DOME_CW\""
    elif task=="ismovingCCW":
        cmd = "indi_getprop \""+instrument+".DOME_MOTION.DOME_CCW\""
    elif task=="domepos":
        cmd = "indi_getprop \""+instrument+".ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION\""
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    out, err = p.communicate()
    output=[]
    if not task=="move":
        for i in range(num):
            try: output.append(((str(out).split('\\n'))[i].split('='))[1])
            except: 
                print("Error! Not connected")
                sys.stdout.flush()
                exit(1)
        return output
        

def jnow_to_j2000(ra_now,dec_now,t):
    koords = SkyCoord(ra=float(ra_now)*u.hourangle, dec=float(dec_now)*u.deg, frame='fk5', equinox=t)
    koords_fk5=koords.transform_to(FK5(equinox="J2000"))
    ra_2000=koords_fk5.ra.hour
    dec_2000=koords_fk5.dec.deg
    return [ra_2000,dec_2000]

def find_object(objects,ra,dec):
    error_list = []
    for obj in objects:
        x = abs(obj[2]-ra)/12*180
        y = abs(obj[3]-dec)
        z=((x/24)**2+(y/180)**2)**(1/2)
        error_list.append(z)
    min_value = min(error_list)
    min_index = error_list.index(min_value)
    min_object=objects[min_index]
    return [min_object,min_value]