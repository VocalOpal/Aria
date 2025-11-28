"""
Profile Switcher Component - Switch between voice training profiles
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QDialog, QLineEdit, QDialogButtonBox, QMessageBox, QButtonGroup, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class ProfileDropdown(QWidget):
    """Profile dropdown widget for sidebar"""
    
    profile_changed = pyqtSignal(str)  # Emits profile_id
    
    def __init__(self, profile_manager, parent=None):
        super().__init__(parent)
        self.profile_manager = profile_manager
        self.init_ui()
    
    def init_ui(self):
        """Initialize modern UI"""
        self.setMinimumHeight(95)  # Increased to prevent cutoff
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Get current profile
        current = self.profile_manager.get_current()
        if not current:
            return
        
        # Modern card style with subtle gradient
        self.setStyleSheet("""
            ProfileDropdown {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(111, 162, 200, 0.25),
                    stop:1 rgba(232, 151, 189, 0.25)
                );
                border-radius: 14px;
                border: none;
            }
            ProfileDropdown:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(111, 162, 200, 0.35),
                    stop:1 rgba(232, 151, 189, 0.35)
                );
            }
        """)
        
        # Create main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)  # Adjusted margins
        layout.setSpacing(6)
        
        # Build content using shared method
        self._build_content(layout, current)
    
    def mousePressEvent(self, event):
        """Handle click to show profile menu"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.show_profile_menu()
    
    def show_profile_menu(self):
        """Show profile selection dialog"""
        dialog = ProfileSelectorDialog(self.profile_manager, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_id = dialog.selected_profile_id
            if selected_id:
                self.profile_changed.emit(selected_id)
                self.refresh()
    
    def refresh(self):
        """Refresh the dropdown display - rebuild from scratch"""
        # Get current profile for display
        current = self.profile_manager.get_current()
        if not current:
            return
        
        # Get the main layout
        layout = self.layout()
        if not layout:
            # First time - create new widget
            self.init_ui()
            return
        
        # Clear everything including nested layouts
        self._clear_layout_recursive(layout)
        
        # Rebuild the content (not the main layout itself)
        self._build_content(layout, current)
    
    def _clear_layout_recursive(self, layout):
        """Recursively clear all items from a layout"""
        if not layout:
            return
        
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout_recursive(item.layout())
                # Don't delete the layout itself, just clear it
    
    def _build_content(self, main_layout, current):
        """Build the dropdown content with current profile data"""
        # Header row with label
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)
        
        header_label = QLabel("VOICE PROFILE")
        header_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.5);
            font-size: 10px;
            font-weight: 600;
            letter-spacing: 1px;
            background: transparent;
        """)
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        
        # Arrow indicator
        arrow = QLabel("›")
        arrow.setStyleSheet("""
            color: rgba(255, 255, 255, 0.5);
            font-size: 18px;
            font-weight: bold;
            background: transparent;
        """)
        header_layout.addWidget(arrow)
        
        main_layout.addLayout(header_layout)
        
        # Profile info row
        info_layout = QHBoxLayout()
        info_layout.setSpacing(10)
        
        # Icon in a subtle circle
        icon_label = QLabel(current.icon)
        icon_label.setFixedSize(32, 32)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("""
            background: rgba(255, 255, 255, 0.15);
            border-radius: 16px;
            font-size: 18px;
        """)
        info_layout.addWidget(icon_label)
        
        # Profile details
        details_layout = QVBoxLayout()
        details_layout.setSpacing(4)  # Increased spacing to prevent overlap
        
        name_label = QLabel(current.name)
        name_label.setStyleSheet("""
            color: white;
            font-size: 14px;
            font-weight: 600;
            background: transparent;
        """)
        name_label.setWordWrap(False)
        name_label.setMaximumWidth(200)  # Prevent text from extending too far
        details_layout.addWidget(name_label)
        
        goal_text = f"{current.goal_range[0]}-{current.goal_range[1]} Hz"
        goal_label = QLabel(goal_text)
        goal_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.7);
            font-size: 12px;
            font-weight: 500;
            background: transparent;
        """)
        goal_label.setWordWrap(False)
        details_layout.addWidget(goal_label)
        
        info_layout.addLayout(details_layout)
        info_layout.addStretch()
        
        main_layout.addLayout(info_layout)


class ProfileSelectorDialog(QDialog):
    """Dialog to select or create profiles"""
    
    def __init__(self, profile_manager, parent=None):
        super().__init__(parent)
        self.profile_manager = profile_manager
        self.selected_profile_id = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("Switch Profile")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        # Main background - match pattern from other dialogs
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #5A7A95,
                    stop:1 #C88AA8
                );
            }
            QLabel {
                background: transparent;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("Select Profile")
        header.setStyleSheet("""
            color: white;
            font-size: 24px;
            font-weight: 600;
            background: transparent;
        """)
        layout.addWidget(header)
        
        # Profile list
        current = self.profile_manager.get_current()
        for profile in self.profile_manager.get_all():
            is_current = profile.id == current.id if current else False
            profile_btn = self._create_profile_button(profile, is_current)
            layout.addWidget(profile_btn)
        
        # Add spacing
        layout.addSpacing(10)
        
        # Create new profile button
        create_btn = QPushButton("+ Create New Profile")
        create_btn.setStyleSheet("""
            QPushButton {
                background: rgba(68, 197, 230, 0.3);
                border: 2px dashed rgba(68, 197, 230, 0.6);
                border-radius: 12px;
                color: white;
                font-size: 14px;
                font-weight: 600;
                padding: 16px;
                text-align: left;
            }
            QPushButton:hover {
                background: rgba(68, 197, 230, 0.4);
                border: 2px dashed rgba(68, 197, 230, 0.8);
            }
        """)
        create_btn.clicked.connect(self.create_new_profile)
        layout.addWidget(create_btn)
        
        layout.addStretch()
    
    def _create_profile_button(self, profile, is_current):
        """Create a profile selection button"""
        btn = QPushButton()
        btn.setFixedHeight(70)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Different style for current profile
        if is_current:
            bg_color = "rgba(68, 197, 230, 0.3)"
            border_color = "rgba(68, 197, 230, 0.6)"
            hover_bg = "rgba(68, 197, 230, 0.35)"
        else:
            bg_color = "rgba(255, 255, 255, 0.1)"
            border_color = "rgba(255, 255, 255, 0.2)"
            hover_bg = "rgba(255, 255, 255, 0.15)"
        
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {bg_color};
                border: 1px solid {border_color};
                border-radius: 12px;
                color: white;
                font-size: 14px;
                font-weight: 600;
                padding: 12px;
                text-align: left;
            }}
            QPushButton:hover {{
                background: {hover_bg};
            }}
        """)
        
        # Button content
        goal_text = f"{profile.goal_range[0]}-{profile.goal_range[1]} Hz"
        current_text = " (Current)" if is_current else ""
        btn_text = f"{profile.icon} {profile.name}{current_text}\n{goal_text} • {profile.preset.upper()}"
        btn.setText(btn_text)
        
        btn.clicked.connect(lambda: self.select_profile(profile.id))
        return btn
    
    def select_profile(self, profile_id):
        """Select a profile"""
        self.selected_profile_id = profile_id
        self.accept()
    
    def create_new_profile(self):
        """Show create profile dialog"""
        dialog = CreateProfileDialog(self.profile_manager, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Refresh and select new profile
            self.selected_profile_id = dialog.created_profile_id
            self.accept()


class CreateProfileDialog(QDialog):
    """Dialog to create a new profile"""
    
    def __init__(self, profile_manager, parent=None):
        super().__init__(parent)
        self.profile_manager = profile_manager
        self.created_profile_id = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("Create New Profile")
        self.setModal(True)
        self.setMinimumWidth(450)
        
        # Main background
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #5A7A95,
                    stop:1 #C88AA8
                );
            }
            QLabel {
                color: white;
                background: transparent;
            }
            QLineEdit, QComboBox {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(111, 162, 200, 0.18),
                    stop:1 rgba(232, 151, 189, 0.18)
                );
                border: 1px solid rgba(255, 255, 255, 0.35);
                border-radius: 8px;
                color: white;
                font-size: 14px;
                padding: 10px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid rgba(68, 197, 230, 0.9);
                background: rgba(255, 255, 255, 0.22);
            }
            QComboBox QAbstractItemView {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(111, 162, 200, 0.9),
                    stop:1 rgba(232, 151, 189, 0.9)
                );
                border: 1px solid rgba(255, 255, 255, 0.25);
                border-radius: 10px;
                color: white;
                selection-background-color: rgba(68, 197, 230, 0.35);
                selection-color: white;
                padding: 6px;
            }
            QComboBox QAbstractItemView::item {
                padding: 8px 12px;
                margin: 2px 0;
            }
            QPushButton#iconChip {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.25);
                border-radius: 12px;
                color: white;
                font-size: 20px;
                font-weight: 600;
            }
            QPushButton#iconChip:hover {
                background: rgba(255, 255, 255, 0.18);
            }
            QPushButton#iconChip:checked {
                background: rgba(68, 197, 230, 0.35);
                border: 1px solid rgba(68, 197, 230, 0.8);
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("Create New Profile")
        header.setStyleSheet("""
            color: white;
            font-size: 24px;
            font-weight: 600;
            background: transparent;
        """)
        layout.addWidget(header)
        
        # Profile name
        name_label = QLabel("Profile Name")
        name_label.setStyleSheet("font-size: 13px; font-weight: 500;")
        layout.addWidget(name_label)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Work Voice, Casual Voice")
        layout.addWidget(self.name_input)
        
        # Icon selection
        icon_label = QLabel("Profile Icon")
        icon_label.setStyleSheet("font-size: 13px; font-weight: 500;")
        layout.addWidget(icon_label)
        
        self.icons = ["\U0001f3a4", "\U0001f3a7", "\U0001f3b5", "\U0001f5e3", "\U0001f3b6", "\u2b50", "\U0001f31f", "\U0001f525", "\U0001f300", "\u2728"]
        self.icon_group = QButtonGroup(self)
        self.icon_group.setExclusive(True)
        
        icon_grid = QGridLayout()
        icon_grid.setSpacing(10)
        
        for idx, icon in enumerate(self.icons):
            btn = QPushButton(icon)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedSize(54, 54)
            btn.setObjectName("iconChip")
            self.icon_group.addButton(btn, idx)
            icon_grid.addWidget(btn, idx // 5, idx % 5)
            if idx == 0:
                btn.setChecked(True)
        
        layout.addLayout(icon_grid)
        
        # Preset selection
        preset_label = QLabel("Voice Preset")
        preset_label.setStyleSheet("font-size: 13px; font-weight: 500;")
        layout.addWidget(preset_label)
        
        self.preset_combo = QComboBox()
        presets = [
            ("mtf", "MTF Voice Training"),
            ("ftm", "FTM Voice Training"),
            ("nonbinary_higher", "Non-Binary (Higher)"),
            ("nonbinary_lower", "Non-Binary (Lower)"),
            ("nonbinary_neutral", "Non-Binary (Neutral)")
        ]
        for preset_id, preset_name in presets:
            self.preset_combo.addItem(preset_name, preset_id)
        layout.addWidget(self.preset_combo)
        
        # Goal range
        goal_label = QLabel("Goal Range (Hz)")
        goal_label.setStyleSheet("font-size: 13px; font-weight: 500;")
        layout.addWidget(goal_label)
        
        goal_layout = QHBoxLayout()
        self.min_goal = QComboBox()
        self.max_goal = QComboBox()
        
        # Populate goal ranges
        ranges = [
            (100, 130), (130, 150), (150, 180), (165, 200), (170, 200),
            (180, 220), (200, 240)
        ]
        for min_hz, max_hz in ranges:
            self.min_goal.addItem(f"{min_hz}-{max_hz} Hz", (min_hz, max_hz))
        
        self.min_goal.setCurrentIndex(2)  # Default to 150-180
        
        goal_layout.addWidget(self.min_goal)
        layout.addLayout(goal_layout)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.create_profile)
        button_box.rejected.connect(self.reject)
        
        button_box.setStyleSheet("""
            QPushButton {
                background: rgba(68, 197, 230, 0.3);
                border: 1px solid rgba(68, 197, 230, 0.5);
                border-radius: 8px;
                color: white;
                font-size: 14px;
                font-weight: 600;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background: rgba(68, 197, 230, 0.4);
            }
        """)
        
        layout.addWidget(button_box)
    
    def create_profile(self):
        """Create the profile"""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Invalid Name", "Please enter a profile name.")
            return
        
        selected_btn = self.icon_group.checkedButton()
        icon = selected_btn.text() if selected_btn else self.icons[0]
        preset_id = self.preset_combo.currentData()
        goal_range = self.min_goal.currentData()
        
        # Create profile with icon in name
        profile_name = f"{icon} {name}"
        profile = self.profile_manager.create_profile(
            name=profile_name,
            icon=icon,
            goal_range=goal_range,
            preset=preset_id
        )
        
        if profile:
            self.created_profile_id = profile.id
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to create profile.")
