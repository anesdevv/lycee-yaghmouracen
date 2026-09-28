import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
import database.db as db
from services.translation_service import tr

import re

EXPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "exports")

def ensure_exports_dir():
    os.makedirs(EXPORTS_DIR, exist_ok=True)

def sanitize_filename(name):
    """Sanitize strings to be safe for filenames across Windows/Linux."""
    clean = re.sub(r'[\\/*?:"<>|]', '_', str(name).strip())
    return clean or "unnamed"


class NumberedCanvas(canvas.Canvas):
    """Custom canvas to compute dynamic total page count and draw custom header/footer on every page."""
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []
        self.doc_lang = getattr(self, 'doc_lang', 'fr')

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#1F497D")) # Sleek Deep Blue
        
        # Draw Header
        header_text = "LYCÉE YAGHMOURACEN — Portails Administratifs" if self.doc_lang == 'fr' else "LYCÉE YAGHMOURACEN — Administrative Portal"
        self.drawString(54, 755, header_text)
        self.setStrokeColor(colors.HexColor("#1F497D"))
        self.setLineWidth(0.75)
        self.line(54, 748, 558, 748)
        
        # Draw Footer
        self.setStrokeColor(colors.HexColor("#E0E0E0"))
        self.setLineWidth(0.5)
        self.line(54, 45, 558, 45)
        
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#777777"))
        gen_text = f"Document généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}" if self.doc_lang == 'fr' else f"Document generated on {datetime.now().strftime('%d/%m/%Y at %H:%M')}"
        self.drawString(54, 32, gen_text)
        
        page_str = f"Page {self._pageNumber} sur {page_count}" if self.doc_lang == 'fr' else f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 32, page_str)
        self.restoreState()


def get_canvas_for_lang(lang="fr"):
    """Factory to create a NumberedCanvas class configured with the chosen language."""
    class LocalizedNumberedCanvas(NumberedCanvas):
        def __init__(self, *args, **kwargs):
            self.doc_lang = lang
            super().__init__(*args, **kwargs)
    return LocalizedNumberedCanvas


def get_official_header_story(lang="fr"):
    """Returns a narrative story block containing the formal Algerian government header."""
    styles = getSampleStyleSheet()
    
    rep_style = ParagraphStyle(
        'RepStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#444444")
    )
    
    title_style = ParagraphStyle(
        'HeaderTitleStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1F497D")
    )
    
    meta_style = ParagraphStyle(
        'HeaderMetaStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        alignment=TA_LEFT,
        textColor=colors.HexColor("#333333")
    )

    meta_right_style = ParagraphStyle(
        'HeaderMetaRightStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        alignment=TA_RIGHT,
        textColor=colors.HexColor("#333333")
    )

    story = []
    
    # Republic Title
    rep_text = (
        "RÉPUBLIQUE ALGÉRIENNE DÉMOCRATIQUE ET POPULAIRE<br/>"
        "MINISTÈRE DE L'ÉDUCATION NATIONALE<br/>"
        "DIRECTION DE L'ÉDUCATION DE LA WILAYA D'ORAN"
    ) if lang == "fr" else (
        "DEMOCRATIC AND POPULAR REPUBLIC OF ALGERIA<br/>"
        "MINISTRY OF NATIONAL EDUCATION<br/>"
        "DIRECTORATE OF EDUCATION OF ORAN PROVINCE"
    )
    
    story.append(Paragraph(rep_text, rep_style))
    story.append(Spacer(1, 15))
    
    # Institution metadata (two columns layout)
    school_info = (
        "<b>Lycée :</b> Yaghmouracen<br/>"
        "<b>Code Établissement :</b> 310892"
    ) if lang == "fr" else (
        "<b>High School:</b> Yaghmouracen<br/>"
        "<b>School Code:</b> 310892"
    )
    
    date_info = f"<b>Date :</b> {datetime.now().strftime('%d/%m/%Y')}"
    
    meta_table_data = [
        [Paragraph(school_info, meta_style), Paragraph(date_info, meta_right_style)]
    ]
    
    meta_table = Table(meta_table_data, colWidths=[250, 250])
    meta_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    
    story.append(meta_table)
    story.append(Spacer(1, 10))
    
    # Thick Divider Line
    divider = Table([[""]], colWidths=[504], rowHeights=[2])
    divider.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 2, colors.HexColor("#1F497D")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(divider)
    story.append(Spacer(1, 20))
    
    return story


# =====================================================================
# PDF Document Builders
# =====================================================================

def generate_student_list_pdf(class_filter=None, lang="fr"):
    ensure_exports_dir()
    suffix = f"_{sanitize_filename(class_filter)}" if class_filter else "_all"
    filepath = os.path.join(EXPORTS_DIR, f"student_list{suffix}.pdf")
    
    # Page layout: Margins set at 0.5 inches (36 points) for maximum table room.
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1F497D"),
        spaceAfter=15
    )
    
    cell_style = ParagraphStyle(
        'CellText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        alignment=TA_LEFT,
        textColor=colors.HexColor("#0F172A")
    )
    
    cell_center = ParagraphStyle(
        'CellCenterText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#0F172A")
    )

    header_style = ParagraphStyle(
        'HeaderCellText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        alignment=TA_LEFT,
        textColor=colors.white
    )
    
    header_center = ParagraphStyle(
        'HeaderCellCenterText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        alignment=TA_CENTER,
        textColor=colors.white
    )

    story = get_official_header_story(lang)
    
    # Title
    t_key = "LISTE OFFICIELLE DES ÉLÈVES" if lang == "fr" else "OFFICIAL STUDENTS REGISTRY"
    if class_filter:
        title_text = f"{t_key} — CLASSE : {class_filter}"
    else:
        title_text = t_key
        
    story.append(Paragraph(title_text, title_style))
    story.append(Spacer(1, 10))
    
    # Load data
    students = db.get_students(class_filter=class_filter)
    
    # Define Table Headers with dedicated header styles
    headers = [
        Paragraph("<b>ID</b>", header_center),
        Paragraph("<b>Nom</b>", header_style) if lang == "fr" else Paragraph("<b>Last Name</b>", header_style),
        Paragraph("<b>Prénom</b>", header_style) if lang == "fr" else Paragraph("<b>First Name</b>", header_style),
        Paragraph("<b>Classe</b>", header_center) if lang == "fr" else Paragraph("<b>Class</b>", header_center),
        Paragraph("<b>Parent / Tuteur</b>", header_style) if lang == "fr" else Paragraph("<b>Parent / Guardian</b>", header_style),
        Paragraph("<b>Absences</b>", header_center) if lang == "fr" else Paragraph("<b>Absences</b>", header_center)
    ]
    
    table_data = [headers]
    
    for s in students:
        table_data.append([
            Paragraph(str(s['id']), cell_center),
            Paragraph(s['last_name'].upper(), cell_style),
            Paragraph(s['first_name'], cell_style),
            Paragraph(s['class_name'] or "", cell_center),
            Paragraph(s['parent_name'] or "", cell_style),
            Paragraph(str(s['absence_count'] or 0), cell_center),
        ])
        
    # Printable width: 504 pt. Distribute columns width beautifully
    col_widths = [40, 104, 100, 70, 130, 60]
    
    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1F497D")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8F9FA")]),
    ]))
    
    story.append(t)
    doc.build(story, canvasmaker=get_canvas_for_lang(lang))
    return filepath


def generate_employee_list_pdf(lang="fr"):
    ensure_exports_dir()
    filepath = os.path.join(EXPORTS_DIR, "employee_list.pdf")
    
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1F497D"),
        spaceAfter=15
    )
    
    cell_style = ParagraphStyle(
        'CellText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=10,
        alignment=TA_LEFT,
        textColor=colors.HexColor("#0F172A")
    )
    
    cell_center = ParagraphStyle(
        'CellCenterText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=10,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#0F172A")
    )

    header_style = ParagraphStyle(
        'EmpHeaderCellText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=10,
        alignment=TA_LEFT,
        textColor=colors.white
    )
    
    header_center = ParagraphStyle(
        'EmpHeaderCellCenterText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=10,
        alignment=TA_CENTER,
        textColor=colors.white
    )

    story = get_official_header_story(lang)
    
    title_text = "REGISTRE OFFICIEL DES EMPLOYÉS" if lang == "fr" else "OFFICIAL EMPLOYEE DIRECTORY"
    story.append(Paragraph(title_text, title_style))
    story.append(Spacer(1, 10))
    
    employees = db.get_employees()
    
    headers = [
        Paragraph("<b>ID</b>", header_center),
        Paragraph("<b>Nom Complet</b>", header_style) if lang == "fr" else Paragraph("<b>Full Name</b>", header_style),
        Paragraph("<b>Rôle / Fonction</b>", header_style) if lang == "fr" else Paragraph("<b>Role / Job</b>", header_style),
        Paragraph("<b>Spécialité / Matière</b>", header_style) if lang == "fr" else Paragraph("<b>Specialty</b>", header_style),
        Paragraph("<b>Téléphone</b>", header_center) if lang == "fr" else Paragraph("<b>Phone</b>", header_center),
        Paragraph("<b>Embauche</b>", header_center) if lang == "fr" else Paragraph("<b>Hired</b>", header_center)
    ]
    
    table_data = [headers]
    for e in employees:
        fullname = f"{e['last_name'].upper()} {e['first_name']}"
        table_data.append([
            Paragraph(e['employee_id'], cell_center),
            Paragraph(fullname, cell_style),
            Paragraph(e['role'], cell_style),
            Paragraph(e['specialty'] or "", cell_style),
            Paragraph(e['phone'] or "", cell_center),
            Paragraph(e['hire_date'] or "", cell_center),
        ])
        
    col_widths = [60, 114, 100, 100, 70, 60]
    
    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1F497D")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8F9FA")]),
    ]))
    
    story.append(t)
    doc.build(story, canvasmaker=get_canvas_for_lang(lang))
    return filepath


def generate_attendance_report_pdf(class_name, date_from=None, date_to=None, lang="fr"):
    ensure_exports_dir()
    clean_name = sanitize_filename(class_name)
    filepath = os.path.join(EXPORTS_DIR, f"attendance_report_{clean_name}.pdf")
    
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1F497D"),
        spaceAfter=15
    )
    
    cell_style = ParagraphStyle(
        'CellText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        alignment=TA_LEFT,
        textColor=colors.HexColor("#0F172A")
    )
    
    cell_center = ParagraphStyle(
        'CellCenterText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#0F172A")
    )

    header_style = ParagraphStyle(
        'AttHeaderCellText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        alignment=TA_LEFT,
        textColor=colors.white
    )
    
    header_center = ParagraphStyle(
        'AttHeaderCellCenterText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        alignment=TA_CENTER,
        textColor=colors.white
    )

    story = get_official_header_story(lang)
    
    # Title text formatting
    if date_from and date_to:
        date_str = f"du {date_from} au {date_to}" if lang == "fr" else f"from {date_from} to {date_to}"
    elif date_from:
        date_str = f"depuis {date_from}" if lang == "fr" else f"since {date_from}"
    else:
        date_str = "Historique Général" if lang == "fr" else "Full History"
        
    title_text = f"BILAN DE PRÉSENCE - CLASSE : {class_name}\n({date_str})" if lang == "fr" else f"ATTENDANCE REPORT - CLASS: {class_name}\n({date_str})"
    story.append(Paragraph(title_text, title_style))
    story.append(Spacer(1, 10))
    
    history = db.get_attendance_history(class_name=class_name, date_from=date_from, date_to=date_to)
    
    headers = [
        Paragraph("<b>Date</b>", header_center),
        Paragraph("<b>Élève</b>", header_style) if lang == "fr" else Paragraph("<b>Student</b>", header_style),
        Paragraph("<b>Classe</b>", header_center) if lang == "fr" else Paragraph("<b>Class</b>", header_center),
        Paragraph("<b>Statut</b>", header_center) if lang == "fr" else Paragraph("<b>Status</b>", header_center)
    ]
    
    table_data = [headers]
    for h in history:
        fullname = f"{h['last_name'].upper()} {h['first_name']}"
        status_label = "Présent" if h['status'] == "Present" and lang == "fr" else \
                       ("Absent" if h['status'] == "Absent" and lang == "fr" else h['status'])
                       
        status_color = "#2E7D32" if h['status'] == "Present" else "#C62828" # Green vs Red
        
        status_para_style = ParagraphStyle(
            'StatusStyle',
            parent=cell_center,
            textColor=colors.HexColor(status_color),
            fontName='Helvetica-Bold'
        )
        
        table_data.append([
            Paragraph(h['attendance_date'], cell_center),
            Paragraph(fullname, cell_style),
            Paragraph(h['class_name'] or "", cell_center),
            Paragraph(status_label, status_para_style)
        ])
        
    col_widths = [110, 214, 90, 90]
    
    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1F497D")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8F9FA")]),
    ]))
    
    story.append(t)
    doc.build(story, canvasmaker=get_canvas_for_lang(lang))
    return filepath


def generate_student_info_sheet_pdf(student_id, lang="fr"):
    ensure_exports_dir()
    student = db.get_student_by_id(student_id)
    if not student:
        raise ValueError(f"Student ID {student_id} not found.")
        
    filepath = os.path.join(EXPORTS_DIR, f"student_sheet_{student['id']}.pdf")
    doc = SimpleDocTemplate(filepath, pagesize=letter, leftMargin=54, rightMargin=54, topMargin=72, bottomMargin=72)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, leading=22,
        alignment=TA_CENTER, textColor=colors.HexColor("#1F497D"), spaceAfter=20
    )
    
    label_style = ParagraphStyle('LabelStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor("#1F497D"))
    value_style = ParagraphStyle('ValStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=10)
    section_style = ParagraphStyle('SecStyle', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12, leading=15, textColor=colors.HexColor("#1F497D"), spaceBefore=10, spaceAfter=8)
    cell_center = ParagraphStyle('CellCenterText', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=11, alignment=TA_CENTER)

    story = get_official_header_story(lang)
    
    title_text = "DOSSIER SIGNALÉTIQUE DE L'ÉLÈVE" if lang == "fr" else "STUDENT INFORMATION SHEET"
    story.append(Paragraph(title_text, title_style))
    
    # Horizontal layout: Photo on left, key stats on right
    # Check photo
    photo_w, photo_h = 100, 110
    photo_element = None
    if student['photo_path'] and os.path.exists(student['photo_path']):
        try:
            photo_element = Image(student['photo_path'], width=photo_w, height=photo_h)
        except Exception:
            pass
            
    if not photo_element:
        # Create empty outline box placeholder
        photo_box = Table([["[ PHOTO ]"]], colWidths=[photo_w], rowHeights=[photo_h])
        photo_box.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#BBBBBB")),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor("#888888")),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
        ]))
        photo_element = photo_box

    # Info grid next to photo
    fullname = f"{student['last_name'].upper()} {student['first_name']}"
    info_table_data = [
        [Paragraph("Nom Complet : " if lang == "fr" else "Full Name: ", label_style), Paragraph(fullname, value_style)],
        [Paragraph("Classe : " if lang == "fr" else "Class: ", label_style), Paragraph(student['class_name'] or "-", value_style)],
        [Paragraph("Genre : " if lang == "fr" else "Gender: ", label_style), Paragraph("Masculin" if student['gender'] == "Male" and lang == "fr" else ("Féminin" if student['gender'] == "Female" and lang == "fr" else student['gender']), value_style)],
        [Paragraph("Date Naissance : " if lang == "fr" else "Birth Date: ", label_style), Paragraph(student['birth_date'] or "-", value_style)]
    ]
    info_table = Table(info_table_data, colWidths=[100, 270])
    info_table.setStyle(TableStyle([
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#EEEEEE")),
    ]))

    header_block_table = Table([[photo_element, info_table]], colWidths=[120, 384])
    header_block_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    
    story.append(header_block_table)
    story.append(Spacer(1, 15))
    
    # 2. Parental Information Section
    story.append(Paragraph("INFORMATIONS COMPLÉMENTAIRES & CONTACT" if lang == "fr" else "ADDITIONAL CONTACT INFORMATION", section_style))
    
    contact_data = [
        [Paragraph("Tuteur / Parent : " if lang == "fr" else "Parent/Guardian: ", label_style), Paragraph(student['parent_name'] or "-", value_style)],
        [Paragraph("Adresse Résidence : " if lang == "fr" else "Address: ", label_style), Paragraph(student['address'] or "-", value_style)],
    ]
    contact_table = Table(contact_data, colWidths=[120, 384])
    contact_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E0E0E0")),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#F8F9FA")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(contact_table)
    story.append(Spacer(1, 15))
    
    # 3. Attendance Summary Section
    story.append(Paragraph("BILAN SCOLAIRE DES ABSENCES" if lang == "fr" else "ACADEMIC ABSENCE SHEET", section_style))
    
    absences = db.get_attendance_history(class_name=student['class_name'])
    student_absences = [a for a in absences if a['student_id'] == student['id'] and a['status'] == 'Absent']
    
    abs_title = f"Total des Absences Enregistrées : {student['absence_count']}" if lang == "fr" else f"Total Registered Absences: {student['absence_count']}"
    story.append(Paragraph(f"<b>{abs_title}</b>", label_style))
    story.append(Spacer(1, 8))
    
    if student_absences:
        abs_headers = [Paragraph("<b>Date d'Absence Enregistrée</b>", cell_center)]
        abs_table_data = [abs_headers]
        for a in student_absences:
            abs_table_data.append([Paragraph(a['attendance_date'], cell_center)])
            
        abs_table = Table(abs_table_data, colWidths=[200])
        abs_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E0E0E0")),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('TOPPADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(abs_table)
    else:
        no_abs = "Aucune absence enregistrée pour cet élève." if lang == "fr" else "No absences recorded for this student."
        story.append(Paragraph(no_abs, value_style))
        
    doc.build(story, canvasmaker=get_canvas_for_lang(lang))
    return filepath


def generate_employee_info_sheet_pdf(employee_db_id, lang="fr"):
    ensure_exports_dir()
    employee = db.get_employee_by_id(employee_db_id)
    if not employee:
        raise ValueError(f"Employee DB ID {employee_db_id} not found.")
        
    clean_emp_id = sanitize_filename(employee['employee_id'])
    filepath = os.path.join(EXPORTS_DIR, f"employee_sheet_{clean_emp_id}.pdf")
    doc = SimpleDocTemplate(filepath, pagesize=letter, leftMargin=54, rightMargin=54, topMargin=72, bottomMargin=72)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, leading=22,
        alignment=TA_CENTER, textColor=colors.HexColor("#1F497D"), spaceAfter=20
    )
    
    label_style = ParagraphStyle('LabelStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor("#1F497D"))
    value_style = ParagraphStyle('ValStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=10)
    section_style = ParagraphStyle('SecStyle', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12, leading=15, textColor=colors.HexColor("#1F497D"), spaceBefore=15, spaceAfter=8)

    story = get_official_header_story(lang)
    
    title_text = "FICHE ADMINISTRATIVE DU PERSONNEL" if lang == "fr" else "EMPLOYEE DATA SHEET"
    story.append(Paragraph(title_text, title_style))
    
    # Info list
    fullname = f"{employee['last_name'].upper()} {employee['first_name']}"
    
    info_data = [
        [Paragraph("ID Employé : " if lang == "fr" else "Employee ID: ", label_style), Paragraph(employee['employee_id'], value_style)],
        [Paragraph("Nom Complet : " if lang == "fr" else "Full Name: ", label_style), Paragraph(fullname, value_style)],
        [Paragraph("Fonction / Rôle : " if lang == "fr" else "Role / Job: ", label_style), Paragraph(employee['role'], value_style)],
        [Paragraph("Matière / Spécialité : " if lang == "fr" else "Specialty / Subject: ", label_style), Paragraph(employee['specialty'] or "-", value_style)],
        [Paragraph("Date d'Embauche : " if lang == "fr" else "Hire Date: ", label_style), Paragraph(employee['hire_date'] or "-", value_style)],
        [Paragraph("Salaire Mensuel : " if lang == "fr" else "Monthly Salary: ", label_style), Paragraph(f"{employee['salary']:,.2f} DA" if employee['salary'] else "-", value_style)],
        [Paragraph("N° Téléphone : " if lang == "fr" else "Phone Number: ", label_style), Paragraph(employee['phone'] or "-", value_style)],
    ]
    
    info_table = Table(info_data, colWidths=[150, 354])
    info_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E0E0E0")),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#F8F9FA")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    
    story.append(info_table)
    doc.build(story, canvasmaker=get_canvas_for_lang(lang))
    return filepath


def generate_work_certificate_pdf(employee_db_id):
    """
    Generate an official Work Certificate (Attestation de Travail) in standard French.
    French is the mandatory administrative standard for employee certificates in Algerian institutions.
    """
    ensure_exports_dir()
    employee = db.get_employee_by_id(employee_db_id)
    if not employee:
        raise ValueError(f"Employee DB ID {employee_db_id} not found.")
        
    clean_emp_id = sanitize_filename(employee['employee_id'])
    filepath = os.path.join(EXPORTS_DIR, f"attestation_travail_{clean_emp_id}.pdf")
    
    # Attestation of work is a formal single page, thus set standard margins: 1 inch (72 points)
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        leftMargin=72,
        rightMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    
    # Typography Styles
    rep_style = ParagraphStyle(
        'CertRepStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        alignment=TA_CENTER,
        textColor=colors.black
    )
    
    school_style = ParagraphStyle(
        'CertSchoolStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        alignment=TA_LEFT
    )
    
    title_style = ParagraphStyle(
        'CertTitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1F497D"),
        spaceBefore=30,
        spaceAfter=30
    )
    
    body_style = ParagraphStyle(
        'CertBodyStyle',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        leading=20,
        alignment=TA_JUSTIFY
    )
    
    signature_title_style = ParagraphStyle(
        'CertSigTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        alignment=TA_RIGHT
    )
    
    signature_sub_style = ParagraphStyle(
        'CertSigSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        alignment=TA_RIGHT
    )

    story = []
    
    # 1. Official Government Banner
    rep_text = (
        "RÉPUBLIQUE ALGÉRIENNE DÉMOCRATIQUE ET POPULAIRE<br/>"
        "MINISTÈRE DE L'ÉDUCATION NATIONALE<br/>"
        "DIRECTION DE L'ÉDUCATION DE LA WILAYA D'ORAN"
    )
    story.append(Paragraph(rep_text, rep_style))
    story.append(Spacer(1, 20))
    
    # 2. Institution Detail
    school_text = (
        "<b>Établissement :</b> Lycée Yaghmouracen<br/>"
        "<b>Code Établissement :</b> 310892"
    )
    story.append(Paragraph(school_text, school_style))
    story.append(Spacer(1, 10))
    
    # Thick separator line
    divider = Table([[""]], colWidths=[468], rowHeights=[2])
    divider.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 2, colors.HexColor("#1F497D")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(divider)
    
    # 3. Main Title
    story.append(Paragraph("ATTESTATION DE TRAVAIL", title_style))
    
    # 4. Formal Narrative Body
    fullname = f"<b>M. {employee['last_name'].upper()} {employee['first_name']}</b>"
    if employee['role'].lower() in ["enseignant", "prof", "professeur", "teacher"]:
        subject_str = f" de {employee['specialty']}" if employee['specialty'] else ""
        role_descr = f"enseignant(e){subject_str}"
    else:
        role_descr = f"en qualité de {employee['role']}"
        
    hire_date_str = employee['hire_date'] or "non définie"
    
    body_text = (
        f"Le Directeur du Lycée Yaghmouracen soussigné, certifie par la présente que "
        f"{fullname}, titulaire de la carte professionnelle ID {employee['employee_id']}, "
        f"est employé(e) au sein de notre établissement {role_descr}, "
        f"depuis le {hire_date_str} jusqu'à ce jour.<br/><br/>"
        f"La présente attestation est délivrée à l'intéressé(e) pour servir et valoir "
        f"ce que de droit."
    )
    story.append(Paragraph(body_text, body_style))
    story.append(Spacer(1, 40))
    
    # 5. Sign-off and Date section (Right align)
    date_place_text = f"Fait à Oran, le {datetime.now().strftime('%d/%m/%Y')}"
    story.append(Paragraph(f"<i>{date_place_text}</i>", signature_sub_style))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("<b>Le Directeur de l'Établissement</b>", signature_title_style))
    story.append(Paragraph("<i>Signature & Sceau</i>", signature_sub_style))
    
    # Signature box spacer for actual signature and stamp
    story.append(Spacer(1, 60))
    
    # Build Document without canvas NumberedCanvas because Attestation is a single certified page
    doc.build(story)
    return filepath
