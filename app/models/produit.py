from dataclasses import dataclass


@dataclass(frozen=True)
class Product:
    category: str
    title: str
    price: str = ""
    rating: str = ""
    review_count: str = ""
    availability: str = ""
    marketplace: str = "France — Amazon.fr"

    def as_record(self) -> dict[str, str]:
        return {
            "marketplace": self.marketplace,
            "category": self.category,
            "title": self.title,
            "price": self.price,
            "rating": self.rating,
            "review_count": self.review_count,
            "availability": self.availability,
        }
