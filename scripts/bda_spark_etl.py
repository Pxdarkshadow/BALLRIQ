"""
Academic Big Data Script: Distributed PySpark ETL & Commentary NLP Aggregator
Demonstrates Apache Spark DataFrame transformations, partitioning, and scalable aggregation.
"""
import sys
from pathlib import Path

def run_spark_etl():
    print("=" * 60)
    print("CRICBHASHA BIG DATA ANALYTICS: SPARK BATCH ETL PIPELINE")
    print("=" * 60)

    try:
        from pyspark.sql import SparkSession
        from pyspark.sql.functions import col, count, avg, sum, when, explode, split

        spark = SparkSession.builder \
            .appName("BALLRIQ_BDA_Commentary_ETL") \
            .master("local[*]") \
            .config("spark.driver.memory", "2g") \
            .getOrCreate()

        print("Spark Session initialized successfully.")

        # Ingest Parquet Lake
        lake_path = Path(__file__).resolve().parents[1] / "data" / "lake"
        comm_parquet = str(lake_path / "commentary").replace("\\", "/")

        df = spark.read.parquet(comm_parquet)
        print(f"Loaded {df.count()} commentary records across partitions.")

        # Aggregation: Language-wise event counts
        lang_summary = df.groupBy("language", "event_label").agg(count("*").alias("total_events"))
        lang_summary.show(20, truncate=False)

        spark.stop()
        print("Spark ETL pipeline completed successfully.")
    except ImportError:
        print("[Note: PySpark not installed in standard local environment. Demonstration fallback below.]")
        print("Distributed Spark Logic Blueprint:")
        print("1. spark.read.parquet('data/lake/commentary/*')")
        print("2. df.withColumn('phase', when(col('over') < 6, 'Powerplay').when(col('over') < 16, 'Middle').otherwise('Death'))")
        print("3. df.groupBy('language', 'phase').agg(count('event_label'), avg('runs'))")
        print("4. df.write.partitionBy('format', 'year').parquet('data/lake/analytics_mart/')")


if __name__ == "__main__":
    run_spark_etl()
