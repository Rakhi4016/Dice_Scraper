# main.py
import time
from datetime import datetime
import pandas as pd
from driver_manager import restart_driver
from scraper import scrape_job_details
from database import insert_jobs_df_to_snowflake
import boto3
import os
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    ElementClickInterceptedException, TimeoutException, NoSuchElementException, WebDriverException, 
    NoSuchWindowException, InvalidSessionIdException
)

load_dotenv()

def main():
    start_time = time.time()
    
    driver, wait = restart_driver()
    job_search_url = 'https://www.dice.com/jobs'
    driver.get(job_search_url)

    jobs_df = pd.DataFrame(columns=[
        'title', 'location', 'date_posted', 'work_setting', 'work_mode', 
        'job_description', 'position_id', 'company_name', 'company_url', 
        'job_url', 'scraped_date'
    ])

    try:
        today_option = wait.until(EC.presence_of_element_located((By.XPATH, "//button[@data-cy='posted-date-option' and contains(text(), 'Today')]")))
        driver.execute_script("arguments[0].click();", today_option)
        print("Today option clicked directly")
    except Exception as e:
        print(f"Failed to click 'Today' option: {e}")
        driver.quit()
        return

    time.sleep(3) 

    try:
        third_party_option = wait.until(EC.presence_of_element_located((By.XPATH, "//span[@data-cy='facet-group-toggle' and contains(text(), 'Third Party')]//button")))
        driver.execute_script("arguments[0].click();", third_party_option)
        print("Third Party option clicked")
    except Exception as e:
        print(f"Failed to click 'Third Party' option: {e}")
        driver.quit()
        return

    time.sleep(3)  

    try:
        total_jobs_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "span[data-cy='search-count-mobile']")))
        total_jobs = driver.execute_script("return arguments[0].textContent;", total_jobs_element).strip()
        print(f"Total jobs found: {total_jobs}")
        if not total_jobs:
            print("Total jobs element found but text is empty")
            driver.quit()
            return
    except Exception as e:
        print("Unable to find total jobs count:", e)
        driver.quit()
        return

    try:
        while True:
            try:
                job_elements = driver.find_elements(By.XPATH, "//a[@data-cy='card-title-link']")

                for job_element in job_elements:
                    original_window = driver.current_window_handle

                    driver.execute_script("arguments[0].scrollIntoView(true);", job_element)
                    driver.execute_script("arguments[0].click();", job_element)
                    wait.until(EC.number_of_windows_to_be(2))

                    for window_handle in driver.window_handles:
                        if window_handle != original_window:
                            driver.switch_to.window(window_handle)
                            break

                    job_url = driver.current_url
                    time.sleep(1)

                    job_details = scrape_job_details(driver, wait)
                    job_details['job_url'] = job_url
                    job_details['scraped_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    jobs_df = pd.concat([jobs_df, pd.DataFrame([job_details])], ignore_index=True)

                    driver.close()
                    driver.switch_to.window(original_window)
                    time.sleep(1)

                try:
                    next_page_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.pagination-next.page-item.ng-star-inserted a.page-link[rel='nofollow']")))
                    if 'disabled' in next_page_element.get_attribute('class'):
                        break
                    current_url = driver.current_url
                    driver.execute_script("arguments[0].click();", next_page_element)
                    wait.until(EC.url_changes(current_url))
                    time.sleep(2)
                except Exception as e:
                    break
            except (InvalidSessionIdException, WebDriverException) as e:
                print(f"WebDriverException occurred: {e}")
                break
            except Exception as e:
                print(f"An error occurred during scraping: {e}")
                break
    except KeyboardInterrupt:
        print("Process interrupted by user")

    finally:
        # 1) Write local CSV
        current_dt = datetime.now().strftime("%Y-%m-%d")
        csv_filename = f'scraped_jobs_{current_dt}.csv'
        jobs_df.to_csv(csv_filename, index=False)
        print(f"✅ Data saved locally: {csv_filename}")

        # 2) Insert into Snowflake
        insert_jobs_df_to_snowflake(jobs_df)

        # 3) Tear down
        driver.quit()
        elapsed = time.time() - start_time
        print(f"Total time taken: {elapsed:.2f} seconds")

if __name__ == "__main__":
    main()
