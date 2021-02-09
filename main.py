import logging
import os

import requests
import urllib3
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlparse, unquote

logger = logging.getLogger(__name__)


def check_for_redirect(response):
    if len(response.history) > 0:
        raise requests.HTTPError


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    books_path = 'books/'
    os.makedirs(books_path, exist_ok=True)
    books_images_path = 'images/'
    os.makedirs(books_images_path, exist_ok=True)

    urllib3.disable_warnings()
    for book_number in range(10):
        book_url = f'https://tululu.org/b{book_number + 1}/'
        try:
            book_title, book_image_url = parse_url(book_url)
            # file_path = download_txt(
            #     f'https://tululu.org/txt.php?id={book_number + 1}', book_number + 1, book_title, books_path)
            # # print(file_path)
            # download_image(book_image_url, books_images_path)
        except requests.HTTPError:
            pass


def parse_url(url):
    urllib3.disable_warnings()

    response = requests.get(url, verify=False)
    response.raise_for_status()
    check_for_redirect(response)
    soup = BeautifulSoup(response.text, 'lxml')
    title_tag = soup.find('table').find('h1')
    book_title, book_author = map(lambda title: title.strip(), title_tag.text.split('::'))
    book_image_url = urljoin('https://tululu.org', soup.find(class_='bookimage').find('img')['src'])
    comments = [comment.find('span', class_='black').text for comment in soup.find_all('div', class_='texts')]

    book_genres = [genre.text for genre in soup.find('span', class_='d_book').find_all('a')]

    print(book_title)
    print(book_genres)
    return book_title, book_image_url


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
        logger.info(file_path)
    return file_path


def download_image(url, folder='images/'):
    response = requests.get(url, verify=False)
    response.raise_for_status()
    file_path = os.path.join(folder, os.path.basename(unquote(urlparse(url).path)))
    if os.path.exists(file_path):
        return file_path
    with open(file_path, 'wb') as file:
        file.write(response.content)
    logger.info(f'download file: {file_path}')
    return file_path


if __name__ == '__main__':
    main()
