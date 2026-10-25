
import csv
import json
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


BASE_URL = "https://ranveerbrar.com/"
RECIPES_URL = urljoin(BASE_URL, "recipes/")


def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")

    return webdriver.Chrome(options=options)


def load_page(driver, url):
    driver.get(url)

    WebDriverWait(driver, 15).until(
        lambda d: d.execute_script(
            "return document.readyState"
        ) == "complete"
    )

    return BeautifulSoup(driver.page_source, "lxml")


def scroll_page(driver, max_scrolls=8):
    """Scroll incrementally to reveal lazy-loaded content."""
    previous_height = 0

    for _ in range(max_scrolls):
        current_height = driver.execute_script(
            "return document.body.scrollHeight"
        )

        if current_height == previous_height:
            break

        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight)"
        )

        previous_height = current_height

        # Wait briefly for the page to update.
        driver.implicitly_wait(1)


def clean_text(element):
    if element is None:
        return ""

    return element.get_text(" ", strip=True)


def extract_recipe_list(soup, page_url):
    results = []
    seen_urls = set()

    # Look at headings and their nearest parent link.
    for heading in soup.select("h2, h3, h4"):
        link = heading.find_parent("a", href=True)

        if link is None:
            continue

        recipe_url = urljoin(page_url, link["href"])
        parsed = urlparse(recipe_url)

        # Keep links on the target website only.
        if parsed.netloc not in {
            "ranveerbrar.com",
            "www.ranveerbrar.com"
        }:
            continue

        title = clean_text(heading)

        if not title or recipe_url in seen_urls:
            continue

        seen_urls.add(recipe_url)

        image = link.find("img")

        image_url = ""
        image_alt = ""

        if image:
            image_url = (
                image.get("data-src")
                or image.get("data-lazy-src")
                or image.get("src")
                or ""
            )

            image_url = urljoin(page_url, image_url)
            image_alt = image.get("alt", "")

        results.append({
            "title": title,
            "url": recipe_url,
            "image_url": image_url,
            "image_alt": image_alt
        })

    return results


def save_csv(data, filename):
    if not data:
        print(f"No data to save to {filename}")
        return

    with open(filename, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=data[0].keys()
        )

        writer.writeheader()
        writer.writerows(data)


def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=4
        )


def main():
    driver = create_driver()

    try:
        # Load first, then scroll, then parse updated HTML.
        load_page(driver, RECIPES_URL)
        scroll_page(driver)

        soup = BeautifulSoup(
            driver.page_source,
            "lxml"
        )

        recipes = extract_recipe_list(
            soup,
            driver.current_url
        )

        print("Recipes extracted:", len(recipes))

        for recipe in recipes[:10]:
            print(recipe)

        save_csv(recipes, "recipes.csv")
        save_json(recipes, "recipes.json")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
