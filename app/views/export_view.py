import csv
from pathlib import Path
from typing import Iterable

import config
from app.models.produit import Product


CATEGORY_LABELS = config.CATEGORY_LABELS
FIELDS = (
    "Marketplace",
    "Catégorie",
    "Produit",
    "Prix",
    "Note",
    "Nombre d'avis",
    "Disponibilité",
)


def ordered_products(products: Iterable[Product]) -> list[Product]:
    category_order = {category: index for index, category in enumerate(CATEGORY_LABELS)}
    return sorted(
        products,
        key=lambda product: (
            product.marketplace.casefold(),
            category_order.get(product.category, len(category_order)),
            product.title.casefold(),
        ),
    )


class CsvExporter:
    def __init__(self, csv_path: Path) -> None:
        self.csv_path = csv_path

    def export(self, products: Iterable[Product]) -> None:
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)
        with self.csv_path.open("w", newline="", encoding="utf-8-sig") as csv_file:
            writer = csv.writer(csv_file, delimiter=";", lineterminator="\n")
            writer.writerow(FIELDS)
            for product in ordered_products(products):
                writer.writerow((
                    product.marketplace,
                    CATEGORY_LABELS.get(product.category, product.category),
                    product.title,
                    product.price,
                    product.rating,
                    product.review_count,
                    product.availability,
                ))
