import tempfile
import zipfile
from io import BytesIO

from PIL import Image

from pycaption.base import CaptionSet
from pycaption.subtitler_image_based import SubtitleImageBasedWriter


class FiltergraphWriter(SubtitleImageBasedWriter):
    """
    FFmpeg subtitle image writer using concat demuxer.

    Generates PNG subtitle images and an FFmpeg concat demuxer file that
    sequences blank (transparent) and subtitle images with proper timing.
    The concat file can be fed directly to ffmpeg as an input.

    By default, generates Full HD (1920x1080) images.

    Uses PNG format for images with 4-color indexed palette for optimal
    compression (~6 KB per Full HD image).
    """

    def __init__(self, relativize=True, video_width=1920, video_height=1080,
                 fit_to_screen=True, frame_rate=25, output_dir=None):
        """
        Initialize the filtergraph writer.

        :param relativize: Convert absolute positioning to percentages
        :param video_width: Width of generated subtitle images (default: 1920 for Full HD)
        :param video_height: Height of generated subtitle images (default: 1080 for Full HD)
        :param fit_to_screen: Ensure captions fit within screen bounds
        :param frame_rate: Frame rate for timing calculations
        """
        if output_dir is None:
            self.output_dir = 'embedded_subs'
        else:
            self.output_dir = output_dir
        super().__init__(relativize, video_width, video_height, fit_to_screen, frame_rate)

    def save_image(self, tmp_dir, index, img):
        """Save RGBA image as PNG with transparency."""
        img.save(
            tmp_dir + '/subtitle%04d.png' % index,
            optimize=True,
            compress_level=9
        )

    def format_ts_seconds(self, value):
        """
        Format timestamp as seconds with 3 decimal places for FFmpeg.

        :param value: Time in microseconds
        :return: Seconds as float string
        """
        return f"{value / 1_000_000:.3f}"

    def write(
            self,
            caption_set: CaptionSet,
            position='bottom',
            avoid_same_next_start_prev_end=False,
            align='center'
    ):
        """
        Write captions as PNG images with an FFmpeg concat demuxer file.

        Returns a ZIP file containing:
        - PNG subtitle images in the specified output_dir
        - blank.png: Transparent image for gaps between subtitles
        - concat.txt: FFmpeg concat demuxer file with timing

        The concat.txt can be used directly as ffmpeg input:
            ffmpeg -f concat -safe 0 -i {output_dir}/concat.txt ...

        :param caption_set: CaptionSet containing the captions to write
        :param position: Position of subtitles ('top', 'bottom', 'source')
        :param avoid_same_next_start_prev_end: Adjust timing to avoid overlaps
        :param align: Text alignment ('left', 'center', 'right')
        :return: ZIP file contents as bytes
        """
        lang = caption_set.get_languages().pop()
        caps = caption_set.get_captions(lang)

        buf = BytesIO()
        with tempfile.TemporaryDirectory() as tmpDir:
            caps_final, overlapping = self.write_images(
                caps, lang, tmpDir, position, align, avoid_same_next_start_prev_end
            )

            # Create blank transparent image for gaps between subtitles
            blank = Image.new('RGBA', (self.video_width, self.video_height), (0, 0, 0, 0))
            blank.save(tmpDir + '/blank.png', optimize=True, compress_level=9)

            # Build concat demuxer file that sequences blank/subtitle images
            concat_lines = ['ffconcat version 1.0']
            prev_end_us = 0
            for i, cap_list in enumerate(caps_final, 1):
                start_us = cap_list[0].start
                end_us = cap_list[0].end

                # Gap before this subtitle
                gap_us = start_us - prev_end_us
                if gap_us > 0:
                    concat_lines.append('file blank.png')
                    concat_lines.append(f'duration {gap_us / 1_000_000:.3f}')

                # Subtitle image
                concat_lines.append(f'file subtitle{i:04d}.png')
                concat_lines.append(f'duration {(end_us - start_us) / 1_000_000:.3f}')

                prev_end_us = end_us

            # Trailing blank so the last subtitle doesn't freeze on screen
            concat_lines.append('file blank.png')
            concat_text = '\n'.join(concat_lines)

            # Create ZIP archive
            with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
                # Add images
                for i in range(1, len(caps_final) + 1):
                    img_path = tmpDir + '/subtitle%04d.png' % i
                    zf.write(img_path, f'{self.output_dir}/subtitle{i:04d}.png')

                # Add blank image and concat file
                zf.write(tmpDir + '/blank.png', f'{self.output_dir}/blank.png')
                zf.writestr(f'{self.output_dir}/concat.txt', concat_text)

        buf.seek(0)
        return buf.read()
