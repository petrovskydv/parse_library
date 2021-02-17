import argparse
import logging
import os
import sys
from urllib.parse import urljoin, urlparse, unquote, parse_qs

import requests
import urllib3
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename

logger = logging.getLogger(__name__)


class BookError(Exception):
    def __init__(self, text):
        self.txt = text


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    library_url = 'https://tululu.org'

    books_path = 'books/'
    os.makedirs(books_path, exist_ok=True)
    books_images_path = 'images/'
    os.makedirs(books_images_path, exist_ok=True)

    parser = argparse.ArgumentParser(description='парсер онлайн-библиотеки https://tululu.org/')
    parser.add_argument('start_id', nargs='?', default='1', type=int, help='с какой страницы начинать')
    parser.add_argument('end_id', nargs='?', default='1000', type=int, help='по какую страницу качать')
    args = parser.parse_args()

    urllib3.disable_warnings()
    for book_number in range(args.start_id, args.end_id + 1):
        book_url = f'{library_url}/b{book_number}/'
        try:
            logger.info(f'ищем книгу по адресу {book_url}')
            response = requests.get(book_url, verify=False)
            response.raise_for_status()
            check_for_redirect(response)
            book = parse_book_page(response.text, book_url)
            download_txt(f'{library_url}/txt.php?id={book_number}', book_number, book['title'], books_path)
            download_image(book['image_url'], books_images_path)
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
        except BookError as e:
            logger.exception(e)
            print(e, file=sys.stderr)


def check_for_redirect(response):
    if len(response.history) > 0:
        logger.info('произошел редирект на основную страницу. переходим к следующему id')
        raise requests.TooManyRedirects


def is_text_url(tag):
    return tag.text == 'скачать txt'


def parse_book_page(content, library_url):
    soup = BeautifulSoup(content, 'lxml')

    title_author_string = soup.select_one('.ow_px_td h1').text
    book_title, book_author = map(lambda title: title.strip(), title_author_string.split('::'))

    book_image_src = soup.select_one('.bookimage img')['src']
    book_image_url = urljoin(library_url, book_image_src)

    search_text_result = soup.select_one('table.d_book a[title$=txt]')
    if not search_text_result:
        raise BookError('Текст этой книги отсутствует')
    book_text_url = search_text_result['href']

    parsed_book_query = parse_qs(urlparse(book_text_url).query)
    book_id = parsed_book_query['id'][0]

    comments = soup.select('.texts .black')
    book_comments = [comment.text for comment in comments]

    genres_string = soup.select('span.d_book a')
    book_genres = [genre.text for genre in genres_string]

    book = {
        'title': book_title,
        'author': book_author,
        'comments': book_comments,
        'genres': book_genres,
        'image_url': book_image_url,
        'id': book_id,
        'text_url': urljoin(library_url, book_text_url)
    }
    return book


def download_txt(url, book_id, filename, folder='books/'):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        book_id (int): Уникальный id книги
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    file_path = os.path.join(folder, f'{book_id}. {sanitize_filename(filename)}.txt')
    response = requests.get(url, verify=False)
    response.raise_for_status()
    check_for_redirect(response)
    with open(file_path, 'wb') as file:
        file.write(response.content)
    logger.info(f'скачали книгу: {file_path}')
    return file_path


def download_image(url, folder='images/', rewrite=False):
    response = requests.get(url, verify=False)
    response.raise_for_status()
    check_for_redirect(response)
    file_path = os.path.join(folder, os.path.basename(unquote(urlparse(url).path)))
    if not rewrite and os.path.exists(file_path):
        return file_path
    with open(file_path, 'wb') as file:
        file.write(response.content)
    logger.info(f'скачали файл: {file_path}')
    return file_path


if __name__ == '__main__':
    main()
