import psycopg2
import pandas as pd
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

def insert_jobs_df_to_db(jobs_df):
    connection = None  # Initialize connection to None before the try block
    print("DEBUG: Entered insert_jobs_df_to_db")  # Debugging print

    try:
        print("DEBUG: Attempting to connect to the database...")  # Debugging print before connection
        connection = psycopg2.connect(...)  # Replace with your actual connection details
        cursor = connection.cursor()
        
        for index, row in jobs_df.iterrows():
            postgres_insert_query = """INSERT INTO job_details (title, location, date_posted, work_setting, work_mode, 
                                        job_description, position_id, company_name, company_url, job_url, scraped_date) 
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            record_to_insert = (
                row['title'], row['location'], row['date_posted'], row['work_setting'], row['work_mode'], 
                row['job_description'], row['position_id'], row['company_name'], row['company_url'], 
                row['job_url'], row['scraped_date']
            )
            print(f"DEBUG: Inserting record {record_to_insert}")  # Debugging print for each record
            cursor.execute(postgres_insert_query, record_to_insert)
        
        connection.commit()
        print("DEBUG: Commit successful")  # Debugging print after commit

    except (Exception, psycopg2.Error) as error:
        print("Failed to insert records into job_details table", error)

    finally:
        if connection is not None:
            print("DEBUG: Closing the connection")  # Debugging print for closing connection
            connection.close()
