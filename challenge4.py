import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from urllib.parse import urljoin

BASE_URL = "https://www.scrapethissite.com/pages/frames/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; learning-scraper/1.0)"
}

def get_soup(BASE_URL):
    response=requests.get(
        BASE_URL,
        headers=HEADERS,
        timeout=10
    )
    response.raise_for_status()

    return BeautifulSoup(response.content,"html.parser")

def get_turtle_data():

    # Step 1: Get the parent page
    parent_soup = get_soup(BASE_URL)

    # Step 2: Find the iframe
    iframe = parent_soup.find("iframe")

    if iframe is None:
        raise ValueError("Iframe not found")

    # Step 3: Get iframe content
    iframe_url = urljoin(BASE_URL, iframe.get("src", ""))
    iframe_soup = get_soup(iframe_url)

    turtles = []

    # Step 4: Find turtle family cards
    for family in iframe_soup.select(".col-md-4"):

        family_name_tag = family.select_one(".family-name")
        detail_link = family.select_one("a[href]")

        if family_name_tag is None or detail_link is None:
            continue

        family_name = family_name_tag.get_text(strip=True)

        detail_url = urljoin(
            iframe_url,
            detail_link.get("href")
        )

        # Step 5: Visit the detail page
        detail_soup = get_soup(detail_url)

        description_tag = detail_soup.select_one("p.lead")
        common_name_tag = detail_soup.select_one(".common-name")

        description = (
            description_tag.get_text(" ", strip=True)
            if description_tag else ""
        )

        common_name = (
            common_name_tag.get_text(strip=True)
            if common_name_tag else ""
        )

        # Step 6: Extract year and discoverer
        match = re.search(
            r"first discovered in (\d{4}) by ([^.]+)",
            description,
            re.IGNORECASE
        )

        year = int(match.group(1)) if match else None
        discoverer = match.group(2).strip() if match else None

        # Step 7: Store the data
        turtles.append({
            "family_name": family_name,
            "common_name": common_name,
            "year_discovered": year,
            "discoverer": discoverer
        })

    return turtles


def main():

    turtles = get_turtle_data()

    # Step 8: Convert to DataFrame
    df = pd.DataFrame(turtles)

    print(df.head())

    print("\nTotal records:", len(df))

    # Step 9: Export to CSV
    df.to_csv("turtle_data.csv", index=False)

    print("\nData saved to turtle_data.csv")


if __name__ == "__main__":
    main()