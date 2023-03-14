# -*- coding: utf-8 -*-
"""
V1: 24.01.2022 TH
V1.1: 11.03.2023 TH

@author: Tobias Hoffmann
tobias.hoffmann3[at]uol.de

**Command prompt script for input of additional objects (NEOs, Minor Planets and DeepSkyObjects) V1.1**

Description:
    ...  
Ideas:
    ...
"""
import tkinter as tk
import json
import os
import NEO_toolbox as NEO

dire = os.path.dirname(os.path.realpath(__file__))
name = "parameters.json"
title_p ="Parameters for NEO for KStars (Linux) System"


#%%
fields_obj = ['Deep Sky Objects', 'Additional Minor Planets']
files_obj = ['dsoObjects.txt','addObjects.txt']
title="Additional Objects for NEO for KStars (Linux) System"

def loadobs(dire,file):
    f = open(os.path.join(dire,file),"r")
    obj = f.readlines()
    f.close()
    obj[:]=[line.replace("\n","") for line in obj]
    obj=NEO.remove_empty(obj)
    out=', '.join(obj)+', '  
    return out

def saveobs(dire,files,obj):
   for i, file in enumerate(files):
       dso = obj[i].split(",")
       dso = [a.strip() for a in dso]
       dso = NEO.remove_empty(dso)
       f = open(os.path.join(dire,file),"w")
       f.write('\n'.join(dso)+'\n')
       f.close()

def submit(dire,files,data):
   obj=[] 
   for entry in data:
      field = entry[0]
      text  = entry[1].get()
      obj.append(text)
      print('%s: "%s"' % (field, text))
   saveobs(dire,files,obj)

       
def save_parameters(directory,name,parameters):
    with open(os.path.join(directory,name),"w") as f:
        json.dump(parameters,f)

def load_parameters(directory,name):
    with open(os.path.join(directory,name),"r") as f:
        parameters = json.load(f)
        return parameters

def submit_parameters(dire,name,touple):
    liste = []
    for entry in touple:
        field = entry[0]
        value = entry[1].get()
        liste.append((field, value))
        print('%s: "%s"' % (field, value))
    p = dict(liste)
    save_parameters(dire,name,p)
    
def makeform(window, fields, insers):
   out=[]
   form = tk.Frame(relief=tk.SUNKEN)
   form.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
   for i in range(len(fields)):
   #for field,inser in zip(fields,insers):
      label = tk.Label(form, width=30, text=fields[i], anchor='w')
      entry = tk.Entry(form, width=50)
      entry.insert(10,insers[i])
      label.grid(row=i, column=0, sticky="e")
      entry.grid(row=i, column=1)
      out.append((fields[i], entry))
   return out
        
#%%
if __name__ == '__main__':
    params = load_parameters(dire,name)
    pwindow = tk.Tk()
    pwindow.title(title_p)
    ptouple = makeform(pwindow, list(params.keys()), list(params.values()))
    pwindow.bind('<Return>', lambda event:[submit_parameters(dire,name,ptouple),pwindow.quit()]) 
    pbuttons = tk.Frame()
    pbuttons.pack(fill=tk.X, ipadx=5, ipady=5)
    b1 = tk.Button(pbuttons, text='Submit', command=lambda:[submit_parameters(dire,name,ptouple),pwindow.quit()])
    b1.pack(side=tk.LEFT, padx=5, pady=5)
    b2 = tk.Button(pbuttons, text='Quit', command=lambda:[pwindow.quit()])
    b2.pack(side=tk.LEFT, padx=5, pady=5)
    pwindow.mainloop()
    pwindow.destroy()
    
    params = load_parameters(dire,name)
    dire = params['Directory of Data/Code']
    insers_obj=[]
    for i, file in enumerate(files_obj):
        if os.path.exists(os.path.join(dire,file)):
            insers_obj.append(loadobs(dire,file))
        else: insers_obj.append("") 
    window = tk.Tk()
    window.title(title)
    ents = makeform(window, fields_obj, insers_obj)
    window.bind('<Return>', lambda event:[submit(dire,files_obj,ents),window.quit()])  
    buttons = tk.Frame()
    buttons.pack(fill=tk.X, ipadx=5, ipady=5)
    b3 = tk.Button(buttons, text='Submit', command=lambda:[submit(dire,files_obj,ents),window.quit()])
    b3.pack(side=tk.LEFT, padx=5, pady=5)
    b4 = tk.Button(buttons, text='Quit', command=lambda:[window.quit()])
    b4.pack(side=tk.LEFT, padx=5, pady=5)
    window.mainloop()
   
