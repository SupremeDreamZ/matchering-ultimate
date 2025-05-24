#!/usr/bin/env python3
"""
🔥 MATCHERING ULTIMATE - QUICK START EXAMPLES 🔥

Simple examples to get you started with the most powerful mastering system!
"""

import sys
sys.path.append('..')  # Add parent directory to path

# Example 1: Simple single track mastering
def example_single_track():
    """Master a single track with one line of code"""
    print("\n🎵 Example 1: Single Track Mastering")
    print("=" * 50)
    
    from matchering_cli import MatcheringCLI
    
    # In real use:
    # python matchering_cli.py master my_song.mp3 reference.wav
    
    print("Command: python matchering_cli.py master my_song.mp3 reference.wav")
    print("This will create both 16-bit and 24-bit mastered versions!")

# Example 2: Multi-reference blending
def example_multi_reference():
    """Blend multiple reference tracks for unique sound"""
    print("\n🔥 Example 2: Multi-Reference Blending")
    print("=" * 50)
    
    from matchering_ultra import MatcheringUltra
    
    ultra = MatcheringUltra()
    
    # Example usage (replace with your files)
    target = "my_track.wav"
    references = [
        "reference1_drake.mp3",
        "reference2_travis.mp3",
        "reference3_metro.mp3"
    ]
    
    print(f"Target: {target}")
    print(f"References: {references}")
    print("\nThis will create 4 variations with different blends!")
    print("A/B/C/D comparison file will be generated.")
    
    # In real use:
    # result = ultra.multi_reference_process(target, references, preset="trap")

# Example 3: Batch processing with genre presets
def example_batch_processing():
    """Process multiple files with genre-specific settings"""
    print("\n📦 Example 3: Batch Processing with Presets")
    print("=" * 50)
    
    from matchering_enhanced import MatcheringEnhanced
    
    enhanced = MatcheringEnhanced()
    
    # Show available presets
    print("Available presets:")
    for key, preset in enhanced.presets.items():
        print(f"  • {key}: {preset.name}")
    
    print("\nExample: Process all files in a directory with 'streaming' preset")
    print("Command: python matchering_enhanced.py --interactive")

# Example 4: Smart auto-detection
def example_quantum():
    """Drop anything - folder, file, ZIP - it figures it out!"""
    print("\n🧠 Example 4: QUANTUM Auto-Detection")
    print("=" * 50)
    
    print("Just drop ANYTHING:")
    print("  • Single file → Automatic single mastering")
    print("  • Album folder → Full album processing")
    print("  • ZIP file → Extract and process")
    print("  • Playlist → Process all tracks")
    print("\nCommand: python matchering_QUANTUM.py")
    print("Then just drag and drop!")

# Example 5: Full album mastering
def example_album_mastering():
    """Master an entire album with track reordering and multi-format export"""
    print("\n💿 Example 5: Full Album Mastering")
    print("=" * 50)
    
    print("Features:")
    print("  • AI-powered track reordering")
    print("  • Album cohesion analysis")
    print("  • Multi-format releases (Streaming/Vinyl/CD)")
    print("  • Professional mastering report")
    
    print("\nCommand: python matchering_album_master_complete.py")
    print("Follow the prompts to master your entire album!")

# Example 6: Genre-specific mastering
def example_genre_presets():
    """Show how to use genre-specific presets"""
    print("\n🎨 Example 6: Genre-Specific Mastering")
    print("=" * 50)
    
    genres = {
        "trap": "Heavy 808s, crisp hi-hats",
        "gangsta_rap": "West Coast warmth",
        "funk": "Punchy drums, groovy bass",
        "drill": "Dark, aggressive sound",
        "lofi_hip_hop": "Warm, vintage feel"
    }
    
    print("Available genre presets:")
    for genre, desc in genres.items():
        print(f"  • {genre}: {desc}")
    
    print("\nUsage with matchering_ultra.py:")
    print("Choose your genre preset when processing!")

def main():
    """Run all examples"""
    print("\n" + "🔥" * 30)
    print("\n🚀 MATCHERING ULTIMATE - QUICK START GUIDE 🚀")
    print("\n" + "🔥" * 30)
    
    examples = [
        example_single_track,
        example_multi_reference,
        example_batch_processing,
        example_quantum,
        example_album_mastering,
        example_genre_presets
    ]
    
    for example in examples:
        example()
        input("\nPress Enter to continue...")
    
    print("\n" + "=" * 60)
    print("🎯 READY TO START?")
    print("=" * 60)
    print("\n1. Activate environment: source matchering_env/bin/activate")
    print("2. Launch control center: python MATCHERING_ULTIMATE_CONTROL.py")
    print("3. Choose your adventure!")
    print("\n🔥 NOW GO MAKE SOME FIRE MUSIC! 🔥")

if __name__ == "__main__":
    main()
