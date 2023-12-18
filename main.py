import requests
from bs4 import BeautifulSoup
import os
import re

NOVEL_URL = input("Input the novel URL: ").strip()
# NOVEL_PATH = input("Input the novel PATH: ").strip()
NOVEL_PATH = "D:\Royal_Road"

ROYAL_URL = "https://www.royalroad.com"
response = requests.get(NOVEL_URL)
soup = BeautifulSoup(response.text, "html.parser")

# for child in soup.descendants:
#     if child.name:
#         print(child.name)

novel_author = soup.h4.find("a").text
novel_desc = soup.find("div", attrs={"class": "description"}).text.strip()
novel_title = soup.title.text
novel_tags = [
    f"**{tag.text}**"
    for tag in soup.find("span", attrs={"class": "tags"}).find_all("a")
]

novel_dir = novel_title.split("|")[0].strip().replace(" ", "_")
novel_path = os.path.join(NOVEL_PATH, novel_dir)
chapters_path = os.path.join(novel_path, "chapters")

try:
    os.mkdir(novel_path)
    os.mkdir(chapters_path)
except OSError as error:
    print("Directory already there")
with open(os.path.join(novel_path, "README.md"), "w", encoding="utf-8") as f:
    f.write(
        f"""# {novel_title}

------------

- Author of the novel: {novel_author}
- [Original link]({NOVEL_URL})
- Tags: {','.join(novel_tags)}

------------
## Description

{novel_desc}

------------
"""
    )


# [{title: chap1, author_note: note1, content: text1, previous_link: link1, next_link: link2}]
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


# test_url = "https://www.royalroad.com/fiction/54476/dungeon-life/chapter/1443328/chapter-two-hundred-eleven"
# test_url2 = "https://www.royalroad.com/fiction/54476/dungeon-life/chapter/909453/chapter-one-a-strange-opportunity"
# test_url3 = "https://www.royalroad.com/fiction/54476/dungeon-life/chapter/1440217/chapter-two-hundred-ten"
# content, is_last = get_chapter_contents(test_url2)

first_chapter_url = soup.find("td").find("a").get("href")
is_last = False
chapter_url = first_chapter_url
chap_links = []
chap_number = 1
prev_link = ""
prev_path = ""

path_regex = '\?|\*|&|"'

# [{title: chap1, author_note: note1, content: text1, previous_link: link1, next_link: link2}]
while not is_last:
    content, is_last = get_chapter_contents(ROYAL_URL + chapter_url)
    temp_chap_file_name = re.sub(path_regex, "", content["title"].replace(" ", "-"))
    chap_file_name = (
        str(chap_number).zfill(3) + "_" + temp_chap_file_name.replace(":", "_")
    )
    chap_number += 1
    chap_links.append((content["title"], chap_file_name))
    with open(
        os.path.join(chapters_path, f"{chap_file_name}.md"), "w", encoding="utf-8"
    ) as f:
        f.write(f"# {content['title']}")
        if "author_note" in content:
            f.write(
                f"""
--------------
## Authors Comment

{content['author_note']}"""
            )
        f.write(
            f"""
--------------

{content['content']}

--------------
"""
        )

        if content["previous_link"]:
            f.write(f"- **[Previous]({prev_link})**\n")
            with open(prev_path, "a", encoding="utf-8") as prev_f:
                prev_f.write(f"- **[Next]({f'{chap_file_name}.md'})**")
        prev_link = f"{chap_file_name}.md"
        prev_path = os.path.join(chapters_path, f"{chap_file_name}.md")
        # if content["next_link"]:
        #     f.write(f'- **[Next]({content["next_link"]})**')

    if not is_last:
        chapter_url = content["next_link"]

print("Chapters done")


with open(os.path.join(novel_path, "README.md"), "a", encoding="utf-8") as f:
    for i in range(len(chap_links)):
        chap_title, chap_link = chap_links[i]
        f.write(f"- **{i + 1}. [{chap_title}](chapters\{chap_link}.md)**\n")

print("README.md complete")
