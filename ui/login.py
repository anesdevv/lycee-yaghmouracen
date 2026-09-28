from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QMessageBox, QSpacerItem, QSizePolicy
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPixmap
from ui.components import SleekCard, PremiumButton
from services.translation_service import TranslationService, tr
from services.auth_service import AuthService

class LoginScreen(QWidget):
    # Emit signal when login succeeds
    login_success = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.auth_service = AuthService.get_instance()
        self.trans = TranslationService.get_instance()
        
        self.init_ui()
        
        # Register for translation changes
        self.trans.register_listener(self.update_translation)
        self.update_translation()

    def init_ui(self):
        # Force exclusive light background for standalone window display
        self.setStyleSheet("background-color: #F8FAFC;")
        
        # Outer Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Top Header Bar (specifically for language selector)
        header_bar = QHBoxLayout()
        header_bar.setContentsMargins(30, 20, 30, 10)
        header_bar.addStretch()
        
        self.lang_combobox = QComboBox(self)
        self.lang_combobox.addItem("Français (FR)", "fr")
        self.lang_combobox.addItem("English (EN)", "en")
        # Style language selector on login screen
        self.lang_combobox.setStyleSheet("""
            QComboBox {
                border: 1.5px solid #1E293B;
                border-radius: 8px;
                padding: 5px 10px;
                background-color: #111827;
                color: #F8FAFC;
                font-weight: bold;
                font-size: 12px;
                min-width: 130px;
            }
        """)
        self.lang_combobox.currentIndexChanged.connect(self.on_language_changed)
        header_bar.addWidget(self.lang_combobox)
        main_layout.addLayout(header_bar)
        
        # Add Stretch to push Card center
        main_layout.addStretch(1)
        
        # Centered Layout for Card
        card_layout = QHBoxLayout()
        card_layout.addStretch(1)
        
        # Card Body
        self.login_card = SleekCard(self)
        self.login_card.setFixedWidth(400)
        self.login_card.setFixedHeight(450)
        
        card_inner_layout = QVBoxLayout(self.login_card)
        card_inner_layout.setContentsMargins(30, 40, 30, 40)
        card_inner_layout.setSpacing(15)
        
        # School Name Logo/Branding
        self.school_title = QLabel("Lycée Yaghmouracen", self.login_card)
        self.school_title.setAlignment(Qt.AlignCenter)
        self.school_title.setStyleSheet("font-size: 22px; font-weight: bold; color: #3B82F6;")
        card_inner_layout.addWidget(self.school_title)
        
        # Title Header
        self.login_title = QLabel(self.login_card)
        self.login_title.setAlignment(Qt.AlignCenter)
        self.login_title.setStyleSheet("font-size: 15px; font-weight: 500; color: #94A3B8;")
        card_inner_layout.addWidget(self.login_title)
        
        card_inner_layout.addSpacing(15)
        
        # Form Fields
        self.username_input = QLineEdit(self.login_card)
        self.username_input.setPlaceholderText("Nom d'utilisateur")
        self.username_input.setFixedHeight(42)
        card_inner_layout.addWidget(self.username_input)
        
        self.password_input = QLineEdit(self.login_card)
        self.password_input.setPlaceholderText("Mot de passe")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(42)
        self.password_input.returnPressed.connect(self.handle_login)
        card_inner_layout.addWidget(self.password_input)
        
        # Error Label
        self.error_label = QLabel("", self.login_card)
        self.error_label.setStyleSheet("color: #E11D48; font-size: 12px; font-weight: bold;")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setWordWrap(True)
        card_inner_layout.addWidget(self.error_label)
        
        card_inner_layout.addSpacing(10)
        
        # Login Button
        self.login_btn = PremiumButton("", is_primary=True, parent=self.login_card)
        self.login_btn.setFixedHeight(42)
        self.login_btn.clicked.connect(self.handle_login)
        card_inner_layout.addWidget(self.login_btn)
        
        card_layout.addWidget(self.login_card)
        card_layout.addStretch(1)
        
        main_layout.addLayout(card_layout)
        
        # Add Stretch at bottom
        main_layout.addStretch(1.5)

    def on_language_changed(self, index):
        lang = self.lang_combobox.currentData()
        self.trans.set_language(lang)

    def update_translation(self):
        """Redraw UI labels on language toggle changes."""
        self.school_title.setText(tr("app_title"))
        self.login_title.setText(tr("login_subtitle"))
        self.username_input.setPlaceholderText(tr("username_placeholder"))
        self.password_input.setPlaceholderText(tr("password_placeholder"))
        self.login_btn.setText(tr("login_button"))
        
        # If there's an active error, translate it
        if self.error_label.text():
            self.error_label.setText(tr("login_failed_msg"))

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if self.auth_service.login(username, password):
            self.error_label.setText("")
            self.password_input.clear()
            self.login_success.emit()
        else:
            self.error_label.setText(tr("login_failed_msg"))

    def closeEvent(self, event):
        # Clean up translation listener on close
        self.trans.unregister_listener(self.update_translation)
        super().closeEvent(event)
