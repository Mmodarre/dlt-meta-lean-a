from pyspark.sql.types import *

##  Function to perform initial load
##  The function takes a list of tables to perform initial load
## @param initalLoadTableList: List of tables to perform initial load
## @type initalLoadTableList: List
## @return None
def perform_initial_load(initalLoadTableList=[]):
  ## Loop through the list of tables to perform initial load
  for table in initalLoadTableList:
    ## Read the seed table
    df_seed = spark.read.table(table["seed_table"])
    ## Read the DLT landing folder
    df_dlt = spark.read.format("parquet").load(table["dlt_landing_folder"])
    ## variable to hold columns to exclude from seed table
    exclude_colunms = []
    
    ## Loop through the schema of the seed table and check if the column is not in the DLT table
    for i in df_seed.schema.fields:
      if i.name not in df_dlt.schema.fieldNames():
        exclude_colunms.append(i.name)

    ## If it is not, add it to the list of columns to exclude
    ## This is to handle the case where the column is in the seed table but not in the DLT table
    if exclude_colunms and len(exclude_colunms) > 0 :
      print(f"Removing {exclude_colunms} from {table['seed_table']}")
      df_seed = df_seed.drop(*exclude_colunms)
    
    ## Loop through the schema of the seed table and check if the column is of type BooleanType
    ## If it is, cast it to BooleanType
    ## This is to handle the case where the column is of type IntegerType in the seed table and BooleanType in the DLT table
    for i in df_dlt.schema.fields:
      if i.dataType == BooleanType():
        df_seed = df_seed.withColumn(i.name,df_seed[i.name].cast("boolean"))
        print(f"Casting {i.name} from IntegerType() to BooleanType in {table['seed_table']}")

    ## Get the data that is only in the seed table
    data_only_in_seed_table_df = df_seed.subtract(df_dlt)
    
    print(f"Writing {data_only_in_seed_table.count()} records to {table['dlt_landing_folder']}")
    ## Write the data that is only in the seed table to the DLT landing folder
    data_only_in_seed_table_df.write.format("parquet").mode("append").save(table["dlt_landing_folder"])

## EXAMPLE USAGE
tables_to_initial_load = [{"seed_table":"mehdidatalake_catalog.retail_cdc.customer_init_load_seed","dlt_landing_folder":"/Volumes/mehdidatalake_catalog/retail_cdc/retail_landing/cdc_raw/customers_init_load_dlt"}]
perform_initial_load(tables_to_initial_load)