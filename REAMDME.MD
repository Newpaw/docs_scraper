# Web Scraper to PDF
This is a Python application designed to scrape the content of webpages and compile it into a PDF document. The program is built using Selenium for web scraping and pdfkit for generating PDFs.

# Features
Web scraping: The application navigates a website and collects unique links, then scrapes the main content of each of these pages.
PDF generation: The application then compiles the scraped content into a PDF document, with each webpage's content being neatly organized. Each PDF is named with a unique identifier to avoid overwriting.
Customizable: You can customize the base URL and the maximum number of pages to be scraped.

# Requirements
Python 3.x
Selenium
pdfkit
Chrome WebDriver
Installation and Usage
Clone this repository.
bash
Copy code
git clone https://github.com/user/repo.git

# Install the required Python packages.
bash
Copy code
pip install -r requirements.txt
Download the Chrome WebDriver from here and add it to your system's PATH.
Run the program with optional arguments.
bash
Copy code
python main.py --base_url "https://www.example.com" --limit_of_pages 5
This will start the web scraper on "https://www.example.com" and limit it to scrape a maximum of 5 pages.

# Contributing
If you want to contribute to this project, please submit a pull request. We appreciate any help!

# License
This project is licensed under the MIT License. See the LICENSE file for details.

# Contact
If you encounter any issues or have questions, please open an issue on this repository.

Please note: This scraper is intended for educational purposes and should be used responsibly and in accordance with each website's terms of service.