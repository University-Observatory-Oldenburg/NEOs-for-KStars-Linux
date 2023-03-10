#!/bin/bash
sudo date -s "$(wget -qSO- --max-redirect=0 google.com 2>&1 | grep Date: | cut -d' ' -f5-8)Z" &
wait
python /home/stellarmate/Robotic/KStars_NEOs/Input_objects_V1.py &
wait
python /home/stellarmate/Robotic/KStars_NEOs/NEO_KStars_V1.py &
wait
kstars &
echo "Fertig"
