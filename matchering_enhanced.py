#!/usr/bin/env python3
"""
Enhanced Matchering Wrapper - Improved User Experience & Productivity Features

This enhanced version adds:
- Batch processing with progress bars
- Automatic file discovery and organization
- Preset configurations for different genres
- Real-time progress feedback
- Error handling with user-friendly messages
- Automatic backup creation
- Processing history logging
- Multiple output format generation
- Quality comparison tools
"""

import os
import sys
import time
import json
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from tqdm import tqdm
except ImportError:
    print("Installing tqdm for progress bars...")
    os.system("pip install tqdm")
    from tqdm import tqdm

import matchering as mg

@dataclass
class ProcessingPreset:
    """Predefined settings for different music genres and use cases"""
    name: str
    description: str
    config_overrides: Dict
    output_formats: List[str]
    use_limiter: bool = True
    normalize: bool = True

class MatcheringEnhanced:
    """Enhanced Matchering with improved UX and productivity features"""
    
    def __init__(self, workspace_dir: str = "./matchering_workspace"):
        self.workspace_dir = Path(workspace_dir)
        self.setup_workspace()
        self.history_file = self.workspace_dir / "processing_history.json"
        self.presets = self._load_presets()
        
    def setup_workspace(self):
        """Create organized workspace structure"""
        directories = [
            "input", "output", "references", "backups", 
            "previews", "logs", "configs", "temp"
        ]
        
        for dir_name in directories:
            (self.workspace_dir / dir_name).mkdir(parents=True, exist_ok=True)
        
        print(f"✅ Workspace initialized at: {self.workspace_dir.absolute()}")
        
    def _load_presets(self) -> Dict[str, ProcessingPreset]:
        """Load predefined presets for different music genres"""
        return {
            "pop_radio": ProcessingPreset(
                name="Pop/Radio Ready",
                description="Loud, punchy sound suitable for radio play",
                config_overrides={"threshold": 0.95},
                output_formats=["wav_16", "wav_24", "mp3_320"],
                use_limiter=True
            ),
            "audiophile": ProcessingPreset(
                name="Audiophile Quality",
                description="High dynamic range for critical listening",
                config_overrides={"threshold": 0.85, "rms_correction_steps": 6},
                output_formats=["wav_24", "flac_24"],
                use_limiter=False,
                normalize=False
            ),
            "streaming": ProcessingPreset(
                name="Streaming Optimized",
                description="Optimized for Spotify, Apple Music, etc.",
                config_overrides={"threshold": 0.90},
                output_formats=["wav_16", "wav_24"],
                use_limiter=True
            ),
            "classical": ProcessingPreset(
                name="Classical/Orchestral",
                description="Preserves wide dynamic range",
                config_overrides={"threshold": 0.75, "rms_correction_steps": 2},
                output_formats=["wav_24", "flac_24"],
                use_limiter=False
            ),
            "electronic": ProcessingPreset(
                name="Electronic/EDM",
                description="Powerful, club-ready sound",
                config_overrides={"threshold": 0.98},
                output_formats=["wav_16", "wav_24"],
                use_limiter=True
            )
        }
    
    def list_presets(self):
        """Display available presets"""
        print("\n🎛️  Available Presets:")
        print("=" * 50)
        for key, preset in self.presets.items():
            print(f"📁 {key}: {preset.name}")
            print(f"   {preset.description}")
            print(f"   Formats: {', '.join(preset.output_formats)}")
            print()
    
    def discover_audio_files(self, directory: str, extensions: List[str] = None) -> List[Path]:
        """Automatically discover audio files in directory"""
        if extensions is None:
            extensions = ['.wav', '.mp3', '.flac', '.aiff', '.ogg', '.m4a']
        
        audio_files = []
        search_path = Path(directory)
        
        for ext in extensions:
            audio_files.extend(search_path.rglob(f"*{ext}"))
            audio_files.extend(search_path.rglob(f"*{ext.upper()}"))
        
        return sorted(audio_files)
    
    def create_backup(self, file_path: Path) -> Path:
        """Create backup of original file"""
        backup_dir = self.workspace_dir / "backups"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        backup_path = backup_dir / backup_name
        
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def generate_file_hash(self, file_path: Path) -> str:
        """Generate hash for file integrity checking"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def log_processing_session(self, session_data: Dict):
        """Log processing session for history tracking"""
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                history = json.load(f)
        else:
            history = []
        
        session_data['timestamp'] = datetime.now().isoformat()
        history.append(session_data)
        
        # Keep only last 100 sessions
        history = history[-100:]
        
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    def batch_process(self, 
                     target_files: List[Path], 
                     reference_file: Path,
                     preset_name: str = "streaming",
                     create_backups: bool = True,
                     max_workers: int = 2) -> Dict:
        """
        Process multiple files with progress tracking and error handling
        """
        if preset_name not in self.presets:
            raise ValueError(f"Unknown preset: {preset_name}. Available: {list(self.presets.keys())}")
        
        preset = self.presets[preset_name]
        results = {"successful": [], "failed": [], "skipped": []}
        
        print(f"\n🎚️  Starting batch processing with '{preset.name}' preset")
        print(f"📁 Reference: {reference_file.name}")
        print(f"🎵 Processing {len(target_files)} files...")
        
        # Create session data for logging
        session_data = {
            "preset": preset_name,
            "reference_file": str(reference_file),
            "target_files": [str(f) for f in target_files],
            "results": results
        }
        
        # Setup output directory
        output_dir = self.workspace_dir / "output" / preset_name / datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Process files with progress bar
        with tqdm(total=len(target_files), desc="Processing", unit="file") as pbar:
            
            def process_single_file(target_file: Path) -> Tuple[Path, bool, str]:
                try:
                    # Create backup if requested
                    if create_backups:
                        backup_path = self.create_backup(target_file)
                        print(f"💾 Backup created: {backup_path.name}")
                    
                    # Generate output files based on preset
                    output_files = []
                    for fmt in preset.output_formats:
                        if fmt == "wav_16":
                            output_files.append(mg.pcm16(str(output_dir / f"{target_file.stem}_mastered_16bit.wav")))
                        elif fmt == "wav_24":
                            output_files.append(mg.pcm24(str(output_dir / f"{target_file.stem}_mastered_24bit.wav")))
                        elif fmt == "flac_24":
                            output_files.append(mg.Result(
                                str(output_dir / f"{target_file.stem}_mastered_24bit.flac"),
                                subtype="PCM_24",
                                use_limiter=preset.use_limiter,
                                normalize=preset.normalize
                            ))
                    
                    # Apply custom config if any
                    config = mg.Config()
                    for key, value in preset.config_overrides.items():
                        setattr(config, key, value)
                    
                    # Enable logging for this process
                    mg.log(print)
                    
                    # Process the file
                    mg.process(
                        target=str(target_file),
                        reference=str(reference_file),
                        results=output_files,
                        config=config,
                        # Create preview files
                        preview_target=mg.pcm16(str(self.workspace_dir / "previews" / f"preview_{target_file.stem}_original.wav")),
                        preview_result=mg.pcm16(str(self.workspace_dir / "previews" / f"preview_{target_file.stem}_mastered.wav"))
                    )
                    
                    return target_file, True, "Success"
                    
                except Exception as e:
                    return target_file, False, str(e)
            
            # Process files (with limited concurrency to avoid memory issues)
            if max_workers > 1 and len(target_files) > 1:
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    future_to_file = {executor.submit(process_single_file, f): f for f in target_files}
                    
                    for future in as_completed(future_to_file):
                        target_file, success, message = future.result()
                        
                        if success:
                            results["successful"].append(str(target_file))
                            pbar.set_postfix_str(f"✅ {target_file.name}")
                        else:
                            results["failed"].append({"file": str(target_file), "error": message})
                            pbar.set_postfix_str(f"❌ {target_file.name}")
                        
                        pbar.update(1)
            else:
                # Sequential processing
                for target_file in target_files:
                    target_file, success, message = process_single_file(target_file)
                    
                    if success:
                        results["successful"].append(str(target_file))
                        pbar.set_postfix_str(f"✅ {target_file.name}")
                    else:
                        results["failed"].append({"file": str(target_file), "error": message})
                        pbar.set_postfix_str(f"❌ {target_file.name}")
                    
                    pbar.update(1)
        
        # Log session
        session_data["results"] = results
        session_data["output_directory"] = str(output_dir)
        self.log_processing_session(session_data)
        
        # Print summary
        print(f"\n📊 Processing Complete!")
        print(f"✅ Successful: {len(results['successful'])}")
        print(f"❌ Failed: {len(results['failed'])}")
        print(f"📁 Output directory: {output_dir}")
        
        return results
    
    def interactive_mode(self):
        """Interactive mode with user-friendly interface"""
        print("\n🎚️  Matchering Enhanced - Interactive Mode")
        print("=" * 50)
        
        while True:
            print("\nChoose an option:")
            print("1. 📁 Discover audio files in directory")
            print("2. 🎛️  View available presets")
            print("3. 🎵 Process single file")
            print("4. 📦 Batch process files")
            print("5. 📊 View processing history")
            print("6. ❌ Exit")
            
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == "1":
                directory = input("Enter directory path: ").strip()
                if os.path.exists(directory):
                    files = self.discover_audio_files(directory)
                    print(f"\n🎵 Found {len(files)} audio files:")
                    for i, file in enumerate(files[:10], 1):  # Show first 10
                        print(f"  {i}. {file.name}")
                    if len(files) > 10:
                        print(f"  ... and {len(files) - 10} more")
                else:
                    print("❌ Directory not found!")
                    
            elif choice == "2":
                self.list_presets()
                
            elif choice == "3":
                print("🎵 Single file processing - Not implemented in this demo")
                
            elif choice == "4":
                print("📦 Batch processing setup:")
                target_dir = input("Target files directory: ").strip()
                reference_file = input("Reference file path: ").strip()
                
                if os.path.exists(target_dir) and os.path.exists(reference_file):
                    files = self.discover_audio_files(target_dir)
                    print(f"Found {len(files)} files to process")
                    
                    print("Available presets:")
                    for i, (key, preset) in enumerate(self.presets.items(), 1):
                        print(f"  {i}. {key} - {preset.name}")
                    
                    preset_choice = input("Choose preset (enter name or number): ").strip()
                    
                    # Handle numeric choice
                    if preset_choice.isdigit():
                        preset_keys = list(self.presets.keys())
                        if 1 <= int(preset_choice) <= len(preset_keys):
                            preset_choice = preset_keys[int(preset_choice) - 1]
                    
                    if preset_choice in self.presets:
                        self.batch_process(files, Path(reference_file), preset_choice)
                    else:
                        print("❌ Invalid preset choice!")
                else:
                    print("❌ Invalid file paths!")
                    
            elif choice == "5":
                if self.history_file.exists():
                    with open(self.history_file, 'r') as f:
                        history = json.load(f)
                    print(f"\n📊 Last {min(5, len(history))} processing sessions:")
                    for session in history[-5:]:
                        print(f"  📅 {session['timestamp'][:19]}")
                        print(f"     Preset: {session['preset']}")
                        print(f"     Files: {len(session['target_files'])}")
                        print(f"     Success: {len(session['results']['successful'])}")
                        print()
                else:
                    print("📊 No processing history found")
                    
            elif choice == "6":
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice!")

def main():
    """Main entry point"""
    enhanced = MatcheringEnhanced()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--interactive":
            enhanced.interactive_mode()
        elif sys.argv[1] == "--presets":
            enhanced.list_presets()
        else:
            print("Usage: python matchering_enhanced.py [--interactive|--presets]")
    else:
        enhanced.interactive_mode()

if __name__ == "__main__":
    main()
