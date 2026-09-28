import os
from datetime import datetime
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget,
                             QDateEdit, QComboBox, QMessageBox, QTableWidgetItem, QHeaderView)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QColor
from ui.components import SleekCard, PremiumButton, ModernTable, create_table_item
from services.translation_service import TranslationService, tr
import database.db as db

class AttendanceScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.trans = TranslationService.get_instance()
        self.daily_status_map = {} # Track active selected status student_id -> 'Present' or 'Absent'
        
        self.init_ui()
        self.populate_classes()
        self.load_history()
        
        # Register translation changes listener
        self.trans.register_listener(self.update_translation)
        self.update_translation()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header Panel
        header_layout = QHBoxLayout()
        title_vbox = QVBoxLayout()
        
        self.title_label = QLabel(self)
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2563EB;")
        title_vbox.addWidget(self.title_label)
        
        self.subtitle_label = QLabel(self)
        self.subtitle_label.setStyleSheet("font-size: 13px; color: #94A3B8;")
        title_vbox.addWidget(self.subtitle_label)
        
        header_layout.addLayout(title_vbox)
        layout.addLayout(header_layout)
        
        # Main Tab Widget
        self.tab_widget = QTabWidget(self)
        
        # -------------------------------------------------------------
        # Tab 1: Daily Appel Sheet
        # -------------------------------------------------------------
        self.daily_tab = QWidget()
        daily_layout = QVBoxLayout(self.daily_tab)
        daily_layout.setContentsMargins(20, 20, 20, 20)
        daily_layout.setSpacing(15)
        
        # Upper control bar
        controls_card = SleekCard(self.daily_tab)
        controls_card.setMinimumHeight(75)
        controls_layout = QHBoxLayout(controls_card)
        controls_layout.setContentsMargins(20, 10, 20, 10)
        controls_layout.setSpacing(15)
        
        # Date selector
        self.date_label = QLabel(controls_card)
        self.date_label.setStyleSheet("font-weight: bold; color: #94A3B8;")
        controls_layout.addWidget(self.date_label)
        
        self.daily_date = QDateEdit(controls_card)
        self.daily_date.setCalendarPopup(True)
        self.daily_date.setDate(QDate.currentDate())
        self.daily_date.setDisplayFormat("dd/MM/yyyy")
        controls_layout.addWidget(self.daily_date)
        
        # Class Selector
        self.class_label = QLabel(controls_card)
        self.class_label.setStyleSheet("font-weight: bold; color: #94A3B8;")
        controls_layout.addWidget(self.class_label)
        
        self.daily_class = QComboBox(controls_card)
        controls_layout.addWidget(self.daily_class)
        
        # Load Button
        self.load_btn = PremiumButton("", is_primary=True, parent=controls_card)
        self.load_btn.clicked.connect(self.load_daily_roster)
        controls_layout.addWidget(self.load_btn)
        
        controls_layout.addStretch(1)
        daily_layout.addWidget(controls_card)
        
        # Roster Table
        self.roster_table = ModernTable(self.daily_tab)
        self.roster_table.setColumnCount(3)
        
        h_roster = self.roster_table.horizontalHeader()
        h_roster.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents) # ID
        h_roster.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)          # Full Name
        h_roster.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)            # Presence switcher
        self.roster_table.setColumnWidth(2, 220)
        
        daily_layout.addWidget(self.roster_table)
        
        # Save Button Footer
        footer_layout = QHBoxLayout()
        footer_layout.addStretch(1)
        self.save_btn = PremiumButton("", is_primary=True, parent=self.daily_tab)
        self.save_btn.clicked.connect(self.save_attendance)
        self.save_btn.setEnabled(False)
        footer_layout.addWidget(self.save_btn)
        daily_layout.addLayout(footer_layout)
        
        self.tab_widget.addTab(self.daily_tab, "")
        
        # -------------------------------------------------------------
        # Tab 2: Attendance Logs History
        # -------------------------------------------------------------
        self.history_tab = QWidget()
        history_layout = QVBoxLayout(self.history_tab)
        history_layout.setContentsMargins(20, 20, 20, 20)
        history_layout.setSpacing(15)
        
        # History filter ribbon card
        history_card = SleekCard(self.history_tab)
        history_card.setMinimumHeight(75)
        history_filt_layout = QHBoxLayout(history_card)
        history_filt_layout.setContentsMargins(20, 10, 20, 10)
        history_filt_layout.setSpacing(15)
        
        # Start Date
        self.hist_from_label = QLabel(history_card)
        self.hist_from_label.setStyleSheet("font-weight: bold; color: #94A3B8;")
        history_filt_layout.addWidget(self.hist_from_label)
        
        self.hist_from_date = QDateEdit(history_card)
        self.hist_from_date.setCalendarPopup(True)
        self.hist_from_date.setDate(QDate.currentDate().addDays(-30)) # default 1 month ago
        self.hist_from_date.setDisplayFormat("dd/MM/yyyy")
        history_filt_layout.addWidget(self.hist_from_date)
        
        # End Date
        self.hist_to_label = QLabel(history_card)
        self.hist_to_label.setStyleSheet("font-weight: bold; color: #94A3B8;")
        history_filt_layout.addWidget(self.hist_to_label)
        
        self.hist_to_date = QDateEdit(history_card)
        self.hist_to_date.setCalendarPopup(True)
        self.hist_to_date.setDate(QDate.currentDate())
        self.hist_to_date.setDisplayFormat("dd/MM/yyyy")
        history_filt_layout.addWidget(self.hist_to_date)
        
        # Class Selector
        self.hist_class_label = QLabel(history_card)
        self.hist_class_label.setStyleSheet("font-weight: bold; color: #94A3B8;")
        history_filt_layout.addWidget(self.hist_class_label)
        
        self.hist_class = QComboBox(history_card)
        history_filt_layout.addWidget(self.hist_class)
        
        # Filter Button
        self.filter_btn = PremiumButton("", is_primary=True, parent=history_card)
        self.filter_btn.clicked.connect(self.load_history)
        history_filt_layout.addWidget(self.filter_btn)
        
        history_filt_layout.addStretch(1)
        history_layout.addWidget(history_card)
        
        # History Table
        self.history_table = ModernTable(self.history_tab)
        self.history_table.setColumnCount(4)
        
        h_hist = self.history_table.horizontalHeader()
        h_hist.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents) # Date
        h_hist.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)          # Full Name
        h_hist.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents) # Class
        h_hist.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents) # Status
        
        history_layout.addWidget(self.history_table)
        
        self.tab_widget.addTab(self.history_tab, "")
        
        layout.addWidget(self.tab_widget)

    def populate_classes(self):
        self.daily_class.clear()
        self.hist_class.clear()
        
        self.hist_class.addItem("All / Tous", "")
        
        self.daily_class.blockSignals(True)
        self.hist_class.blockSignals(True)
        classes = db.get_classes()
        for c in classes:
            name = c['name']
            self.daily_class.addItem(name, name)
            self.hist_class.addItem(name, name)
        self.daily_class.blockSignals(False)
        self.hist_class.blockSignals(False)

    def load_daily_roster(self):
        date_str = self.daily_date.date().toString("dd/MM/yyyy")
        class_name = self.daily_class.currentText().strip()
        
        if not class_name:
            QMessageBox.warning(
                self,
                tr("warning"),
                "Please select or create a class first." if self.trans.current_language == 'en'
                else "Veuillez d'abord sélectionner ou créer une classe."
            )
            self.save_btn.setEnabled(False)
            return

        roster = db.get_attendance_for_date_and_class(date_str, class_name)
        
        self.roster_table.setRowCount(0)
        self.daily_status_map.clear()
        
        if not roster:
            QMessageBox.information(self, tr("info") if tr("info") != "info" else "Information", 
                                    "No students registered in this class. Add students first." if self.trans.current_language == 'en' else
                                    "Aucun élève inscrit dans cette classe. Enregistrez des élèves d'abord.")
            self.save_btn.setEnabled(False)
            return
            
        is_fr = (self.trans.current_language == "fr")
        pres_text = "Présent" if is_fr else "Present"
        abs_text = "Absent"

        for s in roster:
            row_idx = self.roster_table.rowCount()
            self.roster_table.insertRow(row_idx)
            
            # ID
            id_item = create_table_item(s['student_id'], Qt.AlignCenter)
            self.roster_table.setItem(row_idx, 0, id_item)
            
            # Student Name
            fullname = f"{s['last_name'].upper()} {s['first_name']}"
            name_item = create_table_item(fullname)
            self.roster_table.setItem(row_idx, 1, name_item)
            
            # Switcher Widget
            # Initial status from DB, fallback to 'Present'
            status = s['status'] if s['status'] else 'Present'
            self.daily_status_map[s['student_id']] = status
            
            switcher_widget = QWidget()
            switcher_layout = QHBoxLayout(switcher_widget)
            switcher_layout.setContentsMargins(10, 2, 10, 2)
            switcher_layout.setSpacing(8)
            
            # Present Button
            pres_btn = PremiumButton(pres_text, is_primary=True, parent=switcher_widget)
            pres_btn.setFixedSize(85, 28)
            
            # Absent Button
            abs_btn = PremiumButton(abs_text, is_primary=False, parent=switcher_widget)
            abs_btn.setFixedSize(85, 28)
            
            # Set visual states
            self.style_switcher_buttons(pres_btn, abs_btn, status)
            
            pres_btn.clicked.connect(lambda checked=False, sid=s['student_id'], pb=pres_btn, ab=abs_btn: self.on_status_toggled(sid, 'Present', pb, ab))
            abs_btn.clicked.connect(lambda checked=False, sid=s['student_id'], pb=pres_btn, ab=abs_btn: self.on_status_toggled(sid, 'Absent', pb, ab))
            
            switcher_layout.addWidget(pres_btn)
            switcher_layout.addWidget(abs_btn)
            
            self.roster_table.setCellWidget(row_idx, 2, switcher_widget)
            
        self.save_btn.setEnabled(True)

    def on_status_toggled(self, student_id, status, pres_btn, abs_btn):
        self.daily_status_map[student_id] = status
        self.style_switcher_buttons(pres_btn, abs_btn, status)

    def style_switcher_buttons(self, pres_btn, abs_btn, status):
        """Apply active green/red glows to chosen button switcher states."""
        # Simple local styling overrides for buttons
        if status == 'Present':
            # Present active (Green)
            pres_btn.setStyleSheet("""
                QPushButton {
                    background-color: #10B981; /* Emerald Green */
                    color: #FFFFFF;
                    border: none;
                    border-radius: 6px;
                    font-size: 11px;
                    font-weight: bold;
                }
            """)
            abs_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FFFFFF; /* White Background */
                    color: #475569;
                    border: 1.5px solid #CBD5E1;
                    border-radius: 6px;
                    font-size: 11px;
                    font-weight: bold;
                }
            """)
        else:
            # Absent active (Crimson Red)
            pres_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FFFFFF;
                    color: #475569;
                    border: 1.5px solid #CBD5E1;
                    border-radius: 6px;
                    font-size: 11px;
                    font-weight: bold;
                }
            """)
            abs_btn.setStyleSheet("""
                QPushButton {
                    background-color: #EF4444; /* Bright Red */
                    color: #FFFFFF;
                    border: none;
                    border-radius: 6px;
                    font-size: 11px;
                    font-weight: bold;
                }
            """)

    def save_attendance(self):
        date_str = self.daily_date.date().toString("dd/MM/yyyy")
        
        # Save all mapped values in a single atomic database batch
        records = [(student_id, date_str, status) for student_id, status in self.daily_status_map.items()]
        db.save_attendance_batch(records)
            
        QMessageBox.information(self, tr("success"), tr("att_save_success"))
        
        # Sync databases & history
        self.load_history()

    def load_history(self):
        class_name = self.hist_class.currentData()
        date_from = self.hist_from_date.date().toString("dd/MM/yyyy")
        date_to = self.hist_to_date.date().toString("dd/MM/yyyy")
        
        history = db.get_attendance_history(class_name, date_from, date_to)
        
        self.history_table.setRowCount(0)
        for h in history:
            row_idx = self.history_table.rowCount()
            self.history_table.insertRow(row_idx)
            
            # Date
            date_item = create_table_item(h['attendance_date'], Qt.AlignCenter)
            self.history_table.setItem(row_idx, 0, date_item)
            
            # Student Name
            fullname = f"{h['last_name'].upper()} {h['first_name']}"
            name_item = create_table_item(fullname)
            self.history_table.setItem(row_idx, 1, name_item)
            
            # Class
            class_item = create_table_item(h['class_name'] or "-", Qt.AlignCenter)
            self.history_table.setItem(row_idx, 2, class_item)
            
            # Status
            status_str = "Présent" if h['status'] == "Present" and self.trans.current_language == "fr" else \
                         ("Absent" if h['status'] == "Absent" and self.trans.current_language == "fr" else h['status'])
                         
            status_item = create_table_item(status_str, Qt.AlignCenter)
            
            if h['status'] == 'Present':
                status_item.setForeground(QColor("#10B981"))
                status_item.setFont(QFont("Segoe UI", 9, QFont.Bold))
            else:
                status_item.setForeground(QColor("#EF4444"))
                status_item.setFont(QFont("Segoe UI", 9, QFont.Bold))
                
            self.history_table.setItem(row_idx, 3, status_item)

    def update_translation(self):
        self.title_label.setText(tr("att_title"))
        self.subtitle_label.setText(tr("att_subtitle"))
        
        # Tabs titles
        self.tab_widget.setTabText(0, tr("att_tab_daily"))
        self.tab_widget.setTabText(1, tr("att_tab_history"))
        
        # Tab 1 Labels
        self.date_label.setText(tr("att_date_label"))
        self.class_label.setText(tr("att_class_label"))
        self.load_btn.setText(tr("att_load_roster"))
        self.save_btn.setText(tr("att_save_roster"))
        
        # Tab 1 Table Headers
        headers_roster = [
            tr("stud_tab_id"),
            tr("att_tab_name"),
            tr("att_tab_status")
        ]
        self.roster_table.setHorizontalHeaderLabels(headers_roster)
        
        # Tab 2 Labels
        self.hist_from_label.setText(tr("att_hist_date_from"))
        self.hist_to_label.setText(tr("att_hist_date_to"))
        self.hist_class_label.setText(tr("att_class_label"))
        self.filter_btn.setText(tr("att_history_search"))
        
        # Tab 2 Table Headers
        headers_hist = [
            tr("att_date_label").replace(" :", ""),
            tr("att_tab_name"),
            tr("att_class_label").replace(" :", ""),
            tr("att_hist_status")
        ]
        self.history_table.setHorizontalHeaderLabels(headers_hist)
        
        # Reload history data to translate status values
        self.load_history()
        # If active checklist loaded, reload roster to translate Switchers or retain map
        if self.roster_table.rowCount() > 0:
            self.load_daily_roster()
