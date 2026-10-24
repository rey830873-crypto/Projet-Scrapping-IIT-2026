from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
IMAGE_DIR = DATA_DIR / "images"
EXPORT_DIR = BASE_DIR / "exports"
DATABASE_PATH = DATA_DIR / "amazon_scraper.sqlite3"
CSV_PATH = EXPORT_DIR / "produits.csv"
MAX_PRODUCTS_TOTAL = 50
HEADLESS = False
PAGE_LOAD_TIMEOUT_SECONDS = 30
ELEMENT_WAIT_SECONDS = 12
IMAGE_LOAD_TIMEOUT_SECONDS = 5
REQUEST_PAUSE_SECONDS = 2

MARKETPLACES = {
    "fr": {"label": "France — Amazon.fr", "url": "https://www.amazon.fr", "language": "fr", "locale": "fr-FR"},
    "us": {"label": "États-Unis — Amazon.com", "url": "https://www.amazon.com", "language": "en", "locale": "en-US"},
    "uk": {"label": "Royaume-Uni — Amazon.co.uk", "url": "https://www.amazon.co.uk", "language": "en", "locale": "en-GB"},
    "ca": {"label": "Canada — Amazon.ca", "url": "https://www.amazon.ca", "language": "en", "locale": "en-CA"},
    "de": {"label": "Allemagne — Amazon.de", "url": "https://www.amazon.de", "language": "de", "locale": "de-DE"},
    "es": {"label": "Espagne — Amazon.es", "url": "https://www.amazon.es", "language": "es", "locale": "es-ES"},
    "it": {"label": "Italie — Amazon.it", "url": "https://www.amazon.it", "language": "it", "locale": "it-IT"},
    "jp": {"label": "Japon — Amazon.co.jp", "url": "https://www.amazon.co.jp", "language": "ja", "locale": "ja-JP"},
    "au": {"label": "Australie — Amazon.com.au", "url": "https://www.amazon.com.au", "language": "en", "locale": "en-AU"},
    "br": {"label": "Brésil — Amazon.com.br", "url": "https://www.amazon.com.br", "language": "pt", "locale": "pt-BR"},
}

CATEGORY_LABELS = {
    "telephones_portables": "Téléphones portables",
    "casques_bluetooth": "Casques Bluetooth",
    "televisions": "Télévisions",
    "gps": "GPS",
    "accessoires_sans_fil": "Accessoires sans fil",
    "univers_hifi": "Univers Hi-Fi",
    "photo_camescope": "Photo et caméscope",
}

CATEGORY_QUERIES = {
    "fr": {
        "telephones_portables": "smartphone téléphone portable",
        "casques_bluetooth": "casque bluetooth sans fil",
        "televisions": "télévision TV",
        "gps": "GPS navigation",
        "accessoires_sans_fil": "accessoire sans fil",
        "univers_hifi": "univers hi-fi chaîne hi-fi amplificateur",
        "photo_camescope": "appareil photo numérique caméscope",
    },
    "en": {
        "telephones_portables": "smartphones mobile phones",
        "casques_bluetooth": "wireless bluetooth headphones",
        "televisions": "televisions smart TV",
        "gps": "GPS navigation device",
        "accessoires_sans_fil": "wireless accessories",
        "univers_hifi": "hi-fi system stereo amplifier",
        "photo_camescope": "digital camera camcorder",
    },
    "de": {
        "telephones_portables": "Smartphones Mobiltelefone",
        "casques_bluetooth": "Bluetooth Kopfhörer kabellos",
        "televisions": "Fernseher Smart TV",
        "gps": "GPS Navigationsgerät",
        "accessoires_sans_fil": "kabelloses Zubehör",
        "univers_hifi": "Hi-Fi Anlage Stereo Verstärker",
        "photo_camescope": "Digitalkamera Camcorder",
    },
    "es": {
        "telephones_portables": "teléfonos móviles smartphones",
        "casques_bluetooth": "auriculares bluetooth inalámbricos",
        "televisions": "televisores Smart TV",
        "gps": "GPS navegación",
        "accessoires_sans_fil": "accesorios inalámbricos",
        "univers_hifi": "equipo hi-fi amplificador estéreo",
        "photo_camescope": "cámara digital videocámara",
    },
    "it": {
        "telephones_portables": "smartphone telefoni cellulari",
        "casques_bluetooth": "cuffie bluetooth wireless",
        "televisions": "televisori Smart TV",
        "gps": "GPS navigatore",
        "accessoires_sans_fil": "accessori wireless",
        "univers_hifi": "impianto hi-fi amplificatore stereo",
        "photo_camescope": "fotocamera digitale videocamera",
    },
    "ja": {
        "telephones_portables": "スマートフォン 携帯電話",
        "casques_bluetooth": "Bluetooth ワイヤレス ヘッドホン",
        "televisions": "テレビ スマートテレビ",
        "gps": "GPS ナビゲーション",
        "accessoires_sans_fil": "ワイヤレス アクセサリー",
        "univers_hifi": "ハイファイ ステレオ アンプ",
        "photo_camescope": "デジタルカメラ ビデオカメラ",
    },
    "pt": {
        "telephones_portables": "smartphone celular",
        "casques_bluetooth": "fone de ouvido bluetooth sem fio",
        "televisions": "televisão Smart TV",
        "gps": "GPS navegação",
        "accessoires_sans_fil": "acessórios sem fio",
        "univers_hifi": "sistema hi-fi amplificador estéreo",
        "photo_camescope": "câmera digital filmadora",
    },
}

CATEGORIES = CATEGORY_QUERIES["fr"]
AMAZON_BASE_URL = MARKETPLACES["fr"]["url"]
