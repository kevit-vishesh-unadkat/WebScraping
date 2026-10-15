import requests
import pandas as pd



BASE_URL = "https://www.scrapethissite.com/pages/ajax-javascript/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; learning-scraper/1.0)",
    "X-Requested-With": "XMLHttpRequest"
}

def get_films(year):
    """Fetch all films data for a specific year"""
    params={
        "ajax":"true",
        "year":year
    }

    response=requests.get(BASE_URL,params=params,headers=HEADERS,timeout=10)

    response.raise_for_status()

    return response.json()


def main():
    all_films = []

    for year in range(2010, 2016):
        films = get_films(year)

        for film in films:
            all_films.append(film)

        print(f"Year {year}: {len(films)} films scraped")

    df = pd.DataFrame(all_films)

    print("\nFirst 5 records:")
    print(df.head())

    print("\nTotal records:", len(df))

    df.to_csv("oscar_films.csv", index=False)

    print("\nData saved to oscar_films.csv")


if __name__ == "__main__":
    main()