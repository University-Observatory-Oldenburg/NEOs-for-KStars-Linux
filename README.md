# NEOs-for-KStars-Linux
Import Scripts to use current NEO and other Minor Planet data (from MPC, Confirmation Page, ESA, etc.) in KStars for Linux Systems.
Robotic observation pipeline described by (**Hoffmann et al., 2022**): https://doi.org/10.3389/fspas.2022.895732

## Short Description
The script imports the current NEOs on the ESA Priority list, the MPC NEA Observation Aid, the MPC Confirmation Page and some own additional objects (e.g. from a input prompt). It checks all objects for observability in the following night (magnitude, altitude, uncertainty, etc.). The final list of observable objets is put into KStars (asteroid file) and the Wishlist in order to quickly import the objects into the Scheduler. It is necessary to run this script before starting KStars. An Internet connection is also needed.

## Requirements
- Internet connection during whole observation process
- NTP service for time synchronization (e.g. ntpd)
- Python3
- Python Packages: datetime, ephem, os, math, requests, json, sys, subprocess, astropy, tkinter
- INDI Libary (Version 1.9.5 tested)
- KStars (Version 3.5.8 tested)

## Manual
- Save all code files into one folder
- Adapt the parameters and directories in:
  - KStars_startup_script.sh
  - Input_parameters.py
  - NEO_KStars.py
  - Pre_Capture_NEO.py
- Make all scripts executable ("chmod +x *Script.xx*")
- Start KStars_startup_script.sh in order to run the codes in the corresponding order
- A prompt window should open. Insert your parameters for your observatory.
- Also a second prompt window opens. Here put in additional objects you like to capture.
- After script is completed, KStars should be started automatically. You can use the whishlist or the search function in KStars to use the objects
- **IMPORTANT: Use the Pre_Capture_NEO.py script before every Capture as Pre-Capture script in Ekos. The coordinates of the object will be updated and the mount is corrected. The dome needs to be slewed again after that procedure. This will correct for the movement of the object according to latest data from MPC, which is not implemented in KStars.**

## Description
TBD
- Release v1.1 was used to obtain the results for the original research article by Hoffmann et al. (2022), which can be accessed here: [doi.org/10.3389/fspas.2022.895732](https://doi.org/10.3389/fspas.2022.895732). The details of the software are further described in our paper.

## Further Developments (TBD)
- Automatic Schedule Maker

## References
- Hoffmann T, Gehlen M, Plaggenborg T, Drolshagen G, Ott T, Kunz J, Santana-Ros T, Gedek M, Reszelewski R, Żołnowski M and Poppe B (2022) Robotic observation pipeline for small bodies in the solar system based on open-source software and commercially available telescope hardware. Front. Astron. Space Sci. 9:895732. doi: [10.3389/fspas.2022.895732](https://doi.org/10.3389/fspas.2022.895732)
