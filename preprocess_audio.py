"""
Preprocesamiento de audio para HiFi-GAN
Extrae mel-spectrogramas de las pistas de Jamendo
"""

import os
import numpy as np
import librosa
import json
from pathlib import Path
from tqdm import tqdm
import soundfile as sf


class AudioPreprocessor:
    """Preprocesador de audio para HiFi-GAN"""
    
    def __init__(self, config):
        self.sample_rate = config['sample_rate']
        self.n_fft = config['n_fft']
        self.hop_length = config['hop_length']
        self.win_length = config['win_length']
        self.n_mels = config['n_mels']
        self.fmin = config['fmin']
        self.fmax = config['fmax']
        self.segment_size = config['segment_size']
        
    def load_audio(self, audio_path):
        """Carga audio y resamplea si es necesario"""
        audio, sr = librosa.load(audio_path, sr=self.sample_rate, mono=True)
        return audio
    
    def extract_mel_spectrogram(self, audio):
        """Extrae mel-spectrogram de audio"""
        # Compute mel spectrogram
        mel = librosa.feature.melspectrogram(
            y=audio,
            sr=self.sample_rate,
            n_fft=self.n_fft,
            hop_length=self.hop_length,
            win_length=self.win_length,
            n_mels=self.n_mels,
            fmin=self.fmin,
            fmax=self.fmax
        )
        
        # Convert to log scale (dB)
        mel_db = librosa.power_to_db(mel, ref=np.max)
        
        return mel_db
    
    def process_directory(self, input_dir, output_dir, max_files=None):
        """Procesa todos los archivos de audio en un directorio"""
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        
        # Create output directories
        audio_dir = output_dir / 'audio'
        mel_dir = output_dir / 'mels'
        audio_dir.mkdir(parents=True, exist_ok=True)
        mel_dir.mkdir(parents=True, exist_ok=True)
        
        # Get all audio files
        audio_files = list(input_dir.glob('*.mp3'))
        if max_files:
            audio_files = audio_files[:max_files]
        
        print(f"Processing {len(audio_files)} audio files...")
        
        metadata = []
        
        for idx, audio_path in enumerate(tqdm(audio_files, desc="Preprocessing")):
            try:
                # Load audio
                audio = self.load_audio(str(audio_path))
                
                # Save processed audio (resampled, mono)
                audio_filename = f"{idx:04d}.wav"
                audio_output_path = audio_dir / audio_filename
                sf.write(audio_output_path, audio, self.sample_rate)
                
                # Extract and save mel spectrogram
                mel = self.extract_mel_spectrogram(audio)
                mel_filename = f"{idx:04d}.npy"
                mel_output_path = mel_dir / mel_filename
                np.save(mel_output_path, mel)
                
                # Store metadata
                metadata.append({
                    'id': idx,
                    'original_file': audio_path.name,
                    'audio_file': str(audio_filename),
                    'mel_file': str(mel_filename),
                    'audio_length': len(audio),
                    'duration': len(audio) / self.sample_rate,
                    'mel_shape': mel.shape
                })
                
            except Exception as e:
                print(f"\nError processing {audio_path.name}: {e}")
                continue
        
        # Save metadata
        metadata_path = output_dir / 'metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\n✓ Processed {len(metadata)} files")
        print(f"✓ Audio saved to: {audio_dir}")
        print(f"✓ Mel spectrograms saved to: {mel_dir}")
        print(f"✓ Metadata saved to: {metadata_path}")
        
        return metadata


def main():
    """Main preprocessing pipeline"""
    
    # Configuration (matching HiFi-GAN defaults)
    config = {
        'sample_rate': 22050,      # Sample rate
        'n_fft': 1024,             # FFT size
        'hop_length': 256,         # Hop length
        'win_length': 1024,        # Window length
        'n_mels': 80,              # Number of mel bands
        'fmin': 0,                 # Minimum frequency
        'fmax': 8000,              # Maximum frequency (Nyquist/2.75)
        'segment_size': 8192       # Segment size for training
    }
    
    # Paths
    base_dir = Path(__file__).parent
    input_dir = base_dir / 'jamendo_tracks'
    output_dir = base_dir / 'data' / 'processed'
    
    # Check input directory
    if not input_dir.exists():
        print(f"Error: Input directory not found: {input_dir}")
        return
    
    print("=" * 70)
    print("AUDIO PREPROCESSING FOR HIFI-GAN")
    print("=" * 70)
    print("\nConfiguration:")
    for key, value in config.items():
        print(f"  {key}: {value}")
    print("=" * 70)
    
    # Process
    preprocessor = AudioPreprocessor(config)
    metadata = preprocessor.process_directory(input_dir, output_dir)
    
    # Summary
    print("\n" + "=" * 70)
    print("PREPROCESSING COMPLETE")
    print("=" * 70)
    print(f"Total files: {len(metadata)}")
    if metadata:
        total_duration = sum(m['duration'] for m in metadata)
        print(f"Total duration: {total_duration/60:.2f} minutes")
        avg_duration = total_duration / len(metadata)
        print(f"Average duration: {avg_duration:.2f} seconds")
    
    # Save config
    config_path = output_dir / 'config.json'
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"\nConfig saved to: {config_path}")


if __name__ == "__main__":
    main()
