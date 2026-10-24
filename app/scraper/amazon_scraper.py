import hashlib
import re
import unicodedata
from time import sleep
from typing import Callable
from urllib.parse import urlencode

from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as conditions
from selenium.webdriver.support.ui import WebDriverWait

import config
from app.models.produit import Product
from app.scraper.driver import create_driver
from app.scraper.parsing import parse_product_card


class AmazonScraper:
    def __init__(self, categories: dict[str, str] | None = None,
                 max_products_total: int | None = None,
                 on_message: Callable[[str], None] | None = None,
                 on_progress: Callable[[int, str], None] | None = None,
                 base_url: str = config.AMAZON_BASE_URL,
                 marketplace: str = "France — Amazon.fr",
                 language: str = "fr-FR") -> None:
        self.driver = create_driver(language)
        self.categories = config.CATEGORIES if categories is None else categories
        self.max_products_total = max_products_total or config.MAX_PRODUCTS_TOTAL
        self.on_message = on_message
        self.on_progress = on_progress
        self.base_url = base_url.rstrip("/")
        self.marketplace = marketplace

    def _message(self, message: str) -> None:
        if self.on_message is None:
            print(message)
        else:
            self.on_message(message)

    def _progress(self, percent: int, message: str) -> None:
        if self.on_progress is not None:
            self.on_progress(max(0, min(100, percent)), message)

    def scrape_all_categories(self) -> list[Product]:
        config.IMAGE_DIR.mkdir(parents=True, exist_ok=True)
        products: list[Product] = []
        categories = list(self.categories.items())
        if not categories:
            raise ValueError("Sélectionne au moins une catégorie.")

        self._message(f"Marketplace sélectionné : {self.marketplace}")
        for index, (category, query) in enumerate(categories):
            remaining = self.max_products_total - len(products)
            if remaining <= 0:
                break
            categories_left = len(categories) - index
            category_limit = (remaining + categories_left - 1) // categories_left
            self._message(f"Recherche : {category} (maximum {category_limit})")
            self._progress(round(index * 100 / len(categories)), f"Recherche : {category}")

            def report_count(found: int) -> None:
                ratio = min(found / category_limit, 1) if category_limit else 1
                percent = round((index + ratio) * 100 / len(categories))
                self._progress(percent, f"{category} : {found}/{category_limit} produits")

            category_products = self._scrape_category(category, query, category_limit, report_count)
            products.extend(category_products)
            self._progress(
                round((index + 1) * 100 / len(categories)),
                f"{category} : {len(category_products)} produit(s)",
            )
            sleep(config.REQUEST_PAUSE_SECONDS)

        self._progress(100, f"Collecte terminée : {len(products)} produit(s)")
        return products

    def _scrape_category(self, category: str, query: str, limit: int,
                         on_count: Callable[[int], None] | None = None) -> list[Product]:
        search_url = f"{self.base_url}/s?{urlencode({'k': query})}"
        try:
            self.driver.get(search_url)
            WebDriverWait(self.driver, config.ELEMENT_WAIT_SECONDS).until(
                conditions.presence_of_element_located(
                    (By.CSS_SELECTOR, "div[data-component-type='s-search-result']")
                )
            )
        except TimeoutException:
            if "captcha" in self.driver.current_url.lower():
                raise RuntimeError(
                    "Amazon demande une vérification. Termine-la dans Chrome, puis relance le scraper."
                )
            self._message(f"Aucun résultat détecté pour {category} (ou délai dépassé).")
            return []
        except WebDriverException as error:
            raise RuntimeError(f"Impossible d'ouvrir la recherche Amazon : {error}") from error

        products: list[Product] = []
        seen_titles: set[str] = set()
        while len(products) < limit:
            cards = self.driver.find_elements(
                By.CSS_SELECTOR, "div[data-component-type='s-search-result']"
            )
            for card in cards:
                product = parse_product_card(card, category, self.marketplace)
                if product is None or product.title.casefold() in seen_titles:
                    continue
                seen_titles.add(product.title.casefold())
                self._save_product_image(card, product)
                products.append(product)
                if on_count is not None:
                    on_count(len(products))
                if len(products) >= limit:
                    break

            if len(products) >= limit:
                break
            next_buttons = self.driver.find_elements(By.CSS_SELECTOR, "a.s-pagination-next")
            if not next_buttons:
                break
            next_button = next_buttons[0]
            button_classes = next_button.get_attribute("class") or ""
            if "s-pagination-disabled" in button_classes:
                break
            previous_card = cards[0] if cards else None
            try:
                next_button.click()
                if previous_card is not None:
                    WebDriverWait(self.driver, config.ELEMENT_WAIT_SECONDS).until(
                        conditions.staleness_of(previous_card)
                    )
                WebDriverWait(self.driver, config.ELEMENT_WAIT_SECONDS).until(
                    conditions.presence_of_element_located(
                        (By.CSS_SELECTOR, "div[data-component-type='s-search-result']")
                    )
                )
            except (TimeoutException, WebDriverException):
                break
            sleep(config.REQUEST_PAUSE_SECONDS)
        return products

    def _save_product_image(self, card: WebElement, product: Product) -> None:
        try:
            image = card.find_element(By.CSS_SELECTOR, "img.s-image")
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", image
            )
            WebDriverWait(self.driver, config.IMAGE_LOAD_TIMEOUT_SECONDS).until(
                lambda _: image.get_property("naturalWidth") > 0
            )
            identity = f"{product.marketplace}\0{product.category}\0{product.title}"
            digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:12]
            title = unicodedata.normalize("NFKD", product.title)
            title = title.encode("ascii", "ignore").decode("ascii").lower()
            slug = re.sub(r"[^a-z0-9]+", "-", title).strip("-")[:48] or "produit"
            category = re.sub(r"[^a-z0-9]+", "-", product.category.lower()).strip("-")
            image_path = config.IMAGE_DIR / f"{category}-{slug}-{digest}.png"
            image_path.parent.mkdir(parents=True, exist_ok=True)
            image.screenshot(str(image_path))
        except (TimeoutException, WebDriverException, OSError):
            return

    def close(self) -> None:
        if getattr(self, "driver", None) is not None:
            self.driver.quit()
            self.driver = None
