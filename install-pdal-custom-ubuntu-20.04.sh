%sh
lsb_release -a
#apt -y --fix-broken install
phycores=$(cat /proc/cpuinfo|grep -m 1 "cpu cores"|awk '{print $ 4;}')
add-apt-repository ppa:ubuntugis/ppa
apt-get update
apt-get install -y gdal-bin libgdal-dev gcc-multilib
apt-get install -y pdal libpdal-dev

pdal-config --libs 
ls /usr/lib/cmake/PDAL 
pip install pdal==3.0.2