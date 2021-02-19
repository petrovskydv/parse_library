import json
import logging
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked

import parse_tululu_category

logger = logging.getLogger(__name__)


def on_reload():
    for page_number, books_page in enumerate(books_pages):
        books_columns = list(chunked(books_page, 2))
        rendered_page = template.render(books_columns=books_columns, pages_count=len(books_pages),
                                        current_page=page_number + 1)

        index_path = os.path.join(pages_path, f'index{page_number + 1}.html')
        with open(index_path, 'w', encoding="utf8") as file:
            file.write(rendered_page)


if __name__ == '__main__':
    args = parse_tululu_category.get_arguments()
    json_path = os.path.join(args.dest_folder, args.json_path)

    pages_path = 'pages'
    os.makedirs(pages_path, exist_ok=True)

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    with open(json_path, 'r') as file:
        books_json = file.read()
    books = json.loads(books_json)
    for book in books:
        book['book_path'] = book['book_path'].replace(os.sep, '/')
        book['img_src'] = book['img_src'].replace(os.sep, '/')

    books_pages = list(chunked(books, 20))

    on_reload()

    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='.')
