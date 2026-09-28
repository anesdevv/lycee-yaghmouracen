import os
import shutil
from datetime import datetime
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDialog,
                             QFileDialog, QMessageBox, QTableWidgetItem, QFormLayout,
                             QLineEdit, QComboBox, QDateEdit, QAbstractItemView, QHeaderView)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QFont, QPixmap, QIcon
from PIL import Image as PILImage
from ui.components import SearchBox, ModernTable, PremiumButton, SleekCard, create_table_item
from services.translation_service import TranslationService, tr
import database.db as db

IMAGE_UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "images", "students")

class StudentScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.trans = TranslationService.get_instance()
        
        # Ensure student image upload folder exists
        os.makedirs(IMAGE_UPLOAD_DIR, exist_ok=True)
        
        self.init_ui()
        self.load_students()
        
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
        
        # "Add Student" Button
        self.add_student_btn = PremiumButton("", is_primary=True, parent=self)
        self.add_student_btn.clicked.connect(self.open_add_dialog)
        header_layout.addWidget(self.add_student_btn)
        
        layout.addLayout(header_layout)
        
        # Search and Filters Ribbon Card
        filter_card = SleekCard(self)
        filter_card.setMinimumHeight(75)
        filter_layout = QHBoxLayout(filter_card)
        filter_layout.setContentsMargins(20, 10, 20, 10)
        filter_layout.setSpacing(15)
        
        # Search Box
        self.search_box = SearchBox(filter_card)
        self.search_box.setFixedWidth(280)
        self.search_box.textChanged.connect(self.load_students)
        filter_layout.addWidget(self.search_box)
        
        # Class Filter Dropdown
        self.class_label = QLabel(filter_card)
        self.class_label.setStyleSheet("font-weight: bold; color: #94A3B8;")
        filter_layout.addWidget(self.class_label)
        
        self.class_filter = QComboBox(filter_card)
        self.class_filter.currentIndexChanged.connect(self.load_students)
        filter_layout.addWidget(self.class_filter)
        
        # Gender Filter Dropdown
        self.gender_label = QLabel(filter_card)
        self.gender_label.setStyleSheet("font-weight: bold; color: #94A3B8;")
        filter_layout.addWidget(self.gender_label)
        
        self.gender_filter = QComboBox(filter_card)
        self.gender_filter.currentIndexChanged.connect(self.load_students)
        filter_layout.addWidget(self.gender_filter)
        
        filter_layout.addStretch(1)
        layout.addWidget(filter_card)
        
        # Table of Students
        self.students_table = ModernTable(self)
        self.students_table.setColumnCount(6)
        self.students_table.cellDoubleClicked.connect(self.view_student_profile)
        
        # Adjust Columns Sizing (Spacious and extremely robust)
        header = self.students_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive) # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive) # Photo
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)     # Full Name
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive) # Class
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive) # Absences
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)       # Actions
        
        self.students_table.setColumnWidth(0, 60)
        self.students_table.setColumnWidth(1, 65)
        self.students_table.setColumnWidth(3, 140)
        self.students_table.setColumnWidth(4, 90)
        self.students_table.setColumnWidth(5, 230)
        
        layout.addWidget(self.students_table)
        
        # Populate class/gender lists
        self.populate_filters()

    def populate_filters(self):
        # Class lists loaded dynamically
        self.class_filter.clear()
        self.class_filter.addItem("All / Tous", "")
        
        self.class_filter.blockSignals(True)
        classes = db.get_classes()
        for c in classes:
            self.class_filter.addItem(c['name'], c['name'])
        self.class_filter.blockSignals(False)
        
        # Gender lists
        self.gender_filter.clear()
        self.gender_filter.addItem("All / Tous", "")
        self.gender_filter.addItem("Male / Masculin", "Male")
        self.gender_filter.addItem("Female / Féminin", "Female")

    def load_students(self):
        search_query = self.search_box.text().strip()
        class_val = self.class_filter.currentData()
        gender_val = self.gender_filter.currentData()
        
        students = db.get_students(search_query, class_val, gender_val)
        
        self.students_table.setRowCount(0)
        for s in students:
            row_idx = self.students_table.rowCount()
            self.students_table.insertRow(row_idx)
            
            # ID
            id_item = create_table_item(s['id'], Qt.AlignCenter)
            self.students_table.setItem(row_idx, 0, id_item)
            
            # Photo Thumbnail Icon
            photo_label = QLabel()
            photo_label.setAlignment(Qt.AlignCenter)
            photo_path = s['photo_path']
            
            thumbnail_size = 28
            if photo_path and os.path.exists(photo_path):
                pixmap = QPixmap(photo_path)
                scaled_pixmap = pixmap.scaled(thumbnail_size, thumbnail_size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                photo_label.setPixmap(scaled_pixmap)
            else:
                photo_label.setText("👤") # Placeholder avatar
                photo_label.setStyleSheet("font-size: 16px; color: #94A3B8;")
                
            self.students_table.setCellWidget(row_idx, 1, photo_label)
            
            # Full Name
            fullname = f"{s['last_name'].upper()} {s['first_name']}"
            name_item = create_table_item(fullname)
            self.students_table.setItem(row_idx, 2, name_item)
            
            # Class
            class_item = create_table_item(s['class_name'] or "-", Qt.AlignCenter)
            self.students_table.setItem(row_idx, 3, class_item)
            
            # Absences
            absences_item = create_table_item(s['absence_count'] or 0, Qt.AlignCenter)
            self.students_table.setItem(row_idx, 4, absences_item)
            
            # Actions buttons: View, Edit, Delete
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 2, 5, 2)
            actions_layout.setSpacing(6)
            
            view_btn = PremiumButton("👁️", is_primary=False, parent=actions_widget)
            view_btn.setToolTip(tr("action_view"))
            view_btn.setFixedWidth(32)
            view_btn.setFixedHeight(28)
            view_btn.setStyleSheet("padding: 0px; border-radius: 6px;")
            view_btn.clicked.connect(lambda checked=False, sid=s['id']: self.view_student_profile_by_id(sid))
            actions_layout.addWidget(view_btn)
            
            edit_btn = PremiumButton("✏️", is_primary=False, parent=actions_widget)
            edit_btn.setToolTip(tr("action_edit"))
            edit_btn.setFixedWidth(32)
            edit_btn.setFixedHeight(28)
            edit_btn.setStyleSheet("padding: 0px; border-radius: 6px;")
            edit_btn.clicked.connect(lambda checked=False, student_dict=s: self.open_edit_dialog(student_dict))
            actions_layout.addWidget(edit_btn)
            
            del_btn = PremiumButton("🗑️", is_primary=False, parent=actions_widget)
            del_btn.setToolTip(tr("action_delete"))
            del_btn.setFixedWidth(32)
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
            del_btn.clicked.connect(lambda checked=False, student_dict=s: self.confirm_delete_student(student_dict))
            actions_layout.addWidget(del_btn)
            
            actions_layout.addStretch()
            self.students_table.setCellWidget(row_idx, 5, actions_widget)

    def open_add_dialog(self):
        dialog = StudentFormDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.load_students()

    def open_edit_dialog(self, student_dict):
        dialog = StudentFormDialog(student_dict, parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.load_students()

    def confirm_delete_student(self, student):
        fullname = f"{student['last_name'].upper()} {student['first_name']}"
        confirm_text = tr("stud_delete_confirm", name=fullname)
        
        reply = QMessageBox.question(self, tr("warning"), confirm_text, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Remove photo file if inside uploaded folder
            if student['photo_path'] and os.path.exists(student['photo_path']):
                if IMAGE_UPLOAD_DIR in student['photo_path']:
                    try:
                        os.remove(student['photo_path'])
                    except Exception:
                        pass
                        
            db.delete_student(student['id'])
            QMessageBox.information(self, tr("success"), tr("stud_delete_success"))
            self.load_students()

    def view_student_profile(self, row, col):
        # Triggered on double click row
        id_item = self.students_table.item(row, 0)
        if id_item:
            self.view_student_profile_by_id(int(id_item.text()))

    def view_student_profile_by_id(self, student_id):
        student = db.get_student_by_id(student_id)
        if student:
            dialog = StudentProfileDialog(student, parent=self)
            dialog.exec()

    def update_translation(self):
        self.title_label.setText(tr("stud_title"))
        self.subtitle_label.setText(tr("stud_subtitle"))
        self.add_student_btn.setText(tr("stud_add_btn"))
        self.class_label.setText(tr("stud_filter_class"))
        self.gender_label.setText(tr("stud_filter_gender"))
        self.search_box.setPlaceholderText(tr("stud_search_hint"))
        
        # Translate Table Headers
        headers = [
            tr("stud_tab_id"),
            tr("stud_tab_photo"),
            tr("stud_tab_name"),
            tr("stud_tab_class"),
            tr("stud_tab_absences"),
            tr("stud_tab_actions")
        ]
        self.students_table.setHorizontalHeaderLabels(headers)
        self.load_students()


# =====================================================================
# Student Form (Add/Edit) Dialog Overlay
# =====================================================================

class StudentFormDialog(QDialog):
    def __init__(self, student_data=None, parent=None):
        super().__init__(parent)
        self.student_data = student_data
        self.selected_photo_path = None
        self.trans = TranslationService.get_instance()
        
        self.init_ui()
        
        if student_data:
            self.setWindowTitle(tr("action_edit") + " " + tr("sidebar_students"))
            self.fill_form()
        else:
            self.setWindowTitle(tr("stud_add_btn"))
            
    def init_ui(self):
        self.setFixedSize(480, 520)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        # Form Layout
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        # Fields
        self.first_name_input = QLineEdit(self)
        form_layout.addRow(tr("stud_first_name"), self.first_name_input)
        
        self.last_name_input = QLineEdit(self)
        form_layout.addRow(tr("stud_last_name"), self.last_name_input)
        
        self.birth_date_input = QDateEdit(self)
        self.birth_date_input.setCalendarPopup(True)
        self.birth_date_input.setDate(QDate(2010, 1, 1))
        self.birth_date_input.setDisplayFormat("dd/MM/yyyy")
        form_layout.addRow(tr("stud_birth_date"), self.birth_date_input)
        
        self.gender_combo = QComboBox(self)
        self.gender_combo.addItem("Male / Masculin", "Male")
        self.gender_combo.addItem("Female / Féminin", "Female")
        form_layout.addRow(tr("stud_gender"), self.gender_combo)
        
        self.class_combo = QComboBox(self)
        # Load classes dynamically
        classes = db.get_classes()
        for c in classes:
            self.class_combo.addItem(c['name'])
        form_layout.addRow(tr("stud_class"), self.class_combo)
        
        self.parent_input = QLineEdit(self)
        form_layout.addRow(tr("stud_parent"), self.parent_input)
        
        self.address_input = QLineEdit(self)
        form_layout.addRow(tr("stud_address"), self.address_input)
        
        # Photo Row
        photo_row = QHBoxLayout()
        self.photo_preview = QLabel("No Photo / Aucun", self)
        self.photo_preview.setStyleSheet("border: 1.5px solid #CBD5E1; border-radius: 8px; padding: 4px; background-color: #F8FAFC; color: #475569;")
        self.photo_preview.setFixedSize(60, 60)
        self.photo_preview.setAlignment(Qt.AlignCenter)
        photo_row.addWidget(self.photo_preview)
        
        self.browse_photo_btn = PremiumButton(tr("stud_photo_btn"), is_primary=False, parent=self)
        self.browse_photo_btn.clicked.connect(self.browse_photo)
        photo_row.addWidget(self.browse_photo_btn)
        photo_row.addStretch(1)
        
        form_layout.addRow(tr("stud_photo"), photo_row)
        
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

    def fill_form(self):
        s = self.student_data
        self.first_name_input.setText(s['first_name'])
        self.last_name_input.setText(s['last_name'])
        
        # Parse date
        if s['birth_date']:
            try:
                qdate = QDate.fromString(s['birth_date'], "dd/MM/yyyy")
                if qdate.isValid():
                    self.birth_date_input.setDate(qdate)
            except Exception:
                pass
                
        gender_idx = self.gender_combo.findData(s['gender'])
        if gender_idx >= 0:
            self.gender_combo.setCurrentIndex(gender_idx)
            
        class_idx = self.class_combo.findText(s['class_name'] or "")
        if class_idx >= 0:
            self.class_combo.setCurrentIndex(class_idx)
            
        self.parent_input.setText(s['parent_name'] or "")
        self.address_input.setText(s['address'] or "")
        
        if s['photo_path'] and os.path.exists(s['photo_path']):
            self.selected_photo_path = s['photo_path']
            pixmap = QPixmap(s['photo_path'])
            self.photo_preview.setPixmap(pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def browse_photo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Photo", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            self.selected_photo_path = file_path
            pixmap = QPixmap(file_path)
            self.photo_preview.setPixmap(pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def handle_save(self):
        first_name = self.first_name_input.text().strip()
        last_name = self.last_name_input.text().strip()
        birth_date = self.birth_date_input.date().toString("dd/MM/yyyy")
        gender = self.gender_combo.currentData()
        class_name = self.class_combo.currentText()
        parent_name = self.parent_input.text().strip()
        address = self.address_input.text().strip()
        
        # Validation checks
        if not first_name or not last_name:
            QMessageBox.warning(self, tr("warning"), tr("stud_err_name"))
            return
            
        if not class_name:
            QMessageBox.warning(
                self,
                tr("warning"),
                "Please select or create a class first." if self.trans.current_language == 'en'
                else "Veuillez d'abord sélectionner ou créer une classe."
            )
            return
            
        final_photo_path = ""
        # Process and crop photo using Pillow if selected
        if self.selected_photo_path:
            if self.student_data and self.selected_photo_path == self.student_data.get('photo_path'):
                # Photo remained unchanged
                final_photo_path = self.student_data['photo_path']
            else:
                try:
                    # Save a cropped squared 150x150 version of the photo in uploads folder
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"stud_{timestamp}.jpg"
                    dest_path = os.path.join(IMAGE_UPLOAD_DIR, filename)
                    
                    img = PILImage.open(self.selected_photo_path)
                    
                    # Convert to RGB if needed (PNG/RGBA support)
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                        
                    # Crop image to square
                    width, height = img.size
                    min_dim = min(width, height)
                    left = (width - min_dim) / 2
                    top = (height - min_dim) / 2
                    right = (width + min_dim) / 2
                    bottom = (height + min_dim) / 2
                    
                    cropped_img = img.crop((left, top, right, bottom))
                    resized_img = cropped_img.resize((150, 150), PILImage.Resampling.LANCZOS)
                    resized_img.save(dest_path, "JPEG", quality=90)
                    
                    final_photo_path = dest_path
                    
                    # Remove older photo if editing
                    if self.student_data and self.student_data.get('photo_path') and os.path.exists(self.student_data['photo_path']):
                        try:
                            os.remove(self.student_data['photo_path'])
                        except Exception:
                            pass
                except Exception as e:
                    print(f"Error copying/cropping photo: {e}")
                    final_photo_path = self.selected_photo_path # Fallback to original
        
        # Save to DB
        if self.student_data:
            photo_to_save = final_photo_path if self.selected_photo_path else self.student_data.get('photo_path', '')
            db.update_student(
                self.student_data['id'],
                first_name,
                last_name,
                birth_date,
                gender,
                class_name,
                address,
                parent_name,
                photo_to_save
            )
            QMessageBox.information(self, tr("success"), tr("stud_update_success"))
        else:
            db.add_student(
                first_name,
                last_name,
                birth_date,
                gender,
                class_name,
                address,
                parent_name,
                final_photo_path
            )
            QMessageBox.information(self, tr("success"), tr("stud_add_success"))
            
        self.accept()


# =====================================================================
# Student Detailed Profile Dialog
# =====================================================================

class StudentProfileDialog(QDialog):
    def __init__(self, student, parent=None):
        super().__init__(parent)
        self.student = student
        self.trans = TranslationService.get_instance()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle(tr("stud_profile_title"))
        self.setFixedSize(450, 460)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # Top card layout: Big Photo and Name
        top_layout = QHBoxLayout()
        top_layout.setSpacing(20)
        
        photo_label = QLabel(self)
        photo_label.setFixedSize(110, 110)
        photo_label.setStyleSheet("border: 1.5px solid #CBD5E1; border-radius: 8px; background-color: #F1F5F9;")
        photo_label.setAlignment(Qt.AlignCenter)
        
        photo_path = self.student['photo_path']
        if photo_path and os.path.exists(photo_path):
            pixmap = QPixmap(photo_path)
            photo_label.setPixmap(pixmap.scaled(106, 106, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            photo_label.setText("👤")
            photo_label.setStyleSheet("font-size: 50px; background-color: #F1F5F9; border: 1.5px solid #CBD5E1; border-radius: 8px; color: #475569;")
            
        top_layout.addWidget(photo_label)
        
        name_vbox = QVBoxLayout()
        name_vbox.setSpacing(5)
        
        fullname = f"{self.student['last_name'].upper()} {self.student['first_name']}"
        name_label = QLabel(fullname, self)
        name_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2563EB;")
        name_vbox.addWidget(name_label)
        
        class_label = QLabel(f"Classe: {self.student['class_name'] or '-'}", self)
        class_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #475569;")
        name_vbox.addWidget(class_label)
        
        abs_text = tr("stud_tab_absences") + f" : {self.student['absence_count'] or 0}"
        absences_label = QLabel(abs_text, self)
        absences_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #DC2626;")
        name_vbox.addWidget(absences_label)
        
        name_vbox.addStretch(1)
        top_layout.addLayout(name_vbox)
        
        layout.addLayout(top_layout)
        
        # Details layout (Structured inside a sleek card)
        details_card = SleekCard(self)
        card_layout = QFormLayout(details_card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(12)
        
        label_style = "font-weight: bold; color: #2563EB; font-size: 13px;"
        val_style = "color: #0F172A; font-weight: 500; font-size: 13px;"
        
        # Date of Birth
        dob_lbl = QLabel(tr("stud_birth_date"), details_card)
        dob_lbl.setStyleSheet(label_style)
        dob_val = QLabel(self.student['birth_date'] or "-", details_card)
        dob_val.setStyleSheet(val_style)
        card_layout.addRow(dob_lbl, dob_val)
        
        # Gender
        gender_lbl = QLabel(tr("stud_gender"), details_card)
        gender_lbl.setStyleSheet(label_style)
        gender_str = "Masculin" if self.student['gender'] == "Male" and self.trans.current_language == "fr" else \
                     ("Féminin" if self.student['gender'] == "Female" and self.trans.current_language == "fr" else self.student['gender'])
        gender_val = QLabel(gender_str, details_card)
        gender_val.setStyleSheet(val_style)
        card_layout.addRow(gender_lbl, gender_val)
        
        # Parent Name
        parent_lbl = QLabel(tr("stud_parent"), details_card)
        parent_lbl.setStyleSheet(label_style)
        parent_val = QLabel(self.student['parent_name'] or "-", details_card)
        parent_val.setStyleSheet(val_style)
        card_layout.addRow(parent_lbl, parent_val)
        
        # Address
        addr_lbl = QLabel(tr("stud_address"), details_card)
        addr_lbl.setStyleSheet(label_style)
        addr_val = QLabel(self.student['address'] or "-", details_card)
        addr_val.setStyleSheet(val_style)
        addr_val.setWordWrap(True)
        card_layout.addRow(addr_lbl, addr_val)
        
        layout.addWidget(details_card)
        
        # Footer button
        footer_layout = QHBoxLayout()
        footer_layout.addStretch(1)
        close_label = "Fermer" if self.trans.current_language == "fr" else "Close"
        close_btn = PremiumButton(close_label, is_primary=True, parent=self)
        close_btn.clicked.connect(self.accept)
        footer_layout.addWidget(close_btn)
        layout.addLayout(footer_layout)
