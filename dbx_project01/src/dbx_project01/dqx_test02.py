from databricks.labs.dqx.rule import DQRowRule
from databricks.labs.dqx import check_funcs

from databricks.labs.dqx.engine import DQEngine
from databricks.sdk import WorkspaceClient

my_rules = [
    DQRowRule(
        name="product_id_not_null",
        column="product_id",
        check_func=check_funcs.is_not_null_and_not_empty,
        criticality="error" # Will cause the row to be quarantined
    ),
    DQRowRule(
        name="payment_amount_price_check",
        column="payment_amount",
        check_func=check_funcs.sql_expression,
        check_func_kwargs={
        "expression": "payment_amount > 0"},
        criticality="warn" # Row stays in dataset but is flagged
    )   
]

ws = WorkspaceClient()
dq_engine = DQEngine(ws)

# Load your data
df = spark.read.table("test_ak.order_data")

# Apply the rules and split the DataFrame
# 'valid_df' contains valid rows; 'quarantine_df' contains the failures
valid_df, quarantine_df = dq_engine.apply_checks_and_split(df, my_rules)

if not valid_df.isEmpty():
    print("valid_df count ==> ", valid_df.count())
    valid_df.show()
    valid_df.write.mode("overwrite").saveAsTable("test_ak.order_data_clean")
if not quarantine_df.isEmpty():
    print("quarantine_df count ==> ", quarantine_df.count())
    quarantine_df.show()
    quarantine_df.write.mode("overwrite").saveAsTable("test_ak.order_data_quarantine")
