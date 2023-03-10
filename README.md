# NEOs-for-KStars-Linux
Import Scripts to use current NEO and other Minor Planet data (from MPC, Confirmation Page, ESA, etc.) in KStars for Linux Systems.

# Short Description
The script imports the current NEOs on the ESA Priority list, the MPC NEA Observation Aid, the MPC Confirmation Page and some own additional objects (e.g. from a input prompt). It checks all objects for observability in the following night (magnitude, altitude, uncertainty, etc.). The final list of observable objets is put into KStars (asteroid file) and the Wishlist in order to quickly import the objects into the Scheduler. It is necessary to run this script before starting KStars. An Internet connection is also needed.

# Requirements
- Internet connection during whole observation process
- Python3
- Python Packages: datetime, ephem, os, math, requests, json, sys, subprocess, astropy, tkinter
- INDI Libary (Version 1.9.5 tested)
- KStars (Version 3.5.8 tested)

# Manual
- Save all code files into one folder
- Adapt the parameters and directories in:
  - KStars_startup_script.sh
  - Input_objects.py
  - NEO_KStars.py
  - Pre_Capture_NEO.py
- Start KStars_startup_script.sh in order to run the codes in the corresponding order
- After script is completed, KStars should be started automatically. You can use the whishlist or the search function in KStars to use the objects
- IMPORTANT: Use the Pre_Capture_NEO.py script before every Capture as Pre-Capture script in Ekos. The coordinates of the object will be updated and the mount is corrected. The dome needs to be slewed again after that procedure. This will correct for the movement of the object according to latest data from MPC, which is not implemented in KStars.

# Description
TBD
