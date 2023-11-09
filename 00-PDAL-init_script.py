# Databricks notebook source
# MAGIC %md # PDAL Init Script: Resources 
# MAGIC
# MAGIC > Here are the customized resources that are relevant for installing PDAL via init script, on DBFS.
# MAGIC
# MAGIC 1. _Init Script:_ 'install-pdal-custom-ubuntu-22.04.sh' [located in the workspace]
# MAGIC 1. _DBFS_PDAL_RESOURCES:
# MAGIC   * _laz-perf:_ '$DBFS_PDAL_RESOURCES/laz-perf_2.1.0.tar.gz'  
# MAGIC   * _custom debs (main focus is on libpdal-dev):_ '$DBFS_PDAL_RESOURCES/pdal_debs'
# MAGIC   * _shared object:_ '$DBFS_PDAL_RESOURCES/libpdalpython.cpython-310-x86_64-linux-gnu.so'
# MAGIC 1. _Optional:_ If interested in further modifying the custom 'libpdal-dev.deb', see (a) 'deb_reconfigure_pdal_2.3.0.sh' and (b) 'rules' [located in the workspace]
# MAGIC
# MAGIC __Cluster__
# MAGIC
# MAGIC <p/>
# MAGIC
# MAGIC * DBR 13.3 LTS
# MAGIC * DBR 12.2 LTS
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC # DBR 13.3 LTS setup
# MAGIC
# MAGIC - Run CMD 3
# MAGIC - Run CMD 4
# MAGIC - If both command run successfully, you can configure your cluster to use the init-script and restart it 

# COMMAND ----------

import os.path

path = dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get()

path = os.path.dirname(path)


# COMMAND ----------


resources_folder = "dbfs:/FileStore/Geospatial/LiDAR-LAZ/resources"
current_path = f"file:/Workspace/{path}"
dbutils.fs.mkdirs(resources_folder)

dbutils.fs.cp(f"{current_path}/resources", resources_folder, True)
dbutils.fs.cp(f"{current_path}/install-pdal-custom-ubuntu-22.04.sh", resources_folder)

dbutils.fs.ls(resources_folder)

# COMMAND ----------

# MAGIC %sh /FileStore/Geospatial/LiDAR-LAZ/resources/install-pdal-custom-ubuntu-22.04.sh

# COMMAND ----------

# MAGIC %md
# MAGIC # DBR 12.2 LTS setup
# MAGIC
# MAGIC - Run CMD 6
# MAGIC - Run CMD 7
# MAGIC - If both command run successfully, you can configure your cluster to use the init-script and restart it 

# COMMAND ----------

resources_folder = "dbfs:/FileStore/Geospatial/LiDAR-LAZ/resources"
current_path = f"file:/Workspace/{path}"
dbutils.fs.mkdirs(resources_folder)

dbutils.fs.cp(f"{current_path}/resources", resources_folder, True)
dbutils.fs.cp(f"{current_path}/install-pdal-custom-ubuntu-20.04.sh", resources_folder)

dbutils.fs.ls(resources_folder)

# COMMAND ----------

# MAGIC %sh /FileStore/Geospatial/LiDAR-LAZ/resources/install-pdal-custom-ubuntu-20.04.sh

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC ## Test PDAL library

# COMMAND ----------

from pdal import Pipeline
import json

# COMMAND ----------

  params = {
    "pipeline": [
    ]}
  pipeline = Pipeline(json.dumps(params))
  pipeline.execute()

