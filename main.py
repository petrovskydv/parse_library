import logging
import os

import requests
import urllib3


def main():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    source_path = 'books'
    os.makedirs(source_path, exist_ok=True)

    urllib3.disable_warnings()
    for book_number in range(10):
        response = requests.get(f'https://tululu.org/txt.php?id={book_number + 1}', verify=False)
        response.raise_for_status()
        file_path = os.path.join(source_path, f'id{book_number + 1}.txt')
        with open(file_path, 'wb') as file:
            file.write(response.content)


if __name__ == '__main__':
    main()
