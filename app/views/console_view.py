from pathlib import Path

from app.models.produit import Product


class ConsoleView:
    def show_summary(self, products: list[Product], database_path: Path,
                     csv_path: Path) -> None:
        print(f"\nCollecte terminée : {len(products)} produit(s).")
        print(f"Base SQLite : {database_path}")
        print(f"Export CSV : {csv_path}")

        print("Les URL des produits ne sont pas enregistrées.")
