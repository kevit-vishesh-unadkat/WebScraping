# import bs4
#
# print(bs4.__version__)

from bs4 import BeautifulSoup

html = """
<html>
    <body>
        <h1>Hello World</h1>
        <p>Learning Beautiful Soup</p>
    </body>
</html>
"""

soup = BeautifulSoup(html,'html.parser')
# html parser tells BeautifulSoup witch parser to use.
print(soup.prettify())