"""
ExerciseSpec - Evidence-based vocal training exercises for voice modification.

Based on speech therapy research and trans voice training methodologies.
Includes proper validation logic to ensure exercises are performed correctly.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Callable, Tuple


@dataclass
class ExerciseSpec:
    """Standardized exercise specification with validation"""

    # Basic info
    name: str
    description: str
    instructions: str
    
    # Category and progression
    category: str = "warmup"  # warmup, pitch, resonance, articulation, advanced
    difficulty: str = "Beginner"  # Beginner, Intermediate, Advanced
    prerequisite: Optional[str] = None  # Exercise that should be completed first
    
    # Target audience tags
    tags: List[str] = field(default_factory=lambda: ["ALL"])  # MTF, FTM, NB, ALL

    # Requirements
    requires_pitch: bool = False
    requires_resonance: bool = False
    requires_breathing: bool = False

    # Duration and difficulty
    default_duration: int = 60  # seconds
    min_duration: int = 30  # minimum to count as completed
    
    # Validation criteria
    target_pitch_range: Tuple[int, int] = (0, 0)  # (min_hz, max_hz), 0 means no target
    pitch_stability_threshold: float = 0.0  # Max pitch deviation in Hz
    time_in_range_threshold: float = 0.0  # Min % of time that should be in range
    
    # Exercise patterns for validation
    expected_pattern: str = "sustained"  # sustained, glide_up, glide_down, oscillate, varied
    pattern_tolerance: float = 0.2  # How strict the pattern matching is (0.0-1.0)

    # Additional metadata
    tips: List[str] = field(default_factory=list)
    safety_notes: List[str] = field(default_factory=list)
    common_mistakes: List[str] = field(default_factory=list)
    
    # Visual feedback config
    show_pitch_graph: bool = True
    show_target_zone: bool = True
    show_resonance_indicator: bool = False

    # Callbacks for exercise lifecycle
    start_callback: Optional[Callable] = None
    stop_callback: Optional[Callable] = None
    validate_callback: Optional[Callable] = None

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
            'Beginner': '#10b981',      # Green
            'Intermediate': '#f59e0b',  # Amber
            'Advanced': '#ef4444'       # Red
        }
        return colors.get(self.difficulty, '#6b7280')
    
    def validate_performance(self, pitch_data: List[float], duration: int) -> dict:
        """
        Validate if exercise was performed correctly
        
        Args:
            pitch_data: List of pitch values in Hz
            duration: How long the exercise was performed in seconds
            
        Returns:
            dict with 'valid', 'score', 'feedback' keys
        """
        if not self.requires_pitch or not pitch_data:
            # Non-pitch exercises are always valid if duration met
            return {
                'valid': duration >= self.min_duration,
                'score': 100 if duration >= self.default_duration else (duration / self.default_duration) * 100,
                'feedback': []
            }
        
        feedback = []
        score = 100.0
        
        # Check if enough time spent in target range
        if self.target_pitch_range[0] > 0:
            min_hz, max_hz = self.target_pitch_range
            in_range_count = sum(1 for p in pitch_data if min_hz <= p <= max_hz)
            time_in_range = (in_range_count / len(pitch_data)) * 100 if pitch_data else 0
            
            if time_in_range < (self.time_in_range_threshold * 100):
                score -= 30
                feedback.append(f"Try to stay within {min_hz}-{max_hz} Hz range more consistently")
            else:
                feedback.append(f"Great! You stayed in range {time_in_range:.0f}% of the time")
        
        # Check pitch stability for sustained exercises
        if self.expected_pattern == "sustained" and self.pitch_stability_threshold > 0:
            import statistics
            if len(pitch_data) > 1:
                stdev = statistics.stdev(pitch_data)
                if stdev > self.pitch_stability_threshold:
                    score -= 20
                    feedback.append("Try to keep your pitch more stable and consistent")
                else:
                    feedback.append("Excellent pitch stability!")
        
        # Check duration
        if duration < self.min_duration:
            score -= 40
            feedback.append(f"Exercise too short - aim for at least {self.min_duration}s")
        
        return {
            'valid': score >= 50,  # Need at least 50% to pass
            'score': max(0, score),
            'feedback': feedback
        }


# =============================================================================
# WARMUP & FOUNDATION EXERCISES
# =============================================================================

def create_diaphragmatic_breathing_spec() -> ExerciseSpec:
    """Foundation breathing exercise - crucial for all voice work"""
    return ExerciseSpec(
        name="Diaphragmatic Breathing",
        category="warmup",
        description="Build breath support foundation for vocal control",
        instructions="Breathe deeply into your belly, not your chest. Place one hand on chest (should not move) and one on belly (should expand).",
        requires_pitch=False,
        requires_resonance=False,
        requires_breathing=True,
        default_duration=90,
        min_duration=45,
        difficulty="Beginner",
        show_pitch_graph=False,
        show_target_zone=False,
        tips=[
            "Inhale through nose for 4 counts, expand belly",
            "Hold for 4 counts",
            "Exhale through mouth for 6-8 counts, belly contracts",
            "Your chest and shoulders should stay relatively still",
            "This is the foundation for all vocal exercises"
        ],
        safety_notes=[
            "Never force the breath - breathe naturally",
            "If you feel lightheaded, return to normal breathing",
            "Focus on lower rib expansion, not just belly"
        ],
        common_mistakes=[
            "Breathing only into chest (shallow breathing)",
            "Raising shoulders when inhaling",
            "Forcing the breath instead of allowing it"
        ]
    )


def create_gentle_humming_spec() -> ExerciseSpec:
    """Gentle humming for warmup and resonance awareness"""
    return ExerciseSpec(
        name="Gentle Humming Warmup",
        category="warmup",
        description="Develop forward resonance and warm up vocal folds",
        instructions="Hum gently at a comfortable pitch. Feel vibrations in your face/mask area (not throat or chest). Keep lips closed but relaxed.",
        requires_pitch=True,
        requires_resonance=True,
        requires_breathing=True,
        default_duration=60,
        min_duration=30,
        difficulty="Beginner",
        target_pitch_range=(150, 220),
        pitch_stability_threshold=15.0,
        time_in_range_threshold=0.70,
        expected_pattern="sustained",
        tips=[
            "Start at a comfortable, natural pitch",
            "Place fingers lightly on nose bridge - feel vibration",
            "Chest should have minimal vibration",
            "Think of the sound 'buzzing' in your face",
            "Keep volume gentle - this is a warmup, not a workout"
        ],
        safety_notes=[
            "Keep throat completely relaxed",
            "Stop immediately if you feel any strain",
            "This should feel easy and pleasant",
            "Never push or force the sound"
        ],
        common_mistakes=[
            "Tensing the throat or jaw",
            "Humming too loudly",
            "Focusing sound in throat instead of face"
        ]
    )


def create_lip_trills_spec() -> ExerciseSpec:
    """Lip trills for breath control and vocal fold coordination"""
    return ExerciseSpec(
        name="Lip Trills (Lip Bubbles)",
        category="warmup",
        description="Improve breath support, vocal fold closure, and reduce tension",
        instructions="Make a gentle 'brrr' sound by letting your lips vibrate loosely. Glide your pitch up and down smoothly while maintaining the trill.",
        requires_pitch=True,
        requires_resonance=False,
        requires_breathing=True,
        default_duration=45,
        min_duration=30,
        difficulty="Beginner",
        target_pitch_range=(140, 250),
        expected_pattern="oscillate",
        pattern_tolerance=0.3,
        tips=[
            "Keep lips very relaxed and loose",
            "Use steady, consistent airflow",
            "Try different pitches - low to high and back",
            "If lips won't vibrate, try adding more air or relaxing more",
            "This exercise reduces vocal strain and improves efficiency"
        ],
        safety_notes=[
            "Stop if lips become too dry - take a break",
            "Maintain gentle, steady air pressure",
            "Should feel easy and playful"
        ],
        common_mistakes=[
            "Tensing the lips too much",
            "Not enough airflow",
            "Forcing pitch changes"
        ]
    )


# =============================================================================
# PITCH CONTROL EXERCISES
# =============================================================================

def create_pitch_sirens_spec() -> ExerciseSpec:
    """Vocal sirens for pitch flexibility and range expansion"""
    return ExerciseSpec(
        name="Pitch Sirens",
        category="pitch",
        description="Expand vocal range and improve pitch control with smooth glides",
        instructions="On 'ooo' or 'eee' sound, glide smoothly from your lowest comfortable pitch to highest, then back down. Like a siren.",
        requires_pitch=True,
        requires_resonance=True,
        requires_breathing=True,
        default_duration=60,
        min_duration=30,
        difficulty="Intermediate",
        target_pitch_range=(100, 300),  # Wide range for gliding
        expected_pattern="oscillate",
        tips=[
            "Start at bottom of your range, glide up smoothly",
            "Don't jump between notes - make it one continuous slide",
            "Use 'eee' for brighter, forward sound",
            "Use 'ooo' for rounder, fuller sound",
            "Keep throat relaxed throughout the entire range"
        ],
        safety_notes=[
            "Stop at your comfortable limits - don't strain",
            "Keep volume moderate",
            "If you feel any tension, relax and start lower"
        ],
        common_mistakes=[
            "Jumping between notes instead of smooth glide",
            "Pushing too high or too low",
            "Tensing throat on high notes"
        ]
    )


def create_pitch_slides_forward_spec() -> ExerciseSpec:
    """Pitch slides with forward resonance focus - key for voice feminization"""
    return ExerciseSpec(
        name="Forward Pitch Slides",
        category="pitch",
        description="Develop higher pitch with forward placement (MTF focus)",
        instructions="Slide from comfortable mid pitch to higher pitch on 'nee' or 'mee'. Focus on keeping resonance in face/mask, not throat.",
        requires_pitch=True,
        requires_resonance=True,
        requires_breathing=True,
        default_duration=75,
        min_duration=45,
        difficulty="Intermediate",
        target_pitch_range=(180, 280),
        expected_pattern="glide_up",
        prerequisite="Gentle Humming Warmup",
        tips=[
            "Use 'nee' or 'mee' - these naturally create forward placement",
            "Start at 150-180 Hz, slide up to 250-280 Hz",
            "Feel vibrations in nose/face, NOT chest",
            "Keep sound light and bright",
            "This is crucial for feminine voice development"
        ],
        safety_notes=[
            "Never push to uncomfortable heights",
            "Keep throat loose and relaxed",
            "If you feel strain, lower the target pitch"
        ],
        common_mistakes=[
            "Letting sound drop back into chest",
            "Tensing to reach high notes",
            "Using too much air/volume"
        ]
    )


def create_sustained_pitch_practice_spec() -> ExerciseSpec:
    """Hold target pitch steadily - builds muscle memory"""
    return ExerciseSpec(
        name="Sustained Pitch Training",
        category="pitch",
        description="Build pitch stability and muscle memory at target range",
        instructions="Choose a target pitch in your goal range and hold it steadily on 'ah' or 'ee' for as long as comfortable. Focus on consistency.",
        requires_pitch=True,
        requires_resonance=True,
        requires_breathing=True,
        default_duration=90,
        min_duration=45,
        difficulty="Intermediate",
        target_pitch_range=(170, 220),  # Will be customized per profile
        pitch_stability_threshold=10.0,  # Stay within 10 Hz
        time_in_range_threshold=0.80,  # 80% of time in range
        expected_pattern="sustained",
        tips=[
            "Find your target pitch and hold it steady",
            "Use app's target zone as visual guide",
            "Breathe when needed, return to same pitch",
            "Focus on consistency, not perfection",
            "This builds muscle memory for your target voice"
        ],
        safety_notes=[
            "Keep volume comfortable - not loud",
            "Breathe naturally when you need to",
            "Stop if you feel any strain"
        ],
        common_mistakes=[
            "Pitch drifting up or down",
            "Running out of breath and forcing",
            "Tensing to maintain pitch"
        ]
    )


# =============================================================================
# RESONANCE TRAINING EXERCISES
# =============================================================================

def create_big_dog_small_dog_spec() -> ExerciseSpec:
    """Resonance shifting exercise - understand vocal tract changes"""
    return ExerciseSpec(
        name="Big Dog, Small Dog",
        category="resonance",
        description="Feel the difference between chest and head resonance",
        instructions="Say 'woof' in a deep, chest-resonant voice (big dog), then in a bright, forward voice (small dog). Feel where the vibration moves.",
        requires_pitch=True,
        requires_resonance=True,
        requires_breathing=False,
        default_duration=60,
        min_duration=30,
        difficulty="Beginner",
        target_pitch_range=(120, 260),  # Wide range
        expected_pattern="oscillate",
        tips=[
            "Big dog: low pitch, vibration in chest, sound feels 'back' in throat",
            "Small dog: higher pitch, vibration in face, sound feels 'forward'",
            "Alternate between the two - feel the shift",
            "This teaches you where you want resonance (small dog = forward)"
        ],
        safety_notes=[
            "Don't force the low or high pitches",
            "This is about feeling, not perfection",
            "Have fun with it - it should be playful"
        ],
        common_mistakes=[
            "Only changing pitch without changing resonance",
            "Tensing throat for 'small dog'",
            "Not exaggerating enough to feel the difference"
        ]
    )


def create_resonance_buzz_spec() -> ExerciseSpec:
    """Nasal resonance development with 'mmm' and 'nnn'"""
    return ExerciseSpec(
        name="Resonance Buzz",
        category="resonance",
        description="Develop forward, bright resonance in the mask",
        instructions="Hum on 'mmm', then 'nnn', then 'ng'. Feel strong vibration in nose, face, and upper lip. Minimize chest vibration.",
        requires_pitch=True,
        requires_resonance=True,
        requires_breathing=True,
        default_duration=75,
        min_duration=40,
        difficulty="Intermediate",
        target_pitch_range=(160, 240),
        pitch_stability_threshold=12.0,
        time_in_range_threshold=0.75,
        expected_pattern="sustained",
        prerequisite="Gentle Humming Warmup",
        tips=[
            "Place fingers on nose - should buzz intensely",
            "Place hand on chest - minimal vibration",
            "Try 'mmmm', 'nnnnn', 'ng-ng-ng'",
            "This forward buzz is the resonance you want in speech",
            "Start exaggerated, then normalize"
        ],
        safety_notes=[
            "Keep it comfortable - no forcing",
            "Some buzzing sensation is good",
            "If it feels nasal/pinched, relax soft palate slightly"
        ],
        common_mistakes=[
            "Too much chest resonance",
            "Not enough oral closure (lips/tongue)",
            "Pushing too hard for the buzz"
        ]
    )


def create_vowel_resonance_spec() -> ExerciseSpec:
    """Practice maintaining forward resonance through different vowels"""
    return ExerciseSpec(
        name="Vowel Resonance Training",
        category="resonance",
        description="Maintain forward placement across all vowel sounds",
        instructions="Say 'me-may-my-mo-moo' slowly, keeping vibration in face/mask throughout. Don't let sound drop into chest.",
        requires_pitch=True,
        requires_resonance=True,
        requires_breathing=False,
        default_duration=60,
        min_duration=30,
        difficulty="Intermediate",
        target_pitch_range=(180, 240),
        time_in_range_threshold=0.75,
        expected_pattern="varied",
        prerequisite="Resonance Buzz",
        tips=[
            "Start with 'mmmm' to establish forward buzz",
            "Keep that same buzzy feeling through all vowels",
            "Notice how 'moo' wants to drop back - resist this",
            "'ee' and 'ay' are easiest to keep forward",
            "This is the foundation of consistent feminine resonance"
        ],
        safety_notes=[
            "Speak slowly and deliberately",
            "Keep throat completely relaxed",
            "Exaggerate at first, normalize later"
        ],
        common_mistakes=[
            "Letting back vowels drop into chest",
            "Losing the 'm' buzz between vowels",
            "Pitching forward from throat instead of raising soft palate"
        ]
    )


# =============================================================================
# ADVANCED EXERCISES
# =============================================================================

def create_straw_phonation_spec() -> ExerciseSpec:
    """SOVT exercise - highly effective for vocal health and efficiency"""
    return ExerciseSpec(
        name="Straw Phonation (SOVT)",
        category="advanced",
        description="Semi-occluded vocal tract exercise - improves efficiency and reduces strain",
        instructions="Purse lips like sipping through a straw. Hum or sing scales while maintaining the 'straw' shape. Feel gentle back-pressure.",
        tags=["ALL"],
        requires_pitch=True,
        requires_resonance=False,
        requires_breathing=True,
        default_duration=90,
        min_duration=45,
        difficulty="Beginner",
        target_pitch_range=(150, 250),
        pitch_stability_threshold=15.0,
        expected_pattern="oscillate",
        tips=[
            "Lips should be gently pursed, not tight",
            "You should feel slight resistance/back-pressure",
            "Try gliding pitch up and down",
            "This is one of the BEST exercises for vocal health",
            "Used by professional singers and SLPs worldwide"
        ],
        safety_notes=[
            "Keep it gentle - no forcing",
            "Should feel easy and efficient",
            "Stop if you feel any strain"
        ],
        common_mistakes=[
            "Pursing lips too tightly",
            "Not enough airflow",
            "Tensing throat"
        ]
    )


def create_conversational_practice_spec() -> ExerciseSpec:
    """Apply techniques in connected speech"""
    return ExerciseSpec(
        name="Connected Speech Practice",
        category="advanced",
        description="Apply pitch and resonance in actual speech patterns",
        instructions="Read a passage or count to 30 using your target pitch and forward resonance. Focus on consistency across all sounds.",
        requires_pitch=True,
        requires_resonance=True,
        requires_breathing=True,
        default_duration=120,
        min_duration=60,
        difficulty="Advanced",
        target_pitch_range=(180, 230),  # Will be customized
        time_in_range_threshold=0.70,
        expected_pattern="varied",
        prerequisite="Vowel Resonance Training",
        tips=[
            "Speak naturally, don't 'perform' your voice",
            "Focus on maintaining forward resonance",
            "Let pitch vary naturally within your target range",
            "Practice with: numbers, days of week, simple sentences",
            "This is where training becomes your natural voice"
        ],
        safety_notes=[
            "Take breaks between sentences",
            "Never force or push",
            "It's ok if you slip - this takes time"
        ],
        common_mistakes=[
            "Trying to be too perfect",
            "Losing resonance when concentrating on words",
            "Speaking in a monotone"
        ]
    )


def create_vocal_fry_control_spec() -> ExerciseSpec:
    """Vocal fry control for FTM voice training"""
    return ExerciseSpec(
        name="Vocal Fry Practice",
        category="advanced",
        description="Develop controlled vocal fry for more masculine voice quality (FTM)",
        instructions="Produce a low, creaky 'vocal fry' sound. Practice transitioning smoothly from vocal fry to normal voice and back.",
        tags=["FTM", "NB"],
        requires_pitch=True,
        requires_resonance=True,
        requires_breathing=False,
        default_duration=60,
        min_duration=30,
        difficulty="Advanced",
        target_pitch_range=(80, 120),
        expected_pattern="oscillate",
        tips=[
            "Start very low in pitch - almost a creaky sound",
            "Let vocal folds vibrate slowly and irregularly",
            "This adds masculine quality to voice",
            "Practice: fry to normal voice transition",
            "Common in masculine speech patterns"
        ],
        safety_notes=[
            "Use minimal air pressure",
            "Should feel relaxed, not strained",
            "Don't use excessively - just practice the technique"
        ],
        common_mistakes=[
            "Forcing the fry with too much tension",
            "Using too much air",
            "Not relaxing enough"
        ]
    )


def create_water_resistance_therapy_spec() -> ExerciseSpec:
    """Water Resistance Therapy - modern SOVT technique using actual water"""
    return ExerciseSpec(
        name="Water Resistance Therapy",
        category="advanced",
        description="Blow bubbles through water with phonation - modern physiologic voice therapy",
        instructions="Using a straw in a glass of water (2-3cm deep), blow bubbles while phonating. Glide pitch up and down. Feel gentle resistance.",
        tags=["ALL"],
        requires_pitch=True,
        requires_resonance=False,
        requires_breathing=True,
        default_duration=60,
        min_duration=30,
        difficulty="Intermediate",
        target_pitch_range=(150, 250),
        expected_pattern="oscillate",
        tips=[
            "Use a regular drinking straw in 2-3cm of water",
            "Blow steady bubbles while humming or singing",
            "Try pitch glides up and down",
            "This is a proven technique used by SLPs worldwide",
            "Creates optimal vocal fold vibration with minimal effort"
        ],
        safety_notes=[
            "Don't blow too hard - gentle, steady bubbles",
            "Stop if you feel dizzy - you may be blowing too much air",
            "Keep the straw depth consistent (2-3cm)"
        ],
        common_mistakes=[
            "Blowing too hard/fast",
            "Straw too deep in water (makes it harder)",
            "Not phonating while blowing"
        ]
    )


def create_intonation_patterns_spec() -> ExerciseSpec:
    """Intonation practice - critical for natural-sounding feminine speech"""
    return ExerciseSpec(
        name="Intonation Patterns",
        category="advanced",
        description="Practice natural speech melody and inflection patterns",
        instructions="Practice question vs. statement intonation. Questions rise at end, statements fall. Say 'Really?' with rising pitch, 'I know' with falling pitch.",
        tags=["MTF", "NB"],
        requires_pitch=True,
        requires_resonance=True,
        requires_breathing=False,
        default_duration=90,
        min_duration=45,
        difficulty="Advanced",
        target_pitch_range=(180, 260),
        expected_pattern="varied",
        prerequisite="Connected Speech Practice",
        tips=[
            "Feminine speech has more pitch variation (melody)",
            "Questions: pitch rises at the end",
            "Statements: pitch falls at the end",
            "Practice: 'Really?' (up), 'I know.' (down)",
            "Record yourself and compare to target voices"
        ],
        safety_notes=[
            "Keep throat relaxed during pitch changes",
            "Don't force pitch too high on rises",
            "Natural variation, not dramatic swings"
        ],
        common_mistakes=[
            "Monotone delivery (no variation)",
            "Over-exaggerating the inflection",
            "Only changing pitch without changing resonance"
        ]
    )


def create_soft_start_technique_spec() -> ExerciseSpec:
    """Soft glottal onset - reduces vocal strain and creates smoother voice"""
    return ExerciseSpec(
        name="Soft Start Technique",
        category="advanced",
        description="Practice gentle voice onset to reduce strain and create smoother sound",
        instructions="Say words starting with vowels using 'breathy' start: 'apple', 'ocean', 'easy'. Add tiny 'h' before vowel. Prevents harsh glottal attack.",
        tags=["ALL"],
        requires_pitch=True,
        requires_resonance=False,
        requires_breathing=True,
        default_duration=60,
        min_duration=30,
        difficulty="Intermediate",
        target_pitch_range=(160, 230),
        expected_pattern="varied",
        tips=[
            "Say 'apple' as 'h-apple' (very subtle h)",
            "Start words gently, not abruptly",
            "Reduces vocal fold trauma",
            "Creates smoother, less harsh voice quality",
            "Common in contemporary voice therapy"
        ],
        safety_notes=[
            "Should feel easier, not harder",
            "Don't make it overly breathy",
            "Subtle technique - gentle onset only"
        ],
        common_mistakes=[
            "Too much breathiness",
            "Still using hard glottal attack",
            "Making the 'h' too obvious"
        ]
    )


def create_yawn_sigh_technique_spec() -> ExerciseSpec:
    """Yawn-Sigh for vocal relaxation and range expansion"""
    return ExerciseSpec(
        name="Yawn-Sigh Technique",
        category="warmup",
        description="Relax throat and expand range with gentle yawning and sighing",
        instructions="Yawn gently, then sigh from high to low pitch on 'ahhhh'. Let voice glide down naturally. Promotes vocal tract relaxation.",
        tags=["ALL"],
        requires_pitch=True,
        requires_resonance=False,
        requires_breathing=True,
        default_duration=45,
        min_duration=30,
        difficulty="Beginner",
        target_pitch_range=(120, 280),
        expected_pattern="glide_down",
        tips=[
            "Feel the stretch in your throat when you yawn",
            "Sigh from comfortable high to comfortable low",
            "Should feel very relaxed and easy",
            "Great for releasing tension before practice",
            "Used in classical voice training for centuries"
        ],
        safety_notes=[
            "Don't force the yawn - keep it natural",
            "Should feel relaxing, not straining",
            "Perfect exercise if you feel vocal fatigue"
        ],
        common_mistakes=[
            "Forcing the yawn too wide",
            "Making the sigh too loud/harsh",
            "Tensing during the exercise"
        ]
    )


def create_articulation_precision_spec() -> ExerciseSpec:
    """Clear articulation while maintaining target voice"""
    return ExerciseSpec(
        name="Articulation & Clarity",
        category="advanced",
        description="Maintain voice quality while speaking clearly and precisely",
        instructions="Practice tongue twisters or consonant-heavy phrases at your target pitch. Focus on crisp consonants without losing resonance.",
        requires_pitch=True,
        requires_resonance=True,
        requires_breathing=False,
        default_duration=60,
        min_duration=30,
        difficulty="Advanced",
        target_pitch_range=(170, 230),
        time_in_range_threshold=0.65,
        expected_pattern="varied",
        prerequisite="Connected Speech Practice",
        tips=[
            "Try: 'Red leather yellow leather' or 'She sells seashells'",
            "Focus on clean 't', 'd', 'k', 'p' sounds",
            "Keep resonance forward even during consonants",
            "Slightly exaggerate consonants at first",
            "Clear speech makes any voice more confident"
        ],
        safety_notes=[
            "Start slowly, speed up gradually",
            "Don't sacrifice voice quality for speed",
            "Take breaks when needed"
        ],
        common_mistakes=[
            "Losing pitch when focusing on words",
            "Rushing through the exercise",
            "Mumbling or being unclear"
        ]
    )


# =============================================================================
# ALIASES FOR BACKWARD COMPATIBILITY
# =============================================================================

def create_breathing_spec() -> ExerciseSpec:
    """Alias for diaphragmatic breathing spec"""
    return create_diaphragmatic_breathing_spec()


def create_humming_spec() -> ExerciseSpec:
    """Alias for gentle humming spec"""
    return create_gentle_humming_spec()


def create_pitch_slides_spec() -> ExerciseSpec:
    """Alias for forward pitch slides spec"""
    return create_pitch_slides_forward_spec()


def create_resonance_shift_spec() -> ExerciseSpec:
    """Alias for big dog small dog spec"""
    return create_big_dog_small_dog_spec()
