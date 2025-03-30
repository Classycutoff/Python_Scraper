import requests
from bs4 import BeautifulSoup
import os
import re
import time

import utils._global as _global


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
    else:
        chap_content["author_note"] = ""

    chap_content["content"] = chap_soup.find(
        "div", attrs={"class": "chapter-content"}
    ).text.strip()

    # print(chap_content)

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


def loop_through_chapters(soup, chapters_path):
    first_chapter_url = soup.find("td").find("a").get("href")
    is_last = False
    chapter_url = first_chapter_url
    chap_links = []
    chap_number = 1
    prev_link = ""
    prev_path = ""

    path_regex = r'\?|\*|&|"'

    print_count = 0

    # [{title: chap1, author_note: note1, content: text1, previous_link: link1, next_link: link2}]
    while not is_last:
        content, is_last = get_chapter_contents(_global.ROYAL_URL + chapter_url)
        time.sleep(0.03)
        temp_chap_file_name = re.sub(path_regex, "", content["title"].replace(" ", "-"))
        chap_file_name = temp_chap_file_name.replace(":", "_")
        chap_number += 1
        chap_links.append((content["title"], chap_file_name))
        file_path = os.path.join(chapters_path, f"{chap_file_name}.md")
        file_path = file_path.replace("/", "")
        with open(file_path, "w+", encoding="utf-8") as f:

            f.write(
                f"""# {content['title']}
--------------
## Authors Comment

{content['author_note']}
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
            prev_path = file_path
            # if content["next_link"]:
            #     f.write(f'- **[Next]({content["next_link"]})**')

        if not is_last:
            chapter_url = content["next_link"]
            print_count += 1
            if print_count % 10 == 0:
                print(f"{print_count} file: {file_path}")

    print("Chapters done")

    return chap_links


def write_readme(novel_path, chap_links):
    readme_regex = r"- \*\*(\d+)\. \[(.*)\]\(.*\)\*\*"
    with open(os.path.join(novel_path, "README.md"), "r", encoding="utf-8") as f:
        readme_str = f.read()

    found_all = re.findall(readme_regex, readme_str)
    if found_all:
        index, chapter_names = zip(*found_all)
    else:
        index = 0
        chapter_names = []
    biggest_ind = 1

    with open(os.path.join(novel_path, "README.md"), "a", encoding="utf-8") as f:
        for i in range(len(chap_links)):
            chap_title, chap_link = chap_links[i]
            if chap_title in chapter_names:
                chap_name_index = chapter_names.index(chap_title)
                biggest_ind = int(index[chap_name_index]) + 1
                continue
            f.write(f"- **{biggest_ind}. [{chap_title}](chapters\{chap_link}.md)**\n")
            biggest_ind += 1

    print("README.md complete")


def create_dir_and_readme(NOVEL_URL, novel_path, chapters_path, novel_dict):
    try:
        os.mkdir(novel_path)
        os.mkdir(chapters_path)
    except OSError as error:
        print("Directory already there")

    if not os.path.isfile(os.path.join(novel_path, "README.md")):

        with open(os.path.join(novel_path, "README.md"), "w", encoding="utf-8") as f:
            f.write(
                f"""# {novel_dict['title']}

------------

- Author of the novel: {novel_dict['author']}
- [Original link]({novel_dict['url']})
- Tags: {','.join(novel_dict['tags'])}

------------
## Description

{novel_dict['desc']}

------------
"""
            )
