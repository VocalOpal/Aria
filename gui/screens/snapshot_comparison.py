"""Voice Journey - Snapshot comparison and progress visualization screen"""

import wave
import numpy as np
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QComboBox, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

from ..design_system import (
    AriaColors, AriaTypography, AriaSpacing, AriaRadius,
    InfoCard, TitleLabel, HeadingLabel, BodyLabel, CaptionLabel,
    PrimaryButton, SecondaryButton, create_gradient_background,
    create_scroll_container, add_card_shadow
)
from core.voice_snapshots import VoiceSnapshotManager


class SnapshotComparisonScreen(QWidget):
    """Voice Journey screen for comparing snapshots over time"""
    
    def __init__(self, voice_trainer):
        super().__init__()
        self.voice_trainer = voice_trainer
        self.snapshot_manager = VoiceSnapshotManager()
        
        self.player1 = None
        self.player2 = None
        self.audio_output1 = None
        self.audio_output2 = None
        
        self.selected_snapshot1 = None
        self.selected_snapshot2 = None
        
        self.init_ui()
        self.load_snapshots()
    
    def init_ui(self):
        """Initialize the UI"""
        content = QFrame()
        content.setStyleSheet(create_gradient_background())
        
        layout = QVBoxLayout(content)
        layout.setContentsMargins(48, 48, 48, 48)
        layout.setSpacing(32)
        
        layout.addWidget(TitleLabel("Voice Journey 🎵"))
        
        subtitle = CaptionLabel("Track your voice progress over time")
        subtitle.setStyleSheet(f"color: {AriaColors.WHITE_70}; font-size: {AriaTypography.BODY}px;")
        layout.addWidget(subtitle)
        
        scroll = create_scroll_container()
        scroll_content = QWidget()
        scroll_content.setStyleSheet("QWidget { background: transparent; }")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(AriaSpacing.LG)
        
        self.comparison_section = self.create_comparison_section()
        scroll_layout.addWidget(self.comparison_section)
        
        self.timeline_section = self.create_timeline_section()
        scroll_layout.addWidget(self.timeline_section)
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(content)
    
    def create_comparison_section(self):
        """Create the side-by-side comparison section"""
        section = QFrame()
        section.setStyleSheet("background: transparent;")
        section_layout = QVBoxLayout(section)
        section_layout.setSpacing(24)
        
        section_layout.addWidget(HeadingLabel("Compare Snapshots"))
        
        compare_row = QHBoxLayout()
        compare_row.setSpacing(AriaSpacing.XL)
        
        self.snapshot1_card = self.create_snapshot_player_card("Snapshot 1", 1)
        self.snapshot2_card = self.create_snapshot_player_card("Snapshot 2", 2)
        
        compare_row.addWidget(self.snapshot1_card)
        compare_row.addWidget(self.snapshot2_card)
        
        section_layout.addLayout(compare_row)
        
        self.stats_comparison_card = InfoCard("Improvement Analysis", min_height=250)
        self.stats_text = BodyLabel("Select two snapshots to compare")
        self.stats_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stats_text.setStyleSheet(f"color: {AriaColors.WHITE_70}; padding: {AriaSpacing.XL}px;")
        self.stats_comparison_card.content_layout.addWidget(self.stats_text)
        
        section_layout.addWidget(self.stats_comparison_card)
        
        return section
    
    def create_snapshot_player_card(self, title, player_num):
        """Create a snapshot player card"""
        card = InfoCard(title, min_height=300)
        
        dropdown = QComboBox()
        dropdown.setStyleSheet(f"""
            QComboBox {{
                background-color: {AriaColors.WHITE_25};
                color: white;
                border: 1px solid {AriaColors.WHITE_45};
                border-radius: {AriaRadius.SM}px;
                padding: {AriaSpacing.SM}px;
                font-size: {AriaTypography.BODY}px;
                min-height: 40px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: {AriaColors.SIDEBAR_DARK};
                color: white;
                selection-background-color: {AriaColors.TEAL};
            }}
        """)
        dropdown.addItem("Select a snapshot...")
        dropdown.currentIndexChanged.connect(lambda idx: self.on_snapshot_selected(player_num, idx))
        card.content_layout.addWidget(dropdown)
        
        if player_num == 1:
            self.dropdown1 = dropdown
        else:
            self.dropdown2 = dropdown
        
        info_frame = QFrame()
        info_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {AriaColors.WHITE_25};
                border-radius: {AriaRadius.MD}px;
                padding: {AriaSpacing.LG}px;
            }}
        """)
        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(AriaSpacing.SM)
        
        date_label = CaptionLabel("No snapshot selected")
        date_label.setStyleSheet(f"color: {AriaColors.WHITE_85}; font-size: {AriaTypography.BODY_SMALL}px;")
        info_layout.addWidget(date_label)
        
        pitch_label = BodyLabel("Avg Pitch: --")
        pitch_label.setStyleSheet(f"color: white; font-size: {AriaTypography.BODY}px; font-weight: 600;")
        info_layout.addWidget(pitch_label)
        
        card.content_layout.addWidget(info_frame)
        
        if player_num == 1:
            self.info1_date = date_label
            self.info1_pitch = pitch_label
        else:
            self.info2_date = date_label
            self.info2_pitch = pitch_label
        
        play_btn = PrimaryButton("▶ Play")
        play_btn.setMinimumSize(150, 50)
        play_btn.clicked.connect(lambda: self.play_snapshot(player_num))
        play_btn.setEnabled(False)
        card.content_layout.addWidget(play_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        if player_num == 1:
            self.play_btn1 = play_btn
        else:
            self.play_btn2 = play_btn
        
        card.content_layout.addStretch()
        
        return card
    
    def create_timeline_section(self):
        """Create the timeline view section"""
        section = QFrame()
        section.setStyleSheet("background: transparent;")
        section_layout = QVBoxLayout(section)
        section_layout.setSpacing(24)
        
        section_layout.addWidget(HeadingLabel("Your Progress Timeline"))
        
        self.timeline_container = QFrame()
        self.timeline_container.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {AriaColors.CARD_BG},
                    stop:1 {AriaColors.CARD_BG_PINK}
                );
                border-radius: {AriaRadius.LG}px;
                border: 1px solid {AriaColors.WHITE_25};
                padding: {AriaSpacing.XL}px;
            }}
        """)
        add_card_shadow(self.timeline_container)
        
        self.timeline_layout = QVBoxLayout(self.timeline_container)
        self.timeline_layout.setSpacing(AriaSpacing.MD)
        
        section_layout.addWidget(self.timeline_container)
        
        return section
    
    def load_snapshots(self):
        """Load all snapshots into the UI"""
        snapshots = self.snapshot_manager.get_snapshots()
        
        self.dropdown1.clear()
        self.dropdown2.clear()
        self.dropdown1.addItem("Select a snapshot...")
        self.dropdown2.addItem("Select a snapshot...")
        
        for snapshot in snapshots:
            timestamp = datetime.fromisoformat(snapshot['timestamp'])
            label = timestamp.strftime("%b %d, %Y - %I:%M %p")
            if snapshot.get('is_milestone'):
                label = f"🎖️ Milestone #{snapshot.get('milestone_number', '')} - {label}"
            
            self.dropdown1.addItem(label, snapshot['id'])
            self.dropdown2.addItem(label, snapshot['id'])
        
        self.populate_timeline(snapshots)
        
        if len(snapshots) == 0:
            self.stats_text.setText("No snapshots yet.\n\nRecord snapshots during training to track your progress!")
            self.stats_text.setStyleSheet(f"color: {AriaColors.WHITE_70}; padding: {AriaSpacing.XL}px; font-style: italic;")
    
    def populate_timeline(self, snapshots):
        """Populate the timeline with snapshot entries"""
        while self.timeline_layout.count():
            item = self.timeline_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if len(snapshots) == 0:
            empty_label = BodyLabel("No snapshots recorded yet")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet(f"color: {AriaColors.WHITE_70}; padding: {AriaSpacing.XXL}px; font-style: italic;")
            self.timeline_layout.addWidget(empty_label)
            return
        
        for snapshot in snapshots:
            entry = self.create_timeline_entry(snapshot)
            self.timeline_layout.addWidget(entry)
    
    def create_timeline_entry(self, snapshot):
        """Create a timeline entry widget"""
        entry = QFrame()
        entry.setStyleSheet(f"""
            QFrame {{
                background-color: {AriaColors.WHITE_25};
                border-radius: {AriaRadius.MD}px;
                padding: {AriaSpacing.MD}px;
            }}
            QFrame:hover {{
                background-color: {AriaColors.WHITE_35};
            }}
        """)
        entry.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QHBoxLayout(entry)
        layout.setSpacing(AriaSpacing.LG)
        
        timestamp = datetime.fromisoformat(snapshot['timestamp'])
        date_str = timestamp.strftime("%b %d, %Y")
        time_str = timestamp.strftime("%I:%M %p")
        
        icon = "🎖️" if snapshot.get('is_milestone') else "📸"
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: 24px; background: transparent;")
        layout.addWidget(icon_label)
        
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        title = QLabel(f"{date_str} • {time_str}")
        title.setStyleSheet(f"color: white; font-size: {AriaTypography.BODY}px; font-weight: 600; background: transparent;")
        info_layout.addWidget(title)
        
        stats_text = f"Avg Pitch: {int(snapshot['stats'].get('avg_pitch', 0))} Hz"
        if snapshot.get('note'):
            stats_text += f" • {snapshot['note']}"
        
        stats = QLabel(stats_text)
        stats.setStyleSheet(f"color: {AriaColors.WHITE_70}; font-size: {AriaTypography.BODY_SMALL}px; background: transparent;")
        info_layout.addWidget(stats)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        play_mini_btn = QPushButton("▶")
        play_mini_btn.setFixedSize(40, 40)
        play_mini_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {AriaColors.TEAL};
                color: white;
                border: none;
                border-radius: {AriaRadius.SM}px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {AriaColors.TEAL_HOVER};
            }}
        """)
        play_mini_btn.clicked.connect(lambda: self.play_timeline_snapshot(snapshot['id']))
        layout.addWidget(play_mini_btn)
        
        return entry
    
    def on_snapshot_selected(self, player_num, index):
        """Handle snapshot selection"""
        dropdown = self.dropdown1 if player_num == 1 else self.dropdown2
        
        if index == 0:
            return
        
        snapshot_id = dropdown.itemData(index)
        snapshot = self.snapshot_manager.get_snapshot_by_id(snapshot_id)
        
        if not snapshot:
            return
        
        if player_num == 1:
            self.selected_snapshot1 = snapshot
            self.update_snapshot_info(1, snapshot)
            self.play_btn1.setEnabled(True)
        else:
            self.selected_snapshot2 = snapshot
            self.update_snapshot_info(2, snapshot)
            self.play_btn2.setEnabled(True)
        
        if self.selected_snapshot1 and self.selected_snapshot2:
            self.update_comparison()
    
    def update_snapshot_info(self, player_num, snapshot):
        """Update snapshot info display"""
        timestamp = datetime.fromisoformat(snapshot['timestamp'])
        date_str = timestamp.strftime("%B %d, %Y at %I:%M %p")
        avg_pitch = int(snapshot['stats'].get('avg_pitch', 0))
        
        if player_num == 1:
            self.info1_date.setText(date_str)
            self.info1_pitch.setText(f"Avg Pitch: {avg_pitch} Hz")
        else:
            self.info2_date.setText(date_str)
            self.info2_pitch.setText(f"Avg Pitch: {avg_pitch} Hz")
    
    def update_comparison(self):
        """Update the comparison stats"""
        if not self.selected_snapshot1 or not self.selected_snapshot2:
            return
        
        comparison = self.snapshot_manager.compare_snapshots(
            self.selected_snapshot1['id'],
            self.selected_snapshot2['id']
        )
        
        if not comparison:
            return
        
        time_diff = comparison['time_between']['formatted']
        pitch_change = comparison['improvements']['pitch_change']
        quality_change = comparison['improvements']['quality_change']
        
        stats_html = f"""
        <div style='color: white; font-size: {AriaTypography.BODY}px;'>
            <p style='font-size: {AriaTypography.HEADING}px; font-weight: bold; color: {AriaColors.TEAL};'>
                Time Between: {time_diff}
            </p>
            <table style='width: 100%; margin-top: {AriaSpacing.LG}px;'>
                <tr>
                    <td style='padding: {AriaSpacing.SM}px; font-weight: 600;'>Metric</td>
                    <td style='padding: {AriaSpacing.SM}px; text-align: center; font-weight: 600;'>Before</td>
                    <td style='padding: {AriaSpacing.SM}px; text-align: center; font-weight: 600;'>After</td>
                    <td style='padding: {AriaSpacing.SM}px; text-align: center; font-weight: 600;'>Change</td>
                </tr>
                <tr style='background-color: {AriaColors.WHITE_25};'>
                    <td style='padding: {AriaSpacing.SM}px;'>Avg Pitch</td>
                    <td style='padding: {AriaSpacing.SM}px; text-align: center;'>{int(comparison['stats_comparison']['pitch']['before'])} Hz</td>
                    <td style='padding: {AriaSpacing.SM}px; text-align: center;'>{int(comparison['stats_comparison']['pitch']['after'])} Hz</td>
                    <td style='padding: {AriaSpacing.SM}px; text-align: center; color: {'#52C55A' if pitch_change > 0 else '#F14C4C'};'>
                        {'+' if pitch_change > 0 else ''}{int(pitch_change)} Hz
                    </td>
                </tr>
                <tr>
                    <td style='padding: {AriaSpacing.SM}px;'>Resonance</td>
                    <td style='padding: {AriaSpacing.SM}px; text-align: center;'>{int(comparison['stats_comparison']['resonance']['before'])}</td>
                    <td style='padding: {AriaSpacing.SM}px; text-align: center;'>{int(comparison['stats_comparison']['resonance']['after'])}</td>
                    <td style='padding: {AriaSpacing.SM}px; text-align: center;'>--</td>
                </tr>
                <tr style='background-color: {AriaColors.WHITE_25};'>
                    <td style='padding: {AriaSpacing.SM}px;'>Voice Quality</td>
                    <td style='padding: {AriaSpacing.SM}px; text-align: center;'>{int(comparison['stats_comparison']['quality']['before'])}</td>
                    <td style='padding: {AriaSpacing.SM}px; text-align: center;'>{int(comparison['stats_comparison']['quality']['after'])}</td>
                    <td style='padding: {AriaSpacing.SM}px; text-align: center; color: {'#52C55A' if quality_change > 0 else '#F14C4C'};'>
                        {'+' if quality_change > 0 else ''}{int(quality_change)}
                    </td>
                </tr>
            </table>
        </div>
        """
        
        self.stats_text.setText(stats_html)
        self.stats_text.setTextFormat(Qt.TextFormat.RichText)
        self.stats_text.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    
    def play_snapshot(self, player_num):
        """Play the selected snapshot"""
        snapshot = self.selected_snapshot1 if player_num == 1 else self.selected_snapshot2
        
        if not snapshot:
            return
        
        audio_path = self.snapshot_manager.get_snapshot_path(snapshot['id'])
        
        if not audio_path or not audio_path.exists():
            return
        
        try:
            if player_num == 1:
                if self.player1:
                    self.player1.stop()
                self.audio_output1 = QAudioOutput()
                self.player1 = QMediaPlayer()
                self.player1.setAudioOutput(self.audio_output1)
                self.player1.setSource(QUrl.fromLocalFile(str(audio_path)))
                self.player1.play()
            else:
                if self.player2:
                    self.player2.stop()
                self.audio_output2 = QAudioOutput()
                self.player2 = QMediaPlayer()
                self.player2.setAudioOutput(self.audio_output2)
                self.player2.setSource(QUrl.fromLocalFile(str(audio_path)))
                self.player2.play()
        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "SnapshotComparisonScreen.play_snapshot")
    
    def play_timeline_snapshot(self, snapshot_id):
        """Play a snapshot from the timeline"""
        audio_path = self.snapshot_manager.get_snapshot_path(snapshot_id)
        
        if not audio_path or not audio_path.exists():
            return
        
        try:
            if self.player1:
                self.player1.stop()
            self.audio_output1 = QAudioOutput()
            self.player1 = QMediaPlayer()
            self.player1.setAudioOutput(self.audio_output1)
            self.player1.setSource(QUrl.fromLocalFile(str(audio_path)))
            self.player1.play()
        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "SnapshotComparisonScreen.play_timeline_snapshot")
    
    def cleanup(self):
        """Cleanup media players"""
        try:
            if self.player1:
                self.player1.stop()
            if self.player2:
                self.player2.stop()
        except Exception:
            pass
