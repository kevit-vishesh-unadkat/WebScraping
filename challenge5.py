import requests
from bs4 import BeautifulSoup
import pandas as pd

BASE_URL = "https://www.scrapethissite.com/pages/advanced/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; learning-scraper/1.0)"
}

def get_soup(url, params=None):
    """Download a webpage and return its parsed HTML."""

    response = requests.get(
        url,
        params=params,
        headers=HEADERS,
        timeout=15
    )

    response.raise_for_status()

    return BeautifulSoup(response.text, "html.parser")

def get_text(soup):
    """this function is extract all the paragraph text"""

    paragraphs=soup.find_all("p")

    for paragraph in paragraphs:
        return paragraph.text

def get_heading(soup):
    """this function is to extract all the heading text"""

    headings=[]

    for heading in soup.find_all("h4"):
        headings.append(heading.text)

    return headings

def main_heading(soup):
    main_heading=soup.select("h3")

    return main_heading


def main():
    soup = get_soup(BASE_URL)

    print(soup.prettify())

    description = get_text(soup)
    print(description)

    headings=get_heading(soup)
    print(headings)

    main_headings=main_heading(soup)
    print(main_headings)

if __name__ == "__main__":
    main()