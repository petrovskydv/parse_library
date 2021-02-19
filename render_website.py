import json
import logging
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked

import parse_tululu_category

logger = logging.getLogger(__name__)


def on_reload():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')
    rendered_page = template.render(books_columns=books_columns)

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)


if __name__ == '__main__':
    args = parse_tululu_category.get_arguments()
    books_path = os.path.join(args.dest_folder, 'books')
    books_images_path = os.path.join(args.dest_folder, 'images')
    json_path = os.path.join(args.dest_folder, args.json_path)
    with open(json_path, 'r') as file:
        books_json = file.read()
    books = json.loads(books_json)
    for book in books:
        book['book_path'] = book['book_path'].replace(os.sep, '/')
        book['img_src'] = book['img_src'].replace(os.sep, '/')

    books_columns = list(chunked(books, 2))

    on_reload()

    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='.')
