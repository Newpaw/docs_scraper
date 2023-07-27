import json
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from typing import List

from models import Page


logging.basicConfig(
    level=logging.INFO,  # Set the logging level to INFO (you can adjust as needed)
    format="%(asctime)s [%(levelname)s]: %(message)s",  # Define the log message format
    handlers=[
        logging.StreamHandler(),  # Log messages will be printed to the console
        logging.FileHandler("scraping.log")  # Log messages will be saved to a file
    ]
)


CHROME_DRIVER_OPTIONS = {
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing_for_trusted_sources_enabled": False,
    "safebrowsing.enabled": False
}


def set_chrome_options() -> Options:
    """
    Set chrome options for selenium webdriver.
    Returns:
        Options: Selenium webdriver options.
    """
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", CHROME_DRIVER_OPTIONS)
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_prefs = {"profile.default_content_settings": {"images": 2}}
    chrome_options.experimental_options["prefs"] = chrome_prefs
    return chrome_options


def setup_webdriver():
    """
    Set up the selenium webdriver.
    Returns:
        webdriver.Chrome: Selenium webdriver instance.
    """
    return webdriver.Chrome(options=set_chrome_options())


def scrape_page(driver: webdriver.Chrome, url: str) -> dict:
    """
    Scrape the content of a given page.
    Args:
        driver (webdriver.Chrome): Selenium webdriver instance.
        url (str): URL of the page to scrape.
    Returns:
        dict: Scraped data.
    """
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

    data = {
        'url': url,
        'h1': [elem.text for elem in driver.find_elements(By.TAG_NAME, 'h1')],
        'h2': [elem.text for elem in driver.find_elements(By.TAG_NAME, 'h2')],
        'h3': [elem.text for elem in driver.find_elements(By.TAG_NAME, 'h3')],
        'h4': [elem.text for elem in driver.find_elements(By.TAG_NAME, 'h4')],
        'h5': [elem.text for elem in driver.find_elements(By.TAG_NAME, 'h5')],
        'text': " ".join(
            [elem.text.strip() for elem in driver.find_elements(By.TAG_NAME, 'span') if elem.text.strip()]
        )
    }

    return data


def get_links(driver: webdriver.Chrome, base_url: str) -> List[str]:
    """
    Get all the links from the page.
    Args:
        driver (webdriver.Chrome): Selenium webdriver instance.
        base_url (str): Base URL for matching links.
    Returns:
        list: List of matched links.
    """
    links = []
    elements = driver.find_elements(By.CSS_SELECTOR, '.css-175oi2r')
    for elem in elements:
        link_elems = elem.find_elements(By.TAG_NAME, 'a')
        for link_elem in link_elems:
            href = link_elem.get_attribute('href')
            if href and href.startswith(base_url):
                links.append(href)
    return links


def scrape_all_pages(driver: webdriver.Chrome, urls_to_visit: list, max_iterations: int = None) -> List[str]:
    """
    Scrape all the pages starting from the base URL.
    Args:
        driver (webdriver.Chrome): Selenium webdriver instance.
        urls_to_visit (list): List of URLs to visit.
        max_iterations (int, optional): Maximum number of pages to scrape. If None, scrape all pages. Defaults to None.
    Returns:
        list: List of scraped data.
    """
    visited_urls = set()
    data = []
    iterations = 0

    total_urls = len(urls_to_visit)

    while urls_to_visit and (max_iterations is None or iterations < max_iterations):
        url = urls_to_visit.pop(0)  # Get the first URL to visit
        if url not in visited_urls:  # If we have not visited it yet
            logging.info(f"Scraping URL {iterations + 1} of {total_urls}: {url}")
            visited_urls.add(url)  # Mark as visited
            data.append(scrape_page(driver, url))  # Scrape data
            # Add the new links to the end of our list
            urls_to_visit.extend(get_links(driver, url))
            iterations += 1  # Increase the counter after each iteration

    return data


def main():
    """
    Main function to execute the web scraping.
    """
    logging.info("Initializing the web scraper...")
    driver = setup_webdriver()  # Initialize Selenium

    base_url = 'https://docs.mluvii.com'
    driver.get(base_url)

    urls_to_visit = get_links(driver, base_url)

    logging.info(f"Starting scraping {len(urls_to_visit)} pages...")

    data = scrape_all_pages(driver, urls_to_visit, 4)

    driver.quit()

    #pages = [
    #    Page(
    #        url=item["url"], 
    #        h1=item["h1"], 
    #        h2=item["h2"], 
    #        h3=item["h3"], 
    #        h4=item["h4"], 
    #        h5=item["h5"], 
    #        text=item["text"]
    #    )
    #    for item in data
    #]
    #for page in pages:
    #    logging.info(page.url)

    with open('scraped_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    logging.info("Scraping completed!")


if __name__ == "__main__":
    main()
