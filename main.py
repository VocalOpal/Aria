"""
Aria Voice Studio v4.1
Voice training application

Your voice, your journey, your authentic self

Usage: python main.py [options]

Options:
    --config FILE    Configuration file path (default: data/voice_config.json)
    --help           Show this help message
"""

import sys
import argparse
from core import setup_global_error_handling, disable_global_error_handling
from voice_trainer import VoiceTrainer

# Initialize global error handling as early as possible
setup_global_error_handling()

def print_banner():
    """Print application banner"""
    banner = """
================================================================================
                            Aria Voice Studio v4.1
                    Your voice, your journey, your authentic self
================================================================================
Voice training that adapts to your progress:
  ~ Real-time pitch monitoring with gentle high/low alerts
  ~ Progressive goal system that adapts to your improvement
  ~ Vocal exercises and guided warm-up routines
  ~ Voice resonance analysis to help develop authentic sound
  ~ Breathing pattern training and resonance quality detection
  ~ Auto-save progress with detailed tracking over time
  
Smooth terminal interface | Smart coaching | Designed with care
================================================================================
"""
    print(banner)

def main():
    parser = argparse.ArgumentParser(
        description="Aria Voice Studio - Voice training application",
        add_help=False
    )
    
    parser.add_argument("--config", type=str, default="data/voice_config.json",
                        help="Configuration file path")
    parser.add_argument("--help", action="store_true",
                        help="Show help message")
    
    args = parser.parse_args()
    
    if args.help:
        print(__doc__)
        parser.print_help()
        sys.exit(0)
        
    try:
        trainer = VoiceTrainer(config_file=args.config)

        # Only show banner if not first-time user (first-time users see setup screen)
        from voice_presets import FirstTimeUserSetup
        setup = FirstTimeUserSetup(args.config)
        if not setup.is_first_time_user():
            print_banner()

        trainer.run()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        print("Please check your audio system and try again")
        sys.exit(1)
    finally:
        # Clean up error handling system
        disable_global_error_handling()

if __name__ == "__main__":
    main()
