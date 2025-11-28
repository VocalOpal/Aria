"""Pitch heat map widget showing practice patterns by time and day."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QComboBox
from PyQt6.QtCore import Qt
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np


class PitchHeatMapWidget(QWidget):
    """Heat map visualization showing average pitch by day and hour"""
    
    def __init__(self, session_manager, parent=None):
        super().__init__(parent)
        self.session_manager = session_manager
        self.days_range = 30
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # Header with date range selector
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
        
        title = QLabel("Practice Patterns")
        title.setStyleSheet("""
            color: white;
            font-size: 18px;
            font-weight: 600;
            background: transparent;
        """)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Date range selector
        range_label = QLabel("Show:")
        range_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.7);
            font-size: 14px;
            background: transparent;
        """)
        header_layout.addWidget(range_label)
        
        self.range_selector = QComboBox()
        self.range_selector.addItems(["Last 30 days", "Last 60 days", "Last 90 days"])
        self.range_selector.setStyleSheet("""
            QComboBox {
                background: rgba(255, 255, 255, 0.1);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 14px;
                min-width: 120px;
            }
            QComboBox:hover {
                background: rgba(255, 255, 255, 0.15);
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid white;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                background: rgba(40, 40, 60, 0.95);
                color: white;
                selection-background-color: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 6px;
                outline: none;
            }
        """)
        self.range_selector.currentIndexChanged.connect(self.on_range_changed)
        header_layout.addWidget(self.range_selector)
        
        layout.addLayout(header_layout)
        
        # Matplotlib figure
        self.figure = Figure(figsize=(10, 6), facecolor='none')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background: transparent;")
        layout.addWidget(self.canvas)
        
        # Insights section
        self.insights_label = QLabel("")
        self.insights_label.setWordWrap(True)
        self.insights_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.9);
                font-size: 14px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 16px;
                line-height: 1.6;
            }
        """)
        layout.addWidget(self.insights_label)
        
        # Initial render
        self.update_heatmap()
        
    def on_range_changed(self, index):
        """Handle date range selection change"""
        ranges = [30, 60, 90]
        self.days_range = ranges[index]
        self.update_heatmap()
        
    def update_heatmap(self):
        """Update heatmap visualization"""
        # Get data from session manager
        heatmap_data = self.session_manager.get_practice_time_heatmap_data(self.days_range)
        
        if not heatmap_data or all(not day_data for day_data in heatmap_data.values()):
            self._show_empty_state()
            return
            
        # Prepare data for heatmap
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        hours = list(range(24))
        
        # Create 2D array for heatmap (7 days x 24 hours)
        data_matrix = np.full((7, 24), np.nan)
        
        for day_idx, day in enumerate(days):
            if day in heatmap_data:
                for hour in hours:
                    if hour in heatmap_data[day]:
                        avg_pitch = heatmap_data[day][hour].get('avg_pitch', 0)
                        if avg_pitch > 0:
                            data_matrix[day_idx, hour] = avg_pitch
        
        # Create heatmap
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Use masked array to handle NaN values
        masked_data = np.ma.masked_invalid(data_matrix)
        
        # Create heatmap with blue to pink gradient
        im = ax.imshow(masked_data, cmap='coolwarm', aspect='auto', 
                      vmin=np.nanmin(data_matrix) if not np.all(np.isnan(data_matrix)) else 0,
                      vmax=np.nanmax(data_matrix) if not np.all(np.isnan(data_matrix)) else 200,
                      interpolation='nearest')
        
        # Set background color for empty cells
        ax.set_facecolor('#363654')
        
        # Configure axes
        ax.set_xticks(range(24))
        ax.set_xticklabels([f"{h:02d}" if h % 3 == 0 else "" for h in hours], 
                          fontsize=9, color='white')
        ax.set_yticks(range(7))
        ax.set_yticklabels([d[:3] for d in days], fontsize=10, color='white')
        
        ax.set_xlabel('Hour of Day', fontsize=11, color='white', labelpad=8)
        ax.set_ylabel('Day of Week', fontsize=11, color='white', labelpad=8)
        
        # Add colorbar
        cbar = self.figure.colorbar(im, ax=ax, pad=0.02)
        cbar.set_label('Average Pitch (Hz)', fontsize=10, color='white', labelpad=10)
        cbar.ax.tick_params(labelsize=9, colors='white')
        
        # Style the plot
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color((1.0, 1.0, 1.0, 0.3))
        ax.spines['left'].set_color((1.0, 1.0, 1.0, 0.3))
        ax.tick_params(colors='white', which='both')
        
        # Add hover tooltip functionality (basic - shows on click)
        def on_hover(event):
            if event.inaxes == ax:
                x, y = int(event.xdata + 0.5), int(event.ydata + 0.5)
                if 0 <= x < 24 and 0 <= y < 7:
                    day_name = days[y]
                    hour = x
                    if day_name in heatmap_data and hour in heatmap_data[day_name]:
                        info = heatmap_data[day_name][hour]
                        pitch = info.get('avg_pitch', 0)
                        count = info.get('count', 0)
                        if pitch > 0:
                            # Format hour as 12-hour time
                            hour_12 = hour % 12 if hour % 12 != 0 else 12
                            period = 'AM' if hour < 12 else 'PM'
                            tooltip = f"{day_name} {hour_12} {period}: {pitch:.0f} Hz ({count} session{'s' if count != 1 else ''})"
                            ax.set_title(tooltip, fontsize=10, color='white', pad=10)
                            self.canvas.draw_idle()
        
        self.canvas.mpl_connect('motion_notify_event', on_hover)
        
        self.figure.tight_layout()
        self.canvas.draw()
        
        # Generate insights
        insights = self._generate_insights(heatmap_data)
        self.insights_label.setText(insights)
        
    def _show_empty_state(self):
        """Show empty state when no data available"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.text(0.5, 0.5, 'No practice data available\nComplete sessions to see patterns',
                ha='center', va='center', fontsize=14, color=(1.0, 1.0, 1.0, 0.5),
                transform=ax.transAxes)
        ax.axis('off')
        ax.set_facecolor('none')
        self.canvas.draw()
        
        self.insights_label.setText("Complete practice sessions to discover your optimal training times.")
        
    def _generate_insights(self, heatmap_data):
        """Generate insights from heatmap data"""
        if not heatmap_data:
            return "Complete practice sessions to discover your optimal training times."
            
        # Find best performing time slot
        best_pitch = 0
        best_slot = None
        best_count = 0
        
        # Find most consistent time slot (highest session count)
        most_consistent_count = 0
        most_consistent_slot = None
        
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for day in days_order:
            if day not in heatmap_data:
                continue
            for hour, data in heatmap_data[day].items():
                avg_pitch = data.get('avg_pitch', 0)
                count = data.get('count', 0)
                
                if avg_pitch > best_pitch:
                    best_pitch = avg_pitch
                    best_slot = (day, hour)
                    best_count = count
                    
                if count > most_consistent_count:
                    most_consistent_count = count
                    most_consistent_slot = (day, hour)
        
        insights = []
        
        if best_slot:
            day, hour = best_slot
            hour_12 = hour % 12 if hour % 12 != 0 else 12
            period = 'AM' if hour < 12 else 'PM'
            insights.append(f"🎯 <b>Best Performance:</b> {day}s at {hour_12} {period} ({best_pitch:.0f} Hz average)")
        
        if most_consistent_slot and most_consistent_slot != best_slot:
            day, hour = most_consistent_slot
            hour_12 = hour % 12 if hour % 12 != 0 else 12
            period = 'AM' if hour < 12 else 'PM'
            insights.append(f"📊 <b>Most Consistent:</b> {day}s at {hour_12} {period} ({most_consistent_count} sessions)")
        
        if best_slot:
            day, hour = best_slot
            hour_12 = hour % 12 if hour % 12 != 0 else 12
            period = 'AM' if hour < 12 else 'PM'
            insights.append(f"💡 <b>Recommendation:</b> Schedule practice on {day}s around {hour_12} {period} when you perform best")
        
        return " • ".join(insights) if insights else "Keep practicing to discover your optimal training patterns!"
    
    def refresh(self):
        """Refresh the heatmap"""
        self.update_heatmap()
