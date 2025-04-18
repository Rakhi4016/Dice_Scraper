import pytest
from unittest.mock import patch
import pandas as  pd
import psycopg2
from database import insert_jobs_df_to_db

# Sample job data for testing
sample_data = {
    'title': ['Software Engineer'],
    'location': ['New York'],
    'date_posted': ['2024-01-01'],
    'work_setting': ['Remote'],
    'work_mode': ['Full-time'],
    'job_description': ['Develop software'],
    'position_id': ['12345'],
    'company_name': ['Tech Co'],
    'company_url': ['https://techco.com'],
    'job_url': ['https://job123.com'],
    'scraped_date': ['2024-09-01']
}

# Convert the sample data to a DataFrame
jobs_df = pd.DataFrame(sample_data)

@patch('database.psycopg2.connect', side_effect=psycopg2.Error("Connection error"))
def test_insert_jobs_df_to_db_exception(mock_connect):
    """Test handling of exceptions during the database operation."""

    print("DEBUG: Test starting, forcing psycopg2.Error exception")

    # Force the connection to raise an exception
    with pytest.raises(psycopg2.Error) as excinfo:
        insert_jobs_df_to_db(jobs_df)

    print("DEBUG: psycopg2.Error exception raised")

    # Check that the exception message matches the expected error
    assert str(excinfo.value) == "Connection error"
