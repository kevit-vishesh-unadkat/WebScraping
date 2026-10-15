import requests
from bs4 import BeautifulSoup
import re
import pandas as pd


BASE_URL = "https://www.scrapethissite.com/pages/simple/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; learning-scraper/1.0)"
}


# this function is for to get url and return it to parsed HTML content
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

# print(get_soup(BASE_URL))

def get_country(soup):
    """this function is to get all the countries witch are availble"""

    country_name=[]

    for country in soup.select(".country-name"):
        country_name.append(country.text.strip())

    return country_name

def get_capital_information(soup):
    """this function is to get all the countries capital """
    capital_list=[]

    for capital in soup.select(".country-capital"):
        capital_list.append(capital.text.strip())

    return capital_list

def get_population(soup):

    populations=[]

    for population in soup.select(".population"):
        populations.append(population.text.strip())

    return populations

def main():
    soup=get_soup(BASE_URL)
    country=get_country(soup)
    print(country)

    capital=get_capital_information(soup)
    print(capital)

    print(get_population(soup))
if __name__ == "__main__":
    main()