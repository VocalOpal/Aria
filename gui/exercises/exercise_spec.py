"""
ExerciseSpec - Standardized exercise specification with metadata.

Usage:
    from gui.exercises.exercise_spec import ExerciseSpec
    spec = ExerciseSpec(
        name="Breathing Control",
        description="Deep breathing exercise",
        requires_pitch=False,
        requires_resonance=False,
        default_duration=90
    )
"""

from dataclasses import dataclass
from typing import List, Optional, Callable


@dataclass
class ExerciseSpec:
    """Standardized exercise specification with metadata"""

    # Basic info
    name: str
    description: str
    instructions: str

    # Requirements
    requires_pitch: bool = False
    requires_resonance: bool = False
    requires_breathing: bool = False

    # Duration and difficulty
    default_duration: int = 60  # seconds
    difficulty: str = "Beginner"  # Beginner, Intermediate, Advanced

    # Additional metadata
    tips: List[str] = None
    safety_notes: List[str] = None
    target_pitch_range: tuple = (0, 0)  # (min_hz, max_hz), 0 means no target

    # Callbacks for exercise lifecycle
    start_callback: Optional[Callable] = None
    stop_callback: Optional[Callable] = None
    update_callback: Optional[Callable] = None

    def __post_init__(self):
        """Initialize defaults after creation"""
        if self.tips is None:
            self.tips = []
        if self.safety_notes is None:
            self.safety_notes = []

    def get_metrics_required(self) -> List[str]:
        """Get list of metrics required by this exercise"""
        metrics = []
        if self.requires_pitch:
            metrics.append('pitch')
        if self.requires_resonance:
            metrics.append('resonance')
        if self.requires_breathing:
            metrics.append('breathing')
        return metrics

    def format_duration(self) -> str:
        """Format duration as human-readable string"""
        if self.default_duration < 60:
            return f"{self.default_duration}s"
        else:
            minutes = self.default_duration // 60
            seconds = self.default_duration % 60
            if seconds == 0:
                return f"{minutes}m"
            else:
                return f"{minutes}m {seconds}s"

    def get_difficulty_color(self) -> str:
        """Get color for difficulty indicator"""
        colors = {
            'Beginner': '#10b981',    # Green
            'Intermediate': '#f59e0b',  # Amber
            'Advanced': '#ef4444'     # Red
        }
        return colors.get(self.difficulty, '#6b7280')  # Gray as fallback


def create_breathing_spec() -> ExerciseSpec:
    """Create specification for breathing control exercise"""
    return ExerciseSpec(
        name="Breathing Control",
        description="Diaphragmatic breathing foundation",
        instructions="Deep belly breathing, hand on chest should not move",
        requires_pitch=False,
        requires_resonance=False,
        requires_breathing=True,
        default_duration=90,
        difficulty="Beginner",
        tips=[
            "Place one hand on chest, one on belly",
            "Breathe so only belly hand moves",
            "Chest should remain relatively still",
            "This builds the foundation for all voice control"
        ],
        safety_notes=[
            "Breathe naturally - do not force",
            "If you feel dizzy, breathe normally for a moment",
            "Focus on expansion of lower ribs, not just belly"
        ]
    )


def create_humming_spec() -> ExerciseSpec:
    """Create specification for humming warmup exercise"""
    return ExerciseSpec(
        name="Humming Warmup",
        description="Resonance development and vocal warmup",
        instructions="Hum at comfortable pitch, feel vibrations in face/head (not chest)",
        requires_pitch=True,
        requires_resonance=True,
        requires_breathing=True,
        default_duration=60,
        difficulty="Beginner",
        target_pitch_range=(160, 200),
        tips=[
            "Place hand on chest - should feel minimal vibration",
            "Place hand on face/nose - should feel strong vibration",
            "Start low and gradually move higher",
            "Focus on the buzzing sensation in your face and head"
        ],
        safety_notes=[
            "Keep volume comfortable - no straining",
            "Stop if you feel any throat tension",
            "This should feel relaxing and gentle"
        ]
    )


def create_pitch_slides_spec() -> ExerciseSpec:
    """Create specification for pitch slides exercise"""
    return ExerciseSpec(
        name="Pitch Slides",
        description="Pitch control and resonance development",
        instructions="Slide from low to high pitch on 'nee' sound, focus on head resonance",
        requires_pitch=True,
        requires_resonance=True,
        requires_breathing=False,
        default_duration=90,
        difficulty="Intermediate",
        target_pitch_range=(140, 280),
        tips=[
            "Use 'nee' sound for forward resonance placement",
            "Start at comfortable low pitch",
            "Glide smoothly to highest comfortable pitch",
            "Focus resonance in face/head area, not throat"
        ],
        safety_notes=[
            "Stop at your comfortable upper limit",
            "Keep the sound light and forward",
            "Avoid pushing or straining on high notes"
        ]
    )


def create_lip_trills_spec() -> ExerciseSpec:
    """Create specification for lip trills exercise"""
    return ExerciseSpec(
        name="Lip Trills",
        description="Breath control and pitch flexibility",
        instructions="Make 'brrr' sound, glide pitch up and down smoothly",
        requires_pitch=True,
        requires_resonance=False,
        requires_breathing=True,
        default_duration=45,
        difficulty="Beginner",
        target_pitch_range=(150, 250),
        tips=[
            "Keep lips relaxed and loose",
            "Use steady, consistent airflow",
            "Glide smoothly between pitches",
            "Let the lips 'bubble' naturally with the airflow"
        ],
        safety_notes=[
            "Stop if your lips become too dry",
            "Maintain gentle, consistent air pressure",
            "Avoid forcing the sound"
        ]
    )


def create_resonance_shift_spec() -> ExerciseSpec:
    """Create specification for resonance shift exercise"""
    return ExerciseSpec(
        name="Resonance Shift",
        description="Forward placement training",
        instructions="Say 'me-may-my-mo-moo' focusing sound in nasal cavity/face",
        requires_pitch=True,
        requires_resonance=True,
        requires_breathing=False,
        default_duration=75,
        difficulty="Intermediate",
        target_pitch_range=(170, 250),
        tips=[
            "Feel vibrations in nose and face",
            "Avoid chest resonance",
            "Exaggerate the nasal quality initially",
            "Practice slowly, then gradually speed up"
        ],
        safety_notes=[
            "Start with exaggerated nasal quality, then normalize",
            "Keep throat relaxed throughout",
            "Focus on feeling, not just hearing the sound"
        ]
    )


def create_straw_phonation_spec() -> ExerciseSpec:
    """Create specification for straw phonation exercise"""
    return ExerciseSpec(
        name="Straw Phonation",
        description="Vocal efficiency and tension reduction",
        instructions="Hum through imaginary straw, creates efficient phonation",
        requires_pitch=True,
        requires_resonance=False,
        requires_breathing=True,
        default_duration=120,
        difficulty="Beginner",
        target_pitch_range=(165, 220),
        tips=[
            "Purse lips as if drinking through a straw",
            "Hum any comfortable pitch",
            "Focus on smooth, controlled sound",
            "This exercise improves vocal efficiency and reduces strain"
        ],
        safety_notes=[
            "Keep lips gently pursed, not tightly squeezed",
            "Maintain steady, gentle airflow",
            "Should feel easy and effortless"
        ]
    )