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
            book_information = parse_book_page(response.text, library_url)
            download_txt(f'{library_url}/txt.php?id={book_number}', book_number, book_information['title'], books_path)
            download_image(book_information['image_url'], books_images_path)
        except requests.HTTPError:
            pass
        except KeyboardInterrupt:
            print('Скачивание остановлено')
            exit()


def check_for_redirect(response):
    if len(response.history) > 0:
        logger.info('произошел редирект на основную страницу. переходим к следующему id')
        raise requests.HTTPError


def parse_book_page(content, library_url):
    soup = BeautifulSoup(content, 'lxml')
    book_title, book_author = map(lambda title: title.strip(), soup.find('table').find('h1').text.split('::'))
    book_image_url = urljoin(library_url, soup.find(class_='bookimage').find('img')['src'])
    book_comments = [comment.find('span', class_='black').text for comment in soup.find_all('div', class_='texts')]
    book_genres = [genre.text for genre in soup.find('span', class_='d_book').find_all('a')]
    book_information = {
        'title': book_title,
        'author': book_author,
        'image_url': book_image_url,
        'comments': book_comments,
        'genres': book_genres
    }
    return book_information


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
    with open(file_path, 'wb') as file:
        file.write(response.content)
    logger.info(f'скачали книгу: {file_path}')
    return file_path


def download_image(url, folder='images/', rewrite=False):
    response = requests.get(url, verify=False)
    response.raise_for_status()
    file_path = os.path.join(folder, os.path.basename(unquote(urlparse(url).path)))
    if not rewrite and os.path.exists(file_path):
        return file_path
    with open(file_path, 'wb') as file:
        file.write(response.content)
    logger.info(f'скачали файл: {file_path}')
    return file_path


if __name__ == '__main__':
    main()
