import argparse
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

    parser = argparse.ArgumentParser(description='парсер онлайн-библиотеки https://tululu.org/')
    parser.add_argument('--start_page', nargs='?', default='1', type=int, help='с какой страницы начинать')
    parser.add_argument('--end_page', nargs='?', default='1000', type=int, help='по какую страницу качать')
    args = parser.parse_args()

    books_collection_url = 'https://tululu.org/l55/'

    urllib3.disable_warnings()
    books = []
    pages_number = args.end_page
    page_number = args.start_page

    while page_number <= pages_number:
        response = requests.get(f'{books_collection_url}{page_number}/', verify=False)
        logger.info(f'обрабатывается страница {books_collection_url}{page_number}/')
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')

        pages = soup.select('.npage')
        pages_number = min(int(pages[-1].text), args.end_page)

        book_cards = soup.select('.ow_px_td .d_book .bookimage a')
        for book_card in book_cards:
            book_url = urljoin(books_collection_url, book_card['href'])
            logger.debug(f'ищем книгу по адресу {book_url}')

            try:
                book_response = requests.get(book_url, verify=False)
                book_response.raise_for_status()
                parse_tululu.check_for_redirect(response)
                book = parse_tululu.parse_book_page(book_response.text, book_url)
                book_path = parse_tululu.download_txt(book['text_url'], book['id'], book['title'], books_path)
                img_src = parse_tululu.download_image(book['image_url'], books_images_path)
                book['book_path'] = book_path
                book['img_src'] = img_src
                books.append(book)
            except requests.HTTPError as e:
                print(e, file=sys.stderr)
                logger.exception(e)
            except requests.ConnectionError as e:
                logger.exception(e)
                print(e, file=sys.stderr)
            except requests.TooManyRedirects:
                print('обнаружен редирект', file=sys.stderr)
            except KeyboardInterrupt:
                print('Скачивание остановлено')
                sys.exit()
            except parse_tululu.BookError as e:
                logger.exception(e)
                print(e, file=sys.stderr)

        page_number += 1

    with open("books.json", "w") as file:
        json.dump(books, file, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    main()
