import base64
import re

from pycaption import (DFXPReader, SRTReader)
from pycaption.ttml_background import TTMLBackgroundWriter


class TestTTMLBackgroundWriterTestCase:

    def setup_class(self):
        self.writer = TTMLBackgroundWriter()

    def _validate_ttml_structure(self, results, expected_num_images, expected_timings):
        """Validate TTML structure and content."""
        # Check XML header and namespaces
        assert "<?xml version='1.0' encoding='UTF-8'?>" in results
        assert 'xmlns:smpte="http://www.smpte-ra.org/schemas/2052-1/2010/smpte-tt"' in results
        assert 'ttp:profile="http://www.w3.org/ns/ttml/profile/imsc1/image"' in results

        # Check for correct number of images
        image_pattern = r'<smpte:image imageType="PNG" encoding="Base64" xml:id="img_(\d+)">(.*?)</smpte:image>'
        images = re.findall(image_pattern, results, re.DOTALL)
        assert len(images) == expected_num_images, f"Expected {expected_num_images} images, got {len(images)}"

        # Verify each image is valid base64 PNG
        for img_id, img_data in images:
            try:
                decoded = base64.b64decode(img_data)
                # Check PNG magic bytes
                assert decoded[:8] == b'\x89PNG\r\n\x1a\n', f"Image {img_id} is not a valid PNG"
            except Exception as e:
                raise AssertionError(f"Image {img_id} is not valid base64: {e}")

        # Check for correct div elements with timing
        div_pattern = r'<div region="r1" begin="([^"]+)" end="([^"]+)" smpte:backgroundImage="#img_(\d+)"/>'
        divs = re.findall(div_pattern, results)
        assert len(divs) == expected_num_images, f"Expected {expected_num_images} divs, got {len(divs)}"

        # Verify timings
        for i, (begin, end, img_id) in enumerate(divs):
            expected_begin, expected_end = expected_timings[i]
            assert begin == expected_begin, f"Div {i+1}: expected begin={expected_begin}, got {begin}"
            assert end == expected_end, f"Div {i+1}: expected end={expected_end}, got {end}"
            assert img_id == str(i + 1), f"Div {i+1}: expected img_id={i+1}, got {img_id}"

    def test_arabic(self, sample_srt_arabic):
        caption_set = SRTReader().read(sample_srt_arabic, lang='ar')
        results = self.writer.write(caption_set)

        expected_timings = [
            ("00:00:40.000", "00:00:43.250"),
            ("00:00:44.542", "00:00:49.500"),
            ("00:00:51.125", "00:00:54.417"),
            ("00:00:55.292", "00:00:58.917"),
        ]
        self._validate_ttml_structure(results, 4, expected_timings)

    def test_styling(self, sample_dfxp_from_sami_with_positioning):
        caption_set = DFXPReader().read(sample_dfxp_from_sami_with_positioning)
        results = self.writer.write(caption_set)

        expected_timings = [
            ("00:00:09.209", "00:00:12.312"),
            ("00:00:14.848", "00:00:17.000"),
            ("00:00:17.000", "00:00:18.752"),
            ("00:00:18.752", "00:00:20.887"),
            ("00:00:20.887", "00:00:26.760"),
            ("00:00:26.760", "00:00:32.200"),
            ("00:00:32.200", "00:00:36.200"),
        ]
        self._validate_ttml_structure(results, 7, expected_timings)

    def test_simple_srt(self):
        """Test basic SRT conversion to TTML with images."""
        srt_content = """1
00:00:01,000 --> 00:00:04,000
Hello World

2
00:00:05,000 --> 00:00:08,000
Second subtitle
"""
        caption_set = SRTReader().read(srt_content)
        results = self.writer.write(caption_set)

        expected_timings = [
            ("00:00:01.000", "00:00:04.000"),
            ("00:00:05.000", "00:00:08.000"),
        ]
        self._validate_ttml_structure(results, 2, expected_timings)

    def test_image_transparency(self):
        """Test that generated images have proper transparency (index 3)."""
        srt_content = """1
00:00:01,000 --> 00:00:04,000
Test
"""
        caption_set = SRTReader().read(srt_content)
        results = self.writer.write(caption_set)

        # Extract image
        image_pattern = r'<smpte:image[^>]*>(.*?)</smpte:image>'
        match = re.search(image_pattern, results, re.DOTALL)
        assert match is not None

        # Decode and verify it's a PNG
        decoded = base64.b64decode(match.group(1))
        assert decoded[:8] == b'\x89PNG\r\n\x1a\n'
