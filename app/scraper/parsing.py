import re

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from app.models.produit import Product


def _text(element: WebElement, selectors: tuple[str, ...]) -> str:
    for selector in selectors:
        try:
            value = element.find_element(By.CSS_SELECTOR, selector).text.strip()
        except Exception:
            continue
        if value:
            return re.sub(r"\s+", " ", value)
    return ""


def parse_product_card(card: WebElement, category: str,
                       marketplace: str = "France — Amazon.fr") -> Product | None:
    title = _text(card, ("h2 a span", "h2 span", "h2"))
    if not title:
        return None

    whole = _text(card, (".a-price .a-price-whole",))
    fraction = _text(card, (".a-price .a-price-fraction",))
    symbol = _text(card, (".a-price .a-price-symbol",))
    price = f"{whole},{fraction} {symbol}".strip(" ,") if whole else ""
    rating = _text(card, (".a-icon-alt",))
    review_count = _text(card, (".a-size-base.s-underline-text",))
    availability = _text(card, (".a-color-price", ".a-color-success"))

    return Product(category, title, price, rating, review_count, availability, marketplace)
