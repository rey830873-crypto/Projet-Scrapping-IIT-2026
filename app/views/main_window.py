from __future__ import annotations

import sys
import sqlite3
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import QObject, QThread, Qt, QUrl, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QDesktopServices, QFont
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QFrame,
    QGridLayout,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

import config
from app.controllers.scraping_controller import ScrapingController
from app.models.depot import ProductRepository
from app.scraper.amazon_scraper import AmazonScraper
from app.views.console_view import ConsoleView
from app.views.export_view import CATEGORY_LABELS, CsvExporter



class ScraperWorker(QObject):
    progress_changed = pyqtSignal(int, str)
    message_received = pyqtSignal(str)
    completed = pyqtSignal(int, str)
    failed = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, selected_category_keys: list[str], marketplace_key: str,
                 max_products: int) -> None:
        super().__init__()
        self.selected_category_keys = selected_category_keys
        self.marketplace_key = marketplace_key
        self.max_products = max_products

    @pyqtSlot()
    def run(self) -> None:
        try:
            marketplace = config.MARKETPLACES[self.marketplace_key]
            language_queries = config.CATEGORY_QUERIES[marketplace["language"]]
            selected_categories = {
                key: language_queries[key] for key in self.selected_category_keys
            }
            scraper = AmazonScraper(
                categories=selected_categories,
                max_products_total=self.max_products,
                on_message=self.message_received.emit,
                on_progress=self.progress_changed.emit,
                base_url=marketplace["url"],
                marketplace=marketplace["label"],
                language=marketplace["locale"],
            )
            controller = ScrapingController(
                scraper=scraper,
                repository=ProductRepository(config.DATABASE_PATH),
                exporter=CsvExporter(config.CSV_PATH),

                view=ConsoleView(),
            )
            products = controller.run()
            self.completed.emit(len(products), marketplace["label"])
        except Exception as error:
            self.failed.emit(str(error))
        finally:
            self.finished.emit()

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Amazon Scraper")
        self.resize(1240, 820)
        self.setMinimumSize(1080, 700)
        self.thread: QThread | None = None
        self.worker: ScraperWorker | None = None
        self.category_checks: dict[str, QCheckBox] = {}
        self._build_ui()
        self._apply_style()
        self._append_log("Prêt. Choisis les catégories puis lance la collecte.")

    def _build_ui(self) -> None:
        central = QWidget()
        central.setObjectName("background")
        root = QVBoxLayout(central)
        root.setContentsMargins(30, 24, 30, 24)
        root.setSpacing(20)

        header = QHBoxLayout()
        title_stack = QVBoxLayout()
        title = QLabel("Amazon Scraper")
        title.setObjectName("title")
        subtitle = QLabel("Collecte organisée, données sauvegardées localement")
        subtitle.setObjectName("subtitle")
        title_stack.addWidget(title)
        title_stack.addWidget(subtitle)
        header.addLayout(title_stack)
        header.addStretch()
        self.status_badge = QLabel("●  PRÊT")
        self.status_badge.setObjectName("statusBadge")
        header.addWidget(self.status_badge, alignment=Qt.AlignmentFlag.AlignTop)
        root.addLayout(header)

        content = QHBoxLayout()
        content.setSpacing(18)
        left_panel = self._panel()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(22, 20, 22, 22)
        left_layout.setSpacing(16)

        category_heading = QLabel("Catégories à explorer")
        category_heading.setObjectName("sectionTitle")
        category_note = QLabel("Sélectionne une ou plusieurs familles de produits.")
        category_note.setObjectName("muted")
        left_layout.addWidget(category_heading)
        left_layout.addWidget(category_note)

        categories_grid = QGridLayout()
        categories_grid.setHorizontalSpacing(10)
        categories_grid.setVerticalSpacing(10)
        for index, (key, query) in enumerate(config.CATEGORIES.items()):
            checkbox = QCheckBox(CATEGORY_LABELS.get(key, key.replace("_", " ").title()))
            checkbox.setChecked(True)
            checkbox.setProperty("categoryKey", key)
            checkbox.setToolTip(f"Recherche Amazon : {query}")
            checkbox.setMinimumHeight(40)
            self.category_checks[key] = checkbox
            categories_grid.addWidget(checkbox, index // 2, index % 2)
        left_layout.addLayout(categories_grid)

        market_row = QHBoxLayout()
        market_label = QLabel("Boutique Amazon")
        market_label.setObjectName("fieldLabel")
        self.market_combo = QComboBox()
        for marketplace_key, marketplace in config.MARKETPLACES.items():
            self.market_combo.addItem(marketplace["label"], marketplace_key)
        market_row.addWidget(market_label)
        market_row.addStretch()
        market_row.addWidget(self.market_combo, 1)
        left_layout.addLayout(market_row)
        limit_row = QHBoxLayout()
        limit_label = QLabel("Maximum de produits")
        limit_label.setObjectName("fieldLabel")
        self.limit_spin = QSpinBox()
        self.limit_spin.setRange(1, config.MAX_PRODUCTS_TOTAL)
        self.limit_spin.setValue(config.MAX_PRODUCTS_TOTAL)
        self.limit_spin.setSuffix(" produits")
        limit_row.addWidget(limit_label)
        limit_row.addStretch()
        limit_row.addWidget(self.limit_spin)
        left_layout.addLayout(limit_row)

        note = QLabel("Le plafond s’applique à la collecte entière. Aucun lien produit n’est enregistré.")
        note.setObjectName("hint")
        note.setWordWrap(True)
        left_layout.addWidget(note)

        self.start_button = QPushButton("▶   Lancer la collecte")
        self.start_button.setObjectName("primaryButton")
        self.start_button.setMinimumHeight(48)
        self.start_button.clicked.connect(self._start_scraping)
        left_layout.addWidget(self.start_button)

        outputs_title = QLabel("Fichiers générés")
        outputs_title.setObjectName("sectionTitle")
        left_layout.addWidget(outputs_title)
        outputs_info = QLabel("SQLite  ·  CSV")
        outputs_info.setObjectName("outputInfo")
        left_layout.addWidget(outputs_info)
        self.open_database_button = QPushButton("Consulter la base SQLite")
        self.open_database_button.setObjectName("secondaryButton")
        self.open_database_button.clicked.connect(self._open_database)
        left_layout.addWidget(self.open_database_button)
        self.open_exports_button = QPushButton("Ouvrir le dossier des exports")
        self.open_exports_button.setObjectName("secondaryButton")
        self.open_exports_button.clicked.connect(self._open_exports)
        left_layout.addWidget(self.open_exports_button)
        left_layout.addStretch()

        right_panel = self._panel()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(22, 20, 22, 22)
        right_layout.setSpacing(14)
        right_heading = QLabel("Suivi de la collecte")
        right_heading.setObjectName("sectionTitle")
        right_layout.addWidget(right_heading)
        self.progress_text = QLabel("En attente de démarrage")
        self.progress_text.setObjectName("progressText")
        right_layout.addWidget(self.progress_text)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        right_layout.addWidget(self.progress_bar)

        self.result_label = QLabel("Aucune collecte effectuée dans cette session")
        self.result_label.setObjectName("resultCard")
        self.result_label.setWordWrap(True)
        right_layout.addWidget(self.result_label)

        log_heading = QLabel("Journal")
        log_heading.setObjectName("fieldLabel")
        right_layout.addWidget(log_heading)
        self.log_view = QPlainTextEdit()
        self.log_view.setObjectName("logView")
        self.log_view.setReadOnly(True)
        self.log_view.setPlaceholderText("Les étapes de la collecte apparaîtront ici…")
        right_layout.addWidget(self.log_view, 1)

        content.addWidget(left_panel, 5)
        content.addWidget(right_panel, 6)
        root.addLayout(content, 1)

        self.setCentralWidget(central)

    @staticmethod
    def _panel() -> QFrame:
        panel = QFrame()
        panel.setObjectName("panel")
        return panel

    def _apply_style(self) -> None:
        self.setStyleSheet("""
            QWidget#background { background: #fff4f9; color: #382a32; }
            QFrame#panel { background: #ffffff; border: 1px solid #f0c1d6; border-radius: 9px; }
            QLabel#title { color: #382a32; font-size: 27px; font-weight: 650; }
            QLabel#subtitle, QLabel#muted, QLabel#footer { color: #8c7781; }
            QLabel#subtitle { font-size: 13px; }
            QLabel#footer { font-size: 11px; }
            QLabel#sectionTitle { color: #42313a; font-size: 16px; font-weight: 650; }
            QLabel#fieldLabel { color: #604c56; font-size: 13px; font-weight: 600; }
            QLabel#statusBadge { background: #fce0ed; color: #a51e61; border-radius: 5px; padding: 7px 10px; font-weight: 650; }
            QLabel#hint { background: #fff0f6; color: #755b67; border-left: 3px solid #e83e8c; border-radius: 4px; padding: 10px; font-size: 12px; }
            QLabel#outputInfo { color: #745968; font-weight: 550; padding: 4px 0; }
            QLabel#progressText { color: #58434e; font-weight: 600; }
            QLabel#resultCard { background: #fff5f8; border: 1px solid #f2dce5; border-radius: 6px; padding: 12px; color: #705866; }
            QCheckBox { background: #ffffff; border: 1px solid #efc7d9; border-radius: 5px; padding: 10px 9px; color: #55414b; font-size: 12px; font-weight: 550; }
            QCheckBox:hover { border-color: #e83e8c; background: #fff0f6; }
            QCheckBox::indicator { width: 17px; height: 17px; }
            QSpinBox { border: 1px solid #ead3dd; border-radius: 5px; background: #ffffff; padding: 7px 9px; min-width: 118px; color: #493740; }
            QPushButton { border-radius: 5px; padding: 10px 12px; font-weight: 650; }
            QPushButton#primaryButton { background: #e83e8c; color: #ffffff; border: none; font-size: 14px; }
            QPushButton#primaryButton:hover { background: #d92f7c; }
            QPushButton#primaryButton:disabled { background: #efa0c3; color: #fffafd; }
            QPushButton#secondaryButton { background: #fff0f6; color: #9c255e; border: 1px solid #efbfd4; }
            QPushButton#secondaryButton:hover { background: #fbd9e8; border-color: #e83e8c; }
            QProgressBar { height: 12px; border: 1px solid #efbfd4; border-radius: 4px; background: #fff0f6; text-align: center; color: transparent; }
            QProgressBar::chunk { border-radius: 3px; background: #e83e8c; }
            QTableWidget { background: #ffffff; alternate-background-color: #fff5f9; color: #493740; border: 1px solid #efbfd4; gridline-color: #f3d8e4; selection-background-color: #f5a3c5; selection-color: #382a32; }
            QHeaderView::section { background: #fce0ed; color: #8f1d55; border: none; border-bottom: 1px solid #e83e8c; padding: 8px; font-weight: 650; }
            QPlainTextEdit#logView { border: 1px solid #efbfd4; border-radius: 6px; background: #fffdfd; color: #66515c; padding: 9px; font-family: Consolas, monospace; font-size: 11px; }
        """)
    def _append_log(self, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_view.appendPlainText(f"{timestamp}  {message}")

    def _start_scraping(self) -> None:
        selected = {
            key: config.CATEGORIES[key]
            for key, checkbox in self.category_checks.items()
            if checkbox.isChecked()
        }
        if not selected:
            QMessageBox.information(self, "Sélection requise", "Choisis au moins une catégorie.")
            return

        self.start_button.setEnabled(False)
        for checkbox in self.category_checks.values():
            checkbox.setEnabled(False)
        self.limit_spin.setEnabled(False)
        self.market_combo.setEnabled(False)
        self.status_badge.setText("●  EN COURS")
        self.status_badge.setStyleSheet("background:#fde8f0;color:#a23b66;border-radius:5px;padding:7px 10px;font-weight:650")
        self.progress_bar.setValue(0)
        self.result_label.setText("Chrome va s’ouvrir. La progression apparaîtra ici.")
        self._append_log(f"Démarrage sur {self.market_combo.currentText()}…")

        self.thread = QThread(self)
        self.worker = ScraperWorker(list(selected), self.market_combo.currentData(), self.limit_spin.value())
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.progress_changed.connect(self._update_progress)
        self.worker.message_received.connect(self._append_log)
        self.worker.completed.connect(self._scrape_completed)
        self.worker.failed.connect(self._scrape_failed)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self._thread_finished)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def _update_progress(self, percent: int, message: str) -> None:
        self.progress_bar.setValue(percent)
        self.progress_text.setText(message)

    def _scrape_completed(self, count: int, marketplace: str) -> None:
        self.progress_bar.setValue(100)
        self.progress_text.setText("Collecte terminée")
        self.status_badge.setText("●  TERMINÉ")
        self.status_badge.setStyleSheet("background:#f8dce8;color:#96385f;border-radius:5px;padding:7px 10px;font-weight:650")
        self.result_label.setText(
            f"{count} produit(s) enregistré(s) pour {marketplace}, dans SQLite et le CSV."
        )
        self._append_log(f"Collecte terminée : {count} produit(s).")

    def _scrape_failed(self, message: str) -> None:
        self.status_badge.setText("●  ERREUR")
        self.status_badge.setStyleSheet("background:#fff0f0;color:#a94858;border-radius:5px;padding:7px 10px;font-weight:650")
        self.progress_text.setText("La collecte s’est arrêtée")
        self.result_label.setText(message)
        self._append_log(f"Erreur : {message}")
        QMessageBox.warning(self, "Collecte interrompue", message)

    def _thread_finished(self) -> None:
        self.start_button.setEnabled(True)
        for checkbox in self.category_checks.values():
            checkbox.setEnabled(True)
        self.limit_spin.setEnabled(True)
        self.market_combo.setEnabled(True)
        self.thread = None
        self.worker = None

    def _open_database(self) -> None:
        if not config.DATABASE_PATH.is_file():
            QMessageBox.information(self, "Base SQLite", "Aucune base de données n’a encore été créée.")
            return

        try:
            rows = ProductRepository(config.DATABASE_PATH).fetch_all()
        except sqlite3.Error as error:
            QMessageBox.warning(self, "Base SQLite", f"Impossible de lire la base de données : {error}")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Produits enregistrés dans SQLite")
        dialog.resize(1100, 600)
        layout = QVBoxLayout(dialog)
        summary = QLabel(f"{len(rows)} produit(s) enregistré(s) dans la base de données")
        summary.setObjectName("sectionTitle")
        layout.addWidget(summary)

        headers = ("ID", "Boutique", "Catégorie", "Produit", "Prix", "Note", "Avis", "Disponibilité", "Dernière collecte")
        table = QTableWidget(len(rows), len(headers), dialog)
        table.setHorizontalHeaderLabels(headers)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setAlternatingRowColors(True)
        for row_index, values in enumerate(rows):
            for column_index, value in enumerate(values):
                if column_index == 2:
                    value = CATEGORY_LABELS.get(value, value)
                table.setItem(row_index, column_index, QTableWidgetItem("" if value is None else str(value)))
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(table)

        close_button = QPushButton("Fermer")
        close_button.setObjectName("primaryButton")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignRight)
        dialog.exec()

    def _open_exports(self) -> None:
        config.EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(config.EXPORT_DIR.resolve())))


def run_app() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Amazon Scraper")
    app.setFont(QFont("Segoe UI", 10))
    window = MainWindow()
    window.show()
    return app.exec()
