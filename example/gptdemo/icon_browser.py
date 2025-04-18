import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QListWidget,
                             QHBoxLayout, QVBoxLayout, QLabel, QListWidgetItem,
                             QStatusBar, QStyle)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize

class IconBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Qt Standard Icons Browser")
        self.setGeometry(100, 100, 800, 600)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Icon list
        self.icon_list = QListWidget()
        self.icon_list.setIconSize(QSize(32, 32))
        self.icon_list.itemDoubleClicked.connect(self.copy_enum_name)
        layout.addWidget(self.icon_list, 1)
        
        # Details panel
        details_layout = QVBoxLayout()
        self.icon_preview = QLabel()
        self.icon_preview.setAlignment(Qt.AlignCenter)
        self.name_label = QLabel("Select an icon to view details")
        self.value_label = QLabel()
        
        details_layout.addWidget(self.icon_preview)
        details_layout.addWidget(QLabel("Enum Name:"))
        details_layout.addWidget(self.name_label)
        details_layout.addWidget(QLabel("Constant Value:"))
        details_layout.addWidget(self.value_label)
        layout.addLayout(details_layout, 2)
        
        # Status bar
        self.statusBar().showMessage("Double-click items to copy enum names")
        
        # Load icons
        self.load_icons()
        
    def load_icons(self):
        """Populate the list with all available standard icons"""
        # Get all StandardPixmap attributes
        sp_attributes = [attr for attr in dir(QStyle) 
                        if attr.startswith('SP_') and not callable(getattr(QStyle, attr))]
        
        for attr in sorted(sp_attributes):
            try:
                enum_value = getattr(QStyle, attr)
                icon = self.style().standardIcon(enum_value)
                
                if not icon.isNull():
                    item = QListWidgetItem(icon, attr.replace('_', ' ').title())
                    item.setData(Qt.UserRole, (attr, enum_value))
                    self.icon_list.addItem(item)
            except AttributeError:
                continue

    def copy_enum_name(self, item):
        """Copy enum name to clipboard"""
        enum_name = item.data(Qt.UserRole)[0]
        QApplication.clipboard().setText(enum_name)
        self.statusBar().showMessage(f"Copied: {enum_name}", 2000)

    def showEvent(self, event):
        """Handle first display"""
        if self.icon_list.currentRow() == -1:
            self.icon_list.setCurrentRow(0)
            self.on_selection_change()
            
    def on_selection_change(self):
        """Update details when selection changes"""
        current_item = self.icon_list.currentItem()
        if current_item:
            enum_name, enum_value = current_item.data(Qt.UserRole)
            icon = self.style().standardIcon(enum_value)
            
            self.icon_preview.setPixmap(icon.pixmap(64, 64))
            self.name_label.setText(f"QStyle.{enum_name}")
            self.value_label.setText(str(enum_value))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    browser = IconBrowser()
    browser.icon_list.currentItemChanged.connect(browser.on_selection_change)
    browser.show()
    sys.exit(app.exec_())
    