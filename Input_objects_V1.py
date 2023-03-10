# -*- coding: utf-8 -*-
"""
V1: 24.01.2022 TH

@author: Tobias Hoffmann
tobias.hoffmann3[at]uol.de

**Command prompt script for input of additional objects (NEOs, Minor Planets and DeepSkyObjects)**

Description:
    ...  
Ideas:
    ...
"""
from tkinter import *

dir_data="/home/stellarmate/Robotic/KStars_NEOs/"

fields = ['DeepSkyObjects', 'Additional Minor Planets']

def fetch(entries):
   l=[] 
   for entry in entries:
      field = entry[0]
      text  = entry[1].get()
      l.append(text)
      print('%s: "%s"' % (field, text))
   saveobs(l[0],0)
   saveobs(l[1],1)

def makeform(root, fields, insers):
   entries=[]
   for field,inser in zip(fields,insers):
      row = Frame(root)
      lab = Label(row, width=20, text=field, anchor='w')
      ent = Entry(row, width=40)
      ent.insert(10,inser)
      row.pack(side=TOP, fill=X, padx=5, pady=5)
      lab.pack(side=LEFT)
      ent.pack(side=RIGHT, expand=YES, fill=X)
      entries.append((field, ent))
   return entries

#%%
def loadobs():
    fdso = open(dir_data+"dsoObjects.txt", "r") 
    #dso = (fdso.readlines())[0:-1]
    dso=fdso.readlines()
    dso[:]=[line.replace("\n",",") for line in dso]
    dso=' '.join(dso)+' '
    fdso.close()
    
    addobj = open(dir_data+"addObjects.txt","r")
    #aobj = (addobj.readlines())[0:-1]
    aobj=addobj.readlines()
    aobj[:]=[line.replace("\n",",") for line in aobj]
    aobj=' '.join(aobj)+' '
    addobj.close()
    return [dso,aobj]

def saveobs(dso,ind):
   dso=dso.split(",")
   dso=[a.strip() for a in dso]
   if dso[-1] in ['',' ','  ']:
       dso=dso[0:-1]
   if ind==0:
       fdso = open(dir_data+"dsoObjects.txt", "w")
   elif ind==1:
       fdso = open(dir_data+"addObjects.txt", "w")
   else:
       print("Error wrong index")
       quit()
   for obj in dso:
       fdso.write(obj)
       fdso.write('\n')
   fdso.close()
   
   
#%%

insers = loadobs()

#%%

if __name__ == '__main__':
   root = Tk()
   ents = makeform(root, fields, insers)
   root.bind('<Return>', lambda event:[fetch(ents),root.quit()])  
   b1 = Button(root, text='Continue',
          command=lambda:[fetch(ents),root.quit()])
   b1.pack(side=LEFT, padx=5, pady=5)
   b2 = Button(root, text='Quit', command=root.quit)
   b2.pack(side=LEFT, padx=5, pady=5)
   root.mainloop()

