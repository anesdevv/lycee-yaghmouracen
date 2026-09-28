import os
from datetime import datetime
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDialog,
                             QMessageBox, QTableWidgetItem, QFormLayout, QLineEdit,
                             QComboBox, QDateEdit, QAbstractItemView, QHeaderView)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QFont
from ui.components import SearchBox, ModernTable, PremiumButton, SleekCard, create_table_item
from services.translation_service import TranslationService, tr
import database.db as db

class EmployeeScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.trans = TranslationService.get_instance()
        
        self.init_ui()
        self.load_employees()
        
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
        
        # "Add Employee" Button
        self.add_employee_btn = PremiumButton("", is_primary=True, parent=self)
        self.add_employee_btn.clicked.connect(self.open_add_dialog)
        header_layout.addWidget(self.add_employee_btn)
        
        layout.addLayout(header_layout)
        
        # Filters Ribbon Card
        filter_card = SleekCard(self)
        filter_card.setMinimumHeight(75)
        filter_layout = QHBoxLayout(filter_card)
        filter_layout.setContentsMargins(20, 10, 20, 10)
        filter_layout.setSpacing(15)
        
        # Search Box
        self.search_box = SearchBox(filter_card)
        self.search_box.setFixedWidth(250)
        self.search_box.textChanged.connect(self.load_employees)
        filter_layout.addWidget(self.search_box)
        
        # Role Filter
        self.role_label = QLabel(filter_card)
        self.role_label.setStyleSheet("font-weight: bold; color: #94A3B8;")
        filter_layout.addWidget(self.role_label)
        
        self.role_filter = QComboBox(filter_card)
        self.role_filter.currentIndexChanged.connect(self.load_employees)
        filter_layout.addWidget(self.role_filter)
        
        # Subject / Specialty Filter
        self.specialty_label = QLabel(filter_card)
        self.specialty_label.setStyleSheet("font-weight: bold; color: #94A3B8;")
        filter_layout.addWidget(self.specialty_label)
        
        self.specialty_filter = QComboBox(filter_card)
        self.specialty_filter.currentIndexChanged.connect(self.load_employees)
        filter_layout.addWidget(self.specialty_filter)
        
        filter_layout.addStretch(1)
        layout.addWidget(filter_card)
        
        # Employees Table
        self.employees_table = ModernTable(self)
        self.employees_table.setColumnCount(6)
        self.employees_table.cellDoubleClicked.connect(self.view_employee_profile)
        
        # Adjust Sizing (Spacious and extremely robust)
        header = self.employees_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive) # Employee ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)     # Full Name
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive) # Role
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive) # Specialty
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive) # Phone
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)       # Actions
        
        self.employees_table.setColumnWidth(0, 90)
        self.employees_table.setColumnWidth(2, 130)
        self.employees_table.setColumnWidth(3, 150)
        self.employees_table.setColumnWidth(4, 110)
        self.employees_table.setColumnWidth(5, 230)
        
        layout.addWidget(self.employees_table)
        
        self.populate_filters()

    def populate_filters(self):
        # Role Filters
        self.role_filter.clear()
        self.role_filter.addItem("All / Tous", "")
        self.role_filter.addItem("Enseignant (Teacher)", "Enseignant")
        self.role_filter.addItem("Administrateur (Admin)", "Administrateur")
        self.role_filter.addItem("Surveillant (Supervisor)", "Surveillant")
        self.role_filter.addItem("Directeur (Principal)", "Directeur")
        self.role_filter.addItem("Adjoint (Assistant)", "Adjoint")
        self.role_filter.addItem("Autre (Other)", "Autre")
        
        # Specialty Filters
        self.specialty_filter.clear()
        self.specialty_filter.addItem("All / Tous", "")
        self.specialty_filter.addItem("Mathématiques", "Mathématiques")
        self.specialty_filter.addItem("Sciences Physiques", "Sciences Physiques")
        self.specialty_filter.addItem("Sciences de la Nature", "Sciences de la Nature")
        self.specialty_filter.addItem("Langue Arabe", "Langue Arabe")
        self.specialty_filter.addItem("Langue Française", "Langue Française")
        self.specialty_filter.addItem("Langue Anglaise", "Langue Anglaise")
        self.specialty_filter.addItem("Histoire-Géographie", "Histoire-Géographie")
        self.specialty_filter.addItem("Philosophie", "Philosophie")
        self.specialty_filter.addItem("Administration", "Administration")

    def load_employees(self):
        search_query = self.search_box.text().strip()
        role_val = self.role_filter.currentData()
        specialty_val = self.specialty_filter.currentData()
        
        employees = db.get_employees(search_query, role_val, specialty_val)
        
        self.employees_table.setRowCount(0)
        for e in employees:
            row_idx = self.employees_table.rowCount()
            self.employees_table.insertRow(row_idx)
            
            # ID
            id_item = create_table_item(e['employee_id'], Qt.AlignCenter)
            self.employees_table.setItem(row_idx, 0, id_item)
            
            # Full Name
            fullname = f"{e['last_name'].upper()} {e['first_name']}"
            name_item = create_table_item(fullname)
            self.employees_table.setItem(row_idx, 1, name_item)
            
            # Role
            role_item = create_table_item(e['role'], Qt.AlignCenter)
            self.employees_table.setItem(row_idx, 2, role_item)
            
            # Specialty
            spec_item = create_table_item(e['specialty'] or "-", Qt.AlignCenter)
            self.employees_table.setItem(row_idx, 3, spec_item)
            
            # Phone
            phone_item = create_table_item(e['phone'] or "-", Qt.AlignCenter)
            self.employees_table.setItem(row_idx, 4, phone_item)
            
            # Actions buttons widget
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 2, 5, 2)
            actions_layout.setSpacing(6)
            
            view_btn = PremiumButton("👁️", is_primary=False, parent=actions_widget)
            view_btn.setToolTip(tr("action_view"))
            view_btn.setFixedWidth(32)
            view_btn.setFixedHeight(28)
            view_btn.setStyleSheet("padding: 0px; border-radius: 6px;")
            view_btn.clicked.connect(lambda checked=False, dbid=e['id']: self.view_employee_profile_by_id(dbid))
            actions_layout.addWidget(view_btn)
            
            edit_btn = PremiumButton("✏️", is_primary=False, parent=actions_widget)
            edit_btn.setToolTip(tr("action_edit"))
            edit_btn.setFixedWidth(32)
            edit_btn.setFixedHeight(28)
            edit_btn.setStyleSheet("padding: 0px; border-radius: 6px;")
            edit_btn.clicked.connect(lambda checked=False, emp_dict=e: self.open_edit_dialog(emp_dict))
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
            del_btn.clicked.connect(lambda checked=False, emp_dict=e: self.confirm_delete_employee(emp_dict))
            actions_layout.addWidget(del_btn)
            
            actions_layout.addStretch()
            self.employees_table.setCellWidget(row_idx, 5, actions_widget)

    def open_add_dialog(self):
        dialog = EmployeeFormDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.load_employees()

    def open_edit_dialog(self, employee_dict):
        dialog = EmployeeFormDialog(employee_dict, parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.load_employees()

    def confirm_delete_employee(self, employee):
        fullname = f"{employee['last_name'].upper()} {employee['first_name']}"
        confirm_text = tr("emp_delete_confirm", name=fullname)
        
        reply = QMessageBox.question(self, tr("warning"), confirm_text, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            db.delete_employee(employee['id'])
            QMessageBox.information(self, tr("success"), tr("emp_delete_success"))
            self.load_employees()

    def view_employee_profile(self, row, col):
        # Triggered on double click table row
        emp_id_item = self.employees_table.item(row, 0)
        if emp_id_item:
            emp_id = emp_id_item.text().strip()
            employee = db.get_employee_by_employee_id(emp_id)
            if employee:
                dialog = EmployeeProfileDialog(employee, parent=self)
                dialog.exec()

    def view_employee_profile_by_id(self, db_id):
        employee = db.get_employee_by_id(db_id)
        if employee:
            dialog = EmployeeProfileDialog(employee, parent=self)
            dialog.exec()

    def update_translation(self):
        self.title_label.setText(tr("emp_title"))
        self.subtitle_label.setText(tr("emp_subtitle"))
        self.add_employee_btn.setText(tr("emp_add_btn"))
        self.role_label.setText(tr("emp_filter_role"))
        self.specialty_label.setText(tr("emp_filter_subject"))
        self.search_box.setPlaceholderText(tr("emp_search_hint"))
        
        # Table Headers
        headers = [
            tr("emp_tab_id"),
            tr("emp_tab_name"),
            tr("emp_tab_role"),
            tr("emp_tab_subject"),
            tr("emp_tab_phone"),
            tr("emp_tab_actions")
        ]
        self.employees_table.setHorizontalHeaderLabels(headers)
        self.load_employees()


# =====================================================================
# Employee Form (Add/Edit) Dialog Overlay
# =====================================================================

class EmployeeFormDialog(QDialog):
    def __init__(self, employee_data=None, parent=None):
        super().__init__(parent)
        self.employee_data = employee_data
        self.trans = TranslationService.get_instance()
        
        self.init_ui()
        
        if employee_data:
            self.setWindowTitle(tr("action_edit") + " " + tr("sidebar_employees"))
            self.fill_form()
        else:
            self.setWindowTitle(tr("emp_add_btn"))
            
    def init_ui(self):
        self.setFixedSize(480, 500)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        # Form Layout
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        # Fields
        self.emp_id_input = QLineEdit(self)
        form_layout.addRow(tr("emp_id_field"), self.emp_id_input)
        
        self.first_name_input = QLineEdit(self)
        form_layout.addRow(tr("emp_first_name"), self.first_name_input)
        
        self.last_name_input = QLineEdit(self)
        form_layout.addRow(tr("emp_last_name"), self.last_name_input)
        
        self.role_combo = QComboBox(self)
        self.role_combo.addItem("Enseignant", "Enseignant")
        self.role_combo.addItem("Administrateur", "Administrateur")
        self.role_combo.addItem("Surveillant", "Surveillant")
        self.role_combo.addItem("Directeur", "Directeur")
        self.role_combo.addItem("Adjoint", "Adjoint")
        self.role_combo.addItem("Autre", "Autre")
        form_layout.addRow(tr("emp_role"), self.role_combo)
        
        self.specialty_combo = QComboBox(self)
        self.specialty_combo.addItem("Mathématiques", "Mathématiques")
        self.specialty_combo.addItem("Sciences Physiques", "Sciences Physiques")
        self.specialty_combo.addItem("Sciences de la Nature", "Sciences de la Nature")
        self.specialty_combo.addItem("Langue Arabe", "Langue Arabe")
        self.specialty_combo.addItem("Langue Française", "Langue Française")
        self.specialty_combo.addItem("Langue Anglaise", "Langue Anglaise")
        self.specialty_combo.addItem("Histoire-Géographie", "Histoire-Géographie")
        self.specialty_combo.addItem("Philosophie", "Philosophie")
        self.specialty_combo.addItem("Administration", "Administration")
        self.specialty_combo.addItem("- Aucun -", "")
        form_layout.addRow(tr("emp_subject"), self.specialty_combo)
        
        self.salary_input = QLineEdit(self)
        self.salary_input.setPlaceholderText("ex: 62000.00")
        form_layout.addRow(tr("emp_salary"), self.salary_input)
        
        self.hire_date_input = QDateEdit(self)
        self.hire_date_input.setCalendarPopup(True)
        self.hire_date_input.setDate(QDate.currentDate())
        self.hire_date_input.setDisplayFormat("dd/MM/yyyy")
        form_layout.addRow(tr("emp_hire_date"), self.hire_date_input)
        
        self.phone_input = QLineEdit(self)
        form_layout.addRow(tr("emp_phone"), self.phone_input)
        
        layout.addLayout(form_layout)
        
        # Actions footer
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
        e = self.employee_data
        self.emp_id_input.setText(e['employee_id'])
        self.first_name_input.setText(e['first_name'])
        self.last_name_input.setText(e['last_name'])
        
        role_idx = self.role_combo.findData(e['role'])
        if role_idx >= 0:
            self.role_combo.setCurrentIndex(role_idx)
        else:
            role_text_idx = self.role_combo.findText(e['role'])
            if role_text_idx >= 0:
                self.role_combo.setCurrentIndex(role_text_idx)
                
        spec_idx = self.specialty_combo.findText(e['specialty'] or "")
        if spec_idx >= 0:
            self.specialty_combo.setCurrentIndex(spec_idx)
            
        self.salary_input.setText(str(e['salary']) if e['salary'] else "")
        
        if e['hire_date']:
            try:
                qdate = QDate.fromString(e['hire_date'], "dd/MM/yyyy")
                if qdate.isValid():
                    self.hire_date_input.setDate(qdate)
            except Exception:
                pass
                
        self.phone_input.setText(e['phone'] or "")

    def handle_save(self):
        emp_id = self.emp_id_input.text().strip()
        first_name = self.first_name_input.text().strip()
        last_name = self.last_name_input.text().strip()
        role = self.role_combo.currentText()
        specialty = self.specialty_combo.currentText()
        if specialty == "- Aucun -":
            specialty = ""
        salary_str = self.salary_input.text().strip()
        hire_date = self.hire_date_input.date().toString("dd/MM/yyyy")
        phone = self.phone_input.text().strip()
        
        # Validations
        if not emp_id:
            QMessageBox.warning(self, tr("warning"), tr("emp_err_id"))
            return
            
        if not first_name or not last_name:
            QMessageBox.warning(self, tr("warning"), tr("emp_err_names"))
            return
            
        # Unique check
        exclude_db_id = self.employee_data['id'] if self.employee_data else None
        if db.is_employee_id_exists(emp_id, exclude_db_id):
            QMessageBox.warning(self, tr("warning"), tr("emp_err_id_exists"))
            return
            
        # Parse and validate salary
        salary = 0.0
        if salary_str:
            try:
                salary = float(salary_str.replace(',', '.'))
                if salary < 0:
                    raise ValueError()
            except ValueError:
                QMessageBox.warning(
                    self,
                    tr("warning"),
                    "Please enter a valid positive number for salary." if self.trans.current_language == 'en'
                    else "Veuillez entrer un montant de salaire valide et positif."
                )
                return
                
        # DB transactions
        if self.employee_data:
            db.update_employee(
                self.employee_data['id'],
                emp_id,
                first_name,
                last_name,
                role,
                hire_date,
                salary,
                specialty,
                phone
            )
            QMessageBox.information(self, tr("success"), tr("emp_update_success"))
        else:
            db.add_employee(
                emp_id,
                first_name,
                last_name,
                role,
                hire_date,
                salary,
                specialty,
                phone
            )
            QMessageBox.information(self, tr("success"), tr("emp_add_success"))
            
        self.accept()


# =====================================================================
# Employee Profile Dialog Overlay
# =====================================================================

class EmployeeProfileDialog(QDialog):
    def __init__(self, employee, parent=None):
        super().__init__(parent)
        self.employee = employee
        self.trans = TranslationService.get_instance()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle(tr("emp_profile_title"))
        self.setFixedSize(450, 440)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # Upper Card details
        top_layout = QHBoxLayout()
        top_layout.setSpacing(15)
        
        photo_label = QLabel("💼", self)
        photo_label.setFixedSize(70, 70)
        photo_label.setStyleSheet("border: 1.5px solid #CBD5E1; border-radius: 35px; background-color: #F1F5F9; font-size: 36px; color: #2563EB;")
        photo_label.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(photo_label)
        
        name_vbox = QVBoxLayout()
        name_vbox.setSpacing(5)
        
        fullname = f"{self.employee['last_name'].upper()} {self.employee['first_name']}"
        name_label = QLabel(fullname, self)
        name_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2563EB;")
        name_vbox.addWidget(name_label)
        
        role_label = QLabel(f"{self.employee['role']} — {self.employee['specialty'] or 'Général'}", self)
        role_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #475569;")
        name_vbox.addWidget(role_label)
        
        name_vbox.addStretch(1)
        top_layout.addLayout(name_vbox)
        
        layout.addLayout(top_layout)
        
        # Details Card
        details_card = SleekCard(self)
        card_layout = QFormLayout(details_card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(12)
        
        label_style = "font-weight: bold; color: #2563EB; font-size: 13px;"
        val_style = "color: #0F172A; font-weight: 500; font-size: 13px;"
        
        # Employee ID
        id_lbl = QLabel(tr("emp_tab_id"), details_card)
        id_lbl.setStyleSheet(label_style)
        id_val = QLabel(self.employee['employee_id'], details_card)
        id_val.setStyleSheet(val_style)
        card_layout.addRow(id_lbl, id_val)
        
        # Hire Date
        h_lbl = QLabel(tr("emp_hire_date"), details_card)
        h_lbl.setStyleSheet(label_style)
        h_val = QLabel(self.employee['hire_date'] or "-", details_card)
        h_val.setStyleSheet(val_style)
        card_layout.addRow(h_lbl, h_val)
        
        # Salary
        sal_lbl = QLabel(tr("emp_salary"), details_card)
        sal_lbl.setStyleSheet(label_style)
        salary_txt = f"{self.employee['salary']:,.2f} DA" if self.employee['salary'] else "-"
        sal_val = QLabel(salary_txt, details_card)
        sal_val.setStyleSheet(val_style)
        card_layout.addRow(sal_lbl, sal_val)
        
        # Phone
        phone_lbl = QLabel(tr("emp_tab_phone"), details_card)
        phone_lbl.setStyleSheet(label_style)
        phone_val = QLabel(self.employee['phone'] or "-", details_card)
        phone_val.setStyleSheet(val_style)
        card_layout.addRow(phone_lbl, phone_val)
        
        layout.addWidget(details_card)
        
        # Close button
        footer_layout = QHBoxLayout()
        footer_layout.addStretch(1)
        close_label = "Fermer" if self.trans.current_language == "fr" else "Close"
        close_btn = PremiumButton(close_label, is_primary=True, parent=self)
        close_btn.clicked.connect(self.accept)
        footer_layout.addWidget(close_btn)
        layout.addLayout(footer_layout)
