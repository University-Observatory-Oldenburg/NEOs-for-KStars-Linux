#!/bin/bash
sudo date -s "$(wget -qSO- --max-redirect=0 google.com 2>&1 | grep Date: | cut -d' ' -f5-8)Z" &
wait
python /home/stellarmate/Robotic/KStars_NEOs/V1/Input_objects.py &
wait
python /home/stellarmate/Robotic/KStars_NEOs/V1/NEO_KStars.py &
wait
kstars &
echo "Fertig"
