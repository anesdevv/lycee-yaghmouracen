from PySide6.QtWidgets import QFrame, QPushButton, QLineEdit, QTableWidget, QVBoxLayout, QLabel, QHBoxLayout, QGraphicsDropShadowEffect, QTableWidgetItem
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QFont, QCursor, QPalette

def apply_light_palette(app):
    """Configures a clean global light palette across the entire Qt Application."""
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#F8FAFC"))      # Clean light-gray background
    palette.setColor(QPalette.WindowText, QColor("#0F172A"))  # Deep dark slate text
    palette.setColor(QPalette.Base, QColor("#FFFFFF"))        # Pure white base for inputs/tables
    palette.setColor(QPalette.AlternateBase, QColor("#F1F5F9"))
    palette.setColor(QPalette.ToolTipBase, QColor("#0F172A"))
    palette.setColor(QPalette.ToolTipText, QColor("#F8FAFC"))
    palette.setColor(QPalette.Text, QColor("#0F172A"))        # Text color
    palette.setColor(QPalette.Button, QColor("#FFFFFF"))      # Light button base
    palette.setColor(QPalette.ButtonText, QColor("#0F172A"))
    palette.setColor(QPalette.BrightText, QColor("#2563EB"))  # Blue accent
    palette.setColor(QPalette.Highlight, QColor("#2563EB"))   # Selection blue
    palette.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
    app.setPalette(palette)

def create_table_item(text, align=Qt.AlignLeft):
    """Helper to instantiate a QTableWidgetItem with guaranteed dark slate text color for Light Mode."""
    display_text = "" if text is None else str(text)
    item = QTableWidgetItem(display_text)
    item.setForeground(QColor("#0F172A"))
    item.setTextAlignment(align | Qt.AlignVCenter)
    return item

GLOBAL_STYLE = """
QMainWindow {
    background-color: #F8FAFC; /* Clean Light Gray Background */
}

/* Base Styles */
QLabel {
    color: #0F172A; /* Deep Dark Slate Text */
    font-family: "Segoe UI", Arial, sans-serif;
}

QLineEdit {
    border: 1.5px solid #CBD5E1; /* Soft Gray Boundary */
    border-radius: 8px;
    padding: 8px 12px;
    background-color: #FFFFFF; /* Pure White background */
    color: #0F172A;
    font-size: 13px;
}

QLineEdit:focus {
    border: 1.5px solid #2563EB; /* Clean Accent Blue Focus */
}

QLineEdit:disabled {
    background-color: #F1F5F9;
    color: #94A3B8;
    border-color: #E2E8F0;
}

QTextEdit {
    border: 1.5px solid #CBD5E1;
    border-radius: 8px;
    padding: 8px 12px;
    background-color: #FFFFFF;
    color: #0F172A;
    font-size: 13px;
}

QTextEdit:focus {
    border: 1.5px solid #2563EB;
}

QComboBox {
    border: 1.5px solid #CBD5E1;
    border-radius: 8px;
    padding: 7px 12px;
    background-color: #FFFFFF;
    color: #0F172A;
    font-size: 13px;
    min-width: 120px;
}

QComboBox:focus {
    border: 1.5px solid #2563EB;
}

/* combobox dropdown list styling in Light Mode */
QComboBox QAbstractItemView {
    background-color: #FFFFFF;
    color: #0F172A;
    border: 1.5px solid #CBD5E1;
    selection-background-color: #F1F5F9;
    selection-color: #2563EB;
    outline: none;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

/* Date Picker styling in Light Mode */
QDateEdit {
    border: 1.5px solid #CBD5E1;
    border-radius: 8px;
    padding: 7px 12px;
    background-color: #FFFFFF;
    color: #0F172A;
    font-size: 13px;
}

QDateEdit:focus {
    border: 1.5px solid #2563EB;
}

/* Table styling in Light Mode */
QTableWidget {
    background-color: #FFFFFF; /* Pure White Background */
    border: 1.5px solid #E2E8F0;
    border-radius: 12px;
    gridline-color: #E2E8F0;
    color: #0F172A;
    font-size: 13px;
    outline: none;
}

QTableWidget::item {
    color: #0F172A;
    padding: 10px;
    border-bottom: 1px solid #F1F5F9;
}

QTableWidget::item:selected {
    background-color: #E2E8F0;
    color: #2563EB;
}

QTableWidget::item:hover {
    background-color: #F1F5F9;
}

QHeaderView::section {
    background-color: #F1F5F9; /* Clean Light Gray header */
    color: #0F172A;
    font-weight: bold;
    font-size: 13px;
    padding: 10px;
    border: none;
    border-right: 1px solid #E2E8F0;
}

QHeaderView::section:last {
    border-right: none;
}

/* ScrollBars in Light Mode */
QScrollBar:vertical {
    border: none;
    background: #F1F5F9;
    width: 10px;
    margin: 0px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background: #CBD5E1;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #94A3B8;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
}

/* Tab Widgets in Light Mode */
QTabWidget::panel {
    border: 1.5px solid #E2E8F0;
    border-radius: 12px;
    background-color: #FFFFFF;
}

QTabBar::tab {
    background-color: #F1F5F9;
    color: #475569;
    font-weight: bold;
    border: 1.5px solid #E2E8F0;
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    padding: 10px 20px;
    font-size: 13px;
    margin-right: 5px;
}

QTabBar::tab:selected {
    background-color: #FFFFFF;
    color: #2563EB;
    border: 1.5px solid #E2E8F0;
    border-bottom: 2px solid #FFFFFF;
    margin-bottom: -1px;
}

QTabBar::tab:hover {
    background-color: #E2E8F0;
    color: #0F172A;
}

/* Dialog Overlay in Light Mode */
QDialog {
    background-color: #F8FAFC;
    border: 1.5px solid #CBD5E1;
    border-radius: 16px;
}
"""

class SleekCard(QFrame):
    """Custom Card container widget with curved corners and soft light styling."""
    def __init__(self, parent=None, hoverable=True):
        super().__init__(parent)
        self.hoverable = hoverable
        self.setObjectName("Card")
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        
        # Sleek Light Mode Card styling
        self.setStyleSheet("""
            QFrame#Card {
                background-color: #FFFFFF; /* Pure White Background */
                border-radius: 16px;
                border: 1.5px solid #E2E8F0; /* Soft gray border */
            }
            QFrame#Card:hover {
                border-color: #CBD5E1;
            }
        """)
        
        # Soft light shadow for subtle depth
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(15)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(3)
        self.shadow.setColor(QColor(15, 23, 42, 12))
        self.setGraphicsEffect(self.shadow)


class PremiumButton(QPushButton):
    """Custom styled QPushButton supporting primary (Electric Blue) and secondary (White/Border) flat styles."""
    def __init__(self, text="", is_primary=True, parent=None):
        super().__init__(text, parent)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        
        if is_primary:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #2563EB; /* Clean Blue */
                    color: #FFFFFF;
                    border: none;
                    border-radius: 8px;
                    padding: 9px 18px;
                    font-size: 13px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1D4ED8; /* Darker blue hover */
                }
                QPushButton:pressed {
                    background-color: #1E40AF;
                }
                QPushButton:disabled {
                    background-color: #E2E8F0;
                    color: #94A3B8;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #FFFFFF;
                    color: #0F172A;
                    border: 1.5px solid #CBD5E1;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-size: 13px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #F1F5F9;
                    border-color: #94A3B8;
                }
                QPushButton:pressed {
                    background-color: #E2E8F0;
                }
                QPushButton:disabled {
                    background-color: #F8FAFC;
                    border-color: #E2E8F0;
                    color: #CBD5E1;
                }
            """)


class SearchBox(QLineEdit):
    """Custom QLineEdit tailored for data searches in Light Mode."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setClearButtonEnabled(True)
        self.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                border: 1.5px solid #CBD5E1;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
                color: #0F172A;
            }
            QLineEdit:focus {
                border-color: #2563EB;
            }
        """)


class ModernTable(QTableWidget):
    """QTableWidget subclass with light styling, no-edit mode, and double-click behaviors."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.setAlternatingRowColors(True)
        self.setFocusPolicy(Qt.NoFocus)
        self.setShowGrid(False)
        
        self.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setDefaultSectionSize(56)
        
        self.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                alternate-background-color: #F8FAFC;
                border: 1.5px solid #E2E8F0;
                border-radius: 12px;
            }
        """)
