# Парсер книг с сайта [tululu.org](https://tululu.org/)
Этот скрипт скачивает книги с сайта [tululu.org](https://tululu.org/).

## Как установить
Скачайте проект на свой компьютер. Python3 должен быть уже установлен. 

Затем используйте pip (или pip3, если есть конфликт с Python2) для установки зависимостей:
```
pip install -r requirements.txt
```
Для запуска на компьютере необходимо ввести в командной строке:
```
python main.py <start_page> <end_page>
```
`start_page` и `end_page` это обязательные аргументы, которые контролируют с какой по какую страницы сайта скачать.

Ниже пример запуска скрипта, который скачает книги c id начиная с [200](https://tululu.org/b200/) и заканчивая [500](https://tululu.org/b500/):
```
python main.py 200 500
```
Если `start_page` и `end_page` не заданы, то будут загружены книги с id начиная с 1 и заканчивая 1000.

## Цель проекта
Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).

## Лицензия

Этот проект находится под лицензией MIT License - подробности см. в файле LICENSE.