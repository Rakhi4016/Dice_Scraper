# Job Scraper

This project is a job scraper that collects all third party job details from Dice.com and stores as a dataframe >>CSV file and then loaded into Snowflake database and the upload the csv to S3. The scraper uses Selenium for web scraping and the snowflake connector library for database operations.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Environment Variables](#environment-variables)
- [Modules](#modules)

## Installation

1. Clone the repository
   git clone <repository-url>
   cd repository-directory

2. Create a virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows use venv\Scripts\activate

3. Install the required packages
   pip install -r requirements.txt

4. Set up the environment variables
   Create a .env file in the root directory of the project and add the following lines, replacing the placeholder values with your actual database credentials:

   SF_USER=username
   SF_PASSWORD=your password
   SF_ACCOUNT=your account 
   SF_WAREHOUSE=your warehouse
   SF_ROLE=your role

5. Download the ChromeDriver
   Make sure you have the ChromeDriver installed and it's in your system's PATH.

## Usage

To run the job scraper, use the following command:

python main.py

## Project Structure

.
├── .env                # Environment variables
├── database.py         # Database operations
├── main.py             # Main script
├── scraper.py          # Web scraping functions
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation

## Environment Variables

The project requires a .env file in the root directory with the following variables:
* SF_USER: Snowflake username
* SF_PASSWORD: Snowflake password
* SF_ACCOUNT: Snowflake account number
* SF_WAREHOUSE: Snowflake virtual warehouse
* SF_ROLE: Snowflake role name

## Modules

database.py
Contains functions for database operations:
* snowflake.connector: Establishes a connection to the Snowflake database.
* insert_jobs_df_to_snowflake(jobs_df): Inserts job details into the job_details table.

scraper.py
Contains functions for web scraping:
* restart_driver(): Initializes the Selenium WebDriver.
* scrape_job_details(driver, wait): Scrapes job details from the job listing page.

main.py
Main script that orchestrates the scraping and database operations.


   

# CI/CD Pipeline
This project uses a GitHub Actions workflow named "CI Pipeline for Scraping Job" to automate the end-to-end scraping process. The workflow is triggered on:
Pushes to the main, dev, or any feature/** branch

Manual runs using workflow_dispatch

A daily scheduled run at 23:00 UTC (7:00 PM Eastern Time)

# Workflow Summary
The pipeline performs the following steps:

# Checkout Code
Clones the repository to the GitHub runner.

# Set up Python Environment
Installs Python 3.12 and necessary dependencies listed in requirements.txt.

# Install Chrome
Installs Google Chrome for use with Selenium.

# Test Snowflake Connection
Verifies the Snowflake connection using environment secrets.

# Run Scraper
Executes main.py, which scrapes job details and saves them to a CSV file and Snowflake.

# Tag Output File with Date
Adds a timestamp to the filename for versioning.

# Upload to Databricks Workspace
Uploads the resulting CSV to the Databricks workspace for further processing.

# Upload to AWS S3
Transfers the CSV file to an S3 bucket (s3://my-dice-scraper/input/).

# Environment Variables
Secrets used in the pipeline are securely stored in GitHub Actions Secrets:

SF_USER, SF_PASSWORD, SF_ACCOUNT, SF_WAREHOUSE, SF_ROLE: Snowflake credentials

DATABRICKS_HOST, DATABRICKS_TOKEN: Databricks access credentials

AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION: AWS credentials for S3 access

