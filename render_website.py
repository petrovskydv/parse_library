import json
import argparse

import logging
import os
import sys
import time
from urllib.parse import urljoin
import parse_tululu_category

from http.server import HTTPServer, SimpleHTTPRequestHandler

from jinja2 import Environment, FileSystemLoader, select_autoescape


def main():
    global json_path
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

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')
    rendered_page = template.render(books=books)

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)

    server = HTTPServer(('127.0.0.1', 8080), SimpleHTTPRequestHandler)
    server.serve_forever()


if __name__ == '__main__':
    main()
