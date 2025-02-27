# -*- coding: utf-8 -*-
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QTabWidget, 
                            QVBoxLayout, QLabel, QPushButton, QHBoxLayout)

class StylishTabWidget(QTabWidget):
    """Customized QTabWidget with enhanced visual design
    
    Features:
    - Gradient background
    - Rounded corners
    - Animated tab switching
    - Custom close button
    """
    def __init__(self):
        super().__init__()
        # self.setTabsClosable(True) 
        # self.setMovable(True) 
        # self.setDocumentMode(True) 
        # self._init_style()
        self._init_plus_button()

    def _init_style(self):
        """Initialize custom styling for the tab widget"""
        self.setStyleSheet(""" 
            QTabWidget::pane {
                border: 2px solid #1e88e5;
                border-radius: 6px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
            }
            QTabBar::tab {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e3f2fd, stop:1 #bbdefb);
                border: 1px solid #90caf9;
                border-radius: 4px;
                padding: 8px;
                margin: 2px;
                min-width: 100px;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e88e5, stop:1 #1976d2);
                color: white;
            }
        """)

    def _init_plus_button(self):
        """Initialize '+' button for adding new tabs"""
        self.plus_btn  = QPushButton("+")
        self.plus_btn.setFixedSize(32,  32)
        # self.plus_btn.setStyleSheet(""" 
        #     QPushButton {
        #         background: #4CAF50;
        #         border-radius: 16px;
        #         color: white;
        #         font-weight: bold;
        #     }
        #     QPushButton:hover {
        #         background: #66BB6A;
        #     }
        # """)
        self.setCornerWidget(self.plus_btn,  Qt.TopRightCorner)

class DynamicTabContent(QWidget):
    """Reusable tab content template with close functionality"""
    def __init__(self, title):
        super().__init__()
        self.title  = title
        self._init_ui()
        self._init_style()

    def _init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        header = QHBoxLayout()
        
        self.close_btn  = QPushButton("×")
        self.close_btn.setFixedSize(24,  24)
        
        header.addWidget(QLabel(self.title)) 
        header.addStretch() 
        header.addWidget(self.close_btn) 
        
        layout.addLayout(header) 
        layout.addWidget(QLabel("Custom  content area"))
        self.setLayout(layout) 

    def _init_style(self):
        """Apply custom styling"""
        self.close_btn.setStyleSheet(""" 
            QPushButton {
                background: #ef5350;
                border-radius: 12px;
                color: white;
            }
            QPushButton:hover {
                background: #e53935;
            }
        """)

class MainWindow(QMainWindow):
    """Main application window with central tab widget"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced  Tab Manager")
        self.setGeometry(100,  100, 800, 600)
        self._init_central_widget()
        self._connect_signals()

    def _init_central_widget(self):
        """Initialize central widget with tab control"""
        self.central_widget  = QWidget()
        self.setCentralWidget(self.central_widget) 
        
        self.main_layout  = QVBoxLayout()
        self.tab_widget  = StylishTabWidget()
        
        self.main_layout.addWidget(self.tab_widget) 
        self.central_widget.setLayout(self.main_layout) 

        # Add initial tab
        self._create_tab("Welcome")

    def _create_tab(self, title="New Tab"):
        """Create new tab with dynamic content"""
        new_tab = DynamicTabContent(title)
        index = self.tab_widget.addTab(new_tab,  title)
        self.tab_widget.setCurrentIndex(index) 
        return new_tab

    def _connect_signals(self):
        """Connect UI signals to slots"""
        self.tab_widget.plus_btn.clicked.connect( 
            lambda: self._create_tab(f"Tab {self.tab_widget.count()+1}")) 
        
        self.tab_widget.tabCloseRequested.connect( 
            lambda index: self.tab_widget.removeTab(index)) 

if __name__ == "__main__":
    app = QApplication(sys.argv) 
    window = MainWindow()
    window.show() 
    sys.exit(app.exec_()) 
