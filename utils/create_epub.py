import re
import os

from ebooklib import epub
from markdown import markdown
from typing import Tuple, Dict


replaced_chars = {"â€“": "–", "â€™": "’", "/": ""}


def get_chapters_data(novel_path, readme_data):
    CHAPTER_REGEX = r"- \*\*(\d*)\. \[(.*)]\((.*)\)\*\*"

    chapter_matches = re.findall(CHAPTER_REGEX, readme_data)
    chapter_info_lst = []
    # print(chapter_info_list)
    for chapter_info in chapter_matches:
        path = chapter_info[2]

        for replaceable_str, replaced_str in replaced_chars.items():
            path = path.replace(replaceable_str, replaced_str)
        # print(chapter_info)
        with open(
            os.path.join(novel_path, path),
            "r",
            encoding="utf-8",
            errors="ignore",
        ) as f:  # Specify 'utf-8' and handle errors
            content = f.read()

        chapter_info_lst.append(
            {
                "chap_num": chapter_info[0],
                "chap_title": chapter_info[1],
                "content": content,
            }
        )

    return chapter_info_lst


def get_author_info_and_chapter_list(readme_data) -> Tuple[Dict]:
    AUTHOR_INFO_REGEX = r"\# (.*) \|.*\n*-*\n*- .*: (.*)\n- (.*)\n.*\n*-*\n\#\# Description\n([–\-\n# a-zA-Z0-9; '’:!”/+.&,(?)_â\"*€“Â]*)------------\n"

    print(readme_data)
    matches = re.findall(AUTHOR_INFO_REGEX, readme_data)[0]
    author_info = {
        "title": matches[0],
        "author": matches[1],
        "desc": matches[3].strip() + f"\n\n{matches[2]}",
    }
    # print(author_info)

    return author_info


def create_epub(novel_path, chapters_path):
    readme_path = os.path.join(novel_path, "README.md")
    with open(readme_path, "r", encoding="utf-8", errors="ignore") as f:
        data = f.read()
    author_info = get_author_info_and_chapter_list(data)
    chapter_info_list = get_chapters_data(novel_path, data)

    book = epub.EpubBook()
    book.set_title(author_info["title"])
    book.add_author(author_info["author"])
    book.set_language("en")
    # Set description under metadata
    book.add_metadata("DC", "description", author_info["desc"])

    book.spine = ["nav"]
    chapter_files = []
    toc = []

    for chapter_info in chapter_info_list:
        # print(chapter_info)
        file_name = f"chapter_{chapter_info['chap_num']}.xhtml"
        chapter_file = epub.EpubHtml(
            title=chapter_info["chap_title"], file_name=file_name, lang="en"
        )
        # print(chapter_file)
        chapter_content = chapter_info["content"]
        if chapter_content.startswith("##"):
            chapter_content = chapter_content[1:]

        split_chapter = chapter_content.split("--------------")[1:3]
        # chapter_content.replace("\n", "<br />")
        # content = markdown(chapter_content)
        # print(content)

        replaced_content = re.sub(
            "\n", "<br><br>", "--------------".join(split_chapter)
        )
        chapter_file.content = f"<h1>{chapter_info['chap_num']}. {chapter_info['chap_title']}</h1><p>{replaced_content}</p>"
        print(chapter_file)

        book.add_item(chapter_file)
        book.spine.append(chapter_file)
        chapter_files.append(chapter_file)

        toc.append(
            epub.Link(file_name, chapter_info["chap_title"], chapter_info["chap_num"])
        )

    book.toc = tuple(toc)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    epub.write_epub(os.path.join(novel_path, author_info["title"] + ".epub"), book)
