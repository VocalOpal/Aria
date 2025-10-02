"""Modern onboarding screen with multi-step setup wizard."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QStackedWidget, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont

from ..design_system import (
    AriaColors, AriaTypography, AriaSpacing, AriaRadius,
    InfoCard, PrimaryButton, SecondaryButton, create_gradient_background,
    StyledComboBox, BodyLabel, CaptionLabel, create_styled_progress_bar, add_card_shadow
)


class ModernStepIndicator(QWidget):
    """Modern step indicator with animated progress"""
    
    def __init__(self, total_steps=4):
        super().__init__()
        self.total_steps = total_steps
        self.current = 0
        self.init_ui()
    
    def init_ui(self):
        """Initialize step indicator"""
        layout = QHBoxLayout(self)
        layout.setSpacing(AriaSpacing.SM)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.dots = []
        for i in range(self.total_steps):
            dot = QFrame()
            dot.setFixedSize(12, 12)
            dot.setStyleSheet(f"""
                QFrame {{
                    background: {AriaColors.WHITE_25};
                    border-radius: 6px;
                }}
            """)
            layout.addWidget(dot)
            self.dots.append(dot)
        
        self.set_step(0)
    
    def set_step(self, step):
        """Update step indicator"""
        self.current = step
        for i, dot in enumerate(self.dots):
            if i <= step:
                # Active/completed
                dot.setStyleSheet(f"""
                    QFrame {{
                        background: {AriaColors.TEAL};
                        border-radius: 6px;
                    }}
                """)
                if i == step:
                    dot.setFixedSize(16, 16)
                else:
                    dot.setFixedSize(12, 12)
            else:
                # Inactive
                dot.setFixedSize(12, 12)
                dot.setStyleSheet(f"""
                    QFrame {{
                        background: {AriaColors.WHITE_25};
                        border-radius: 6px;
                    }}
                """)


class PresetCard(QFrame):
    """Clickable preset selection card"""
    
    clicked = pyqtSignal(dict)
    
    def __init__(self, title, icon, description, preset_data):
        super().__init__()
        self.title = title
        self.icon = icon
        self.description = description
        self.preset_data = preset_data
        self.is_selected = False
        self.init_ui()
    
    def init_ui(self):
        """Initialize preset card"""
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(140)
        self.update_style()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(AriaSpacing.LG, AriaSpacing.LG, AriaSpacing.LG, AriaSpacing.LG)
        layout.setSpacing(AriaSpacing.SM)
        
        # Icon
        icon_label = QLabel(self.icon)
        icon_label.setStyleSheet(f"""
            color: white;
            font-size: 40px;
            background: transparent;
            border: none;
            padding: 0px;
        """)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setMinimumHeight(50)
        layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel(self.title)
        title_label.setStyleSheet(f"""
            color: white;
            font-size: {AriaTypography.BODY}px;
            font-weight: 600;
            background: transparent;
            border: none;
            padding: 0px;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setWordWrap(True)
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(self.description)
        desc_label.setStyleSheet(f"""
            color: {AriaColors.WHITE_70};
            font-size: {AriaTypography.CAPTION}px;
            background: transparent;
            border: none;
            padding: 0px;
        """)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        add_card_shadow(self)
    
    def update_style(self):
        """Update card style based on selection"""
        if self.is_selected:
            self.setStyleSheet(f"""
                QFrame {{
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:1,
                        stop:0 {AriaColors.TEAL},
                        stop:1 rgba(68, 197, 230, 0.7)
                    );
                    border-radius: {AriaRadius.LG}px;
                    border: 2px solid {AriaColors.TEAL_HOVER};
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QFrame {{
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:1,
                        stop:0 {AriaColors.CARD_BG_LIGHT},
                        stop:1 {AriaColors.CARD_BG_PINK_LIGHT}
                    );
                    border-radius: {AriaRadius.LG}px;
                    border: 1px solid {AriaColors.WHITE_25};
                }}
                QFrame:hover {{
                    border: 1px solid {AriaColors.WHITE_45};
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:1,
                        stop:0 rgba(111, 162, 200, 0.5),
                        stop:1 rgba(232, 151, 189, 0.5)
                    );
                }}
            """)
    
    def set_selected(self, selected):
        """Set selection state"""
        self.is_selected = selected
        self.update_style()
    
    def mousePressEvent(self, event):
        """Handle click"""
        self.clicked.emit(self.preset_data)


class OnboardingStep(QWidget):
    """Base class for onboarding steps"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")

    def get_data(self):
        """Override to return step data"""
        return {}


class WelcomeStep(OnboardingStep):
    """Welcome and introduction step"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(AriaSpacing.GIANT, AriaSpacing.XXL, AriaSpacing.GIANT, AriaSpacing.XXL)
        layout.setSpacing(AriaSpacing.XXL)
        layout.addStretch()

        # Large animated icon
        icon = QLabel("🎵")
        icon.setStyleSheet(f"""
            color: white;
            font-size: 96px;
            background: transparent;
        """)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon)

        # Title with gradient accent
        title = QLabel("Welcome to Aria")
        title.setStyleSheet(f"""
            color: white;
            font-size: {AriaTypography.LOGO}px;
            font-weight: 700;
            background: transparent;
            letter-spacing: 2px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Your Voice Training Companion")
        subtitle.setStyleSheet(f"""
            color: {AriaColors.TEAL};
            font-size: {AriaTypography.HEADING}px;
            font-weight: 500;
            background: transparent;
        """)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(AriaSpacing.XXL)

        # Modern feature grid
        features_container = QFrame()
        features_container.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {AriaColors.CARD_BG_LIGHT},
                    stop:1 {AriaColors.CARD_BG_PINK_LIGHT}
                );
                border-radius: {AriaRadius.XL}px;
                border: none;
            }}
        """)
        add_card_shadow(features_container)
        
        features_layout = QVBoxLayout(features_container)
        features_layout.setContentsMargins(AriaSpacing.XXL, AriaSpacing.XXL, AriaSpacing.XXL, AriaSpacing.XXL)
        features_layout.setSpacing(AriaSpacing.LG)

        features = [
            ("🎤", "Real-time Pitch Monitoring", "Track your voice live with instant visual feedback"),
            ("🏃", "Guided Voice Exercises", "Structured warmups and training routines"),
            ("📈", "Progress Tracking", "Monitor your improvement over time"),
            ("❤️", "Safety Monitoring", "Alerts to prevent vocal strain")
        ]

        for emoji, feature_title, feature_desc in features:
            feature_row = QHBoxLayout()
            feature_row.setSpacing(AriaSpacing.MD)
            
            # Emoji icon
            icon_label = QLabel(emoji)
            icon_label.setStyleSheet(f"""
                color: white;
                font-size: 28px;
                background: transparent;
            """)
            icon_label.setFixedWidth(40)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            feature_row.addWidget(icon_label)
            
            # Text container
            text_container = QVBoxLayout()
            text_container.setSpacing(2)
            
            title_label = QLabel(feature_title)
            title_label.setStyleSheet(f"""
                color: white;
                font-size: {AriaTypography.BODY}px;
                font-weight: 600;
                background: transparent;
            """)
            text_container.addWidget(title_label)
            
            desc_label = QLabel(feature_desc)
            desc_label.setStyleSheet(f"""
                color: {AriaColors.WHITE_70};
                font-size: {AriaTypography.BODY_SMALL}px;
                background: transparent;
            """)
            desc_label.setWordWrap(True)
            text_container.addWidget(desc_label)
            
            feature_row.addLayout(text_container)
            features_layout.addLayout(feature_row)

        layout.addWidget(features_container)
        layout.addStretch()


class VoiceGoalsStep(OnboardingStep):
    """Modern voice training goal selection with cards"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_preset = None
        self.preset_cards = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(AriaSpacing.GIANT, AriaSpacing.XL, AriaSpacing.GIANT, AriaSpacing.XL)
        layout.setSpacing(AriaSpacing.XXL)

        # Title section
        title = QLabel("Choose Your Voice Goal")
        title.setStyleSheet(f"""
            color: white;
            font-size: {AriaTypography.TITLE}px;
            font-weight: 700;
            background: transparent;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        desc = QLabel("Select the training path that matches your goals. You can change this anytime in Settings.")
        desc.setStyleSheet(f"""
            color: {AriaColors.WHITE_85};
            font-size: {AriaTypography.BODY}px;
            background: transparent;
        """)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addSpacing(AriaSpacing.LG)

        # Preset cards in grid
        cards_container = QWidget()
        cards_layout = QVBoxLayout(cards_container)
        cards_layout.setSpacing(AriaSpacing.LG)
        
        # Row 1
        row1 = QHBoxLayout()
        row1.setSpacing(AriaSpacing.LG)
        
        # MTF Card
        mtf_card = PresetCard(
            "Feminine Voice",
            "💃",
            "165-265 Hz",
            {
                "voice_goals": "Feminine voice development (MTF)",
                "voice_preset": "MTF - Feminine voice training (165-265 Hz)",
                "base_goal": 165,
                "current_goal": 165,
                "goal_increment": 3,
                "target_pitch_range": [165, 265]
            }
        )
        mtf_card.clicked.connect(self.on_preset_selected)
        self.preset_cards.append(mtf_card)
        row1.addWidget(mtf_card)
        
        # FTM Card
        ftm_card = PresetCard(
            "Masculine Voice",
            "🗣️",
            "85-165 Hz",
            {
                "voice_goals": "Masculine voice development (FTM)",
                "voice_preset": "FTM - Masculine voice training (85-165 Hz)",
                "base_goal": 120,
                "current_goal": 120,
                "goal_increment": -3,
                "target_pitch_range": [85, 165]
            }
        )
        ftm_card.clicked.connect(self.on_preset_selected)
        self.preset_cards.append(ftm_card)
        row1.addWidget(ftm_card)
        
        cards_layout.addLayout(row1)
        
        # Row 2
        row2 = QHBoxLayout()
        row2.setSpacing(AriaSpacing.LG)
        
        # Non-Binary Higher
        nb_higher_card = PresetCard(
            "Androgynous (Higher)",
            "✨",
            "145-220 Hz",
            {
                "voice_goals": "Non-binary voice development (Higher)",
                "voice_preset": "Non-Binary (Higher) - Androgynous with elevation",
                "base_goal": 180,
                "current_goal": 180,
                "goal_increment": 2,
                "target_pitch_range": [145, 220]
            }
        )
        nb_higher_card.clicked.connect(self.on_preset_selected)
        self.preset_cards.append(nb_higher_card)
        row2.addWidget(nb_higher_card)
        
        # Non-Binary Lower
        nb_lower_card = PresetCard(
            "Androgynous (Lower)",
            "🎙️",
            "100-200 Hz",
            {
                "voice_goals": "Non-binary voice development (Lower)",
                "voice_preset": "Non-Binary (Lower) - Androgynous with deepening",
                "base_goal": 140,
                "current_goal": 140,
                "goal_increment": -2,
                "target_pitch_range": [100, 200]
            }
        )
        nb_lower_card.clicked.connect(self.on_preset_selected)
        self.preset_cards.append(nb_lower_card)
        row2.addWidget(nb_lower_card)
        
        cards_layout.addLayout(row2)
        
        # Row 3 - Custom
        row3 = QHBoxLayout()
        row3.setSpacing(AriaSpacing.LG)
        row3.addStretch()
        
        custom_card = PresetCard(
            "Custom Configuration",
            "⚙️",
            "Set your own range",
            {
                "voice_goals": "Custom voice development",
                "voice_preset": "Custom - Manual configuration",
                "base_goal": 180,
                "current_goal": 180,
                "goal_increment": 0,
                "target_pitch_range": [120, 220]
            }
        )
        custom_card.clicked.connect(self.on_preset_selected)
        custom_card.setMaximumWidth(360)
        self.preset_cards.append(custom_card)
        row3.addWidget(custom_card)
        row3.addStretch()
        
        cards_layout.addLayout(row3)
        
        layout.addWidget(cards_container)
        layout.addStretch()
        
        # Select first by default
        self.on_preset_selected(self.preset_cards[0].preset_data)

    def on_preset_selected(self, preset_data):
        """Handle preset selection"""
        self.selected_preset = preset_data
        
        # Update card styles
        for card in self.preset_cards:
            is_selected = card.preset_data == preset_data
            card.set_selected(is_selected)

    def get_data(self):
        """Return selected preset data"""
        return self.selected_preset if self.selected_preset else self.preset_cards[0].preset_data


class SafetyTipsStep(OnboardingStep):
    """Safety tips with modern icon layout"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(AriaSpacing.GIANT, AriaSpacing.XL, AriaSpacing.GIANT, AriaSpacing.XL)
        layout.setSpacing(AriaSpacing.XXL)

        # Title
        title = QLabel("Voice Training Safety")
        title.setStyleSheet(f"""
            color: white;
            font-size: {AriaTypography.TITLE}px;
            font-weight: 700;
            background: transparent;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        desc = QLabel("Keep these guidelines in mind for healthy and effective voice training.")
        desc.setStyleSheet(f"""
            color: {AriaColors.WHITE_85};
            font-size: {AriaTypography.BODY}px;
            background: transparent;
        """)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addSpacing(AriaSpacing.LG)

        # Safety tips container
        tips_container = QFrame()
        tips_container.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {AriaColors.CARD_BG_LIGHT},
                    stop:1 {AriaColors.CARD_BG_PINK_LIGHT}
                );
                border-radius: {AriaRadius.XL}px;
                border: 1px solid {AriaColors.WHITE_25};
            }}
        """)
        add_card_shadow(tips_container)
        
        tips_layout = QVBoxLayout(tips_container)
        tips_layout.setContentsMargins(AriaSpacing.XXL, AriaSpacing.XXL, AriaSpacing.XXL, AriaSpacing.XXL)
        tips_layout.setSpacing(AriaSpacing.LG)

        tips = [
            ("💧", "Stay hydrated", "Drink water before and during training sessions"),
            ("⏱️", "Take breaks", "Rest for 5-10 minutes every 20-30 minutes"),
            ("🎯", "Start gradually", "Begin with short sessions and build up over time"),
            ("🚫", "Stop if it hurts", "Never push through pain or discomfort"),
            ("🌡️", "Warm up first", "Do gentle humming and breathing exercises"),
            ("📅", "Rest days matter", "Give your voice time to recover between sessions")
        ]

        for emoji, tip_title, tip_desc in tips:
            tip_row = QHBoxLayout()
            tip_row.setSpacing(AriaSpacing.MD)
            
            # Emoji
            emoji_label = QLabel(emoji)
            emoji_label.setStyleSheet(f"""
                color: white;
                font-size: 28px;
                background: transparent;
                border: none;
                padding: 0px;
            """)
            emoji_label.setFixedWidth(40)
            emoji_label.setMinimumHeight(40)
            emoji_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            tip_row.addWidget(emoji_label)
            
            # Text
            text_container = QVBoxLayout()
            text_container.setSpacing(2)
            
            title_label = QLabel(tip_title)
            title_label.setStyleSheet(f"""
                color: white;
                font-size: {AriaTypography.BODY}px;
                font-weight: 600;
                background: transparent;
                border: none;
                padding: 0px;
            """)
            text_container.addWidget(title_label)
            
            desc_label = QLabel(tip_desc)
            desc_label.setStyleSheet(f"""
                color: {AriaColors.WHITE_70};
                font-size: {AriaTypography.BODY_SMALL}px;
                background: transparent;
                border: none;
                padding: 0px;
            """)
            desc_label.setWordWrap(True)
            text_container.addWidget(desc_label)
            
            tip_row.addLayout(text_container)
            tips_layout.addLayout(tip_row)

        layout.addWidget(tips_container)
        layout.addStretch()


class FinishStep(OnboardingStep):
    """Final step with welcoming call to action"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(AriaSpacing.XXL, AriaSpacing.LG, AriaSpacing.XXL, AriaSpacing.LG)
        layout.setSpacing(24)  # Reduced spacing
        layout.addStretch(1)  # Less stretch at top

        # Success icon - slightly smaller
        icon = QLabel("✨")
        icon.setStyleSheet(f"""
            color: {AriaColors.TEAL};
            font-size: 80px;
            background: transparent;
        """)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon)

        layout.addSpacing(AriaSpacing.SM)

        # Title - more welcoming
        title = QLabel("You're Ready to Begin!")
        title.setStyleSheet(f"""
            color: white;
            font-size: {AriaTypography.TITLE}px;
            font-weight: 700;
            background: transparent;
            letter-spacing: 1px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        layout.addSpacing(AriaSpacing.SM)

        # Subtitle - encouraging message
        subtitle = QLabel("Your voice training journey starts now")
        subtitle.setStyleSheet(f"""
            color: {AriaColors.TEAL};
            font-size: {AriaTypography.SUBHEADING}px;
            font-weight: 500;
            background: transparent;
        """)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(AriaSpacing.MD)

        # Description - more comfortable width and spacing
        desc = QLabel(
            "Take your time, listen to your body, and remember that progress comes "
            "with patience and practice. We're here to support you every step of the way."
        )
        desc.setStyleSheet(f"""
            color: {AriaColors.WHITE_85};
            font-size: {AriaTypography.BODY_SMALL}px;
            background: transparent;
            line-height: 1.5;
        """)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        desc.setMaximumWidth(650)
        layout.addWidget(desc, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addSpacing(AriaSpacing.LG)

        # Quick start suggestions - more compact
        tips_container = QFrame()
        tips_container.setMaximumWidth(700)
        tips_container.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {AriaColors.CARD_BG_LIGHT},
                    stop:1 {AriaColors.CARD_BG_PINK_LIGHT}
                );
                border-radius: {AriaRadius.XL}px;
                border: 1px solid {AriaColors.WHITE_25};
            }}
        """)
        add_card_shadow(tips_container)
        
        tips_layout = QVBoxLayout(tips_container)
        tips_layout.setContentsMargins(32, 24, 32, 24)  # More compact padding
        tips_layout.setSpacing(16)  # Tighter spacing
        
        tips_title = QLabel("Where to Start")
        tips_title.setStyleSheet(f"""
            color: white;
            font-size: {AriaTypography.SUBHEADING}px;
            font-weight: 600;
            background: transparent;
        """)
        tips_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tips_layout.addWidget(tips_title)
        
        tips_layout.addSpacing(AriaSpacing.SM)
        
        # More compact tip layout
        tips = [
            ("🎤", "Try the 5-Minute Warmup to prepare your voice"),
            ("📊", "Visit Progress to see your journey unfold"),
            ("❤️", "Keep an eye on Vocal Health for safety tips"),
            ("⚙️", "Customize your experience in Settings anytime")
        ]
        
        for emoji, tip_text in tips:
            tip_container = QHBoxLayout()
            tip_container.setSpacing(AriaSpacing.SM)
            
            # Emoji
            emoji_label = QLabel(emoji)
            emoji_label.setStyleSheet(f"""
                color: white;
                font-size: 26px;
                background: transparent;
                border: none;
                padding: 0px;
            """)
            emoji_label.setFixedWidth(36)
            emoji_label.setMinimumHeight(36)
            emoji_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            tip_container.addWidget(emoji_label)
            
            # Tip text
            tip_label = QLabel(tip_text)
            tip_label.setStyleSheet(f"""
                color: {AriaColors.WHITE_90};
                font-size: {AriaTypography.BODY_SMALL}px;
                background: transparent;
                border: none;
                padding: 0px;
            """)
            tip_label.setWordWrap(True)
            tip_container.addWidget(tip_label)
            
            tips_layout.addLayout(tip_container)

        layout.addWidget(tips_container, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addStretch(1)  # Less stretch at bottom


class OnboardingScreen(QWidget):
    """Modern multi-step onboarding wizard"""

    onboarding_completed = pyqtSignal(dict)
    onboarding_cancelled = pyqtSignal()

    def __init__(self, voice_trainer):
        super().__init__()
        self.voice_trainer = voice_trainer
        self.current_step = 0
        self.config = {}
        self.init_ui()

    def init_ui(self):
        """Initialize modern onboarding UI"""
        # Gradient background
        content = QFrame()
        content.setStyleSheet(create_gradient_background())

        layout = QVBoxLayout(content)
        layout.setContentsMargins(AriaSpacing.XXL, AriaSpacing.XXL, AriaSpacing.XXL, AriaSpacing.XXL)
        layout.setSpacing(AriaSpacing.XL)

        # Modern header with step indicator
        header = QHBoxLayout()
        header.addStretch()
        
        self.step_indicator = ModernStepIndicator(total_steps=4)
        header.addWidget(self.step_indicator)
        
        header.addStretch()
        layout.addLayout(header)

        layout.addSpacing(AriaSpacing.MD)

        # Step stack
        self.step_stack = QStackedWidget()
        self.step_stack.setStyleSheet("background: transparent;")

        # Create steps
        self.steps = [
            WelcomeStep(),
            VoiceGoalsStep(),
            SafetyTipsStep(),
            FinishStep()
        ]

        for step in self.steps:
            self.step_stack.addWidget(step)

        layout.addWidget(self.step_stack, stretch=1)

        # Modern navigation buttons
        buttons = QHBoxLayout()
        buttons.setSpacing(AriaSpacing.LG)

        # Left side - Back button
        self.back_btn = SecondaryButton("← Back")
        self.back_btn.clicked.connect(self.previous_step)
        self.back_btn.setVisible(False)
        self.back_btn.setMinimumWidth(120)
        buttons.addWidget(self.back_btn)

        buttons.addStretch()

        # Right side - Skip and Next
        right_buttons = QHBoxLayout()
        right_buttons.setSpacing(AriaSpacing.MD)
        
        self.skip_btn = SecondaryButton("Skip Setup")
        self.skip_btn.clicked.connect(self.skip_onboarding)
        self.skip_btn.setMinimumWidth(120)
        right_buttons.addWidget(self.skip_btn)

        self.next_btn = PrimaryButton("Next →")
        self.next_btn.clicked.connect(self.next_step)
        self.next_btn.setMinimumWidth(140)
        right_buttons.addWidget(self.next_btn)
        
        buttons.addLayout(right_buttons)

        layout.addLayout(buttons)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(content)

    def next_step(self):
        """Move to next step"""
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.step_stack.setCurrentIndex(self.current_step)
            self.update_navigation()
        else:
            self.complete_onboarding()

    def previous_step(self):
        """Move to previous step"""
        if self.current_step > 0:
            self.current_step -= 1
            self.step_stack.setCurrentIndex(self.current_step)
            self.update_navigation()

    def update_navigation(self):
        """Update navigation buttons and step indicator"""
        # Update step indicator
        self.step_indicator.set_step(self.current_step)

        # Update buttons
        self.back_btn.setVisible(self.current_step > 0)

        if self.current_step == len(self.steps) - 1:
            self.next_btn.setText("Start Training")
            self.skip_btn.setVisible(False)
        else:
            self.next_btn.setText("Next →")
            self.skip_btn.setVisible(True)

    def complete_onboarding(self):
        """Complete onboarding with collected data"""
        # Collect data from voice goals step
        goals_step = self.steps[1]
        self.config = goals_step.get_data()

        self.onboarding_completed.emit(self.config)

    def skip_onboarding(self):
        """Skip onboarding and use defaults"""
        self.onboarding_cancelled.emit()
