import requests
import pandas as pd

from bs4 import BeautifulSoup


BASE_URL = "https://www.scrapethissite.com/pages/forms/"

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

# this function is use to extract the all hockey team
def extract_teams(soup):
    """Extract hockey team records from one page."""

    teams = []

    for row in soup.select("tr.team"):

        teams.append({
            "team_name": row.select_one("td.name").get_text(strip=True),
            "year": row.select_one("td.year").get_text(strip=True),
            "wins": row.select_one("td.wins").get_text(strip=True),
            "losses": row.select_one("td.losses").get_text(strip=True),
            "ot_losses": row.select_one("td.ot-losses").get_text(strip=True),
            "win_percentage": row.select_one("td.pct").get_text(strip=True),
            "goals_for": row.select_one("td.gf").get_text(strip=True),
            "goals_against": row.select_one("td.ga").get_text(strip=True),
            "goal_difference": row.select_one("td.diff").get_text(strip=True)
        })

    return teams

# this function is for to calculate a total pages in hocky link .
def get_total_pages(soup):
    """Find the highest numbered page in the pagination links."""

    page_numbers = []

    for link in soup.select(".pagination a"):

        href = link.get("href", "")

        if "page_num=" in href:

            try:
                page_number = int(href.split("page_num=")[1].split("&")[0])
                page_numbers.append(page_number)

            except ValueError:
                continue

    return max(page_numbers, default=1)


def scrape_hockey_teams():
    """Scrape all available numbered pages."""

    first_page = get_soup(BASE_URL)

    total_pages = get_total_pages(first_page)

    all_teams = extract_teams(first_page)

    print(f"Page 1: scraped {len(all_teams)} records")

    for page in range(2, total_pages + 1):

        soup = get_soup(
            BASE_URL,
            params={"page_num": page, "per_page": 25}
        )

        teams = extract_teams(soup)

        if not teams:
            print(f"No records found on page {page}. Stopping.")
            break

        all_teams.extend(teams)

        print(f"Page {page}: scraped {len(teams)} records")

    return all_teams


def main():

    try:
        teams = scrape_hockey_teams()

        if not teams:
            print("No team records were found.")
            return

        df = pd.DataFrame(teams)

        numeric_columns = [
            "year",
            "wins",
            "losses",
            "ot_losses",
            "win_percentage",
            "goals_for",
            "goals_against",
            "goal_difference"
        ]

        df[numeric_columns] = df[numeric_columns].apply(
            pd.to_numeric,
            errors="coerce"
        )

        df.to_csv("hockey_teams.csv", index=False)

        print("\nScraping completed!")
        print("Total records:", len(df))
        print("DataFrame shape:", df.shape)

        print("\nFirst five records:")
        print(df.head())

        print("\nTop 5 records by wins:")
        print(
            df.nlargest(5, "wins")[
                ["team_name", "year", "wins"]
            ]
        )

        print("\nSaved to hockey_teams.csv")

    except requests.RequestException as error:
        print("Network or HTTP error:", error)


if __name__ == "__main__":
    main()