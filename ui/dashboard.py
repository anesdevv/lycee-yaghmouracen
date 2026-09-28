from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QScrollArea
from PySide6.QtCore import Qt, QTimer, QDateTime
from ui.components import SleekCard
from services.translation_service import TranslationService, tr
import database.db as db

class DashboardScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.trans = TranslationService.get_instance()
        self.init_ui()
        
        # Clock timer (updates every second)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)
        
        # Initial updates
        self.update_clock()
        
        # Register translation listener
        self.trans.register_listener(self.update_translation)
        self.update_translation()
        
    def init_ui(self):
        # Outer main layout for the screen
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll Area to prevent bottom section (Date & Time card) from being cut off on low resolution/scaled displays
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Container widget for scroll area content
        container = QWidget()
        container.setObjectName("DashboardContainer")
        container.setStyleSheet("QWidget#DashboardContainer { background-color: transparent; }")
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)
        
        # Welcome Banner Header
        welcome_layout = QVBoxLayout()
        welcome_layout.setSpacing(5)
        
        self.welcome_title = QLabel(container)
        self.welcome_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2563EB;")
        welcome_layout.addWidget(self.welcome_title)
        
        self.welcome_subtitle = QLabel(container)
        self.welcome_subtitle.setStyleSheet("font-size: 14px; color: #475569;")
        welcome_layout.addWidget(self.welcome_subtitle)
        
        layout.addLayout(welcome_layout)
        
        # Grid layout for Stat Cards (2x2 structure)
        stats_grid = QGridLayout()
        stats_grid.setSpacing(20)
        
        # 1. Total Students Card
        self.card_students = SleekCard(container)
        self.setup_stat_card(self.card_students, "👥", tr("dash_total_students"), "0", "#3B82F6")
        stats_grid.addWidget(self.card_students, 0, 0)
        
        # 2. Total Employees Card
        self.card_employees = SleekCard(container)
        self.setup_stat_card(self.card_employees, "💼", tr("dash_total_employees"), "0", "#10B981")
        stats_grid.addWidget(self.card_employees, 0, 1)
        
        # 3. Total Classes Card
        self.card_classes = SleekCard(container)
        self.setup_stat_card(self.card_classes, "🏫", tr("dash_total_classes"), "0", "#8B5CF6")
        stats_grid.addWidget(self.card_classes, 1, 0)
        
        # 4. Total Absences Card
        self.card_absences = SleekCard(container)
        self.setup_stat_card(self.card_absences, "⚠️", tr("dash_total_absences"), "0", "#EF4444")
        stats_grid.addWidget(self.card_absences, 1, 1)
        
        layout.addLayout(stats_grid)
        
        # Time & Info Card at bottom
        self.info_card = SleekCard(container)
        self.info_card.setFixedHeight(120)
        info_layout = QHBoxLayout(self.info_card)
        info_layout.setContentsMargins(25, 20, 25, 20)
        
        clock_icon = QLabel("🕒", self.info_card)
        clock_icon.setStyleSheet("font-size: 32px;")
        info_layout.addWidget(clock_icon)
        
        time_details_layout = QVBoxLayout()
        time_details_layout.setSpacing(5)
        
        self.time_label_title = QLabel(self.info_card)
        self.time_label_title.setStyleSheet("font-size: 13px; font-weight: bold; color: #475569;")
        time_details_layout.addWidget(self.time_label_title)
        
        self.clock_display = QLabel(self.info_card)
        self.clock_display.setStyleSheet("font-size: 22px; font-weight: bold; color: #0F172A;")
        time_details_layout.addWidget(self.clock_display)
        
        info_layout.addLayout(time_details_layout)
        info_layout.addStretch(1)
        
        layout.addWidget(self.info_card)
        layout.addStretch(1)
        
        # Set container to scroll area and add scroll area to main layout
        self.scroll_area.setWidget(container)
        main_layout.addWidget(self.scroll_area)

    def setup_stat_card(self, card, icon, label_text, count_val, color_hex):
        """Build elements within a statistics card."""
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(20)
        
        # Big emoji icon
        icon_label = QLabel(icon, card)
        icon_label.setStyleSheet(f"font-size: 40px; color: {color_hex};")
        card_layout.addWidget(icon_label)
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)
        
        card.label = QLabel(label_text, card)
        card.label.setStyleSheet("font-size: 14px; font-weight: bold; color: #64748B;")
        text_layout.addWidget(card.label)
        
        card.count = QLabel(count_val, card)
        card.count.setStyleSheet(f"font-size: 26px; font-weight: bold; color: {color_hex};")
        text_layout.addWidget(card.count)
        
        card_layout.addLayout(text_layout)
        card_layout.addStretch(1)

    def update_clock(self):
        """Update live clock text labels."""
        now = QDateTime.currentDateTime()
        lang = self.trans.current_language
        
        if lang == "fr":
            time_str = now.toString("dddd d MMMM yyyy - HH:mm:ss")
        else:
            time_str = now.toString("dddd, MMMM d, yyyy - hh:mm:ss AP")
            
        self.clock_display.setText(time_str)

    def refresh_data(self):
        """Fetch updated statistics from sqlite3 DB."""
        stats = db.get_dashboard_stats()
        self.card_students.count.setText(str(stats["students"]))
        self.card_employees.count.setText(str(stats["employees"]))
        self.card_classes.count.setText(str(stats["classes"]))
        self.card_absences.count.setText(str(stats["absences"]))

    def update_translation(self):
        """Handle language switcher updates."""
        self.welcome_title.setText(tr("dash_welcome"))
        self.welcome_subtitle.setText(tr("dash_subtitle"))
        self.time_label_title.setText(tr("dash_time_title"))
        
        # Update cards labels
        self.card_students.label.setText(tr("dash_total_students"))
        self.card_employees.label.setText(tr("dash_total_employees"))
        self.card_classes.label.setText(tr("dash_total_classes"))
        self.card_absences.label.setText(tr("dash_total_absences"))
        
        # Trigger clock refresh
        self.update_clock()
