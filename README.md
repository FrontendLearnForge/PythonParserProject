Для получения данных по названию или бренду используется GET /products/;
Для добавления данных POST /products/;
Для запуска парсера POST /parse/ в query необходимо указать название запроса, а также количество обрабатываемых страниц;
Для проверки статуса парсера используется GET /parse/status

Для работы, после открытия проекта необходимо:
1. Установить зависимости:
pip install -r requirements.txt
2. Создать базу данных в postgresql:
CREATE DATABASE products_db;
3. Поменять url подключения к БД в файлах env и migrations/env.py
4. Произвести миграцию таблицы продуктов:
alembic revision --autogenerate -m "Create products table"
alembic upgrade head
5. Запустить сервер:
uvicorn app.main:app --reload
6. Запустить парсер
7. После окончания работы парсера можно получать необходимые товары по бренду или названию
8. В папке logs хранятся логи работы парсера
