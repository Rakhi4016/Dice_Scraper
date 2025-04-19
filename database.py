import os
import snowflake.connector
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

SF_USER      = os.getenv('SF_USER')
SF_PASSWORD  = os.getenv('SF_PASSWORD')
SF_ACCOUNT   = os.getenv('SF_ACCOUNT')
SF_WAREHOUSE = os.getenv('SF_WAREHOUSE')
SF_ROLE = os.getenv("SF_ROLE")
# We’ll explicitly connect to the ACCOUNT-level; database/schema will be created below

def insert_jobs_df_to_snowflake(jobs_df):
    """
    Creates dev_blue database, bronze schema, Job_listings table (if they don't exist),
    then inserts all rows from jobs_df into Job_listings.
    """
    ctx = None
    try:
        print("DEBUG: Connecting to Snowflake…")
        ctx = snowflake.connector.connect(
            user=SF_USER,
            password=SF_PASSWORD,
            account=SF_ACCOUNT,
            warehouse=SF_WAREHOUSE
        )
        cs = ctx.cursor()

        # 1) Create database and switch to it
        cs.execute("CREATE DATABASE IF NOT EXISTS dev_blue")
        cs.execute("USE DATABASE dev_blue")

        # 2) Create schema and switch to it
        cs.execute("CREATE SCHEMA IF NOT EXISTS bronze")
        cs.execute("USE SCHEMA bronze")

        # 3) Create table if not exists
        cs.execute("""
            CREATE TABLE IF NOT EXISTS Job_listings (
              title            VARCHAR,
              location         VARCHAR,
              date_posted      VARCHAR,
              work_setting     VARCHAR,
              work_mode        VARCHAR,
              job_description  VARCHAR,
              position_id      VARCHAR,
              company_name     VARCHAR,
              company_url      VARCHAR,
              job_url          VARCHAR,
              scraped_date     VARCHAR
            )
        """)

        # 4) Insert rows
        insert_sql = """
            INSERT INTO Job_listings
              (title, location, date_posted, work_setting, work_mode,
               job_description, position_id, company_name, company_url, job_url, scraped_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        for idx, row in jobs_df.iterrows():
            record = (
                row['title'], row['location'], row['date_posted'],
                row['work_setting'], row['work_mode'], row['job_description'],
                row['position_id'], row['company_name'], row['company_url'],
                row['job_url'], row['scraped_date']
            )
            print(f"DEBUG: Inserting record {idx}")
            cs.execute(insert_sql, record)

        ctx.commit()
        print("DEBUG: Snowflake commit successful")

    except Exception as e:
        print("❌ Failed to insert records into Snowflake:", e)

    finally:
        if ctx:
            print("DEBUG: Closing Snowflake connection")
            ctx.close()
