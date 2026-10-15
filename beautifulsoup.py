import requests
import pandas as pd
import json

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser


# -----------------------------------
# 1. Website configuration
# -----------------------------------

BASE_URL = "https://ranveerbrar.com/"
HEADERS = {
    "User-Agent": "RecipeLearningProject/1.0"
}


# -----------------------------------
# 2. Check website crawling rules
# -----------------------------------

robots_url = urljoin(BASE_URL, "robots.txt")

try:
    response = requests.get(
        robots_url,
        headers=HEADERS,
        timeout=15
    )
    response.raise_for_status()

    robots = RobotFileParser()
    robots.set_url(robots_url)
    robots.parse(response.text.splitlines())

except requests.RequestException:
    print("Could not check robots.txt. Stopping safely.")
    raise SystemExit


# -----------------------------------
# 3. Download the homepage
# -----------------------------------

if not robots.can_fetch(HEADERS["User-Agent"], BASE_URL):
    print("The website's rules do not allow scraping the homepage.")
    raise SystemExit

try:
    response = requests.get(
        BASE_URL,
        headers=HEADERS,
        timeout=15
    )
    response.raise_for_status()

except requests.RequestException as error:
    print("Could not download the website:", error)
    raise SystemExit

soup = BeautifulSoup(response.text, "html.parser")

print("Website downloaded successfully!")


# -----------------------------------
# 4. Find recipe page links
# -----------------------------------

recipe_urls = set()

for link in soup.find_all("a", href=True):

    url = urljoin(BASE_URL, link["href"])

    # Only consider links from this website
    if urlparse(url).netloc != urlparse(BASE_URL).netloc:
        continue

    # Look for common recipe URL patterns
    path = urlparse(url).path.lower()

    if "/recipe/" in path or "/recipes/" in path:

        # Check whether crawling this URL is allowed
        if robots.can_fetch(HEADERS["User-Agent"], url):
            recipe_urls.add(url)

recipe_urls = list(recipe_urls)[:5]

print("Recipe links found:", len(recipe_urls))


# -----------------------------------
# 5. Extract information from recipes
# -----------------------------------

recipes = []

for url in recipe_urls:

    print("Scraping:", url)

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=15
        )
        response.raise_for_status()

    except requests.RequestException as error:
        print("Skipping page:", error)
        continue

    soup = BeautifulSoup(response.text, "html.parser")

    # Default values
    recipe_name = ""
    description = ""
    ingredients = []
    image_url = ""

    # Find structured recipe data
    for script in soup.find_all(
        "script",
        type="application/ld+json"
    ):

        try:
            data = json.loads(script.string or script.get_text())

        except (json.JSONDecodeError, TypeError):
            continue

        # JSON-LD can contain a list or an @graph
        if isinstance(data, dict):
            data = data.get("@graph", [data])

        if isinstance(data, dict):
            data = [data]

        if not isinstance(data, list):
            continue

        for item in data:

            if not isinstance(item, dict):
                continue

            recipe_type = item.get("@type", [])

            if isinstance(recipe_type, str):
                recipe_type = [recipe_type]

            if "Recipe" not in recipe_type:
                continue

            recipe_name = item.get("name", "")
            description = item.get("description", "")

            ingredients = item.get("recipeIngredient", [])

            image = item.get("image", "")

            if isinstance(image, dict):
                image_url = image.get("url", "")

            elif isinstance(image, list):
                if image and isinstance(image[0], dict):
                    image_url = image[0].get("url", "")
                elif image:
                    image_url = str(image[0])

            else:
                image_url = image

            break

        if recipe_name:
            break

    # Fallback: try extracting the page title
    if not recipe_name:
        title = soup.find("h1")

        if title:
            recipe_name = title.get_text(
                " ",
                strip=True
            )

    # Fallback: try the page description
    if not description:
        meta = soup.find(
            "meta",
            attrs={"name": "description"}
        )

        if meta:
            description = meta.get("content", "")

    # Make relative image URLs absolute
    if image_url:
        image_url = urljoin(url, image_url)

    # Save the extracted recipe
    if recipe_name:

        recipes.append({
            "Recipe Name": recipe_name,
            "Description": description,
            "Ingredients": " | ".join(ingredients)
                if isinstance(ingredients, list)
                else ingredients,
            "Recipe URL": url,
            "Image URL": image_url
        })


# -----------------------------------
# 6. Convert data into a Pandas table
# -----------------------------------

df = pd.DataFrame(recipes)

print("\nRecipe Data:")
print(df)


# -----------------------------------
# 7. Save the data to CSV
# -----------------------------------

if not df.empty:

    df.to_csv(
        "recipes.csv",
        index=False,
        encoding="utf-8-sig"
    )

    print("\nData saved to recipes.csv")

else:
    print("\nNo recipes were extracted.")
    print("The website may use different URL patterns.")
    print("Check the page structure and crawling rules.")