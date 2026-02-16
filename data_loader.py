import os
import pandas as pd
from pathlib import Path
import sqlite3
from functions import prinfo

def load_largest_table(db_file):
    """
    Connects to an SQLite database and loads the largest table into a pandas DataFrame.

    Args:
        db_file (str): Path to the database file.

    Returns:
        tuple: (DataFrame, table_name)
    """
    conn = sqlite3.connect(db_file)
    
    # Get the list of tables in the database
    table_query = "SELECT name FROM sqlite_master WHERE type='table';"
    tables = pd.read_sql(table_query, conn)['name'].tolist()
    
    # Find the table with the maximum number of rows
    largest_table = None
    max_rows = 0
    
    for table in tables:
        count_query = f"SELECT COUNT(*) FROM {table};"
        row_count = pd.read_sql(count_query, conn).iloc[0, 0]
        
        if row_count > max_rows:
            max_rows = row_count
            largest_table = table
    
    # Load the data from the largest table
    DF = pd.read_sql(f"SELECT * FROM {largest_table}", conn)
    
    conn.close()
    return DF, largest_table

def load_data(root_dir=None):
    """
    Loads data from the first .db file found in the root directory.

    Args:
        root_dir (str, optional): The directory to search for the database.

    Returns:
        tuple: (all_categorical_options, all_numeric_options, DF)
    """
    prinfo(f"Loading data from {root_dir}...")
    # Efficiently get the first *.db file
    db_file = next(Path(root_dir).glob('*.db'), None)
    if db_file is None:
        raise FileNotFoundError("No Database file found in the specified directory.")
    
    # read sql database into pandas dataframe
    DF, largest_table = load_largest_table(db_file)
    # print DF info:
    prinfo(f"Largest table: {largest_table}")
    prinfo(DF.info())
    
    df_categorical = DF.select_dtypes(include=["category", "object"]).columns
    DF[df_categorical] = DF[df_categorical].apply(lambda x: x.astype('category'))
    prinfo(DF.info())
    df_numeric = DF.select_dtypes(include=["number"]).columns

    all_categorical_options = [{"label": col, "value": col} for col in df_categorical]
    all_numeric_options = [{"label": col, "value": col} for col in df_numeric]

    all_categorical_options = sorted(all_categorical_options, key=lambda x: x['label'])
    all_numeric_options = sorted(all_numeric_options, key=lambda x: x['label'])
        
    return all_categorical_options, all_numeric_options, DF

if __name__ == "__main__":
    # Test the load_data function
    try:
        ROOT_DIR = r"C:\Temp\Lukas_miniSub"
        options, categorical_options, numeric_options, df = load_data(ROOT_DIR)
        print(f"Data loaded from {ROOT_DIR}.")
        print(f"Total options: {len(options)}")
        print(f"Categorical options: {len(categorical_options)}")
        # print all categorical options
        for i in categorical_options:
            print(i)
        print(f"Numeric options: {len(numeric_options)}")
        # print all numeric options
        for i in numeric_options:
            print(i)
        print("Sample data:", df.head())
    except Exception as e:
        print(f"An error occurred: {e}")
