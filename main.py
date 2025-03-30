import requests
from bs4 import BeautifulSoup
import os
import re
import time

import utils._global as _global
from utils.scraping_and_file_creation_funcs import (
    get_chapter_contents,
    loop_through_chapters,
    write_readme,
    create_dir_and_readme,
)
from utils.create_epub import create_epub


def main():
    # user_inp = input("Start scraping? (y/n): ")
    user_inp = "y"
    if user_inp.lower() == "y":

        NOVEL_URL = input("Input the novel URL: ").strip()
        # NOVEL_PATH = input("Input the novel PATH: ").strip()
        response = requests.get(NOVEL_URL)
        soup = BeautifulSoup(response.text, "html.parser")

        novel_author = soup.h4.find("a").text
        novel_desc = soup.find("div", attrs={"class": "description"}).text.strip()
        try:
            novel_title = soup.title.text
        except AttributeError as e:
            novel_title = NOVEL_URL.split("/")[-1]
        novel_tags = [
            f"**{tag.text}**"
            for tag in soup.find("span", attrs={"class": "tags"}).find_all("a")
        ]

        novel_dir = novel_title.split("|")[0].strip().replace(" ", "_")
        novel_path = os.path.join(_global.NOVEL_PATH, novel_dir)
        chapters_path = os.path.join(novel_path, "chapters")

        create_dir_and_readme(
            NOVEL_URL,
            novel_path,
            chapters_path,
            {
                "author": novel_author,
                "title": novel_title,
                "tags": novel_tags,
                "desc": novel_desc,
                "url": NOVEL_URL,
            },
        )
        chap_links = loop_through_chapters(soup, chapters_path)
        write_readme(novel_path, chap_links)

    else:
        novel_path = input("Give path to the dir where the files are: ")
        # novel_path = r"O:\Books\Royal_Road\Syl_[A_Slime_Monster_Evolution_LitRPG]"
        # novel_path = r"O:\Books\Royal_Road\Syl_[Book_2_STUBBING_April_6th]"
        # novel_path = r"O:\Books\Royal_Road\Immovable_Mage"
        # novel_path = r"O:\Books\Royal_Road\The_Runic_Artist"
        chapters_path = os.path.join(novel_path, "chapters")

    create_epub(novel_path, chapters_path)


if __name__ == "__main__":
    start = time.time()
    main()
    print(f"{round(start - time.time(), 2)} seconds.")
