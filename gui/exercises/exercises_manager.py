<<<<<<< HEAD
"""
ExercisesManager - Main coordinator for exercises UI with list + detail panes.

Usage:
    from gui.exercises.exercises_manager import ExercisesManager
    manager = ExercisesManager(voice_trainer)
    # Use as main widget for exercises screen
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, # type: ignore
                           QLabel, QListWidget, QListWidgetItem, QStackedWidget,
                           QFrame, QScrollArea, QSizePolicy, QSplitter) 
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSize # type: ignore
from PyQt6.QtGui import QFont, QFontMetrics # type: ignore
from ..design_system import AriaDesignSystem
from .exercise_spec import (ExerciseSpec, create_breathing_spec, create_humming_spec,
                           create_pitch_slides_spec, create_lip_trills_spec,
                           create_resonance_shift_spec, create_straw_phonation_spec)
from .exercise_runner import ExerciseRunner


class ExercisesManager(QWidget):
    """Main exercises coordinator with list pane + detail pane layout"""

    back_requested = pyqtSignal()

    def __init__(self, voice_trainer):
        super().__init__()
        self.voice_trainer = voice_trainer
        self.exercises_registry = {}
        self.current_runner = None
        self.init_ui()
        self.load_exercises()

    def init_ui(self):
        """Initialize flat two-column layout - no nested frames"""
        # Main layout with clean spacing
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(16)

        # Header - smaller, cleaner
        self.create_header(main_layout)

        # Content area - flat design
        self.create_content_area(main_layout)

        # Apply minimal styling
        self.setStyleSheet(f"""
            ExercisesManager {{
                background-color: {AriaDesignSystem.COLORS['bg_primary']};
                color: {AriaDesignSystem.COLORS['text_primary']};
                font-family: {AriaDesignSystem.FONTS['family_primary']};
            }}
        """)

    def create_header(self, layout):
        """Create minimal header with back button and centered title on same line"""
        # Single horizontal layout with back button and title
        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)

        self.back_btn = QPushButton("← Back")
        self.back_btn.clicked.connect(self.back_requested.emit)
        self.back_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {AriaDesignSystem.COLORS['text_secondary']};
                font-size: {AriaDesignSystem.FONTS['sm']}pt;
                padding: 4px 8px;
            }}
            QPushButton:hover {{
                color: {AriaDesignSystem.COLORS['text_primary']};
            }}
        """)
        header_layout.addWidget(self.back_btn)

        # Title - centered in remaining space
        title_label = QLabel("Voice Exercises")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont(AriaDesignSystem.FONTS['family_primary'], 18, QFont.Weight.Bold))
        title_label.setStyleSheet(f"""
            color: {AriaDesignSystem.COLORS['primary']};
        """)
        header_layout.addWidget(title_label, 1)  # Give it stretch factor

        # Right spacer to balance the back button (invisible)
        spacer = QLabel()
        spacer.setMinimumWidth(self.back_btn.sizeHint().width())
        header_layout.addWidget(spacer)

        layout.addLayout(header_layout)

    def create_content_area(self, layout):
        """Create flat content area - no frame wrapper"""
        # Direct splitter layout - no frame wrapper
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: transparent;
                width: 2px;
            }
            QSplitter::handle:hover {
                background-color: rgba(99, 102, 241, 0.2);
            }
        """)

        # Left: Exercise list (minimal styling)
        self.list_widget = self.create_list_pane()
        self.splitter.addWidget(self.list_widget)

        # Right: Detail/Runner
        self.detail_widget = self.create_detail_pane()
        self.splitter.addWidget(self.detail_widget)

        # Set proportional sizes
        self.splitter.setSizes([1, 2])  # 1:2 ratio
        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)

        layout.addWidget(self.splitter)

    def create_list_pane(self):
        """Create minimal exercise list"""
        list_container = QWidget()
        list_container.setMinimumWidth(200)
        list_layout = QVBoxLayout(list_container)
        list_layout.setSpacing(8)
        list_layout.setContentsMargins(8, 8, 8, 8)

        # Simple list title
        list_title = QLabel("Exercises")
        list_title.setStyleSheet(f"""
            color: {AriaDesignSystem.COLORS['text_primary']};
            font-size: {AriaDesignSystem.FONTS['sm']}pt;
            font-weight: 600;
            margin-bottom: 4px;
        """)
        list_layout.addWidget(list_title)

        # Minimal list styling
        self.exercise_list = QListWidget()
        self.exercise_list.setMinimumHeight(200)
        self.exercise_list.setWordWrap(True)
        self.exercise_list.setUniformItemSizes(False)
        self.exercise_list.setStyleSheet(f"""
            QListWidget {{
                background-color: transparent;
                border: none;
                padding: 4px;
            }}
            QListWidget::item {{
                padding: 8px;
                border-radius: 4px;
                margin: 1px 0px;
                min-height: 40px;
                font-size: {AriaDesignSystem.FONTS['sm']}pt;
                color: {AriaDesignSystem.COLORS['text_primary']};
            }}
            QListWidget::item:hover {{
                background-color: {AriaDesignSystem.COLORS['bg_accent']};
            }}
            QListWidget::item:selected {{
                background-color: {AriaDesignSystem.COLORS['primary']};
                color: white;
            }}
        """)
        self.exercise_list.itemClicked.connect(self.on_exercise_selected)
        list_layout.addWidget(self.exercise_list)

        return list_container


    def create_detail_pane(self):
        """Create detail/runner pane using QStackedWidget"""
        # Stack for detail view vs runner view
        self.content_stack = QStackedWidget()
        self.content_stack.setMinimumWidth(300)  # Ensure readable detail view

        # Default detail view
        self.detail_widget_default = self.create_detail_widget()
        self.content_stack.addWidget(self.detail_widget_default)

        return self.content_stack

    def create_detail_widget(self):
        """Create default detail view"""
        detail_widget = QWidget()
        detail_layout = QVBoxLayout(detail_widget)
        detail_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        welcome_label = QLabel("Select an exercise to see details")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet(f"""
            color: {AriaDesignSystem.COLORS['text_muted']};
            font-size: {AriaDesignSystem.FONTS['md']}pt;
            padding: 20px;
        """)
        detail_layout.addWidget(welcome_label)

        return detail_widget

    def resizeEvent(self, event):
        """Handle window resize with dynamic sizing based on content and available space"""
        super().resizeEvent(event)

        # Dynamic sizing based on content and available space
        if hasattr(self, 'splitter') and event.size().width() > 0:
            total_width = event.size().width() - 80  # Account for padding and margins

            if total_width < 600:
                # Very narrow: minimal list, max detail
                list_width = 220
                detail_width = max(300, total_width - list_width)
            elif total_width < 900:
                # Medium: 35% list, 65% detail
                list_width = max(250, min(320, total_width * 0.35))
                detail_width = total_width - list_width
            else:
                # Wide: 30% list up to 400px, rest for detail
                list_width = max(280, min(400, total_width * 0.3))
                detail_width = total_width - list_width

            self.splitter.setSizes([int(list_width), int(detail_width)])

    def load_exercises(self):
        """Load all exercises using ExerciseSpec"""
        self.exercises_registry = {
            'breathing': create_breathing_spec(),
            'humming': create_humming_spec(),
            'pitch_slides': create_pitch_slides_spec(),
            'lip_trills': create_lip_trills_spec(),
            'resonance_shift': create_resonance_shift_spec(),
            'straw_phonation': create_straw_phonation_spec(),
        }
        self.populate_exercise_list()

    def populate_exercise_list(self):
        """Populate the exercise list widget with simple items that show selection properly"""
        self.exercise_list.clear()
        for exercise_id, exercise_spec in self.exercises_registry.items():
            # Create simple text item with formatting
            display_text = f"{exercise_spec.name}\n{exercise_spec.format_duration()} • {exercise_spec.difficulty}"
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, exercise_id)

            # Set size hint for proper text wrapping
            font_metrics = QFontMetrics(QFont())
            text_width = 200  # Reasonable default width
            text_height = font_metrics.boundingRect(0, 0, text_width, 0,
                                                   Qt.TextFlag.TextWordWrap, display_text).height()
            item.setSizeHint(QSize(text_width, max(50, text_height + 20)))

            self.exercise_list.addItem(item)

    def on_exercise_selected(self, item):
        """Handle exercise selection"""
        exercise_id = item.data(Qt.ItemDataRole.UserRole)
        exercise_spec = self.exercises_registry.get(exercise_id)
        if exercise_spec:
            self.show_exercise_detail(exercise_id, exercise_spec)

    def show_exercise_detail(self, exercise_id, exercise_spec):
        """Show exercise detail view"""
        # Create detailed exercise view
        detail_widget = self.create_exercise_detail_widget(exercise_spec)

        # Replace current detail widget in stack
        if self.content_stack.count() > 1:
            self.content_stack.removeWidget(self.content_stack.widget(1))
        self.content_stack.addWidget(detail_widget)
        self.content_stack.setCurrentIndex(1)

    def create_exercise_detail_widget(self, exercise_spec):
        """Create clean detail widget with start button"""
        detail_widget = QWidget()
        layout = QVBoxLayout(detail_widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Exercise header - simple layout
        header_layout = QVBoxLayout()
        header_layout.setSpacing(8)

        # Title
        title_label = QLabel(exercise_spec.name)
        title_label.setWordWrap(True)
        title_label.setStyleSheet(f"""
            color: {AriaDesignSystem.COLORS['text_primary']};
            font-size: {AriaDesignSystem.FONTS['lg']}pt;
            font-weight: 600;
        """)
        header_layout.addWidget(title_label)

        # Metadata
        meta_text = f"{exercise_spec.format_duration()} • {exercise_spec.difficulty}"
        if exercise_spec.requires_breathing:
            meta_text += " • Breathing Focus"

        meta_label = QLabel(meta_text)
        meta_label.setStyleSheet(f"""
            color: {AriaDesignSystem.COLORS['text_muted']};
            font-size: {AriaDesignSystem.FONTS['sm']}pt;
        """)
        header_layout.addWidget(meta_label)
        layout.addLayout(header_layout)

        # Description
        desc_label = QLabel(exercise_spec.description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(f"""
            color: {AriaDesignSystem.COLORS['text_secondary']};
            font-size: {AriaDesignSystem.FONTS['md']}pt;
            margin: 8px 0px;
        """)
        layout.addWidget(desc_label)

        # Instructions
        inst_text = QLabel(exercise_spec.instructions)
        inst_text.setWordWrap(True)
        inst_text.setStyleSheet(f"""
            color: {AriaDesignSystem.COLORS['text_secondary']};
            font-size: {AriaDesignSystem.FONTS['sm']}pt;
            line-height: 1.4;
            padding: 12px;
            background-color: {AriaDesignSystem.COLORS['bg_tertiary']};
            border-radius: 6px;
        """)
        layout.addWidget(inst_text)

        # Metrics info
        metrics = exercise_spec.get_metrics_required()
        if metrics:
            metrics_label = QLabel(f"Tracks: {', '.join(metrics).title()}")
            metrics_label.setStyleSheet(f"""
                color: {AriaDesignSystem.COLORS['text_muted']};
                font-size: {AriaDesignSystem.FONTS['xs']}pt;
            """)
            layout.addWidget(metrics_label)

        layout.addStretch()

        # Start button
        start_btn = QPushButton("Start Exercise →")
        start_btn.clicked.connect(lambda: self.start_exercise_runner(exercise_spec))
        start_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {AriaDesignSystem.COLORS['primary']};
                border: none;
                border-radius: 6px;
                padding: 10px 24px;
                color: white;
                font-size: {AriaDesignSystem.FONTS['sm']}pt;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {AriaDesignSystem.COLORS['primary_hover']};
            }}
        """)
        layout.addWidget(start_btn)

        return detail_widget

    def start_exercise_runner(self, exercise_spec):
        """Start exercise runner - seamless transition in same space"""
        # Create runner widget
        runner_widget = ExerciseRunner(exercise_spec, self.voice_trainer)
        runner_widget.exercise_stopped.connect(self.return_to_detail)

        # Add to stack and switch
        self.content_stack.addWidget(runner_widget)
        self.content_stack.setCurrentWidget(runner_widget)

        # Store current runner
        self.current_runner = runner_widget

        # Start the exercise
        runner_widget.start_exercise()

    def return_to_detail(self):
        """Return to detail view after exercise stops"""
        if self.current_runner:
            # Remove runner from stack
            self.content_stack.removeWidget(self.current_runner)
            self.current_runner.cleanup()
            self.current_runner = None

        # Return to detail view (index 1) or default (index 0)
        if self.content_stack.count() > 1:
            self.content_stack.setCurrentIndex(1)
        else:
            self.content_stack.setCurrentIndex(0)

    def cleanup(self):
        """Clean up resources"""
        if self.current_runner:
            self.current_runner.cleanup()
            self.current_runner = None