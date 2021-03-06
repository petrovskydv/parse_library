import argparse
import json
import logging
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked

logger = logging.getLogger(__name__)


def on_reload():
    template = env.get_template(template_path)
    for page_number, books_page in enumerate(books_pages, start=1):
        books_columns = list(chunked(books_page, columns_number))
        rendered_page = template.render(books_columns=books_columns, pages_count=len(books_pages),
                                        current_page=page_number)

        index_path = os.path.join(pages_path, f'index{page_number}.html')
        with open(index_path, 'w', encoding="utf8") as file:
            file.write(rendered_page)
            logger.info(f'processed {index_path}')


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.ERROR)
    logger.setLevel(logging.INFO)

    parser = argparse.ArgumentParser(description='рендеринг сайта скачанных книг')
    parser.add_argument('json_path', nargs='?', default='books.json', help='путь к json файлу с результатами')
    parser.add_argument('dest_folder', nargs='?', default='media', help='путь к каталогу с результатами парсинга')
    args = parser.parse_args()
    json_path = os.path.join(args.dest_folder, args.json_path)

    pages_path = 'pages'
    os.makedirs(pages_path, exist_ok=True)

    template_path = 'template.html'
    books_per_page_number = 20
    columns_number = 2

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    with open(json_path, 'r', encoding='utf-8') as file:
        books_json = file.read()
    books = json.loads(books_json)
    # заменяем обратные слеши для шаблона HTML
    for book in books:
        book['book_path'] = book['book_path'].replace('\\', '/')
        book['img_src'] = book['img_src'].replace('\\', '/')

    books_pages = list(chunked(books, books_per_page_number))

    on_reload()

    server = Server()
    server.watch(template_path, on_reload)
    server.serve(root='.')
