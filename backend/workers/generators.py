import asyncio
import logging
import os
import numpy as np
from moviepy.editor import ColorClip, AudioArrayClip
from typing import List

logger = logging.getLogger(__name__)

# Ensure tmp directory exists
os.makedirs("tmp", exist_ok=True)

async def generate_images_mock(prompts: List[str]) -> List[str]:
    """Mock Nano Banana 2: Generates candidate images."""
    logger.info("Mock Nano Banana: Generating images...")
    await asyncio.sleep(2) # Simulate delay
    # Actually we just return dummy paths, Veo doesn't strictly need real images for the mock
    logger.info("Mock Nano Banana: Done.")
    return [f"tmp/mock_image_{i}.jpg" for i in range(len(prompts))]

async def generate_video_mock(image_path: str, style: str) -> str:
    """Mock Veo 3: Turns an image into an 8-second video."""
    logger.info("Mock Veo: Generating video from image...")
    await asyncio.sleep(4)
    # Create a simple 8-second color clip using moviepy
    filepath = f"tmp/mock_veo_video.mp4"
    try:
        clip = ColorClip(size=(640, 480), color=(50, 50, 200), duration=8)
        clip.write_videofile(filepath, fps=24, logger=None)
        logger.info(f"Mock Veo: Done. Saved to {filepath}")
    except Exception as e:
        logger.error(f"Failed to create mock video: {e}")
        # fallback
    return filepath

async def generate_music_mock(bpm: int, vibe: str) -> str:
    """Mock Lyria 3: Generates synced soundtrack."""
    logger.info(f"Mock Lyria: Generating music ({bpm} BPM, {vibe})...")
    await asyncio.sleep(3)
    
    filepath = "tmp/mock_lyria_audio.mp3"
    try:
        # Create 8 seconds of silence or a simple tone
        duration = 8  # seconds
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio_array = np.sin(440 * 2 * np.pi * t) * 0.3
        
        # Need stereo
        stereo_array = np.column_stack((audio_array, audio_array))
        clip = AudioArrayClip(stereo_array, fps=sample_rate)
        clip.write_audiofile(filepath, logger=None)
        logger.info(f"Mock Lyria: Done. Saved to {filepath}")
    except Exception as e:
        logger.error(f"Failed to create mock audio: {e}")

    return filepath

async def generate_tts_mock(narration: str) -> str:
    """Mock TTS: Generates voice narration."""
    logger.info(f"Mock TTS: Generating narration: {narration[:20]}...")
    await asyncio.sleep(2)
    filepath = "tmp/mock_tts_audio.mp3"
    try:
        # Create 4 seconds of a lower tone for voice
        duration = 4
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio_array = np.sin(220 * 2 * np.pi * t) * 0.5
        stereo_array = np.column_stack((audio_array, audio_array))
        clip = AudioArrayClip(stereo_array, fps=sample_rate)
        clip.write_audiofile(filepath, logger=None)
        logger.info(f"Mock TTS: Done. Saved to {filepath}")
    except Exception as e:
        logger.error(f"Failed to create mock TTS: {e}")

    return filepath
