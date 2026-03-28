import logging
import asyncio
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip, ImageClip, CompositeVideoClip, concatenate_videoclips
import numpy as np

logger = logging.getLogger(__name__)

async def synthesize_ad(task_id: str, video_path: str, image_path: str, audio_path: str, tts_path: str) -> str:
    """
    Merges Veo generated video with Lyria soundtrack and TTS narration.
    Uses Nano Banana image as a 20-second background layer.
    """
    logger.info("Synthesizer: Starting professional 20s video assembly...")
    output_path = f"tmp/final_synthetic_ad_{task_id}.mp4"

    def merge_media():
        try:
            # Load components
            bg_image = ImageClip(image_path, duration=20).resized(width=1280)
            motion_video = VideoFileClip(video_path).resized(width=1280)
            bgm = AudioFileClip(audio_path)
            tts = AudioFileClip(tts_path)

            # 1. Video Layering & Looping
            # Ensure there is constant motion for the full 20 seconds.
            # If the AI video is 5-8s, we loop it to fill the 20s.
            if motion_video.duration < 20:
                loop_count = int(np.ceil(20 / motion_video.duration))
                motion_video = concatenate_videoclips([motion_video] * loop_count).with_duration(20)

            final_video_clip = CompositeVideoClip([bg_image, motion_video.with_position("center")])
            final_video_clip = final_video_clip.with_duration(20)

            # 2. Audio Mixing
            # Lower the bgm volume significantly so voiceover is clear
            bgm = bgm.with_volume_scaled(0.15)
            # Start tts after 1 second
            tts = tts.with_start(1.0)
            # Combine audio
            final_audio = CompositeAudioClip([bgm, tts])
            
            # Trim the combined audio to exactly 20 seconds
            if final_audio.duration > 20:
                final_audio = final_audio.subclipped(0, 20)
            
            # 3. Final Assembly
            final_video = final_video_clip.with_audio(final_audio)
            
            # Write out
            final_video.write_videofile(
                output_path, 
                codec='libx264', 
                audio_codec='aac', 
                logger=None,
                fps=24
            )
            
            # Close clips to free resources
            bg_image.close()
            motion_video.close()
            bgm.close()
            tts.close()
            
            return output_path
        except Exception as e:
            logger.error(f"Synthesizer Engine Error: {e}")
            raise e

    await asyncio.to_thread(merge_media)
    logger.info(f"Synthesizer: Composition finished {output_path}")

    return output_path
