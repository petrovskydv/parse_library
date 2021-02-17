import json
import logging
import os
import sys
from urllib.parse import urljoin

import requests
import urllib3
from bs4 import BeautifulSoup

import parse_tululu

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    books_path = 'books/'
    os.makedirs(books_path, exist_ok=True)
    books_images_path = 'images/'
    os.makedirs(books_images_path, exist_ok=True)

    books_collection_url = 'https://tululu.org/l55/'

    urllib3.disable_warnings()
    books = []
    pages_number = 2
    page_number = 1

    while page_number < 5:
        response = requests.get(f'{books_collection_url}{page_number}/', verify=False)
        logger.info(f'{books_collection_url}{page_number}/')
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')

        pages = soup.find_all(class_='npage')
        pages_number = int(pages[-1].text)

        book_cards = soup.find_all(class_='d_book')
        for book_card in book_cards:
            book_href = book_card.find('a')['href']
            book_url = urljoin(books_collection_url, book_href)
            print(book_url)

            book_response = requests.get(book_url, verify=False)
            book_response.raise_for_status()
            try:
                book = parse_tululu.parse_book_page(book_response.text, book_url)
                book_path = parse_tululu.download_txt(book['text_url'], book['id'], book['title'], books_path)
                img_src = parse_tululu.download_image(book['image_url'], books_images_path)
                book['book_path'] = book_path
                book['img_src'] = img_src
            except parse_tululu.BookError as e:
                logger.info(e)
                print(e, file=sys.stderr)

            books.append(book)

        page_number += 1

    with open("books.json", "w") as file:
        json.dump(books, file, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    main()
