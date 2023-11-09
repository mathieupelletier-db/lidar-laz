# Databricks notebook source
# MAGIC %md # NB-01: Create the LiDAR Dataset
# MAGIC
# MAGIC > Download a grid reference chips of LiDAR Point Cloud LAZ data from Ordnance Survey in UK onto DBFS and then split the files into smaller files.
# MAGIC
# MAGIC #### Databricks Author(s)
# MAGIC * __Original: Stuart Lynn (On Sabbatical)__
# MAGIC * __Maintainer: Michael Johns | <mjohns@databricks.com>__
# MAGIC ---
# MAGIC _Last Modified: 26 JUL 2022_

# COMMAND ----------

import json
import os
import shutil

import pandas as pd

from subprocess import run, PIPE
from pdal import Pipeline
from glob import glob

from pyspark import Row
from pyspark.sql.types import *

# COMMAND ----------

# MAGIC %md ## Data Sourcing

# COMMAND ----------

# MAGIC %md
# MAGIC Download a set of OS grid reference chips of LiDAR Point Cloud data.

# COMMAND ----------

session = "ade4ccfb1358480cbec0a6cbe40ce9ce78628"
grid_refs = ["NY2505", "NY2510"]

#https://api.agrimetrics.co.uk/tiles/collections/survey/national_lidar_programme_point_cloud/2021/1/NY2505?subscription-key=public

urls = [f"https://api.agrimetrics.co.uk/tiles/collections/survey/national_lidar_programme_point_cloud/2021/1/{grid_ref}?subscription-key=public" for grid_ref in grid_refs]
local_uris = [f"/tmp/National-LIDAR-Programme-Point-Cloud-2021-{grid_ref}.zip" for grid_ref in grid_refs]

for url, local_uri in zip(urls, local_uris):
  output_wget = run(['wget', '-O', local_uri, url], capture_output=False)
  print(output_wget)
  output_unzip = run(['unzip', '-d', '/tmp', local_uri])
  print(output_unzip)

# COMMAND ----------

import zipfile
path_to_zip_file = '/tmp/National-LIDAR-Programme-Point-Cloud-2018-TQ46sw.zip'
directory_to_extract_to = '/tmp'
with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
    zip_ref.extractall(directory_to_extract_to)


# COMMAND ----------

# MAGIC %sh unzip -d /tmp /tmp/National-LIDAR-Programme-Point-Cloud-2018-TQ46sw.zip

# COMMAND ----------

# MAGIC %fs ls file:/tmp/

# COMMAND ----------

# MAGIC %md __Move these downloaded LAZ files to DBFS__

# COMMAND ----------

dbutils.fs.mkdirs("/home/mathieu.pelletier@databricks.com/datasets/lidar/raw/")

# COMMAND ----------

dbutils.fs.cp("file:/tmp/NY2505_P_10625_20201130_20210112.laz", "/home/mathieu.pelletier@databricks.com/datasets/lidar/raw/")

# COMMAND ----------

dbutils.fs.cp("file:/tmp/NY2510_P_10625_20201130_20210112.laz", "/home/mathieu.pelletier@databricks.com/datasets/lidar/raw/")

# COMMAND ----------

# MAGIC %fs ls /home/mathieu.pelletier@databricks.com/datasets/lidar/raw/

# COMMAND ----------

# MAGIC %md ## Pre-processing
# MAGIC For demo purposes, we can divide these files into many smaller parts to facilitate parallel processing.

# COMMAND ----------

def dbfs_to_local(path: str) -> str:
  return f"dbfs{path}" if path[0] == "/" else f"dbfs/{path}"

def local_to_dbfs(path: str) -> str:
  return path.split("/dbfs")[-1]

# COMMAND ----------

# MAGIC %md __A function that will split an input LAZ file into multiple smaller files (based on a path supplied in a Pandas DataFrame).__

# COMMAND ----------

def split_laz(pdf: pd.DataFrame) -> pd.DataFrame:
  in_path = pdf.loc[0, "input_uri"]
  output_path_local = pdf.loc[0, "output_path"]
  output_filename_stem = os.path.splitext(os.path.basename(in_path))[0]
  
  os.makedirs(output_path_local, exist_ok=True)
  os.makedirs(f"/tmp/{output_filename_stem}", exist_ok=True)
  
  params = {
    "pipeline": [
      {"type": "readers.las", "filename": in_path},
      {"type":"filters.divider", "count": 50},
      {
        "type":"writers.las", 
        "filename": f"/tmp/{output_filename_stem}/{output_filename_stem}_#.laz"
      }
    ]}
  # "compression": "lazperf",
  pipeline = Pipeline(json.dumps(params))
  pipeline.execute()
  for filename in glob(os.path.join(f"/tmp/{output_filename_stem}", '*.laz')):
    shutil.copy(filename, output_path_local)
  return pd.DataFrame([pdf["input_uri"], pd.Series(["OK"])])

# COMMAND ----------

# MAGIC %md __Create my 'target' dataframe, with paths to files to original LAZ files.__

# COMMAND ----------

lidar_inputs = glob("/dbfs/home/mathieu.pelletier@databricks.com/datasets/lidar/raw/*.laz")
output_dir = "/dbfs/home/mathieu.pelletier@databricks.com/datasets/lidar/"

lidar_inputs_sdf = (
  spark.createDataFrame(
    [Row(pth, output_dir) for pth in lidar_inputs], 
    schema=StructType([
      StructField("input_uri", StringType()),
      StructField("output_path", StringType())
    ])
  )
)

lidar_inputs_sdf.display()

# COMMAND ----------

# MAGIC %md __GroupBy + Apply execution of the function, in parallel across the cluster.__
# MAGIC
# MAGIC > Uses UDF `split_laz`

# COMMAND ----------

split_results = lidar_inputs_sdf.groupBy("input_uri", "output_path").applyInPandas(split_laz, schema="result string")
split_results.write.mode("overwrite").csv("/home/mathieu.pelletier@databricks.com/datasets/lidar/split_log")

# COMMAND ----------

# MAGIC %fs ls /home/mathieu.pelletier@databricks.com/datasets/lidar

# COMMAND ----------

#dbutils.fs.cp("/dbfs/home/mjohns@databricks.com/geospatial/pdal/pdal_debs", "")
