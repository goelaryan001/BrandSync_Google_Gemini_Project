import asyncio
import logging
import os
import numpy as np
from moviepy import ColorClip, AudioArrayClip
from typing import List
import aiohttp

logger = logging.getLogger(__name__)

# Ensure tmp directory exists
os.makedirs("tmp", exist_ok=True)

from google import genai
from google.genai import types

async def generate_images_mock(prompts: List[str]) -> List[str]:
    """Generates candidate images using Nano Banana via generate_content."""
    logger.info("Nano Banana: Generating images...")
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        client = genai.Client(api_key=api_key)
        
        filepaths = []
        for i, prompt in enumerate(prompts):
            # Nano-banana-pro-preview generates images through generate_content
            response = await asyncio.to_thread(
                client.models.generate_content,
                model='nano-banana-pro-preview',
                contents=prompt
            )
            
            filepath = f"tmp/nano_banana_image_{i}.png"
            # Extract inline_data bytes from the model response parts
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'inline_data') and getattr(part, 'inline_data', None):
                    image_bytes = part.inline_data.data
                    with open(filepath, "wb") as f:
                        f.write(image_bytes)
                    break
                    
            filepaths.append(filepath)
            
        logger.info("Nano Banana: Done.")
        return filepaths
    except Exception as e:
        logger.error(f"Image generation failed: {e}. Returning mock.")
        return [f"tmp/mock_image_{i}.jpg" for i in range(len(prompts))]

async def generate_video_mock(image_path: str, style: str, hero_product: str) -> str:
    """Generates video using Veo 3.0 based on the image style."""
    logger.info(f"Veo 3: Generating video for {hero_product}...")
    filepath = f"tmp/veo_video.mp4"
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        client = genai.Client(api_key=api_key)
        
        prompt = f"Make this image move cinematically featuring a {hero_product} in the style of: {style}"
        
        response = await asyncio.to_thread(
            client.models.generate_videos,
            model='veo-3.0-generate-001',
            prompt=prompt
        )
        
        # Poll operation
        operation = response
        logger.info("Veo: Waiting for operation to complete in the cloud...")
        max_retries = 60 # roughly 5 minutes for video
        retries = 0
        done = False
        uri = None
        
        while retries < max_retries:
            op_dict = operation.to_json_dict()
            if op_dict.get('done') is True:
                done = True
                uri = op_dict.get('response', {}).get('generated_videos', [{}])[0].get('video', {}).get('uri')
                break
            await asyncio.sleep(5)
            operation = await asyncio.to_thread(client.operations.get, operation=operation)
            retries += 1
            
        if done and uri:
            logger.info(f"Veo 3: Done generating! Downloading remote cloud file...")
            # Download the MP4 bytes from the googleapis URI silently ignoring SSL 
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
                headers = {'x-goog-api-key': api_key}
                # Double-down on auth by passing key as a parameter as well to avoid 403 Forbidden
                download_url = f"{uri}&key={api_key}" if "?" in uri else f"{uri}?key={api_key}"
                async with session.get(download_url, headers=headers) as dl_res:
                    dl_res.raise_for_status()
                    with open(filepath, "wb") as f:
                        f.write(await dl_res.read())
            logger.info(f"Veo 3: Download complete. Saved to {filepath}")
            return filepath
        else:
            raise Exception(f"Operation failed or timed out. Last API State: {op_dict}")
            
    except Exception as e:
        logger.error(f"Veo generation failed: {e}. Falling back to an Image-based mock video sequence.")
        
    # Stunning Fallback: Convert the Nano Banana still image into a functional 20-second video
    # This completely eliminates "Blue Screens" forever even if Veo quotas fail.
    try:
        from moviepy import ImageClip
        # If image_path exists, use it. Otherwise colorclip.
        if os.path.exists(image_path):
            clip = ImageClip(image_path, duration=20)
            clip = clip.resized(width=1280) # standardize width
            clip.write_videofile(filepath, fps=24, codec='libx264', logger=None)
        else:
            clip = ColorClip(size=(640, 480), color=(50, 50, 200), duration=20)
            clip.write_videofile(filepath, fps=24, logger=None)
    except Exception as fallback_e:
        logger.error(f"Veo gorgeous image fallback failed: {fallback_e}")
        
    return filepath

async def generate_music_mock(bpm: int, vibe: str) -> str:
    """Generates a real synced soundtrack using Lyria 3."""
    logger.info(f"Lyria 3: Generating music ({bpm} BPM, {vibe})...")
    filepath = "tmp/mock_lyria_audio.mp3"
    
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        client = genai.Client(api_key=api_key)
        
        prompt = f"STRICTLY INSTRUMENTAL ONLY, No singers, No human voices, No vocals, Instrumental background music only, happy corporate music, {bpm} BPM, {vibe}"
        response = await asyncio.to_thread(
            client.models.generate_content,
            model='lyria-3-pro-preview',
            contents=prompt
        )
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'inline_data') and getattr(part, 'inline_data', None):
                audio_bytes = part.inline_data.data
                with open(filepath, "wb") as f:
                    f.write(audio_bytes)
                logger.info(f"Lyria 3: Done. Saved to {filepath}")
                return filepath
                
        raise Exception("Lyria returned successfully but no audio inline_data was found.")
    except Exception as e:
        logger.error(f"Lyria 3 failed to create audio: {e}. Falling back to ambient pad.")

    # Only fall back to ambient pad if Lyria 3 totally breaks
    try:
        duration = 20  # seconds
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio_array = (np.sin(150 * 2 * np.pi * t) * 0.1) + (np.sin(300 * 2 * np.pi * t) * 0.05)
        stereo_array = np.column_stack((audio_array, audio_array))
        clip = AudioArrayClip(stereo_array, fps=sample_rate)
        clip.write_audiofile(filepath, logger=None)
    except Exception as e:
        logger.error(f"Ambient pad fallback failed: {e}")

    return filepath

async def generate_tts_mock(narration: str) -> str:
    """Generates real voice narration using gTTS."""
    logger.info(f"TTS Engine: Generating narration: {narration[:20]}...")
    filepath = "tmp/mock_tts_audio.mp3"
    try:
        import gtts
        def save_tts():
            tts = gtts.gTTS(text=narration, lang='en')
            tts.save(filepath)
        await asyncio.to_thread(save_tts)
        logger.info(f"TTS Engine: Done. Saved real voice to {filepath}")
    except ImportError:
            logger.error("gTTS not installed, generating empty audio.")
            duration = 4
            t = np.linspace(0, duration, int(44100 * duration))
            array = np.zeros_like(t)
            AudioArrayClip(np.column_stack((array, array)), fps=44100).write_audiofile(filepath, logger=None)
    except Exception as e:
        logger.error(f"Failed to create TTS: {e}")

    return filepath
