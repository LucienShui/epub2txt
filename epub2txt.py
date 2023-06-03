import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import bs4
from typing import List


def is_blank(text: str) -> bool:
    if text is None:
        return True
    if text.strip() == "":
        return True
    return False


class Paragraph:
    def __init__(self, text: str, tag: str):
        self.text = text
        self.tag = tag

    def __len__(self):
        return len(self.text)

    def __str__(self):
        if 'h' in self.tag:
            level = int(self.tag.replace('h', ''))
            return f"{'#' * level} {self.text}"
        return self.text


class Chapter:
    def __init__(self, paragraph_list: List[Paragraph] = None):
        self.paragraph_list = paragraph_list or []

    def __len__(self):
        return sum(map(len, self.paragraph_list))

    def __str__(self):
        return '\n'.join(map(str, self.paragraph_list))

    def __bool__(self):
        return len(self.paragraph_list) > 0 and self.__len__() > 0


def epub2text(epub_path: str) -> str:
    book = epub.read_epub(epub_path, options={'ignore_ncx': True})
    guide_href_list = [each['href'] for each in book.guide]  # exclude toc and so on

    items: List[epub.EpubHtml] = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
    tag_filter = ['p'] + [f'h{i}' for i in range(1, 6)]  # fetch paragraph and header only

    chapter_list: List[Chapter] = []

    for item in items:
        if item.file_name in guide_href_list:
            continue
        soup = BeautifulSoup(item.get_body_content(), 'lxml')
        tag_list: List[bs4.element.Tag] = list(soup.find_all(tag_filter))
        chapter: Chapter = Chapter([
            Paragraph(tag.get_text(strip=True), tag.name)
            for tag in tag_list
            if not is_blank(tag.get_text()) and 'img' not in tag.attrs.get('class', [])
        ])
        if chapter:
            chapter_list.append(chapter)

    avg_chapter_length = sum(map(len, chapter_list)) / len(chapter_list)
    filtered_chapter_list = [chapter for chapter in chapter_list if len(chapter) >= avg_chapter_length]

    return '\n'.join(map(str, filtered_chapter_list))
