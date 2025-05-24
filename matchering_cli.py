#!/usr/bin/env python3
"""
Matchering CLI - Simplified Command Line Interface

A user-friendly CLI wrapper for Matchering with common use cases
and simplified syntax for quick audio mastering.
"""

import sys
import os
import argparse
from pathlib import Path
from typing import List

try:
    import matchering as mg
except ImportError:
    print("Error: Matchering not found. Activate the virtual environment first:")
    print("  source matchering_env/bin/activate")
    sys.exit(1)

class MatcheringCLI:
    def __init__(self):
        self.parser = self.setup_parser()
        
    def setup_parser(self):
        """Setup argument parser with subcommands"""
        parser = argparse.ArgumentParser(
            description="🎚️ Matchering CLI - Easy Audio Mastering",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Master a single file
  %(prog)s master song.mp3 reference.wav
  
  # Master with specific output format
  %(prog)s master song.wav reference.wav -f 24bit
  
  # Master all files in a directory
  %(prog)s batch ./my_songs/ reference.wav
  
  # Create preview files
  %(prog)s master song.wav reference.wav --preview
  
  # Use without limiter (for manual limiting)
  %(prog)s master song.wav reference.wav --no-limiter
"""
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Commands')
        
        # Master command
        master_parser = subparsers.add_parser(
            'master', 
            help='Master a single audio file'
        )
        master_parser.add_argument(
            'target',
            help='Target audio file to master'
        )
        master_parser.add_argument(
            'reference',
            help='Reference audio file to match'
        )
        master_parser.add_argument(
            '-f', '--format',
            choices=['16bit', '24bit', 'both', 'flac'],
            default='both',
            help='Output format (default: both)'
        )
        master_parser.add_argument(
            '-o', '--output',
            help='Output file name (auto-generated if not specified)'
        )
        master_parser.add_argument(
            '--no-limiter',
            action='store_true',
            help='Skip the limiter stage (for manual limiting)'
        )
        master_parser.add_argument(
            '--preview',
            action='store_true',
            help='Create 30-second preview files'
        )
        master_parser.add_argument(
            '-q', '--quiet',
            action='store_true',
            help='Suppress progress messages'
        )
        
        # Batch command
        batch_parser = subparsers.add_parser(
            'batch',
            help='Master multiple audio files'
        )
        batch_parser.add_argument(
            'directory',
            help='Directory containing target files'
        )
        batch_parser.add_argument(
            'reference',
            help='Reference audio file to match'
        )
        batch_parser.add_argument(
            '-f', '--format',
            choices=['16bit', '24bit', 'both'],
            default='24bit',
            help='Output format (default: 24bit)'
        )
        batch_parser.add_argument(
            '-e', '--extensions',
            nargs='+',
            default=['.wav', '.mp3', '.flac', '.aiff'],
            help='File extensions to process'
        )
        batch_parser.add_argument(
            '-o', '--output-dir',
            help='Output directory (default: creates "mastered" subfolder)'
        )
        batch_parser.add_argument(
            '-q', '--quiet',
            action='store_true',
            help='Suppress progress messages'
        )
        
        # Check command
        check_parser = subparsers.add_parser(
            'check',
            help='Analyze an audio file'
        )
        check_parser.add_argument(
            'file',
            help='Audio file to analyze'
        )
        
        return parser
    
    def master_single(self, args):
        """Master a single audio file"""
        target_path = Path(args.target)
        reference_path = Path(args.reference)
        
        # Validate files exist
        if not target_path.exists():
            print(f"❌ Error: Target file not found: {args.target}")
            return 1
        
        if not reference_path.exists():
            print(f"❌ Error: Reference file not found: {args.reference}")
            return 1
        
        # Setup logging
        if not args.quiet:
            mg.log(print)
            print(f"🎵 Target: {target_path.name}")
            print(f"📀 Reference: {reference_path.name}")
            print(f"📦 Format: {args.format}")
            print()
        
        # Prepare output files
        output_files = []
        stem = target_path.stem
        
        if args.output:
            output_path = Path(args.output)
            if args.format == 'both':
                output_files.append(mg.pcm16(str(output_path.with_suffix('.16bit.wav'))))
                output_files.append(mg.pcm24(str(output_path.with_suffix('.24bit.wav'))))
            elif args.format == '16bit':
                output_files.append(mg.pcm16(str(output_path)))
            elif args.format == '24bit':
                output_files.append(mg.pcm24(str(output_path)))
            elif args.format == 'flac':
                output_files.append(mg.Result(
                    str(output_path.with_suffix('.flac')),
                    subtype="PCM_24",
                    use_limiter=not args.no_limiter
                ))
        else:
            # Auto-generate output names
            if args.format in ['both', '16bit']:
                output_files.append(mg.pcm16(f"{stem}_mastered_16bit.wav"))
            if args.format in ['both', '24bit']:
                output_files.append(mg.pcm24(f"{stem}_mastered_24bit.wav"))
            if args.format == 'flac':
                output_files.append(mg.Result(
                    f"{stem}_mastered.flac",
                    subtype="PCM_24",
                    use_limiter=not args.no_limiter
                ))
        
        # Add no-limiter option
        if args.no_limiter and args.format != 'flac':
            output_files = [
                mg.Result(
                    f.file,
                    subtype=f.subtype,
                    use_limiter=False,
                    normalize=True
                ) for f in output_files
            ]
        
        # Process
        try:
            kwargs = {
                'target': str(target_path),
                'reference': str(reference_path),
                'results': output_files
            }
            
            # Add preview if requested
            if args.preview:
                kwargs['preview_target'] = mg.pcm16(f"preview_{stem}_original.wav")
                kwargs['preview_result'] = mg.pcm16(f"preview_{stem}_mastered.wav")
            
            mg.process(**kwargs)
            
            if not args.quiet:
                print("\n✅ Mastering completed successfully!")
                for output in output_files:
                    print(f"📁 Output: {output.file}")
                
                if args.preview:
                    print(f"🎵 Preview: preview_{stem}_original.wav")
                    print(f"🎵 Preview: preview_{stem}_mastered.wav")
            
            return 0
            
        except Exception as e:
            print(f"\n❌ Error during processing: {str(e)}")
            return 1
    
    def master_batch(self, args):
        """Master multiple audio files"""
        directory = Path(args.directory)
        reference_path = Path(args.reference)
        
        # Validate inputs
        if not directory.exists():
            print(f"❌ Error: Directory not found: {args.directory}")
            return 1
        
        if not reference_path.exists():
            print(f"❌ Error: Reference file not found: {args.reference}")
            return 1
        
        # Find audio files
        audio_files = []
        for ext in args.extensions:
            audio_files.extend(directory.rglob(f"*{ext}"))
            audio_files.extend(directory.rglob(f"*{ext.upper()}"))
        
        audio_files = sorted(set(audio_files))  # Remove duplicates
        
        if not audio_files:
            print(f"❌ No audio files found in {directory}")
            print(f"   Extensions searched: {', '.join(args.extensions)}")
            return 1
        
        print(f"🎵 Found {len(audio_files)} files to process")
        print(f"📀 Reference: {reference_path.name}")
        
        # Setup output directory
        if args.output_dir:
            output_dir = Path(args.output_dir)
        else:
            output_dir = directory / "mastered"
        
        output_dir.mkdir(exist_ok=True)
        print(f"📁 Output directory: {output_dir}")
        print()
        
        # Setup logging
        if not args.quiet:
            mg.log(info_handler=print, warning_handler=print)
        
        # Process files
        successful = 0
        failed = 0
        
        for i, audio_file in enumerate(audio_files, 1):
            print(f"[{i}/{len(audio_files)}] Processing: {audio_file.name}")
            
            try:
                # Prepare output files
                output_files = []
                stem = audio_file.stem
                
                if args.format in ['both', '16bit']:
                    output_files.append(mg.pcm16(str(output_dir / f"{stem}_mastered_16bit.wav")))
                if args.format in ['both', '24bit']:
                    output_files.append(mg.pcm24(str(output_dir / f"{stem}_mastered_24bit.wav")))
                
                # Process
                mg.process(
                    target=str(audio_file),
                    reference=str(reference_path),
                    results=output_files
                )
                
                successful += 1
                print(f"   ✅ Success\n")
                
            except Exception as e:
                failed += 1
                print(f"   ❌ Failed: {str(e)}\n")
        
        # Summary
        print(f"\n📊 Batch processing complete!")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"📁 Output directory: {output_dir}")
        
        return 0 if failed == 0 else 1
    
    def check_file(self, args):
        """Analyze an audio file"""
        file_path = Path(args.file)
        
        if not file_path.exists():
            print(f"❌ Error: File not found: {args.file}")
            return 1
        
        print(f"🔍 Analyzing: {file_path.name}")
        
        try:
            # Load file
            import soundfile as sf
            data, samplerate = sf.read(str(file_path))
            
            # Basic info
            duration = len(data) / samplerate
            channels = data.shape[1] if len(data.shape) > 1 else 1
            
            print(f"\n📊 File Information:")
            print(f"   Format: {file_path.suffix}")
            print(f"   Sample Rate: {samplerate} Hz")
            print(f"   Channels: {channels}")
            print(f"   Duration: {duration:.2f} seconds")
            print(f"   Samples: {len(data):,}")
            
            # Peak and RMS
            import numpy as np
            if channels > 1:
                peak = np.max(np.abs(data))
                rms = np.sqrt(np.mean(data**2))
            else:
                peak = np.max(np.abs(data))
                rms = np.sqrt(np.mean(data**2))
            
            peak_db = 20 * np.log10(peak) if peak > 0 else -np.inf
            rms_db = 20 * np.log10(rms) if rms > 0 else -np.inf
            
            print(f"\n📈 Level Analysis:")
            print(f"   Peak: {peak:.4f} ({peak_db:.2f} dB)")
            print(f"   RMS: {rms:.4f} ({rms_db:.2f} dB)")
            
            return 0
            
        except Exception as e:
            print(f"❌ Error analyzing file: {str(e)}")
            return 1
    
    def run(self):
        """Main entry point"""
        args = self.parser.parse_args()
        
        if not args.command:
            self.parser.print_help()
            return 1
        
        if args.command == 'master':
            return self.master_single(args)
        elif args.command == 'batch':
            return self.master_batch(args)
        elif args.command == 'check':
            return self.check_file(args)

def main():
    cli = MatcheringCLI()
    sys.exit(cli.run())

if __name__ == "__main__":
    main()
