from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDialog,
                             QMessageBox, QTableWidgetItem, QFormLayout, QLineEdit, QHeaderView)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from ui.components import SleekCard, PremiumButton, ModernTable, create_table_item
from services.translation_service import TranslationService, tr
import database.db as db

class ClassScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.trans = TranslationService.get_instance()
        
        self.init_ui()
        self.load_classes()
        
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
        self.subtitle_label.setStyleSheet("font-size: 13px; color: #64748B;")
        title_vbox.addWidget(self.subtitle_label)
        
        header_layout.addLayout(title_vbox)
        header_layout.addStretch(1)
        
        # "Add Class" Button
        self.add_class_btn = PremiumButton("", is_primary=True, parent=self)
        self.add_class_btn.clicked.connect(self.open_add_dialog)
        header_layout.addWidget(self.add_class_btn)
        
        layout.addLayout(header_layout)
        
        # Table of Classes
        self.classes_table = ModernTable(self)
        self.classes_table.setColumnCount(3)
        
        # Adjust Columns Sizing (Spacious and extremely robust)
        header = self.classes_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive) # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)     # Name
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)       # Actions
        
        self.classes_table.setColumnWidth(0, 80)
        self.classes_table.setColumnWidth(2, 160)
        
        layout.addWidget(self.classes_table)

    def load_classes(self):
        classes = db.get_classes()
        
        self.classes_table.setRowCount(0)
        for c in classes:
            row_idx = self.classes_table.rowCount()
            self.classes_table.insertRow(row_idx)
            
            # ID
            id_item = create_table_item(c['id'], Qt.AlignCenter)
            self.classes_table.setItem(row_idx, 0, id_item)
            
            # Class Name
            name_item = create_table_item(c['name'])
            self.classes_table.setItem(row_idx, 1, name_item)
            
            # Actions buttons: Edit, Delete
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 2, 5, 2)
            actions_layout.setSpacing(10)
            
            edit_btn = PremiumButton("✏️", is_primary=False, parent=actions_widget)
            edit_btn.setToolTip(tr("action_edit"))
            edit_btn.setFixedWidth(36)
            edit_btn.setFixedHeight(28)
            edit_btn.setStyleSheet("padding: 0px; border-radius: 6px;")
            edit_btn.clicked.connect(lambda checked=False, class_dict=c: self.open_edit_dialog(class_dict))
            actions_layout.addWidget(edit_btn)
            
            del_btn = PremiumButton("🗑️", is_primary=False, parent=actions_widget)
            del_btn.setToolTip(tr("action_delete"))
            del_btn.setFixedWidth(36)
            del_btn.setFixedHeight(28)
            del_btn.setStyleSheet("""
                QPushButton {
                    border: 1.5px solid #FCA5A5;
                    color: #DC2626;
                    padding: 0px;
                    border-radius: 6px;
                    background-color: #FFFFFF;
                }
                QPushButton:hover {
                    background-color: #FEE2E2;
                    border-color: #EF4444;
                }
            """)
            del_btn.clicked.connect(lambda checked=False, class_dict=c: self.confirm_delete_class(class_dict))
            actions_layout.addWidget(del_btn)
            
            actions_layout.addStretch()
            self.classes_table.setCellWidget(row_idx, 2, actions_widget)

    def open_add_dialog(self):
        dialog = ClassFormDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.load_classes()

    def open_edit_dialog(self, class_dict):
        dialog = ClassFormDialog(class_dict, parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.load_classes()

    def confirm_delete_class(self, class_dict):
        confirm_text = tr("class_delete_confirm", name=class_dict['name'])
        reply = QMessageBox.question(self, tr("warning"), confirm_text, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            db.delete_class(class_dict['id'])
            QMessageBox.information(self, tr("success"), tr("class_delete_success"))
            self.load_classes()

    def update_translation(self):
        self.title_label.setText(tr("class_title"))
        self.subtitle_label.setText(tr("class_subtitle"))
        self.add_class_btn.setText(tr("class_add_btn"))
        
        # Translate Table Headers
        headers = [
            tr("class_tab_id"),
            tr("class_tab_name"),
            tr("class_tab_actions")
        ]
        self.classes_table.setHorizontalHeaderLabels(headers)
        self.load_classes()


class ClassFormDialog(QDialog):
    def __init__(self, class_data=None, parent=None):
        super().__init__(parent)
        self.class_data = class_data
        self.trans = TranslationService.get_instance()
        
        self.init_ui()
        
        if class_data:
            self.setWindowTitle(tr("action_edit") + " " + tr("sidebar_classes"))
            self.name_input.setText(class_data['name'])
        else:
            self.setWindowTitle(tr("class_add_btn"))

    def init_ui(self):
        self.setFixedSize(400, 180)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        self.name_input = QLineEdit(self)
        form_layout.addRow(tr("class_tab_name"), self.name_input)
        
        layout.addLayout(form_layout)
        
        # Action Buttons footer
        btn_layout = QHBoxLayout()
        btn_layout.addStretch(1)
        
        self.cancel_btn = PremiumButton(tr("cancel"), is_primary=False, parent=self)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        
        self.save_btn = PremiumButton(tr("save"), is_primary=True, parent=self)
        self.save_btn.clicked.connect(self.handle_save)
        btn_layout.addWidget(self.save_btn)
        
        layout.addLayout(btn_layout)

    def handle_save(self):
        name = self.name_input.text().strip()
        
        # Name Validation
        if not name:
            QMessageBox.warning(self, tr("warning"), tr("class_err_name"))
            return
            
        exclude_id = self.class_data['id'] if self.class_data else None
        if db.is_class_name_exists(name, exclude_id):
            QMessageBox.warning(self, tr("warning"), tr("class_err_name"))
            return
            
        try:
            if self.class_data:
                db.update_class(self.class_data['id'], name)
                QMessageBox.information(self, tr("success"), tr("class_update_success"))
            else:
                db.add_class(name)
                QMessageBox.information(self, tr("success"), tr("class_add_success"))
                
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, tr("error"), f"Database Error: {e}")
