import re

from pycaption import DFXPReader, SRTReader
from pycaption.ass import ASSWriter


class TestASSWriterTestCase:

    def setup_method(self):
        self.writer = ASSWriter()

    def test_basic_output_structure(self):
        """Test that basic ASS structure is correct."""
        srt_content = """1
00:00:01,000 --> 00:00:04,000
Hello World
"""
        caption_set = SRTReader().read(srt_content)
        results = self.writer.write(caption_set)

        # Check for required sections
        assert '[Script Info]' in results
        assert '[V4+ Styles]' in results
        assert '[Graphics]' in results
        assert '[Events]' in results

    def test_script_info_section(self):
        """Test Script Info section contains correct metadata."""
        srt_content = """1
00:00:01,000 --> 00:00:04,000
Test
"""
        caption_set = SRTReader().read(srt_content)
        results = self.writer.write(caption_set)

        assert 'ScriptType: v4.00+' in results
        assert 'PlayResX: 1920' in results
        assert 'PlayResY: 1080' in results

    def test_custom_resolution(self):
        """Test custom video resolution."""
        writer = ASSWriter(video_width=1280, video_height=720)
        srt_content = """1
00:00:01,000 --> 00:00:04,000
Test
"""
        caption_set = SRTReader().read(srt_content)
        results = writer.write(caption_set)

        assert 'PlayResX: 1280' in results
        assert 'PlayResY: 720' in results

    def test_custom_title(self):
        """Test custom title in Script Info."""
        writer = ASSWriter(title='My Custom Title')
        srt_content = """1
00:00:01,000 --> 00:00:04,000
Test
"""
        caption_set = SRTReader().read(srt_content)
        results = writer.write(caption_set)

        assert 'Title: My Custom Title' in results

    def test_graphics_section_contains_images(self):
        """Test that Graphics section contains embedded PNG images."""
        srt_content = """1
00:00:01,000 --> 00:00:04,000
Hello World
"""
        caption_set = SRTReader().read(srt_content)
        results = self.writer.write(caption_set)

        # Check for embedded image
        assert 'filename: subtitle0001.png' in results
        # Check for base64 PNG header (iVBORw0KGgo is base64 for PNG magic bytes)
        assert 'iVBORw0KGgo' in results

    def test_events_section_has_picture_events(self):
        """Test that Events section contains Picture events."""
        srt_content = """1
00:00:01,000 --> 00:00:04,000
Hello World

2
00:00:05,000 --> 00:00:08,000
Second subtitle
"""
        caption_set = SRTReader().read(srt_content)
        results = self.writer.write(caption_set)

        # Check for Picture events
        assert 'Picture: 0,0:00:01.00,0:00:04.00' in results
        assert 'Picture: 0,0:00:05.00,0:00:08.00' in results
        assert 'subtitle0001.png' in results
        assert 'subtitle0002.png' in results

    def test_timestamp_format(self):
        """Test ASS timestamp format (H:MM:SS.cc)."""
        srt_content = """1
01:23:45,670 --> 02:34:56,780
Test
"""
        caption_set = SRTReader().read(srt_content)
        results = self.writer.write(caption_set)

        # ASS uses centiseconds, so 670ms -> 67cs, 780ms -> 78cs
        assert '1:23:45.67' in results
        assert '2:34:56.78' in results

    def test_arabic(self, sample_srt_arabic):
        """Test Arabic subtitle rendering."""
        caption_set = SRTReader().read(sample_srt_arabic, lang='ar')
        results = self.writer.write(caption_set)

        # Should have 4 images for 4 captions
        assert results.count('filename: subtitle') == 4
        assert '[Graphics]' in results
        assert '[Events]' in results

    def test_styling(self, sample_dfxp_from_sami_with_positioning):
        """Test subtitle with positioning."""
        caption_set = DFXPReader().read(sample_dfxp_from_sami_with_positioning)
        results = self.writer.write(caption_set)

        # Should have images for each caption
        assert 'filename: subtitle0001.png' in results
        assert '[Events]' in results

    def test_multiple_captions_same_start_time(self):
        """Test handling of multiple captions with same start time."""
        srt_content = """1
00:00:01,000 --> 00:00:04,000
First line

2
00:00:01,000 --> 00:00:04,000
Second line (same time)
"""
        caption_set = SRTReader().read(srt_content)
        results = self.writer.write(caption_set)

        # Both captions with same time should be combined into one image
        # So we should only have one Picture event at 0:00:01.00
        picture_count = results.count('Picture: 0,0:00:01.00')
        assert picture_count == 1

    def test_image_count_matches_caption_groups(self):
        """Test that number of images matches number of unique time slots."""
        srt_content = """1
00:00:01,000 --> 00:00:04,000
First

2
00:00:05,000 --> 00:00:08,000
Second

3
00:00:10,000 --> 00:00:13,000
Third
"""
        caption_set = SRTReader().read(srt_content)
        results = self.writer.write(caption_set)

        # Should have 3 images
        assert results.count('filename: subtitle') == 3
        # Should have 3 Picture events
        assert results.count('Picture: 0,') == 3

    def test_full_screen_positioning(self):
        """Test that Picture events have full-screen positioning."""
        srt_content = """1
00:00:01,000 --> 00:00:04,000
Test
"""
        caption_set = SRTReader().read(srt_content)
        results = self.writer.write(caption_set)

        # Picture event should have positioning: x=0, y=0, scalex=100, scaley=100
        # Format: Picture: layer,start,end,style,name,marginL,marginR,marginV,effect,filename,x,y,scalex,scaley,fsp
        assert ',0,0,100,100,0' in results

    def test_styles_have_zero_margins(self):
        """Test that default style has zero margins for full-screen images."""
        srt_content = """1
00:00:01,000 --> 00:00:04,000
Test
"""
        caption_set = SRTReader().read(srt_content)
        results = self.writer.write(caption_set)

        # Style line should end with 0,0,0,1 (MarginL, MarginR, MarginV, Encoding)
        assert ',0,0,0,1' in results
