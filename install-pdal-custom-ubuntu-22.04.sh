%sh
#!/bin/bash
# -- 
# OPTION: TO GET LAZ Support (Pre-Modified DEB)
# This is for Ubuntu 22.04 (Jammy)
# - Corresponds to DBR 13+
# - Jammy offers GDAL 3.4.1:
#   we are using that for this example
# Author: Michael Johns | mjohns@databricks.com
# Last Modified: 23 AUG, 2023

# !!! ASSUMES A BIT OF PREP ALREADY DONE on DBFS (Volumes) !!!
DBFS_PDAL_RESOURCES=/dbfs/FileStore/Geospatial/LiDAR-LAZ/resources
echo "DBFS_PDAL_RESOURCES -> '$DBFS_PDAL_RESOURCES'"

# -- determine num cores
phycores=$(cat /proc/cpuinfo|grep -m 1 "cpu cores"|awk '{print $ 4;}')

# -- refresh package info
#  - make sure updates and backports are available
#  - https://askubuntu.com/questions/703923/problem-with-sources-list-apt-get-not-working-properly
apt-add-repository "deb http://archive.ubuntu.com/ubuntu $(lsb_release -sc)-backports main universe multiverse restricted"
apt-add-repository "deb http://archive.ubuntu.com/ubuntu $(lsb_release -sc)-updates main universe multiverse restricted"
apt-add-repository "deb http://archive.ubuntu.com/ubuntu $(lsb_release -sc)-security main multiverse restricted universe"
apt-add-repository "deb http://archive.ubuntu.com/ubuntu $(lsb_release -sc) main multiverse restricted universe"
apt-get update -y

# -- laz-perf
#  - pull in from DBFS (Volumes)
cd $DB_HOME \
  && rm -rf laz-perf \
  && mkdir laz-perf \
  && cd laz-perf \
  && tar -xzf $DBFS_PDAL_RESOURCES/laz-perf_2.1.0.tar.gz \
  && cd build \
  && cmake .. \
  && make -j $phycores install/fast

# -- dependencies needed by pdal deb
#  - second line for pdal-dev
apt-get install -y gdal-bin libgdal-dev libgeotiff-dev libhdf5-dev libjs-mathjax liblaszip8 liblaszip-dev libxerces-c-dev libzstd-dev \
  libgeos++-dev


# -- pull down pre-built debs
#  - not all are required to be custom installed;
#    libpdal-dev has the headers and custom config
mkdir -p $DB_HOME/custom_debs \
  && cp -r $DBFS_PDAL_RESOURCES/pdal_debs $DB_HOME/custom_debs \
  && cd $DB_HOME/custom_debs/pdal_debs \
  && apt-get --reinstall install -y ./libpdal-dev_2.3.0+ds-2ubuntu4_amd64.deb

apt-get install -y pdal

# -- install GDAL python bindings (from PyPI) for version installed
#  - see requirements at https://pypi.org/project/pdal/2.3.0/
#  - make sure GDAL version matches
apt-get install -y python3-gdal

pip install --upgrade pip

# - being explicit
# - vs $(gdalinfo --version | grep -Po '(?<=GDAL )[^;]+' | cut -d, -f1)
pip install GDAL==3.4.1

# -- pull in previously built libpdalpython 
mkdir -p /usr/local/pdal
cp $DBFS_PDAL_RESOURCES/libpdalpython.cpython-310-x86_64-linux-gnu.so /usr/local/pdal
#cp $DBFS_PDAL_RESOURCES/libpdalpython.cpython-310-x86_64-linux-gnu.so $(find $DATABRICKS_LIBS_NFS_ROOT_PATH -type d -name pdal)
cp $DBFS_PDAL_RESOURCES/libpdalpython.cpython-310-x86_64-linux-gnu.so /usr/lib
cp $DBFS_PDAL_RESOURCES/libpdalpython.cpython-310-x86_64-linux-gnu.so /usr/local/lib

# -- finally can install pdal python bindings
#  - https://pypi.org/project/pdal/3.0.2/ is the best python version for pdal 2.3.0
pip install scikit-build cmake ninja numpy pybind11[global]
pip install pdal==3.0.2