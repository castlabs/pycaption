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
            assert 'embedded_subs/filtergraph.txt' in names

    def test_filtergraph_structure(self):
        """Test that filtergraph has correct structure."""
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

            # Should have movie input for image (path relative to ffmpeg working dir)
            assert 'movie=embedded_subs/subtitle0001.png' in filtergraph

            # Should have overlay with timing
            assert 'overlay=x=0:y=0:enable=' in filtergraph
            assert "between(t,1.000,4.000)" in filtergraph

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
            assert 'subs/filtergraph.txt' in names

            filtergraph = zf.read('subs/filtergraph.txt').decode()
            assert 'movie=subs/subtitle0001.png' in filtergraph

    def test_multiple_overlays_chained(self):
        """Test that multiple subtitles are chained correctly."""
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
            filtergraph = zf.read('embedded_subs/filtergraph.txt').decode()

            # Should have 3 movie inputs
            assert 'movie=embedded_subs/subtitle0001.png' in filtergraph
            assert 'movie=embedded_subs/subtitle0002.png' in filtergraph
            assert 'movie=embedded_subs/subtitle0003.png' in filtergraph

            # Should have chained overlays
            assert '[base][s1]overlay' in filtergraph
            assert '[v1][s2]overlay' in filtergraph
            assert '[v2][s3]overlay' in filtergraph

            # Last one should output to [out]
            assert '[out]' in filtergraph

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
