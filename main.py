import requests
from bs4 import BeautifulSoup

NOVEL_URL = "https://www.royalroad.com/fiction/54476/dungeon-life"

response = requests.get(NOVEL_URL)
soup = BeautifulSoup(response.text, "html.parser")

# for child in soup.descendants:
#     if child.name:
#         print(child.name)
novel_author = soup.h4.find("a").text
novel_desc = soup.find("div", attrs={"class": "description"}).text.strip()
novel_title = soup.title.text
novel_tags = [
    tag.text for tag in soup.find("span", attrs={"class": "tags"}).find_all("a")
]

first_chapter_url = soup.find("td").find("a").get("href")
# print(first_chapter_url)

# [{title: chap1, author_note: note1, content: text1, previous_link: link1, next_link: link2}]
chap_contents = []


# Returns a tuple which has a dict with all the required content in a dict for a chapter, and a check if is the last one
def get_chapter_contents(chap_URL):
    chap_content = {}

    chap_response = requests.get(chap_URL)
    chap_soup = BeautifulSoup(chap_response.text, "html.parser")

    chap_content["title"] = chap_soup.h1.text

    author_note = chap_soup.find("div", attrs={"author-note-portlet"})
    if author_note:
        chap_content["author_note"] = author_note.text.strip()

    chap_content["content"] = chap_soup.find(
        "div", attrs={"class": "chapter-content"}
    ).text.strip()

    nav_buttons = chap_soup.find("div", attrs={"class": "nav-buttons"}).find_all("a")
    if len(nav_buttons) == 1:
        if nav_buttons[0].text.strip() == "Previous Chapter":
            chap_content["previous_link"] = nav_buttons[0].get("href")
            chap_content["next_link"] = False
            return (chap_content, True)
        else:
            chap_content["next_link"] = nav_buttons[0].get("href")
            chap_content["previous_link"] = False
    else:
        chap_content["previous_link"] = nav_buttons[0].get("href")
        chap_content["next_link"] = nav_buttons[1].get("href")

    return (chap_content, False)


test_url = "https://www.royalroad.com/fiction/54476/dungeon-life/chapter/1443328/chapter-two-hundred-eleven"
test_url2 = "https://www.royalroad.com/fiction/54476/dungeon-life/chapter/909453/chapter-one-a-strange-opportunity"
test_url3 = "https://www.royalroad.com/fiction/54476/dungeon-life/chapter/1440217/chapter-two-hundred-ten"

content, is_last = get_chapter_contents(test_url2)
print(content)
