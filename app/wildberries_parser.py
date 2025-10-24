from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import re
from typing import List, Dict, Optional
from app.schemas import ProductCreate
from app.logger import logger


class WildberriesSeleniumParser:
    def __init__(self):
        self.logger = logger

    def _create_driver(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        options.add_argument("--window-size=1920,1080")

        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        return driver

    def parse_search_page(self, search_url: str, max_pages: int = 1) -> List[ProductCreate]:
        """Парсит страницу поиска Wildberries"""
        self.logger.info(f"Начинаем парсинг по URL: {search_url}, страниц: {max_pages}")

        all_products = []

        for page in range(1, max_pages + 1):
            self.logger.info(f"\n{'=' * 50}")
            self.logger.info(f"Парсим страницу {page}")
            self.logger.info(f"{'=' * 50}")

            if page == 1:
                url = search_url
            else:
                url = f"{search_url}&page={page}"

            products_in_page = self._parse_single_page(url)
            all_products.extend(products_in_page)

            self.logger.info(f"С страницы {page} получено товаров: {len(products_in_page)}")
            self.logger.info(f"Всего собрано товаров: {len(all_products)}")

            if page < max_pages:
                time.sleep(1)

        self.logger.info(f"\nПарсинг завершен. Итого собрано товаров: {len(all_products)}")
        return all_products

    def _parse_single_page(self, url: str) -> List[ProductCreate]:
        """Парсит одну страницу с товарами"""
        driver = self._create_driver()
        parsed_products = []

        try:
            self.logger.info("Загружаем страницу...")
            driver.get(url)

            wait = WebDriverWait(driver, 15)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "product-card")))

            # Прокрутка для загрузки всех товаров
            total_products = self._scroll_to_load_all_products(driver)
            self.logger.info(f"Итого загружено товаров: {total_products}")

            # Парсим все товары
            soup = BeautifulSoup(driver.page_source, 'lxml')
            products = soup.find_all('article', class_='product-card')

            self.logger.info(f"Найдено товаров для парсинга: {len(products)}")

            if not products:
                self.logger.warning("Товары не найдены. Сохраняем HTML для отладки...")
                with open('debug_page.html', 'w', encoding='utf-8') as f:
                    f.write(driver.page_source)
                self.logger.info("HTML страницы сохранен в debug_page.html")
                return []

            for i, product in enumerate(products, 1):
                try:
                    product_data = self._parse_single_product(product, i)
                    if product_data:
                        parsed_products.append(product_data)
                except Exception as e:
                    self.logger.warning(f"Ошибка при парсинге товара #{i}: {e}")
                    continue

            self.logger.info(f"Успешно спарсено товаров: {len(parsed_products)}")
            return parsed_products

        except Exception as e:
            self.logger.error(f"Произошла ошибка: {e}")
            with open('error_page.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            self.logger.info("HTML страницы сохранен в error_page.html")
            return []

        finally:
            driver.quit()

    def _scroll_to_load_all_products(self, driver):
        """Прокрутка для загрузки всех товаров"""
        self.logger.info("Начинаем постепенную прокрутку...")

        for i in range(1, 16):
            scroll_position = i * 700
            driver.execute_script(f"window.scrollTo(0, {scroll_position});")
            time.sleep(0.3)

            current_products = driver.find_elements(By.CLASS_NAME, "product-card")
            self.logger.info(f"Шаг {i}: {len(current_products)} товаров")

            if len(current_products) >= 100:
                self.logger.info("Все продукты на странице проанализированы")
                break

        final_count = len(driver.find_elements(By.CLASS_NAME, "product-card"))
        self.logger.info(f"Всего загружено товаров: {final_count}")
        return final_count

    def _parse_single_product(self, product, index: int) -> Optional[ProductCreate]:
        """Парсит один товар и преобразует в ProductCreate"""
        self.logger.info(f"\n--- Товар #{index} ---")

        try:
            # Цена
            current_price_elem = product.find('ins', class_='price__lower-price')
            current_price_text = current_price_elem.get_text(
                strip=True) if current_price_elem else "Текущая цена не найдена"
            current_price = self._price_to_float(current_price_text)

            # Старая цена
            old_price_elem = product.find('del')
            old_price_text = old_price_elem.get_text(strip=True) if old_price_elem else "Старая цена не найдена"
            old_price = self._price_to_float(old_price_text) if old_price_text != "Старая цена не найдена" else None

            # Скидка
            discount_elem = product.find('span', class_='percentage-sale')
            discount_text = discount_elem.get_text(strip=True) if discount_elem else ""
            discount = int(discount_text[1:-1]) if discount_text  else None

            # Бренд
            brand_elem = product.find('span', class_='product-card__brand')
            brand = brand_elem.get_text(strip=True) if brand_elem else None

            # Название
            name_elem = product.find('span', class_='product-card__name')
            name = name_elem.get_text(strip=True) if name_elem else ""
            name = name[1:] if name and name.startswith('/') else name
            if not name:
                name = "Название не найдено"

            # Рейтинг
            rating_elem = product.find('span', class_='address-rate-mini')
            rating_text = rating_elem.get_text(strip=True) if rating_elem else "Рейтинг не найден"
            rating = self._text_to_float(rating_text) if rating_text != "Рейтинг не найден" else None

            # Количество отзывов
            reviews_elem = product.find('span', class_='product-card__count')
            reviews_text = reviews_elem.get_text(strip=True) if reviews_elem else ""
            reviews = self._text_to_int(reviews_text.split(" ")[0])

            # Остатки товара
            remaining_elem = product.find('span', class_='product-card__tip--quantity')
            remaining_text = remaining_elem.get_text(strip=True) if remaining_elem else ""
            stock = remaining_text.split(" ")[0] if remaining_text else "Остатки не указаны"

            # Логируем
            self.logger.info(f"Текущая цена: {current_price}")
            self.logger.info(f"Старая цена: {old_price}" if old_price else "Старая цена: не найдена")
            self.logger.info(f"Скидка: {discount}" if discount else "Скидка: не найдена")
            self.logger.info(f"Бренд: {brand}" if brand else "Бренд: не найден")
            self.logger.info(f"Название: {name}")
            self.logger.info(f"Рейтинг: {rating}" if rating else "Рейтинг: не найден")
            self.logger.info(f"Отзывы: {reviews}" if reviews else "Отзывы: не найдены")
            self.logger.info(f"Остатки: {stock}")

            # Создаем ProductCreate
            return ProductCreate(
                current_price=current_price,
                old_price=old_price,
                discount=discount,
                brand=brand,
                name=name,
                rating=rating,
                reviews_count=reviews,
                stock=stock,
                currency="RUB"
            )

        except Exception as e:
            self.logger.error(f"Ошибка при парсинге товара #{index}: {e}")
            return None

    def _price_to_float(self, price_text: str) -> float:
        try:
            cleaned = re.sub(r'[^\d]', '', price_text)
            return float(cleaned) if cleaned else 0.0
        except (ValueError, TypeError):
            return 0.0

    def _text_to_float(self, text: str) -> Optional[float]:
        try:
            cleaned = re.sub(r',', '.', text)
            cleaned = re.sub(r'[^\d.]', '', cleaned)
            return float(cleaned) if cleaned else None
        except (ValueError, TypeError):
            return None

    def _text_to_int(self, text: str) -> Optional[int]:
        try:
            cleaned = re.sub(r'[^\d]', '', text)
            return int(cleaned) if cleaned else None
        except (ValueError, TypeError):
            return None