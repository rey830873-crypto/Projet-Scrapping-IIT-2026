from app.models.depot import ProductRepository
from app.models.produit import Product
from app.scraper.amazon_scraper import AmazonScraper
from app.views.console_view import ConsoleView
from app.views.export_view import CsvExporter



class ScrapingController:
    def __init__(self, scraper: AmazonScraper, repository: ProductRepository,
                 exporter: CsvExporter,
                 view: ConsoleView) -> None:
        self.scraper = scraper
        self.repository = repository
        self.exporter = exporter

        self.view = view

    def run(self) -> list[Product]:
        try:
            self.repository.initialize()
            products = self.scraper.scrape_all_categories()
            self.repository.save_many(products)
            self.exporter.export(products)

            self.view.show_summary(products, self.repository.database_path,
                                   self.exporter.csv_path)
            return products
        finally:
            self.scraper.close()
            self.repository.close()
