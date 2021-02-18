import argparse
import json
import logging
import os
import sys
import time
from urllib.parse import urljoin

import requests
import urllib3
from bs4 import BeautifulSoup

import parse_tululu

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    args = get_arguments()

    books_path = os.path.join(args.dest_folder, 'books')
    books_images_path = os.path.join(args.dest_folder, 'images')
    json_path = os.path.join(args.dest_folder, args.json_path)
    if not args.skip_txt:
        os.makedirs(books_path, exist_ok=True)
    if not args.skip_imgs:
        os.makedirs(books_images_path, exist_ok=True)
    os.makedirs(args.dest_folder, exist_ok=True)

    books_collection_url = 'https://tululu.org/l55/'

    urllib3.disable_warnings()
    books = []
    pages_number = args.end_page
    page_number = args.start_page

    while page_number <= pages_number:
        try:
            response = requests.get(f'{books_collection_url}{page_number}/', verify=False)
            logger.info(f'обрабатывается страница {books_collection_url}{page_number}/')
            response.raise_for_status()
            parse_tululu.check_for_redirect(response)
            soup = BeautifulSoup(response.text, 'lxml')

            last_page = int(soup.select_one('.npage:last-of-type').text)
            pages_number = min(last_page, args.end_page)

            book_cards = soup.select('.ow_px_td .d_book .bookimage a')
            for book_card in book_cards:
                book_url = urljoin(books_collection_url, book_card['href'])
                book = fetch_book(args, book_url, books_images_path, books_path)
                if book:
                    books.append(book)
        # ловим ошибки при попытке обработать станицу коллекции с книгами
        except requests.HTTPError as e:
            print(e, file=sys.stderr)
            logger.exception(e)
        except requests.ConnectionError as e:
            logger.exception(e)
            print(e, file=sys.stderr)
            time.sleep(10)
        except requests.TooManyRedirects:
            print('Обнаружен редирект', file=sys.stderr)
        except KeyboardInterrupt:
            print('Скачивание прервано')
            sys.exit()

        page_number += 1

    with open(json_path, 'w') as file:
        json.dump(books, file, ensure_ascii=False, indent=4)


def fetch_book(args, book_url, books_images_path, books_path):
    logger.info(f'ищем книгу по адресу {book_url}')
    try:
        book_response = requests.get(book_url, verify=False)
        book_response.raise_for_status()
        parse_tululu.check_for_redirect(book_response)
        book = parse_tululu.parse_book_page(book_response.text, book_url)
        if not args.skip_txt:
            book_path = parse_tululu.download_txt(book['text_url'], book['id'], book['title'], books_path)
            book['book_path'] = book_path
        if not args.skip_imgs:
            img_src = parse_tululu.download_image(book['image_url'], books_images_path)
            book['img_src'] = img_src
        return book
    # ловим ошибки при попытке обработать карточку книги
    except requests.HTTPError as e:
        print(e, file=sys.stderr)
        logger.exception(e)
    except requests.ConnectionError as e:
        logger.exception(e)
        print(e, file=sys.stderr)
        time.sleep(10)
    except requests.TooManyRedirects:
        print('обнаружен редирект', file=sys.stderr)
    except parse_tululu.BookError as e:
        print(e, file=sys.stderr)


def get_arguments():
    parser = argparse.ArgumentParser(description='парсер онлайн-библиотеки https://tululu.org/')
    parser.add_argument('--start_page', default='1', type=int, help='с какой страницы начинать')
    parser.add_argument('--end_page', default='1000', type=int, help='по какую страницу качать')
    parser.add_argument('--skip_imgs', action='store_true', help='не скачивать картинки')
    parser.add_argument('--skip_txt', action='store_true', help='не скачивать книги')
    parser.add_argument('--json_path', default='books.json', help='путь к json файлу с результатами')
    parser.add_argument('--dest_folder', default='static', help='путь к каталогу с результатами парсинга')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    main()
