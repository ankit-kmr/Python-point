from databricks.connect import DatabricksSession
from databricks.labs.dqx.profiler.profiler import DQProfiler
from databricks.sdk import WorkspaceClient

# Initialize Spark and Databricks Client
spark = DatabricksSession.builder.getOrCreate()
ws = WorkspaceClient()

# Load your data
df = spark.read.table("test_ak.order_data")

# Initialize Profiler and analyze data
profiler = DQProfiler(ws)
summary_stats, profiles = profiler.profile(df)

print(profiles)