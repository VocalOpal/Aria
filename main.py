#!/usr/bin/env python3
"""
Aria Voice Studio v4.0
Voice training application

Your voice, your journey, your authentic self

Usage: python main.py [options]

Options:
    --config FILE    Configuration file path (default: data/voice_config.json)
    --help           Show this help message
"""

import sys
import argparse
from voice_trainer import VoiceTrainer

def print_banner():
    """Print application banner"""
    banner = """
================================================================================
                            Aria Voice Studio v4.0
                    Your voice, your journey, your authentic self
================================================================================
Voice training with intelligent features:
  ~ Real-time pitch monitoring with gentle high/low alerts
  ~ Progressive goal system that adapts to your improvement
  ~ Vocal exercises and guided warm-up routines
  ~ Advanced formant analysis for authentic voice feminization
  ~ Breathing pattern training and resonance quality detection
  ~ Auto-save progress with comprehensive trend analysis
  
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

if __name__ == "__main__":
    main()