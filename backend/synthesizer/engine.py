import logging
import asyncio
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip, ImageClip, CompositeVideoClip, concatenate_videoclips
import numpy as np

logger = logging.getLogger(__name__)

async def synthesize_ad(task_id: str, video_path: str, image_path: str, audio_path: str, tts_path: str, overlay_paths: list) -> str:
    """
    Professional Sequential Ad: 12s Motion -> 8s Hero Reveal + Dynamic Text Overlays.
    """
    logger.info("Synthesizer: Starting professional 20s Sequence Reveal...")
    output_path = f"tmp/final_synthetic_ad_{task_id}.mp4"

    def merge_media():
        try:
            # 1. Load Components
            bg_image = ImageClip(image_path, duration=8).resized(width=1280)
            motion_clip_raw = VideoFileClip(video_path).resized(width=1280)
            bgm = AudioFileClip(audio_path)
            tts = AudioFileClip(tts_path)

            # 2. Sequence Assembly (12s Motion | 8s Image)
            # Loop motion clip to exactly 12 seconds
            loop_count = int(np.ceil(12 / motion_clip_raw.duration))
            motion_video = concatenate_videoclips([motion_clip_raw] * loop_count).with_duration(12)
            
            # The Hero image starts at 12s and lasts until 20s
            hero_reval = bg_image.with_start(12).with_duration(8).with_position("center")
            
            # 3. Dynamic Text Overlays (Slideshow effect)
            text_layers = []
            timings = [(1, 4), (5, 8), (9, 12)] # Start, End for each punchline
            for i, path in enumerate(overlay_paths[:3]):
                start, end = timings[i]
                txt = ImageClip(path).with_start(start).with_duration(end - start).with_position("center")
                text_layers.append(txt)

            # 4. Composite Video
            # Base logic: [Motion Video at start, Hero Reveal at 12s] + Text layers
            final_video_clip = CompositeVideoClip(
                [motion_video] + [hero_reval] + text_layers,
                size=(1280, 720)
            ).with_duration(20)

            # 5. Audio Mixing
            bgm = bgm.with_volume_scaled(0.15)
            tts = tts.with_start(1.0)
            final_audio = CompositeAudioClip([bgm, tts])
            
            if final_audio.duration > 20:
                final_audio = final_audio.subclipped(0, 20)
            
            # 6. Final Export
            final_video = final_video_clip.with_audio(final_audio)
            final_video.write_videofile(
                output_path, 
                codec='libx264', 
                audio_codec='aac', 
                logger=None,
                fps=24
            )
            
            # Cleanup
            bg_image.close()
            motion_clip_raw.close()
            bgm.close()
            tts.close()
            for tx in text_layers: tx.close()
            
            return output_path
        except Exception as e:
            logger.error(f"Synthesizer Engine Error: {e}")
            raise e

    await asyncio.to_thread(merge_media)
    logger.info(f"Synthesizer: Sequence Reveal finished {output_path}")

    return output_path
