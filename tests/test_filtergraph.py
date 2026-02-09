import zipfile
from io import BytesIO

from pycaption import SRTReader
from pycaption.filtergraph import FiltergraphWriter


class TestFiltergraphWriterTestCase:
    """Tests for the FiltergraphWriter that generates FFmpeg filtergraphs."""

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
            assert 'embedded_subs/filtergraph.txt' in names

    def test_filtergraph_structure(self):
        """Test that filtergraph uses concat demuxer via single movie filter."""
        srt_content = """1
00:00:01,000 --> 00:00:04,000
Test
"""
        caption_set = SRTReader().read(srt_content)
        zip_data = self.writer.write(caption_set)

        with zipfile.ZipFile(BytesIO(zip_data), 'r') as zf:
            filtergraph = zf.read('embedded_subs/filtergraph.txt').decode()

            # Should have color source for transparent base
            assert 'color=c=black@0:s=1920x1080' in filtergraph
            assert 'format=yuva444p' in filtergraph

            # Should use single movie filter with concat demuxer
            assert 'movie=embedded_subs/concat.txt:f=concat' in filtergraph

            # Should have single overlay to [out]
            assert '[base][subs]overlay=0:0:format=auto[out]' in filtergraph

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

            assert 'ffconcat version 1.0' in concat

            # Gap before first subtitle (1 second)
            assert 'file blank.png\nduration 1.000' in concat

            # First subtitle (3 seconds)
            assert 'file subtitle0001.png\nduration 3.000' in concat

            # Gap between subtitles (1 second)
            # After first sub ends at 4s, second starts at 5s
            lines = concat.split('\n')
            # Find the gap between subtitle0001 and subtitle0002
            idx_sub1 = next(i for i, l in enumerate(lines) if 'subtitle0001' in l)
            # After subtitle0001 duration, should be blank with 1s gap
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
            assert 'subs/filtergraph.txt' in names

            filtergraph = zf.read('subs/filtergraph.txt').decode()
            assert 'movie=subs/concat.txt:f=concat' in filtergraph

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

            # All three subtitle images referenced
            assert 'file subtitle0001.png' in concat
            assert 'file subtitle0002.png' in concat
            assert 'file subtitle0003.png' in concat

            # Filtergraph should be simple - no per-subtitle movie filters
            filtergraph = zf.read('embedded_subs/filtergraph.txt').decode()
            assert filtergraph.count('movie=') == 1  # single movie filter

    def test_duration_calculation(self):
        """Test that duration is calculated from last subtitle end time."""
        srt_content = """1
00:00:01,000 --> 00:00:04,000
First

2
00:01:30,000 --> 00:01:35,500
Last one at 1:35
"""
        caption_set = SRTReader().read(srt_content)
        zip_data = self.writer.write(caption_set)

        with zipfile.ZipFile(BytesIO(zip_data), 'r') as zf:
            filtergraph = zf.read('embedded_subs/filtergraph.txt').decode()

            # Duration should be ~96.5 seconds (95.5 + 1 buffer)
            assert 'd=96.500' in filtergraph

    def test_custom_resolution(self):
        """Test custom video resolution."""
        writer = FiltergraphWriter(video_width=1280, video_height=720)
        srt_content = """1
00:00:01,000 --> 00:00:04,000
Test
"""
        caption_set = SRTReader().read(srt_content)
        zip_data = writer.write(caption_set)

        with zipfile.ZipFile(BytesIO(zip_data), 'r') as zf:
            filtergraph = zf.read('embedded_subs/filtergraph.txt').decode()
            assert 's=1280x720' in filtergraph

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
