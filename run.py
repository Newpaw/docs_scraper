import logging
import pdfkit
import time
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

from typing import List


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s",
)


CHROME_DRIVER_OPTIONS = {
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing_for_trusted_sources_enabled": False,
    "safebrowsing.enabled": False,
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


def setup_webdriver(base_url: str) -> webdriver.Chrome:
    """
    Set up the selenium webdriver.
    Returns:
        webdriver.Chrome: Selenium webdriver instance.
    """
    logging.info(f"Initializing and setup the web scraper for base url: {base_url}")
    driver = webdriver.Chrome(options=set_chrome_options())
    driver.get(base_url)
    return driver


def get_links(driver: webdriver.Chrome, base_url: str, limit: int = None) -> List[str]:
    """
    Gather all unique links from a website that meet certain conditions.
    
    This function uses a Selenium WebDriver instance to navigate a website and collect
    unique links. It first collects links from all 'nav' elements on the base_url page.
    Then, it navigates to each of these links and gathers further links.
    The function can be limited to a certain number of links.
    Logs the number of links found every 15 seconds.
    
    Parameters
    ----------
    driver : webdriver.Chrome
        A Selenium WebDriver instance.
    base_url : str
        The URL of the page from where to start gathering links.
    limit : int, optional
        The maximum number of links to gather. If None, gather all links (default is None).

    Returns
    -------
    List[str]
        A list of unique URLs gathered from the website.

    Raises
    ------
    Exception
        If there's an error navigating to a URL, an error message is logged and the
        exception is raised.
    """
    logging.info("Getting links...")
    links = set()
    nav_elements = driver.find_elements(By.TAG_NAME, "nav")

    primary_hrefs = []
    start_time = time.time()
    for nav_elem in nav_elements:
        link_elems = nav_elem.find_elements(By.TAG_NAME, "a")
        for link_elem in link_elems:
            href = link_elem.get_attribute("href")
            if href and href.startswith(base_url) and "#" not in href:
                primary_hrefs.append(href)
                if limit is not None and len(primary_hrefs) >= limit:
                    break
            # Log the number of links every 15 seconds
            if time.time() - start_time > 15:
                logging.info(f"Found {len(links)} links so far.")
                start_time = time.time()
        if limit is not None and len(primary_hrefs) >= limit:
            break

    for href in primary_hrefs:
        links.add(href)
        if limit is not None and len(links) >= limit:
            break
        try:
            driver.get(href)
            further_elements = driver.find_elements(By.TAG_NAME, "a")
            for further_elem in further_elements:
                further_href = further_elem.get_attribute("href")
                if (
                    further_href
                    and further_href.startswith(base_url)
                    and "#" not in further_href
                ):
                    links.add(further_href)
                    if limit is not None and len(links) >= limit:
                        break
            # Log the number of links every 15 seconds
            if time.time() - start_time > 15:
                logging.info(f"Found {len(links)} links so far.")
                start_time = time.time()
            if limit is not None and len(links) < limit:
                driver.back()
        except Exception as e:
            logging.error(f"Error navigating to {href}: {e}")
    logging.info(f"Found {len(links)} links.")

    return list(links)[:limit] if limit is not None else list(links)


def scrape_page(driver: webdriver.Chrome, url: str) -> dict:
    logging.debug(f"Scraping URL: {url}")
    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    main_content = driver.find_element(By.TAG_NAME, "main")
    data = {"url": url, "content": main_content.text}
    logging.debug(f"Scraped content for URL: {url}")
    return data


def create_pdf(data: List[dict]) -> str:
    """
    Creates a PDF document from the given data. The PDF file is named using
    the current timestamp to ensure uniqueness.

    Parameters
    ----------
    data : List[dict]
        List of dictionaries containing URL and content.

    Returns
    -------
    str
        The absolute path of the created PDF document.
    """
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    unique_file_name = f"scraped_data_{timestamp}.pdf"
    
    html_data = '<html><head><meta charset="UTF-8"></head><body>'
    for item in data:
        html_data += "<h1>URL: {}</h1>".format(item["url"])
        html_data += "<p>{}</p>".format(item["content"].replace("\n", "<br>"))
    html_data += "</body></html>"

    output_path = os.path.join(os.getcwd(), unique_file_name)
    pdfkit.from_string(html_data, output_path)

    logging.info(f"PDF file created at {output_path}.")

    return output_path


def main():
    base_url:url = "https://portainer.gitbook.io/"
    limit_of_pages:int = 2

    driver = setup_webdriver(base_url)
    urls_to_visit = get_links(driver, base_url, limit=limit_of_pages)

    data = []
    number_of_pages = len(urls_to_visit)
    
    for i, url in enumerate(urls_to_visit):
        data.append(scrape_page(driver, url))
        logging.info(f"Scraped {i+1} from {number_of_pages} pages.")

    driver.quit()
    create_pdf(data)


if __name__ == "__main__":
    main()
