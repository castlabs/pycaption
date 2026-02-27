import zipfile
from io import BytesIO

from pycaption import SRTReader
from pycaption.filtergraph import FiltergraphWriter


class TestFiltergraphWriterTestCase:
    """Tests for the FiltergraphWriter that generates FFmpeg concat demuxer files."""

    def setup_method(self):
        self.writer = FiltergraphWriter()

    def test_zip_contents(self):
        """Test that write returns a ZIP with correct contents."""
        srt_content = """1
00:00:01,000 --> 00:00:04,000
Hello World

2
00:00:05,000 --> 00:00:08,000
Second subtitle
"""
        caption_set = SRTReader().read(srt_content)
        zip_data = self.writer.write(caption_set)

        with zipfile.ZipFile(BytesIO(zip_data), 'r') as zf:
            names = zf.namelist()
            assert 'embedded_subs/subtitle0001.png' in names
            assert 'embedded_subs/subtitle0002.png' in names
            assert 'embedded_subs/blank.png' in names
            assert 'embedded_subs/concat.txt' in names

    def test_concat_header(self):
        """Test that concat file starts with ffconcat header."""
        srt_content = """1
00:00:01,000 --> 00:00:04,000
Test
"""
        caption_set = SRTReader().read(srt_content)
        zip_data = self.writer.write(caption_set)

        with zipfile.ZipFile(BytesIO(zip_data), 'r') as zf:
            concat = zf.read('embedded_subs/concat.txt').decode()
            assert concat.startswith('ffconcat version 1.0')

    def test_concat_file_structure(self):
        """Test that concat demuxer file has correct timing entries."""
        srt_content = """1
00:00:01,000 --> 00:00:04,000
First

2
00:00:05,000 --> 00:00:08,000
Second
"""
        caption_set = SRTReader().read(srt_content)
        zip_data = self.writer.write(caption_set)

        with zipfile.ZipFile(BytesIO(zip_data), 'r') as zf:
            concat = zf.read('embedded_subs/concat.txt').decode()

            # Gap before first subtitle (1 second)
            assert 'file blank.png\nduration 1.000' in concat

            # First subtitle (3 seconds)
            assert 'file subtitle0001.png\nduration 3.000' in concat

            # Gap between subtitles (1 second)
            lines = concat.split('\n')
            idx_sub1 = next(i for i, l in enumerate(lines) if 'subtitle0001' in l)
            assert lines[idx_sub1 + 2] == 'file blank.png'
            assert lines[idx_sub1 + 3] == 'duration 1.000'

            # Second subtitle (3 seconds)
            assert 'file subtitle0002.png\nduration 3.000' in concat

            # Trailing blank at the end
            assert lines[-1] == 'file blank.png'

    def test_custom_output_dir(self):
        """Test custom output directory."""
        writer = FiltergraphWriter(output_dir='subs')
        srt_content = """1
00:00:01,000 --> 00:00:04,000
Test
"""
        caption_set = SRTReader().read(srt_content)
        zip_data = writer.write(caption_set)

        with zipfile.ZipFile(BytesIO(zip_data), 'r') as zf:
            names = zf.namelist()
            assert 'subs/subtitle0001.png' in names
            assert 'subs/blank.png' in names
            assert 'subs/concat.txt' in names

    def test_multiple_subtitles_in_concat(self):
        """Test that multiple subtitles produce correct concat entries."""
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
        zip_data = self.writer.write(caption_set)

        with zipfile.ZipFile(BytesIO(zip_data), 'r') as zf:
            concat = zf.read('embedded_subs/concat.txt').decode()

            assert 'file subtitle0001.png' in concat
            assert 'file subtitle0002.png' in concat
            assert 'file subtitle0003.png' in concat

    def test_custom_resolution(self):
        """Test custom video resolution produces correctly sized images."""
        writer = FiltergraphWriter(video_width=1280, video_height=720)
        srt_content = """1
00:00:01,000 --> 00:00:04,000
Test
"""
        caption_set = SRTReader().read(srt_content)
        zip_data = writer.write(caption_set)

        with zipfile.ZipFile(BytesIO(zip_data), 'r') as zf:
            # Verify blank image has correct dimensions
            from PIL import Image
            blank_data = zf.read('embedded_subs/blank.png')
            img = Image.open(BytesIO(blank_data))
            assert img.size == (1280, 720)

    def test_back_to_back_subtitles_no_gap(self):
        """Test subtitles with no gap between them produce no blank entry."""
        srt_content = """1
00:00:01,000 --> 00:00:04,000
First

2
00:00:04,000 --> 00:00:07,000
Immediately after
"""
        caption_set = SRTReader().read(srt_content)
        zip_data = self.writer.write(caption_set)

        with zipfile.ZipFile(BytesIO(zip_data), 'r') as zf:
            concat = zf.read('embedded_subs/concat.txt').decode()
            lines = concat.split('\n')

            # Find subtitle0001 line
            idx_sub1 = next(i for i, l in enumerate(lines) if 'subtitle0001' in l)
            # Next file entry should be subtitle0002 directly (no blank in between)
            assert lines[idx_sub1 + 2] == 'file subtitle0002.png'

    def test_subtitle_starting_at_zero(self):
        """Test subtitle starting at time 0 produces no leading blank."""
        srt_content = """1
00:00:00,000 --> 00:00:03,000
Starts immediately
"""
        caption_set = SRTReader().read(srt_content)
        zip_data = self.writer.write(caption_set)

        with zipfile.ZipFile(BytesIO(zip_data), 'r') as zf:
            concat = zf.read('embedded_subs/concat.txt').decode()
            lines = concat.split('\n')

            # First file entry should be the subtitle, not blank
            assert lines[1] == 'file subtitle0001.png'