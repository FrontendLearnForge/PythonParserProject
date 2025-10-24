from sqlalchemy.orm import Session
from typing import List, Dict
from app.wildberries_parser import WildberriesSeleniumParser
from app import crud, schemas


class ParserService:
    def __init__(self, db: Session):
        self.db = db
        self.parser = WildberriesSeleniumParser()

    def parse_and_save_search(self, search_query: str, max_pages: int = 1) -> Dict:
        """Парсит товары по поисковому запросу и сохраняет в БД"""
        print(f"Начинаем парсинг по запросу: '{search_query}'")

        # Формируем URL для поиска
        search_url = f"https://www.wildberries.ru/catalog/0/search.aspx?search={search_query}"

        # Парсим товары
        products_data = self.parser.parse_search_page(search_url, max_pages)

        results = {
            'parsed': len(products_data),
            'saved': 0,
            'skipped': 0,
            'products': []
        }

        for product_data in products_data:
            existing = crud.get_products(self.db, search=product_data.name)
            if not existing:
                product = crud.create_product(self.db, product_data)
                results['saved'] += 1
                results['products'].append(product)
                print(f"Сохранен: {product.name} - {product.current_price}{product.currency}")
            else:
                print(f"Уже существует: {product_data.name}")
                results['skipped'] += 1

        return results

    def get_parsed_products(self, search: str = None) -> List[schemas.Product]:
        """Получает спарсенные товары из БД"""
        return crud.get_products(self.db, search=search)