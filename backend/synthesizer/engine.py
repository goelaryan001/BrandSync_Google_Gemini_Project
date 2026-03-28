import logging
import asyncio
import os
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip

logger = logging.getLogger(__name__)

async def synthesize_ad(task_id: str, video_path: str, audio_path: str, tts_path: str) -> str:
    """
    Merges Veo generated video with Lyria soundtrack and TTS narration.
    Saves final .mp4.
    """
    logger.info("Synthesizer: Starting video assembly...")
    output_path = f"tmp/final_synthetic_ad_{task_id}.mp4"

    def merge_media():
        # Using moviepy in a sync block, but we run it via asyncio.to_thread mapped loop wrapper if needed, 
        # or just calling inside async because moviepy isn't async itself 
        try:
            video = VideoFileClip(video_path)
            bgm = AudioFileClip(audio_path)
            tts = AudioFileClip(tts_path)

            # Lower the bgm volume
            bgm = bgm.volumex(0.3)
            
            # Start tts after 1 second
            tts = tts.set_start(1.0)
            
            # Combine audio
            final_audio = CompositeAudioClip([bgm, tts])
            
            # Attach to video
            final_video = video.set_audio(final_audio)
            
            # Write out
            final_video.write_videofile(
                output_path, 
                codec='libx264', 
                audio_codec='aac', 
                logger=None, # suppress tqdm output 
                fps=24
            )
            
            # Close clips to free resources
            video.close()
            bgm.close()
            tts.close()
            
            return output_path
        except Exception as e:
            logger.error(f"Synthesizer Engine Error: {e}")
            raise e

    # MoviePy operations are blocking, run in another thread to not freeze async loop
    await asyncio.to_thread(merge_media)
    logger.info(f"Synthesizer: Composition finished {output_path}")

    return output_path
