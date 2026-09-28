import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon
import database.db as db
from ui.login import LoginScreen
from ui.main_window import MainWindow
from ui.components import GLOBAL_STYLE, apply_light_palette

class HighSchoolApp:
    def __init__(self):
        # Create necessary directories in workspace
        self.create_directories()
        
        # Initialize Database and seed admin account
        db.init_db()
        
        # Initialize PySide6 App
        self.app = QApplication(sys.argv)
        self.app.setStyle("Fusion")
        
        # Configure Premium Typography Global Font
        font = QFont("Segoe UI", 10)
        self.app.setFont(font)
        
        # Apply global CSS stylesheet and Clean Light Palette
        self.app.setStyleSheet(GLOBAL_STYLE)
        apply_light_palette(self.app)
        
        # Set premium window icon globally
        root_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(root_dir, "assets", "icons", "icon.png")
        if os.path.exists(icon_path):
            self.app.setWindowIcon(QIcon(icon_path))
            
        # Session views
        self.login_window = None
        self.main_window = None

    def create_directories(self):
        """Build required folders on startup."""
        root_dir = os.path.dirname(os.path.abspath(__file__))
        folders = [
            os.path.join(root_dir, "database"),
            os.path.join(root_dir, "exports"),
            os.path.join(root_dir, "assets", "icons"),
            os.path.join(root_dir, "assets", "images", "students"),
        ]
        for folder in folders:
            os.makedirs(folder, exist_ok=True)

    def show_login(self):
        """Instantiate and show the authentication view."""
        if self.main_window:
            self.main_window.close()
            self.main_window = None
            
        self.login_window = LoginScreen()
        self.login_window.setWindowTitle("Lycée Yaghmouracen — Connexion")
        self.login_window.resize(600, 550)
        
        # Connect success signal to open main dashboard
        self.login_window.login_success.connect(self.show_main_window)
        self.login_window.show()

    def show_main_window(self):
        """Instantiate and transition into the primary main window dashboard."""
        if self.login_window:
            self.login_window.close()
            self.login_window = None
            
        self.main_window = MainWindow()
        self.main_window.setWindowTitle("Lycée Yaghmouracen — Gestion Administrative")
        
        # Connect logout signal to return to auth login
        self.main_window.logout_requested.connect(self.show_login)
        self.main_window.show()

    def run(self):
        self.show_login()
        sys.exit(self.app.exec())

if __name__ == "__main__":
    # Boot the application
    app_runner = HighSchoolApp()
    app_runner.run()
