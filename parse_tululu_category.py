import argparse
import logging
import os
from urllib.parse import urljoin, urlparse, unquote

import requests
import urllib3
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    library_url = 'https://tululu.org'

    books_path = 'books/'
    os.makedirs(books_path, exist_ok=True)
    books_images_path = 'images/'
    os.makedirs(books_images_path, exist_ok=True)

    # parser = argparse.ArgumentParser(description='парсер онлайн-библиотеки https://tululu.org/')
    # parser.add_argument('start_id', nargs='?', default='1', type=int, help='с какой страницы начинать')
    # parser.add_argument('end_id', nargs='?', default='1000', type=int, help='по какую страницу качать')
    # args = parser.parse_args()

    books_collection_url = 'https://tululu.org/l55/'

    urllib3.disable_warnings()
    response = requests.get(books_collection_url, verify=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    books = soup.find_all(class_='d_book')
    for book in books:
        book_href = book.find('a')['href']
        book_url = urljoin(books_collection_url, book_href)
        print(book_url)

    pages = soup.find_all(class_='npage')
    last_page = int(pages[-1].text)
    for page_number in range(2, last_page):
        response = requests.get(f'{books_collection_url}{page_number}/', verify=False)
        logger.info(f'{books_collection_url}{page_number}/')
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        books = soup.find_all(class_='d_book')
        for book in books:
            book_href = book.find('a')['href']
            book_url = urljoin(books_collection_url, book_href)
            print(book_url)



if __name__ == '__main__':
    main()
