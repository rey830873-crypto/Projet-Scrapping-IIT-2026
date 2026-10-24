import sqlite3
from pathlib import Path
from typing import Iterable

from app.models.produit import Product


class ProductRepository:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path
        self.connection: sqlite3.Connection | None = None

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.database_path)
        table = self.connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='products'"
        ).fetchone()
        if table is None:
            self._create_products_table()
        else:
            columns = {
                row[1] for row in self.connection.execute("PRAGMA table_info(products)")
            }
            if "marketplace" not in columns:
                self._migrate_legacy_table()
        self.connection.commit()

    def _create_products_table(self) -> None:
        self.connection.execute(
            """CREATE TABLE products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                marketplace TEXT NOT NULL,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                price TEXT NOT NULL DEFAULT '',
                rating TEXT NOT NULL DEFAULT '',
                review_count TEXT NOT NULL DEFAULT '',
                availability TEXT NOT NULL DEFAULT '',
                scraped_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(marketplace, category, title)
            )"""
        )

    def _migrate_legacy_table(self) -> None:
        self.connection.execute("ALTER TABLE products RENAME TO products_legacy")
        self._create_products_table()
        self.connection.execute(
            """INSERT INTO products
                (id, marketplace, category, title, price, rating, review_count, availability, scraped_at)
                SELECT id, 'France — Amazon.fr', category, title, price, rating,
                       review_count, availability, scraped_at
                FROM products_legacy"""
        )
        self.connection.execute("DROP TABLE products_legacy")

    def save_many(self, products: Iterable[Product]) -> None:
        if self.connection is None:
            raise RuntimeError("Le dépôt SQLite n'est pas initialisé.")
        self.connection.executemany(
            """INSERT INTO products
                (marketplace, category, title, price, rating, review_count, availability)
                VALUES (:marketplace, :category, :title, :price, :rating, :review_count, :availability)
                ON CONFLICT(marketplace, category, title) DO UPDATE SET
                    price = excluded.price,
                    rating = excluded.rating,
                    review_count = excluded.review_count,
                    availability = excluded.availability,
                    scraped_at = CURRENT_TIMESTAMP""",
            (product.as_record() for product in products),
        )
        self.connection.commit()

    def fetch_all(self) -> list[tuple]:
        connection = sqlite3.connect(self.database_path)
        try:
            return connection.execute(
                """SELECT id, marketplace, category, title, price, rating,
                          review_count, availability, scraped_at
                   FROM products
                   ORDER BY scraped_at DESC, id DESC"""
            ).fetchall()
        finally:
            connection.close()

    def close(self) -> None:
        if self.connection is not None:
            self.connection.close()
            self.connection = None
