import os

# ============================================================
# WINDOWS HADOOP CONFIGURATION
# ============================================================

os.environ["HADOOP_HOME"] = r"C:\winutils"
os.environ["hadoop.home.dir"] = r"C:\winutils"

# ============================================================
# IMPORTS
# ============================================================

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, datediff, when, to_date

# ============================================================
# START SPARK
# ============================================================

spark = (
    SparkSession.builder
    .appName("ShipTrack")
    .master("local[*]")
    .config(
        "spark.hadoop.fs.file.impl",
        "org.apache.hadoop.fs.LocalFileSystem"
    )
    .config(
        "spark.hadoop.mapreduce.fileoutputcommitter.algorithm.version",
        "2"
    )
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

# ============================================================
# READ RAW SHIPMENT DATA
# ============================================================

input_path = "data/shipments.csv"

print("\n================ READING DATA ================\n")
print("Input:", input_path)

df = (
    spark.read
    .csv(
        input_path,
        header=True,
        inferSchema=True
    )
)

print("\n================ ORIGINAL DATA ================\n")

df.show(10, truncate=False)

# ============================================================
# CONVERT DATE COLUMNS
# ============================================================

df = (
    df
    .withColumn("order_date", to_date(col("order_date")))
    .withColumn("promised_date", to_date(col("promised_date")))
    .withColumn("delivery_date", to_date(col("delivery_date")))
)

# ============================================================
# REMOVE DUPLICATE ORDERS
# ============================================================

df = df.dropDuplicates(["order_id"])

# ============================================================
# CALCULATE DELIVERY DAYS
# ============================================================

df = df.withColumn(
    "delivery_days",
    datediff(
        col("delivery_date"),
        col("order_date")
    )
)

# ============================================================
# CALCULATE DAYS LATE
# ============================================================

df = df.withColumn(
    "days_late",
    when(
        col("delivery_date").isNull(),
        0
    )
    .when(
        col("delivery_date") > col("promised_date"),
        datediff(
            col("delivery_date"),
            col("promised_date")
        )
    )
    .otherwise(0)
)

# ============================================================
# DISPLAY PROCESSED DATA
# ============================================================

print("\n================ PROCESSED DATA ================\n")

df.show(10, truncate=False)

# ============================================================
# TOTAL ORDERS
# ============================================================

total_orders = df.count()

print("\n================ TOTAL ORDERS ================\n")
print("Total Orders:", total_orders)

# ============================================================
# LATE ORDERS
# ============================================================

print("\n================ LATE ORDERS ================\n")

df.filter(
    col("status") == "LATE"
).show(truncate=False)

# ============================================================
# ORDERS BY WAREHOUSE
# ============================================================

print("\n================ ORDERS BY WAREHOUSE ================\n")

(
    df.groupBy("warehouse")
    .count()
    .orderBy(col("count").desc())
    .show()
)

# ============================================================
# ORDERS BY CARRIER
# ============================================================

print("\n================ ORDERS BY CARRIER ================\n")

(
    df.groupBy("carrier")
    .count()
    .orderBy(col("count").desc())
    .show()
)

# ============================================================
# SAVE PROCESSED DATA
# ============================================================
print("\n================ SAVING OUTPUT ================\n")

import csv

output_path = "output/processed_shipments.csv"

rows = df.collect()
columns = df.columns

with open(output_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(columns)
    for row in rows:
        writer.writerow(row)

print("Processed data saved successfully!")


# ============================================================
# STOP SPARK
# ============================================================

spark.stop()

print("\n================================================")
print("PySpark processing completed successfully!")
print("Total Orders:", total_orders)
print("Output Folder:", output_path)
print("================================================")