import tempfile
import zipfile
from io import BytesIO

from pycaption.base import CaptionSet
from pycaption.subtitler_image_based import SubtitleImageBasedWriter


class FiltergraphWriter(SubtitleImageBasedWriter):
    """
    FFmpeg filtergraph writer for image-based subtitles.

    Generates PNG subtitle images and an FFmpeg filtergraph that can be used
    to create a transparent WebM video with subtitle overlays.

    By default, generates Full HD (1920x1080) images. The filtergraph uses
    the overlay filter with timing to display each subtitle at the correct time.

    Uses PNG format for images with 4-color indexed palette for optimal
    compression (~6 KB per Full HD image).
    """

    def __init__(self, relativize=True, video_width=1920, video_height=1080,
                 fit_to_screen=True, frame_rate=25):
        """
        Initialize the filtergraph writer.

        :param relativize: Convert absolute positioning to percentages
        :param video_width: Width of generated subtitle images (default: 1920 for Full HD)
        :param video_height: Height of generated subtitle images (default: 1080 for Full HD)
        :param fit_to_screen: Ensure captions fit within screen bounds
        :param frame_rate: Frame rate for timing calculations
        """
        super().__init__(relativize, video_width, video_height, fit_to_screen, frame_rate)

    def save_image(self, tmp_dir, index, img):
        """Save subtitle image as optimized PNG with transparency."""
        img.save(
            tmp_dir + '/subtitle%04d.png' % index,
            transparency=3,
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
            align='center',
            output_dir='embedded_subs'
    ):
        """
        Write captions as PNG images with an FFmpeg filtergraph for creating
        a transparent WebM video overlay.

        Returns a ZIP file containing:
        - PNG subtitle images in the specified image_dir
        - filtergraph.txt: FFmpeg filter_complex script

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

            # Calculate total duration (last end time)
            max_end = max(cap_list[0].end for cap_list in caps_final)
            duration_seconds = max_end / 1_000_000 + 1  # Add 1 second buffer

            # Build FFmpeg filtergraph
            # Start with transparent base
            filter_parts = []
            filter_parts.append(
                f"color=c=black@0:s={self.video_width}x{self.video_height}:d={duration_seconds:.3f},format=yuva420p[base]"
            )

            # Load each image
            for i in range(1, len(caps_final) + 1):
                filter_parts.append(
                    f"movie={output_dir}/subtitle{i:04d}.png,format=yuva420p[s{i}]"
                )

            # Chain overlays
            prev_label = "base"
            for i, cap_list in enumerate(caps_final, 1):
                start_sec = self.format_ts_seconds(cap_list[0].start)
                end_sec = self.format_ts_seconds(cap_list[0].end)
                next_label = f"v{i}" if i < len(caps_final) else "out"

                filter_parts.append(
                    f"[{prev_label}][s{i}]overlay=x=0:y=0:enable='between(t,{start_sec},{end_sec})':format=auto[{next_label}]"
                )
                prev_label = next_label

            filtergraph = ";\n".join(filter_parts)


            # Create ZIP archive
            with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
                # Add images
                for i in range(1, len(caps_final) + 1):
                    img_path = tmpDir + '/subtitle%04d.png' % i
                    zf.write(img_path, f'{output_dir}/subtitle{i:04d}.png')

                # Add filtergraph
                zf.writestr('filtergraph.txt', filtergraph)


        buf.seek(0)
        return buf.read()
