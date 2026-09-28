class TranslationService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TranslationService, cls).__new__(cls, *args, **kwargs)
            cls._instance._init_service()
        return cls._instance

    def _init_service(self):
        self.current_language = "fr"  # Default to French as it's an Algerian high school
        self.listeners = []

        # Comprehensive Translation Dictionary
        self.translations = {
            "en": {
                # Sidebar / General
                "app_title": "Lycée Yaghmouracen",
                "sidebar_dashboard": "Dashboard",
                "sidebar_students": "Students",
                "sidebar_employees": "Employees",
                "sidebar_attendance": "Attendance",
                "sidebar_exports": "Exports & Reports",
                "sidebar_logout": "Logout",
                "lang_label": "Language:",
                "footer_text": "Lycée Yaghmouracen Management System © 2026",
                "action_edit": "Edit",
                "action_delete": "Delete",
                "action_view": "View Profile",
                "save": "Save",
                "cancel": "Cancel",
                "confirm": "Confirm",
                "success": "Success",
                "error": "Error",
                "warning": "Warning",
                "yes": "Yes",
                "no": "No",
                "all": "All",
                "search_placeholder": "Search...",
                
                # Login Screen
                "login_title": "Administrator Login",
                "login_subtitle": "Access the High School Management Portal",
                "username_placeholder": "Username",
                "password_placeholder": "Password",
                "login_button": "Log In",
                "login_failed_title": "Login Failed",
                "login_failed_msg": "Invalid username or password. Please try again.",

                # Dashboard Screen
                "dash_welcome": "Welcome back, Administrator",
                "dash_subtitle": "Here is the summary of Lycée Yaghmouracen for today.",
                "dash_total_students": "Total Students",
                "dash_total_employees": "Total Staff",
                "dash_total_classes": "Total Classes",
                "dash_total_absences": "Total Absences",
                "dash_school_name": "Lycée Yaghmouracen",
                "dash_stats_title": "Quick Overview",
                "dash_time_title": "Date & Time",
                "dash_active_classes": "Active Classes",

                # Classes Module
                "sidebar_classes": "Classes",
                "class_title": "Classes Registry",
                "class_subtitle": "Manage high school class sections, divisions, and academic pathways.",
                "class_add_btn": "Add New Class",
                "class_tab_id": "ID",
                "class_tab_name": "Class Name",
                "class_tab_actions": "Actions",
                "class_err_name": "Class name is required and must be unique.",
                "class_add_success": "Class added successfully.",
                "class_update_success": "Class updated successfully.",
                "class_delete_confirm": "Are you sure you want to delete class: {name}?\nStudents currently in this class will have their class field cleared.",
                "class_delete_success": "Class record deleted successfully.",

                # Student Module
                "stud_title": "Student Directory",
                "stud_subtitle": "Manage and view student academic profiles and records.",
                "stud_add_btn": "Add New Student",
                "stud_filter_class": "Class:",
                "stud_filter_gender": "Gender:",
                "stud_search_hint": "Search by name or parent...",
                "stud_tab_id": "ID",
                "stud_tab_photo": "Photo",
                "stud_tab_name": "Full Name",
                "stud_tab_class": "Class",
                "stud_tab_absences": "Absences",
                "stud_tab_actions": "Actions",
                
                # Student Dialog / Profile
                "stud_profile_title": "Student Profile Card",
                "stud_personal_info": "Personal Information",
                "stud_parental_info": "Parent / Contact Information",
                "stud_first_name": "First Name:",
                "stud_last_name": "Last Name:",
                "stud_birth_date": "Date of Birth:",
                "stud_gender": "Gender:",
                "stud_class": "Class Name:",
                "stud_address": "Home Address:",
                "stud_parent": "Parent/Guardian Name:",
                "stud_photo": "Profile Photo:",
                "stud_photo_btn": "Browse Photo...",
                "stud_err_name": "First and Last Names are required fields.",
                "stud_err_class": "A valid class name is required.",
                "stud_add_success": "Student added successfully.",
                "stud_update_success": "Student profile updated successfully.",
                "stud_delete_confirm": "Are you sure you want to delete student: {name}?\nAll attendance logs for this student will be permanently deleted.",
                "stud_delete_success": "Student record deleted successfully.",

                # Employee Module
                "emp_title": "Employee Directory",
                "emp_subtitle": "Manage teacher assignments, staff operations, and certificates.",
                "emp_add_btn": "Add New Employee",
                "emp_filter_role": "Role:",
                "emp_filter_subject": "Specialty:",
                "emp_search_hint": "Search by name or Employee ID...",
                "emp_tab_id": "Employee ID",
                "emp_tab_name": "Full Name",
                "emp_tab_role": "Role / Job Title",
                "emp_tab_subject": "Specialty / Subject",
                "emp_tab_phone": "Phone Number",
                "emp_tab_actions": "Actions",

                # Employee Dialog / Profile
                "emp_profile_title": "Employee Profile Card",
                "emp_job_details": "Employment details",
                "emp_contact_details": "Contact details",
                "emp_id_field": "Employee ID (Unique):",
                "emp_first_name": "First Name:",
                "emp_last_name": "Last Name:",
                "emp_role": "Role:",
                "emp_hire_date": "Hire Date:",
                "emp_salary": "Monthly Salary (DZD):",
                "emp_subject": "Specialty / Subject:",
                "emp_phone": "Phone Number:",
                "emp_err_id": "A unique Employee ID is required.",
                "emp_err_id_exists": "This Employee ID already exists. Please choose a unique one.",
                "emp_err_names": "First and Last names are required.",
                "emp_add_success": "Employee record added successfully.",
                "emp_update_success": "Employee record updated successfully.",
                "emp_delete_confirm": "Are you sure you want to delete employee: {name}?",
                "emp_delete_success": "Employee record deleted successfully.",

                # Attendance Module
                "att_title": "Attendance Registry",
                "att_subtitle": "Take daily rolls, register student absences, and review historical logs.",
                "att_tab_daily": "Mark Daily Attendance",
                "att_tab_history": "Attendance History Log",
                "att_date_label": "Date:",
                "att_class_label": "Class:",
                "att_load_roster": "Load Roster",
                "att_save_roster": "Save Attendance Registry",
                "att_tab_name": "Student Name",
                "att_tab_status": "Attendance Status",
                "att_status_present": "Present",
                "att_status_absent": "Absent",
                "att_save_success": "Attendance registered and absence counts synchronized successfully.",
                "att_history_search": "Filter Logs",
                "att_hist_date_from": "Date From:",
                "att_hist_date_to": "Date To:",
                "att_hist_status": "Status",
                "att_hist_no_records": "No attendance records found matching filters.",

                # Exports Module
                "exp_title": "Document & Report Hub",
                "exp_subtitle": "Export tables to Excel format and generate premium printable PDF administrative sheets.",
                "exp_sec_pdf": "PDF Administrative Document Suite",
                "exp_sec_excel": "Excel Data Exports",
                "exp_pdf_general_list": "Student List Report",
                "exp_pdf_general_list_desc": "Generates a clean grid of all enrolled students sorted by class.",
                "exp_pdf_employee_list": "Employee Directory Report",
                "exp_pdf_employee_list_desc": "Generates a standard listing of all teachers and administrative staff.",
                "exp_pdf_att_report": "Class Attendance Summary",
                "exp_pdf_att_report_desc": "Export attendance reports for a class and selected date range.",
                "exp_pdf_work_cert": "Employee Work Certificate",
                "exp_pdf_work_cert_desc": "Generate a formal French 'Attestation de Travail' for a selected employee.",
                "exp_pdf_student_sheet": "Student Information Sheet",
                "exp_pdf_student_sheet_desc": "Compile personal details and full absence counts into a printable PDF folder sheet.",
                "exp_pdf_employee_sheet": "Employee Details Sheet",
                "exp_pdf_employee_sheet_desc": "Print comprehensive administrative record and contact information for an employee.",
                
                "exp_excel_students": "Export Students Table (.xlsx)",
                "exp_excel_students_desc": "Export complete student directory database with custom auto-sized column widths.",
                "exp_excel_employees": "Export Employees Table (.xlsx)",
                "exp_excel_employees_desc": "Export complete employee registry database.",
                "exp_excel_attendance": "Export Attendance Logs (.xlsx)",
                "exp_excel_attendance_desc": "Export historical student check-in/absence logs.",
                
                "exp_btn_generate": "Generate PDF",
                "exp_btn_export": "Export to Excel",
                "exp_success_pdf": "PDF document generated successfully:\n{path}",
                "exp_success_excel": "Excel sheet exported successfully:\n{path}",
                "exp_select_student": "Select Student:",
                "exp_select_employee": "Select Employee:",
                "exp_select_class": "Select Class:",
                "exp_folder_open_btn": "Open Exports Folder",
            },
            "fr": {
                # Sidebar / General
                "app_title": "Lycée Yaghmouracen",
                "sidebar_dashboard": "Tableau de Bord",
                "sidebar_students": "Élèves",
                "sidebar_employees": "Personnel",
                "sidebar_attendance": "Absences / Présence",
                "sidebar_exports": "Rapports & Exports",
                "sidebar_logout": "Déconnexion",
                "lang_label": "Langue :",
                "footer_text": "Système de Gestion du Lycée Yaghmouracen © 2026",
                "action_edit": "Modifier",
                "action_delete": "Supprimer",
                "action_view": "Fiche Profil",
                "save": "Enregistrer",
                "cancel": "Annuler",
                "confirm": "Confirmer",
                "success": "Succès",
                "error": "Erreur",
                "warning": "Avertissement",
                "yes": "Oui",
                "no": "Non",
                "all": "Tous",
                "search_placeholder": "Rechercher...",
                
                # Login Screen
                "login_title": "Connexion Administrateur",
                "login_subtitle": "Accéder au portail de gestion administrative",
                "username_placeholder": "Nom d'utilisateur",
                "password_placeholder": "Mot de passe",
                "login_button": "Se Connecter",
                "login_failed_title": "Échec de connexion",
                "login_failed_msg": "Nom d'utilisateur ou mot de passe incorrect. Veuillez réessayer.",

                # Dashboard Screen
                "dash_welcome": "Ravi de vous revoir, Administrateur",
                "dash_subtitle": "Voici le récapitulatif du Lycée Yaghmouracen pour aujourd'hui.",
                "dash_total_students": "Total Élèves",
                "dash_total_employees": "Total Personnel",
                "dash_total_classes": "Total Classes",
                "dash_total_absences": "Total Absences",
                "dash_school_name": "Lycée Yaghmouracen",
                "dash_stats_title": "Aperçu Rapide",
                "dash_time_title": "Date & Heure",
                "dash_active_classes": "Classes Actives",

                # Classes Module
                "sidebar_classes": "Classes",
                "class_title": "Registre des Classes",
                "class_subtitle": "Gérez les divisions de classes, filières et sections du lycée.",
                "class_add_btn": "Ajouter une Classe",
                "class_tab_id": "ID",
                "class_tab_name": "Nom de la Classe",
                "class_tab_actions": "Actions",
                "class_err_name": "Le nom de la classe est requis et doit être unique.",
                "class_add_success": "Classe ajoutée avec succès.",
                "class_update_success": "Classe mise à jour avec succès.",
                "class_delete_confirm": "Êtes-vous sûr de vouloir supprimer la classe: {name}?\nLes élèves de cette classe auront leur champ classe réinitialisé.",
                "class_delete_success": "Classe supprimée avec succès.",

                # Student Module
                "stud_title": "Répertoire des Élèves",
                "stud_subtitle": "Gérez et visualisez les profils scolaires et dossiers d'élèves.",
                "stud_add_btn": "Ajouter un Élève",
                "stud_filter_class": "Classe :",
                "stud_filter_gender": "Genre :",
                "stud_search_hint": "Rechercher par nom, prénom ou parent...",
                "stud_tab_id": "ID",
                "stud_tab_photo": "Photo",
                "stud_tab_name": "Nom Complet",
                "stud_tab_class": "Classe",
                "stud_tab_absences": "Absences",
                "stud_tab_actions": "Actions",
                
                # Student Dialog / Profile
                "stud_profile_title": "Fiche Profil Élève",
                "stud_personal_info": "Informations Personnelles",
                "stud_parental_info": "Informations Parentales & Contact",
                "stud_first_name": "Prénom :",
                "stud_last_name": "Nom :",
                "stud_birth_date": "Date de Naissance :",
                "stud_gender": "Genre :",
                "stud_class": "Classe :",
                "stud_address": "Adresse :",
                "stud_parent": "Nom du Tuteur/Parent :",
                "stud_photo": "Photo de profil :",
                "stud_photo_btn": "Parcourir...",
                "stud_err_name": "Le nom et le prénom de l'élève sont requis.",
                "stud_err_class": "Une classe valide doit être renseignée.",
                "stud_add_success": "Élève ajouté avec succès.",
                "stud_update_success": "Profil élève mis à jour avec succès.",
                "stud_delete_confirm": "Êtes-vous sûr de vouloir supprimer l'élève: {name}?\nTout l'historique d'absences de cet élève sera définitivement détruit.",
                "stud_delete_success": "Dossier élève supprimé avec succès.",

                # Employee Module
                "emp_title": "Registre des Employés",
                "emp_subtitle": "Gérez les enseignants, le personnel administratif et les attestations.",
                "emp_add_btn": "Ajouter un Employé",
                "emp_filter_role": "Rôle :",
                "emp_filter_subject": "Spécialité :",
                "emp_search_hint": "Rechercher par nom ou ID Employé...",
                "emp_tab_id": "ID Employé",
                "emp_tab_name": "Nom Complet",
                "emp_tab_role": "Rôle / Fonction",
                "emp_tab_subject": "Spécialité / Matière",
                "emp_tab_phone": "Téléphone",
                "emp_tab_actions": "Actions",

                # Employee Dialog / Profile
                "emp_profile_title": "Fiche Profil Employé",
                "emp_job_details": "Informations Professionnelles",
                "emp_contact_details": "Informations de Contact",
                "emp_id_field": "ID Employé (Unique) :",
                "emp_first_name": "Prénom :",
                "emp_last_name": "Nom :",
                "emp_role": "Rôle / Poste :",
                "emp_hire_date": "Date d'Embauche :",
                "emp_salary": "Salaire Mensuel (DZD) :",
                "emp_subject": "Matière / Spécialité :",
                "emp_phone": "N° Téléphone :",
                "emp_err_id": "Un identifiant unique (ID) est requis.",
                "emp_err_id_exists": "Cet identifiant unique existe déjà. Veuillez en choisir un autre.",
                "emp_err_names": "Le nom et le prénom de l'employé sont requis.",
                "emp_add_success": "Employé enregistré avec succès.",
                "emp_update_success": "Dossier employé mis à jour avec succès.",
                "emp_delete_confirm": "Êtes-vous sûr de vouloir supprimer l'employé: {name} ?",
                "emp_delete_success": "Fiche employé supprimée avec succès.",

                # Attendance Module
                "att_title": "Registre d'Absence & Présence",
                "att_subtitle": "Effectuez l'appel quotidien par classe et consultez l'historique général.",
                "att_tab_daily": "Appel Quotidien",
                "att_tab_history": "Historique des Absences",
                "att_date_label": "Date :",
                "att_class_label": "Classe :",
                "att_load_roster": "Charger la liste",
                "att_save_roster": "Enregistrer l'Appel",
                "att_tab_name": "Nom de l'Élève",
                "att_tab_status": "Statut de Présence",
                "att_status_present": "Présent",
                "att_status_absent": "Absent",
                "att_save_success": "Appel enregistré et statistiques des absences synchronisées.",
                "att_history_search": "Filtrer l'historique",
                "att_hist_date_from": "Date Début :",
                "att_hist_date_to": "Date Fin :",
                "att_hist_status": "Statut",
                "att_hist_no_records": "Aucun enregistrement d'absence ne correspond à vos filtres.",

                # Exports Module
                "exp_title": "Centre de Documents & Rapports",
                "exp_subtitle": "Exportez les bases de données vers Excel et générez des documents administratifs PDF prêts à imprimer.",
                "exp_sec_pdf": "Génération de Documents PDF Officiels",
                "exp_sec_excel": "Exports des Données en Excel",
                "exp_pdf_general_list": "Liste des Élèves",
                "exp_pdf_general_list_desc": "Génère un tableau complet de tous les élèves inscrits classés par niveau.",
                "exp_pdf_employee_list": "Registre des Employés",
                "exp_pdf_employee_list_desc": "Génère la liste officielle de tous les enseignants et agents du lycée.",
                "exp_pdf_att_report": "Rapport des Absences par Classe",
                "exp_pdf_att_report_desc": "Exportez les absences d'une classe sur une plage de dates définie.",
                "exp_pdf_work_cert": "Attestation de Travail",
                "exp_pdf_work_cert_desc": "Génère une attestation de travail officielle en français pour un membre du personnel sélectionné.",
                "exp_pdf_student_sheet": "Fiche d'Information Élève",
                "exp_pdf_student_sheet_desc": "Rassemble toutes les informations personnelles et le bilan des absences dans un PDF imprimable.",
                "exp_pdf_employee_sheet": "Fiche Signalétique Employé",
                "exp_pdf_employee_sheet_desc": "Imprime le dossier complet et les coordonnées de l'employé dans un format standardisé.",
                
                "exp_excel_students": "Exporter la Table des Élèves (.xlsx)",
                "exp_excel_students_desc": "Exporter l'annuaire complet des élèves avec ajustement automatique des largeurs de colonnes.",
                "exp_excel_employees": "Exporter la Table du Personnel (.xlsx)",
                "exp_excel_employees_desc": "Exporter l'intégralité du registre du personnel du lycée.",
                "exp_excel_attendance": "Exporter l'Historique des Absences (.xlsx)",
                "exp_excel_attendance_desc": "Exporter les lignes d'appels et d'absences historiques enregistrées.",
                
                "exp_btn_generate": "Générer le PDF",
                "exp_btn_export": "Exporter sous Excel",
                "exp_success_pdf": "Fichier PDF généré avec succès :\n{path}",
                "exp_success_excel": "Classeur Excel généré avec succès :\n{path}",
                "exp_select_student": "Sélectionner l'Élève :",
                "exp_select_employee": "Sélectionner l'Employé :",
                "exp_select_class": "Sélectionner la Classe :",
                "exp_folder_open_btn": "Ouvrir le Dossier d'Exports",
            }
        }

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def set_language(self, lang):
        """Set the active language ('en' or 'fr') and trigger listeners."""
        if lang in ["en", "fr"]:
            self.current_language = lang
            
            # Defensively clean up any listeners whose underlying C++ QWidgets have been deleted
            active_listeners = []
            for callback in self.listeners:
                try:
                    if hasattr(callback, '__self__'):
                        widget = callback.__self__
                        # Accessing a widget method will raise RuntimeError if the C++ object has been deleted
                        widget.objectName()
                    active_listeners.append(callback)
                except RuntimeError:
                    # Shiboken deleted C++ object, discard it
                    continue
                except Exception:
                    active_listeners.append(callback)
            
            self.listeners = active_listeners
            
            # Notify registered screens to refresh text labels
            for callback in self.listeners:
                try:
                    callback()
                except Exception as e:
                    print(f"Error in translation listener callback: {e}")

    def register_listener(self, callback):
        """Register a callback function to be called when language changes."""
        if callback not in self.listeners:
            self.listeners.append(callback)

    def unregister_listener(self, callback):
        """Unregister a language change callback."""
        if callback in self.listeners:
            self.listeners.remove(callback)

    def tr(self, key, **kwargs):
        """Retrieve the localized string for a key, formatting with kwargs if provided."""
        lang_dict = self.translations.get(self.current_language, self.translations["fr"])
        text = lang_dict.get(key, key)
        if kwargs:
            try:
                return text.format(**kwargs)
            except KeyError:
                pass
        return text

# Global dynamic translate shortcut helper
def tr(key, **kwargs):
    return TranslationService.get_instance().tr(key, **kwargs)
