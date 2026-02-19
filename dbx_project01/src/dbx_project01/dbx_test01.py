from databricks.connect import DatabricksSession
spark = DatabricksSession.builder.getOrCreate()

df = spark.table("test_ak.order_data")
# df.show()
pandas_df = df.toPandas()
print(pandas_df)