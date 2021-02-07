import logging
import os

import requests
import urllib3
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename

logger = logging.getLogger(__name__)


def check_for_redirect(response):
    if len(response.history) > 0:
        raise requests.HTTPError


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    source_path = 'books/'
    os.makedirs(source_path, exist_ok=True)

    urllib3.disable_warnings()
    for book_number in range(10):
        book_url = f'https://tululu.org/b{book_number + 1}/'
        try:
            book_title = parse_url(book_url)
            file_path = download_txt(
                f'https://tululu.org/txt.php?id={book_number + 1}', book_number + 1, book_title, source_path)
            print(file_path)
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
    return book_title


def download_txt(url, id, filename, folder='books/'):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        id (int): Уникальный id книги
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    file_path = os.path.join(folder, f'{id}. {sanitize_filename(filename)}.txt')
    response = requests.get(url, verify=False)
    response.raise_for_status()
    check_for_redirect(response)
    with open(file_path, 'wb') as file:
        file.write(response.content)
        logger.info(file_path)
    return file_path


if __name__ == '__main__':
    main()
