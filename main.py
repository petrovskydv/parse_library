import logging
import os

import requests
import urllib3

logger = logging.getLogger(__name__)


def check_for_redirect(response):
    if len(response.history) > 0:
        raise requests.HTTPError


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    source_path = 'books'
    os.makedirs(source_path, exist_ok=True)

    urllib3.disable_warnings()
    for book_number in range(10):
        try:
            response = requests.get(f'https://tululu.org/txt.php?id={book_number + 1}', verify=False)
            response.raise_for_status()
            check_for_redirect(response)
            file_path = os.path.join(source_path, f'id{book_number + 1}.txt')
            with open(file_path, 'wb') as file:
                file.write(response.content)
                logger.info(file_path)
        except requests.HTTPError:
            pass


if __name__ == '__main__':
    main()
