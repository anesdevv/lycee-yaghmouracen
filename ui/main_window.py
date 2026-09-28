from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QLabel, QComboBox, QSpacerItem, QSizePolicy, QMessageBox
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from ui.dashboard import DashboardScreen
from ui.students import StudentScreen
from ui.classes import ClassScreen
from ui.employees import EmployeeScreen
from ui.attendance import AttendanceScreen
from ui.exports import ExportsScreen
from services.translation_service import TranslationService, tr
from services.auth_service import AuthService

class MainWindow(QMainWindow):
    # Emit signal when user logs out
    logout_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.trans = TranslationService.get_instance()
        self.auth_service = AuthService.get_instance()
        
        self.init_ui()
        
        # Register for translation listeners
        self.trans.register_listener(self.update_translation)
        self.update_translation()
        
        # Navigate to Dashboard initially
        self.navigate_to_dashboard()

    def init_ui(self):
        self.resize(1150, 750)
        self.setMinimumSize(1000, 680)
        
        # Center Widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        
        main_hbox = QHBoxLayout(central_widget)
        main_hbox.setContentsMargins(0, 0, 0, 0)
        main_hbox.setSpacing(0)
        
        # =============================================================
        # 1. Dark Blue Sidebar Widget
        # =============================================================
        sidebar = QWidget(central_widget)
        sidebar.setFixedWidth(240)
        sidebar.setObjectName("Sidebar")
        sidebar.setStyleSheet("""
            QWidget#Sidebar {
                background-color: #F1F5F9; /* Clean light gray sidebar background */
                border-right: 1px solid #E2E8F0;
            }
            QPushButton {
                background-color: transparent;
                color: #475569;
                border: none;
                border-radius: 8px;
                padding: 12px 15px;
                text-align: left;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
                color: #0F172A;
            }
            QPushButton:checked {
                background-color: #2563EB; /* Clean Accent Blue highlight */
                color: #FFFFFF;
            }
        """)
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 30, 20, 30)
        sidebar_layout.setSpacing(8)
        
        # School logo branding
        self.sidebar_school = QLabel("Lycée\nYaghmouracen", sidebar)
        self.sidebar_school.setStyleSheet("font-size: 20px; font-weight: bold; color: #0F172A; line-height: 24px;")
        self.sidebar_school.setAlignment(Qt.AlignLeft)
        sidebar_layout.addWidget(self.sidebar_school)
        
        sidebar_layout.addSpacing(30)
        
        # Nav buttons
        self.btn_dash = QPushButton("📊  Dashboard", sidebar)
        self.btn_dash.setCheckable(True)
        self.btn_dash.clicked.connect(self.navigate_to_dashboard)
        sidebar_layout.addWidget(self.btn_dash)
        
        self.btn_students = QPushButton("👥  Students", sidebar)
        self.btn_students.setCheckable(True)
        self.btn_students.clicked.connect(self.navigate_to_students)
        sidebar_layout.addWidget(self.btn_students)
        
        self.btn_classes = QPushButton("🏫  Classes", sidebar)
        self.btn_classes.setCheckable(True)
        self.btn_classes.clicked.connect(self.navigate_to_classes)
        sidebar_layout.addWidget(self.btn_classes)
        
        self.btn_attendance = QPushButton("📅  Attendance", sidebar)
        self.btn_attendance.setCheckable(True)
        self.btn_attendance.clicked.connect(self.navigate_to_attendance)
        sidebar_layout.addWidget(self.btn_attendance)
        
        self.btn_employees = QPushButton("💼  Employees", sidebar)
        self.btn_employees.setCheckable(True)
        self.btn_employees.clicked.connect(self.navigate_to_employees)
        sidebar_layout.addWidget(self.btn_employees)
        
        self.btn_exports = QPushButton("📂  Exports & Reports", sidebar)
        self.btn_exports.setCheckable(True)
        self.btn_exports.clicked.connect(self.navigate_to_exports)
        sidebar_layout.addWidget(self.btn_exports)
        
        # Spacer
        sidebar_layout.addStretch(1)
        
        # Info Button
        self.btn_info = QPushButton("ℹ️  About", sidebar)
        self.btn_info.clicked.connect(self.show_about_dialog)
        self.btn_info.setStyleSheet("""
            QPushButton {
                color: #2563EB;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
                color: #1E40AF;
            }
        """)
        sidebar_layout.addWidget(self.btn_info)
        
        # Logout
        self.btn_logout = QPushButton("🚪  Logout", sidebar)
        self.btn_logout.clicked.connect(self.handle_logout)
        self.btn_logout.setStyleSheet("""
            QPushButton {
                color: #DC2626;
            }
            QPushButton:hover {
                background-color: #FEE2E2;
                color: #B91C1C;
            }
        """)
        sidebar_layout.addWidget(self.btn_logout)
        
        main_hbox.addWidget(sidebar)
        
        # =============================================================
        # 2. Main Content Stack Panel (VBox with Header + Stack)
        # =============================================================
        content_pane = QWidget(central_widget)
        content_layout = QVBoxLayout(content_pane)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Top Header Navbar (Fully Themed for Light Mode)
        navbar = QWidget(content_pane)
        navbar.setFixedHeight(65)
        navbar.setStyleSheet("""
            QWidget {
                background-color: #F1F5F9;
                border-bottom: 1.5px solid #E2E8F0;
            }
        """)
        navbar_layout = QHBoxLayout(navbar)
        navbar_layout.setContentsMargins(30, 0, 30, 0)
        
        # Active Section Title Indicator
        self.section_title = QLabel("Dashboard", navbar)
        self.section_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #0F172A;")
        navbar_layout.addWidget(self.section_title)
        
        navbar_layout.addStretch(1)
        
        # Logged-in admin indicator
        self.user_lbl = QLabel(navbar)
        self.user_lbl.setStyleSheet("font-size: 13px; font-weight: bold; color: #475569; margin-right: 15px;")
        navbar_layout.addWidget(self.user_lbl)
        
        # Top Language Selector (Flag toggles dropdown)
        self.lang_selector = QComboBox(navbar)
        self.lang_selector.addItem("🇫🇷 Français", "fr")
        self.lang_selector.addItem("🇺🇸 English", "en")
        self.lang_selector.setMinimumWidth(120)
        self.lang_selector.setStyleSheet("""
            QComboBox {
                border: 1.5px solid #E2E8F0;
                border-radius: 6px;
                padding: 4px 8px;
                background-color: #FFFFFF;
                color: #0F172A;
                font-weight: bold;
                font-size: 12px;
            }
        """)
        # Match current translator settings
        curr_lang = self.trans.current_language
        index = self.lang_selector.findData(curr_lang)
        if index >= 0:
            self.lang_selector.setCurrentIndex(index)
            
        self.lang_selector.currentIndexChanged.connect(self.on_lang_combo_changed)
        navbar_layout.addWidget(self.lang_selector)
        
        content_layout.addWidget(navbar)
        
        # 3. Stacked View pages switcher
        self.stacked_widget = QStackedWidget(content_pane)
        self.stacked_widget.setStyleSheet("background-color: #F8FAFC;")
        
        # Instantiate sub-views
        self.screen_dash = DashboardScreen(self.stacked_widget)
        self.screen_students = StudentScreen(self.stacked_widget)
        self.screen_classes = ClassScreen(self.stacked_widget)
        self.screen_attendance = AttendanceScreen(self.stacked_widget)
        self.screen_employees = EmployeeScreen(self.stacked_widget)
        self.screen_exports = ExportsScreen(self.stacked_widget)
        
        # Add to stack index
        self.stacked_widget.addWidget(self.screen_dash)       # Index 0
        self.stacked_widget.addWidget(self.screen_students)   # Index 1
        self.stacked_widget.addWidget(self.screen_classes)    # Index 2
        self.stacked_widget.addWidget(self.screen_attendance) # Index 3
        self.stacked_widget.addWidget(self.screen_employees)  # Index 4
        self.stacked_widget.addWidget(self.screen_exports)    # Index 5
        
        content_layout.addWidget(self.stacked_widget)
        main_hbox.addWidget(content_pane)

    def on_lang_combo_changed(self, idx):
        lang = self.lang_selector.itemData(idx)
        self.trans.set_language(lang)

    def update_sidebar_checked_state(self, checked_btn):
        # Deselect others
        self.btn_dash.setChecked(self.btn_dash == checked_btn)
        self.btn_students.setChecked(self.btn_students == checked_btn)
        self.btn_classes.setChecked(self.btn_classes == checked_btn)
        self.btn_attendance.setChecked(self.btn_attendance == checked_btn)
        self.btn_employees.setChecked(self.btn_employees == checked_btn)
        self.btn_exports.setChecked(self.btn_exports == checked_btn)

    # =============================================================
    # Stack Navigation
    # =============================================================
    def navigate_to_dashboard(self):
        self.screen_dash.refresh_data()
        self.stacked_widget.setCurrentIndex(0)
        self.update_sidebar_checked_state(self.btn_dash)
        self.section_title.setText(tr("sidebar_dashboard"))

    def navigate_to_students(self):
        self.screen_students.populate_filters()
        self.screen_students.load_students()
        self.stacked_widget.setCurrentIndex(1)
        self.update_sidebar_checked_state(self.btn_students)
        self.section_title.setText(tr("sidebar_students"))

    def navigate_to_classes(self):
        self.screen_classes.load_classes()
        self.stacked_widget.setCurrentIndex(2)
        self.update_sidebar_checked_state(self.btn_classes)
        self.section_title.setText(tr("sidebar_classes"))

    def navigate_to_attendance(self):
        self.screen_attendance.populate_classes()
        self.screen_attendance.load_history()
        self.stacked_widget.setCurrentIndex(3)
        self.update_sidebar_checked_state(self.btn_attendance)
        self.section_title.setText(tr("sidebar_attendance"))

    def navigate_to_employees(self):
        self.screen_employees.load_employees()
        self.stacked_widget.setCurrentIndex(4)
        self.update_sidebar_checked_state(self.btn_employees)
        self.section_title.setText(tr("sidebar_employees"))

    def navigate_to_exports(self):
        self.screen_exports.refresh_lists()
        self.stacked_widget.setCurrentIndex(5)
        self.update_sidebar_checked_state(self.btn_exports)
        self.section_title.setText(tr("sidebar_exports"))

    def handle_logout(self):
        self.auth_service.logout()
        self.logout_requested.emit()

    def update_translation(self):
        """Re-translate all sidebar links and top banner headers instantly."""
        self.sidebar_school.setText("Lycée\nYaghmouracen" if self.trans.current_language == 'fr' else "Yaghmouracen\nHigh School")
        self.btn_dash.setText("📊  " + tr("sidebar_dashboard"))
        self.btn_students.setText("👥  " + tr("sidebar_students"))
        self.btn_classes.setText("🏫  " + tr("sidebar_classes"))
        self.btn_attendance.setText("📅  " + tr("sidebar_attendance"))
        self.btn_employees.setText("💼  " + tr("sidebar_employees"))
        self.btn_exports.setText("📂  " + tr("sidebar_exports"))
        
        info_text = "ℹ️  À propos" if self.trans.current_language == 'fr' else "ℹ️  About"
        self.btn_info.setText(info_text)
        
        self.btn_logout.setText("🚪  " + tr("sidebar_logout"))
        
        # User dynamic card label
        username = self.auth_service.current_user or "admin"
        self.user_lbl.setText(f"👤  {username.upper()} (Admin)")
        
        # Refresh current tab section title
        curr_idx = self.stacked_widget.currentIndex()
        if curr_idx == 0:
            self.section_title.setText(tr("sidebar_dashboard"))
        elif curr_idx == 1:
            self.section_title.setText(tr("sidebar_students"))
        elif curr_idx == 2:
            self.section_title.setText(tr("sidebar_classes"))
        elif curr_idx == 3:
            self.section_title.setText(tr("sidebar_attendance"))
        elif curr_idx == 4:
            self.section_title.setText(tr("sidebar_employees"))
        elif curr_idx == 5:
            self.section_title.setText(tr("sidebar_exports"))
            
        # Keep dropdown indices synchronized if language changed elsewhere
        curr_lang = self.trans.current_language
        index = self.lang_selector.findData(curr_lang)
        if index >= 0 and self.lang_selector.currentIndex() != index:
            # Block signals to avoid recursive calling index change events
            self.lang_selector.blockSignals(True)
            self.lang_selector.setCurrentIndex(index)
            self.lang_selector.blockSignals(False)

    def show_about_dialog(self):
        """Displays a clean light-mode styled dialog with app version and creator details."""
        title = "À propos de l'application" if self.trans.current_language == 'fr' else "About Application"
        
        if self.trans.current_language == 'fr':
            message = (
                "<h3><b>Gestion Administrative</b></h3>"
                "<p><b>Version :</b> v1.1.0</p>"
                "<p><b>Créateur :</b> Mediani Abdlkader</p>"
                "<p><b>Établissement :</b> Lycée Yaghmouracen</p>"
                "<hr/>"
                "<p><i>Développé avec succès pour la gestion administrative et l'appel quotidien.</i></p>"
            )
        else:
            message = (
                "<h3><b>Administrative Management System</b></h3>"
                "<p><b>Version:</b> v1.1.0</p>"
                "<p><b>Creator:</b> Mediani Abdlkader</p>"
                "<p><b>Establishment:</b> Yaghmouracen High School</p>"
                "<hr/>"
                "<p><i>Developed successfully for school administration and daily attendance tracking.</i></p>"
            )
            
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setStandardButtons(QMessageBox.Ok)
        
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #F8FAFC;
            }
            QLabel {
                color: #0F172A;
                font-size: 13px;
            }
            QPushButton {
                background-color: #2563EB;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 6px 14px;
                font-weight: bold;
                font-size: 12px;
                min-width: 65px;
            }
            QPushButton:hover {
                background-color: #1D4ED8;
            }
        """)
        msg_box.exec()

    def closeEvent(self, event):
        self.trans.unregister_listener(self.update_translation)
        
        # Explicitly unregister all child screen translation listeners to prevent Shiboken memory/dangling callback errors
        if hasattr(self, 'screen_dash'):
            self.trans.unregister_listener(self.screen_dash.update_translation)
        if hasattr(self, 'screen_students'):
            self.trans.unregister_listener(self.screen_students.update_translation)
        if hasattr(self, 'screen_classes'):
            self.trans.unregister_listener(self.screen_classes.update_translation)
        if hasattr(self, 'screen_attendance'):
            self.trans.unregister_listener(self.screen_attendance.update_translation)
        if hasattr(self, 'screen_employees'):
            self.trans.unregister_listener(self.screen_employees.update_translation)
        if hasattr(self, 'screen_exports'):
            self.trans.unregister_listener(self.screen_exports.update_translation)
            
        super().closeEvent(event)
