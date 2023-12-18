import requests
from bs4 import BeautifulSoup

NOVEL_URL = "https://www.royalroad.com/fiction/54476/dungeon-life"

response = requests.get(NOVEL_URL)
soup = BeautifulSoup(response.text, "html.parser")

# for child in soup.descendants:
#     if child.name:
#         print(child.name)

novel_desc = soup.find("div", attrs={"class": "description"}).text.strip()
novel_title = soup.title.text
print(novel_title)

first_chapter = soup.find("td").find("a").get("href")
