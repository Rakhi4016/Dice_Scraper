import os
import snowflake.connector
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

SF_USER      = os.getenv('SF_USER')
SF_PASSWORD  = os.getenv('SF_PASSWORD')
SF_ACCOUNT   = os.getenv('SF_ACCOUNT')
SF_WAREHOUSE = os.getenv('SF_WAREHOUSE')
SF_ROLE      = os.getenv('SF_ROLE')      # optional


def insert_jobs_df_to_snowflake(jobs_df):
    """
    Creates dev_blue database, bronze schema, and Job_listings table (if they don't exist),
    bulk-loads new records via a temporary table and MERGE to skip existing position_ids.
    """
    ctx = None
    try:
        print("DEBUG: Connecting to Snowflake…")
        ctx = snowflake.connector.connect(
            user=SF_USER,
            password=SF_PASSWORD,
            account=SF_ACCOUNT,
            warehouse=SF_WAREHOUSE,
            role=SF_ROLE
        )
        cs = ctx.cursor()

        # Create database, schema, and table if not exists
        cs.execute("CREATE DATABASE IF NOT EXISTS dev_blue")
        cs.execute("USE DATABASE dev_blue")
        cs.execute("CREATE SCHEMA IF NOT EXISTS bronze")
        cs.execute("USE SCHEMA bronze")
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

        # Return early if there's no data
        if jobs_df.empty:
            print("DEBUG: No data to insert")
            return

        # 1) Create a temporary table for bulk load
        cs.execute("CREATE OR REPLACE TEMPORARY TABLE tmp_job_listings LIKE Job_listings")

        # 2) Bulk load into temp table
        insert_temp_sql = """
            INSERT INTO tmp_job_listings
            (title, location, date_posted, work_setting, work_mode,
             job_description, position_id, company_name, company_url, job_url, scraped_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        records = [(
            row['title'], row['location'], row['date_posted'],
            row['work_setting'], row['work_mode'], row['job_description'],
            row['position_id'], row['company_name'], row['company_url'],
            row['job_url'], row['scraped_date']
        ) for _, row in jobs_df.iterrows()]

        print(f"DEBUG: Inserting {len(records)} rows into temporary table")
        cs.executemany(insert_temp_sql, records)

        # 3) Merge new rows into the main table, skipping existing position_ids
        merge_sql = """
            MERGE INTO Job_listings AS tgt
            USING tmp_job_listings AS src
            ON tgt.position_id = src.position_id
            WHEN NOT MATCHED THEN
              INSERT (title, location, date_posted, work_setting, work_mode,
                      job_description, position_id, company_name, company_url, job_url, scraped_date)
              VALUES (src.title, src.location, src.date_posted, src.work_setting, src.work_mode,
                      src.job_description, src.position_id, src.company_name, src.company_url, src.job_url, src.scraped_date)
        """
        cs.execute(merge_sql)

        ctx.commit()
        print("DEBUG: Merge complete, new records inserted")

    except Exception as e:
        print("❌ Failed to insert records into Snowflake:", e)

    finally:
        if ctx:
            print("DEBUG: Closing Snowflake connection")
            ctx.close()
