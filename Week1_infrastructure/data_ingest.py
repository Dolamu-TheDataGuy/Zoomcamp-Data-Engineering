import os
import pandas as pd
from time import time
import pyarrow
import fastparquet
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()


def main() -> None:
    user = os.getenv('POSTGRES_USER')
    password = os.getenv('POSTGRES_PASSWORD')
    database = os.getenv('POSTGRES_DB')
    host = os.getenv('HOST')
    port = os.getenv('PORT')
    url = os.getenv('URL')
    table_name = os.getenv('TABLE_NAME')
    
    # connect to database
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database}')
    conn = engine.connect()
    
    source_file = 'data.parquet'
    
    os.system(f"wget {url} -O {source_file}")
    
    pd.read_parquet("data.parquet").to_csv("data.csv") # convert parquet file to csv
    
    df_iter = pd.read_csv("data.csv", iterator=True, chunksize=100000) #convert to a generator
    

    n = 0
    while True:
        try:
            start_time = time()
            data1 = next(df_iter)
            data1.drop("Unnamed: 0", axis=1, inplace=True)
            data1.to_sql(name='yellow_taxi_data', con=conn, if_exists='append')
            end_time = time()
            if n == 0:
                print(f"inserted first chunk, it took {end_time - start_time:3f} seconds")
            else:
                print(f"inserted another chunk, it took {end_time - start_time:3f} seconds")
            n += 1
        except StopIteration:
            print("Finished ingesting all dataset to dataset")
            break
        
if __name__ == "__main__":
    main()