import os
import subprocess
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout,
                             QComboBox, QMessageBox, QDateEdit)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont
from ui.components import SleekCard, PremiumButton
from services.translation_service import TranslationService, tr
import services.excel_service as excel_service
import services.pdf_service as pdf_service
import database.db as db

class ExportsScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.trans = TranslationService.get_instance()
        self.init_ui()
        self.populate_dropdowns()
        
        # Register translation changes listener
        self.trans.register_listener(self.update_translation)
        self.update_translation()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)
        
        # Header Panel
        header_layout = QHBoxLayout()
        title_vbox = QVBoxLayout()
        
        self.title_label = QLabel(self)
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #1F497D;")
        title_vbox.addWidget(self.title_label)
        
        self.subtitle_label = QLabel(self)
        self.subtitle_label.setStyleSheet("font-size: 13px; color: #64748B;")
        title_vbox.addWidget(self.subtitle_label)
        
        header_layout.addLayout(title_vbox)
        header_layout.addStretch(1)
        
        # Open Exports folder button shortcut
        self.open_folder_btn = PremiumButton("", is_primary=False, parent=self)
        self.open_folder_btn.clicked.connect(self.open_exports_folder)
        self.open_folder_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #1F497D;
                border: 1.5px solid #1F497D;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E2EBF5;
            }
        """)
        header_layout.addWidget(self.open_folder_btn)
        layout.addLayout(header_layout)
        
        # Grid Dashboard (Left: PDF Suite, Right: Excel Exports)
        grid_layout = QGridLayout()
        grid_layout.setSpacing(25)
        
        # =============================================================
        # Column 1: PDF Administrative Suite (Span 3 rows or stack in vbox)
        # =============================================================
        pdf_section_widget = QWidget(self)
        pdf_vbox = QVBoxLayout(pdf_section_widget)
        pdf_vbox.setContentsMargins(0, 0, 0, 0)
        pdf_vbox.setSpacing(20)
        
        self.pdf_section_title = QLabel("", pdf_section_widget)
        self.pdf_section_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1F497D;")
        pdf_vbox.addWidget(self.pdf_section_title)
        
        # 1. Student List PDF Generator
        card_stud_list = SleekCard(pdf_section_widget)
        card_stud_list.setFixedHeight(95)
        cl_layout = QHBoxLayout(card_stud_list)
        cl_layout.setContentsMargins(20, 15, 20, 15)
        
        desc_layout1 = QVBoxLayout()
        self.lbl_pdf_list = QLabel("", card_stud_list)
        self.lbl_pdf_list.setStyleSheet("font-weight: bold; font-size: 13px; color: #1E293B;")
        desc_layout1.addWidget(self.lbl_pdf_list)
        self.desc_pdf_list = QLabel("", card_stud_list)
        self.desc_pdf_list.setStyleSheet("font-size: 11px; color: #64748B;")
        desc_layout1.addWidget(self.desc_pdf_list)
        cl_layout.addLayout(desc_layout1)
        cl_layout.addStretch(1)
        
        self.combo_pdf_class = QComboBox(card_stud_list)
        cl_layout.addWidget(self.combo_pdf_class)
        
        self.btn_gen_stud_list = PremiumButton("", is_primary=True, parent=card_stud_list)
        self.btn_gen_stud_list.clicked.connect(self.generate_student_list_pdf)
        cl_layout.addWidget(self.btn_gen_stud_list)
        pdf_vbox.addWidget(card_stud_list)
        
        # 2. Employee List PDF Generator
        card_emp_list = SleekCard(pdf_section_widget)
        card_emp_list.setFixedHeight(95)
        cel_layout = QHBoxLayout(card_emp_list)
        cel_layout.setContentsMargins(20, 15, 20, 15)
        
        desc_layout2 = QVBoxLayout()
        self.lbl_pdf_emp = QLabel("", card_emp_list)
        self.lbl_pdf_emp.setStyleSheet("font-weight: bold; font-size: 13px; color: #1E293B;")
        desc_layout2.addWidget(self.lbl_pdf_emp)
        self.desc_pdf_emp = QLabel("", card_emp_list)
        self.desc_pdf_emp.setStyleSheet("font-size: 11px; color: #64748B;")
        desc_layout2.addWidget(self.desc_pdf_emp)
        cel_layout.addLayout(desc_layout2)
        cel_layout.addStretch(1)
        
        self.btn_gen_emp_list = PremiumButton("", is_primary=True, parent=card_emp_list)
        self.btn_gen_emp_list.clicked.connect(self.generate_employee_list_pdf)
        cel_layout.addWidget(self.btn_gen_emp_list)
        pdf_vbox.addWidget(card_emp_list)
        
        # 3. Work Certificate (Attestation de travail) PDF Generator
        card_work_cert = SleekCard(pdf_section_widget)
        card_work_cert.setFixedHeight(95)
        cwc_layout = QHBoxLayout(card_work_cert)
        cwc_layout.setContentsMargins(20, 15, 20, 15)
        
        desc_layout3 = QVBoxLayout()
        self.lbl_pdf_cert = QLabel("", card_work_cert)
        self.lbl_pdf_cert.setStyleSheet("font-weight: bold; font-size: 13px; color: #1E293B;")
        desc_layout3.addWidget(self.lbl_pdf_cert)
        self.desc_pdf_cert = QLabel("", card_work_cert)
        self.desc_pdf_cert.setStyleSheet("font-size: 11px; color: #64748B;")
        desc_layout3.addWidget(self.desc_pdf_cert)
        cwc_layout.addLayout(desc_layout3)
        cwc_layout.addStretch(1)
        
        self.combo_employees_cert = QComboBox(card_work_cert)
        self.combo_employees_cert.setMinimumWidth(180)
        cwc_layout.addWidget(self.combo_employees_cert)
        
        self.btn_gen_cert = PremiumButton("", is_primary=True, parent=card_work_cert)
        self.btn_gen_cert.clicked.connect(self.generate_work_certificate_pdf)
        cwc_layout.addWidget(self.btn_gen_cert)
        pdf_vbox.addWidget(card_work_cert)
        
        # 4. Student Detailed Sheet PDF Generator
        card_stud_sheet = SleekCard(pdf_section_widget)
        card_stud_sheet.setFixedHeight(95)
        css_layout = QHBoxLayout(card_stud_sheet)
        css_layout.setContentsMargins(20, 15, 20, 15)
        
        desc_layout4 = QVBoxLayout()
        self.lbl_pdf_stud = QLabel("", card_stud_sheet)
        self.lbl_pdf_stud.setStyleSheet("font-weight: bold; font-size: 13px; color: #1E293B;")
        desc_layout4.addWidget(self.lbl_pdf_stud)
        self.desc_pdf_stud = QLabel("", card_stud_sheet)
        self.desc_pdf_stud.setStyleSheet("font-size: 11px; color: #64748B;")
        desc_layout4.addWidget(self.desc_pdf_stud)
        css_layout.addLayout(desc_layout4)
        css_layout.addStretch(1)
        
        self.combo_students_sheet = QComboBox(card_stud_sheet)
        self.combo_students_sheet.setMinimumWidth(180)
        css_layout.addWidget(self.combo_students_sheet)
        
        self.btn_gen_stud_sheet = PremiumButton("", is_primary=True, parent=card_stud_sheet)
        self.btn_gen_stud_sheet.clicked.connect(self.generate_student_sheet_pdf)
        css_layout.addWidget(self.btn_gen_stud_sheet)
        pdf_vbox.addWidget(card_stud_sheet)
        
        grid_layout.addWidget(pdf_section_widget, 0, 0)
        
        # =============================================================
        # Column 2: Excel Exports
        # =============================================================
        excel_section_widget = QWidget(self)
        excel_vbox = QVBoxLayout(excel_section_widget)
        excel_vbox.setContentsMargins(0, 0, 0, 0)
        excel_vbox.setSpacing(20)
        
        self.excel_section_title = QLabel("", excel_section_widget)
        self.excel_section_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1F497D;")
        excel_vbox.addWidget(self.excel_section_title)
        
        # 1. Excel Students
        card_ex_stud = SleekCard(excel_section_widget)
        card_ex_stud.setFixedHeight(95)
        ces_layout = QHBoxLayout(card_ex_stud)
        ces_layout.setContentsMargins(20, 15, 20, 15)
        
        ex_desc1 = QVBoxLayout()
        self.lbl_ex_stud = QLabel("", card_ex_stud)
        self.lbl_ex_stud.setStyleSheet("font-weight: bold; font-size: 13px; color: #1E293B;")
        ex_desc1.addWidget(self.lbl_ex_stud)
        self.desc_ex_stud = QLabel("", card_ex_stud)
        self.desc_ex_stud.setStyleSheet("font-size: 11px; color: #64748B;")
        ex_desc1.addWidget(self.desc_ex_stud)
        ces_layout.addLayout(ex_desc1)
        ces_layout.addStretch(1)
        
        self.btn_ex_stud = PremiumButton("", is_primary=True, parent=card_ex_stud)
        self.btn_ex_stud.clicked.connect(self.export_students_excel)
        ces_layout.addWidget(self.btn_ex_stud)
        excel_vbox.addWidget(card_ex_stud)
        
        # 2. Excel Employees
        card_ex_emp = SleekCard(excel_section_widget)
        card_ex_emp.setFixedHeight(95)
        cee_layout = QHBoxLayout(card_ex_emp)
        cee_layout.setContentsMargins(20, 15, 20, 15)
        
        ex_desc2 = QVBoxLayout()
        self.lbl_ex_emp = QLabel("", card_ex_emp)
        self.lbl_ex_emp.setStyleSheet("font-weight: bold; font-size: 13px; color: #1E293B;")
        ex_desc2.addWidget(self.lbl_ex_emp)
        self.desc_ex_emp = QLabel("", card_ex_emp)
        self.desc_ex_emp.setStyleSheet("font-size: 11px; color: #64748B;")
        ex_desc2.addWidget(self.desc_ex_emp)
        cee_layout.addLayout(ex_desc2)
        cee_layout.addStretch(1)
        
        self.btn_ex_emp = PremiumButton("", is_primary=True, parent=card_ex_emp)
        self.btn_ex_emp.clicked.connect(self.export_employees_excel)
        cee_layout.addWidget(self.btn_ex_emp)
        excel_vbox.addWidget(card_ex_emp)
        
        # 3. Excel Attendance
        card_ex_att = SleekCard(excel_section_widget)
        card_ex_att.setFixedHeight(95)
        cea_layout = QHBoxLayout(card_ex_att)
        cea_layout.setContentsMargins(20, 15, 20, 15)
        
        ex_desc3 = QVBoxLayout()
        self.lbl_ex_att = QLabel("", card_ex_att)
        self.lbl_ex_att.setStyleSheet("font-weight: bold; font-size: 13px; color: #1E293B;")
        ex_desc3.addWidget(self.lbl_ex_att)
        self.desc_ex_att = QLabel("", card_ex_att)
        self.desc_ex_att.setStyleSheet("font-size: 11px; color: #64748B;")
        ex_desc3.addWidget(self.desc_ex_att)
        cea_layout.addLayout(ex_desc3)
        cea_layout.addStretch(1)
        
        self.btn_ex_att = PremiumButton("", is_primary=True, parent=card_ex_att)
        self.btn_ex_att.clicked.connect(self.export_attendance_excel)
        cea_layout.addWidget(self.btn_ex_att)
        excel_vbox.addWidget(card_ex_att)
        
        excel_vbox.addStretch(1)
        grid_layout.addWidget(excel_section_widget, 0, 1)
        
        layout.addLayout(grid_layout)
        layout.addStretch(1)

    def populate_dropdowns(self):
        """Seed dropdown menus dynamically from database records."""
        # Class Selection
        self.combo_pdf_class.clear()
        self.combo_pdf_class.addItem("All / Tous", "")
        
        self.combo_pdf_class.blockSignals(True)
        classes = db.get_classes()
        for c in classes:
            name = c['name']
            self.combo_pdf_class.addItem(name, name)
        self.combo_pdf_class.blockSignals(False)
            
        # Employees Dropdown
        self.combo_employees_cert.clear()
        employees = db.get_employees()
        for e in employees:
            fullname = f"{e['last_name'].upper()} {e['first_name']} (ID: {e['employee_id']})"
            self.combo_employees_cert.addItem(fullname, e['id'])
            
        # Students Dropdown
        self.combo_students_sheet.clear()
        students = db.get_students()
        for s in students:
            fullname = f"{s['last_name'].upper()} {s['first_name']} ({s['class_name'] or '-'})"
            self.combo_students_sheet.addItem(fullname, s['id'])

    def refresh_lists(self):
        """Called whenever the view is focused to load newly inserted records."""
        self.populate_dropdowns()

    def _handle_export_error(self, e, action_name="Error"):
        if isinstance(e, PermissionError):
            msg = (
                "The export file is currently open in Excel or another program. Please close it and retry."
                if self.trans.current_language == 'en'
                else "Le fichier est actuellement ouvert dans Excel ou un autre programme. Veuillez le fermer et réessayer."
            )
            QMessageBox.warning(self, tr("warning"), msg)
        else:
            QMessageBox.critical(self, tr("error"), f"{action_name}: {e}")

    # =============================================================
    # Excel Generators
    # =============================================================
    def export_students_excel(self):
        try:
            lang = self.trans.current_language
            filepath = excel_service.export_students_to_excel(lang)
            QMessageBox.information(self, tr("success"), tr("exp_success_excel", path=filepath))
        except Exception as e:
            self._handle_export_error(e, "Error exporting students")

    def export_employees_excel(self):
        try:
            lang = self.trans.current_language
            filepath = excel_service.export_employees_to_excel(lang)
            QMessageBox.information(self, tr("success"), tr("exp_success_excel", path=filepath))
        except Exception as e:
            self._handle_export_error(e, "Error exporting employees")

    def export_attendance_excel(self):
        try:
            lang = self.trans.current_language
            filepath = excel_service.export_attendance_to_excel(lang)
            QMessageBox.information(self, tr("success"), tr("exp_success_excel", path=filepath))
        except Exception as e:
            self._handle_export_error(e, "Error exporting attendance")

    # =============================================================
    # PDF Generators
    # =============================================================
    def generate_student_list_pdf(self):
        try:
            lang = self.trans.current_language
            class_filter = self.combo_pdf_class.currentData()
            filepath = pdf_service.generate_student_list_pdf(class_filter, lang)
            QMessageBox.information(self, tr("success"), tr("exp_success_pdf", path=filepath))
        except Exception as e:
            self._handle_export_error(e, "Error generating student list PDF")

    def generate_employee_list_pdf(self):
        try:
            lang = self.trans.current_language
            filepath = pdf_service.generate_employee_list_pdf(lang)
            QMessageBox.information(self, tr("success"), tr("exp_success_pdf", path=filepath))
        except Exception as e:
            self._handle_export_error(e, "Error generating employee list PDF")

    def generate_work_certificate_pdf(self):
        emp_id = self.combo_employees_cert.currentData()
        if not emp_id:
            QMessageBox.warning(self, tr("warning"), "Please select an employee first." if self.trans.current_language == 'en' else "Veuillez sélectionner un employé d'abord.")
            return
        try:
            filepath = pdf_service.generate_work_certificate_pdf(emp_id)
            QMessageBox.information(self, tr("success"), tr("exp_success_pdf", path=filepath))
        except Exception as e:
            self._handle_export_error(e, "Error generating work certificate PDF")

    def generate_student_sheet_pdf(self):
        student_id = self.combo_students_sheet.currentData()
        if not student_id:
            QMessageBox.warning(self, tr("warning"), "Please select a student first." if self.trans.current_language == 'en' else "Veuillez sélectionner un élève d'abord.")
            return
        try:
            lang = self.trans.current_language
            filepath = pdf_service.generate_student_info_sheet_pdf(student_id, lang)
            QMessageBox.information(self, tr("success"), tr("exp_success_pdf", path=filepath))
        except Exception as e:
            self._handle_export_error(e, "Error generating student sheet PDF")

    def open_exports_folder(self):
        """Shell helper to launch Windows Explorer directly into exports."""
        exports_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "exports")
        os.makedirs(exports_path, exist_ok=True)
        try:
            # Multiplatform compatible opening
            if os.name == 'nt':
                os.startfile(exports_path)
            else:
                subprocess.Popen(['xdg-open', exports_path])
        except Exception as e:
            QMessageBox.critical(self, tr("error"), f"Could not open directory: {e}")

    def update_translation(self):
        self.title_label.setText(tr("exp_title"))
        self.subtitle_label.setText(tr("exp_subtitle"))
        self.open_folder_btn.setText(tr("exp_folder_open_btn"))
        
        # Sections titles
        self.pdf_section_title.setText(tr("exp_sec_pdf"))
        self.excel_section_title.setText(tr("exp_sec_excel"))
        
        # Card Labels PDF
        self.lbl_pdf_list.setText(tr("exp_pdf_general_list"))
        self.desc_pdf_list.setText(tr("exp_pdf_general_list_desc"))
        self.lbl_pdf_emp.setText(tr("exp_pdf_employee_list"))
        self.desc_pdf_emp.setText(tr("exp_pdf_employee_list_desc"))
        self.lbl_pdf_cert.setText(tr("exp_pdf_work_cert"))
        self.desc_pdf_cert.setText(tr("exp_pdf_work_cert_desc"))
        self.lbl_pdf_stud.setText(tr("exp_pdf_student_sheet"))
        self.desc_pdf_stud.setText(tr("exp_pdf_student_sheet_desc"))
        
        # Card Buttons PDF
        self.btn_gen_stud_list.setText(tr("exp_btn_generate"))
        self.btn_gen_emp_list.setText(tr("exp_btn_generate"))
        self.btn_gen_cert.setText(tr("exp_btn_generate"))
        self.btn_gen_stud_sheet.setText(tr("exp_btn_generate"))
        
        # Card Labels Excel
        self.lbl_ex_stud.setText(tr("exp_excel_students"))
        self.desc_ex_stud.setText(tr("exp_excel_students_desc"))
        self.lbl_ex_emp.setText(tr("exp_excel_employees"))
        self.desc_ex_emp.setText(tr("exp_excel_employees_desc"))
        self.lbl_ex_att.setText(tr("exp_excel_attendance"))
        self.desc_ex_att.setText(tr("exp_excel_attendance_desc"))
        
        # Card Buttons Excel
        self.btn_ex_stud.setText(tr("exp_btn_export"))
        self.btn_ex_emp.setText(tr("exp_btn_export"))
        self.btn_ex_att.setText(tr("exp_btn_export"))
