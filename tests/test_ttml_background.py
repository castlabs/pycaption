from pycaption import (DFXPReader, SRTReader)
from pycaption.ttml_background import TTMLBackgroundWriter


class TestTTMLBackgroundWriterTestCase:

    def setup_class(self):
        self.writer = TTMLBackgroundWriter()

    def test_arabic(self, sample_srt_arabic):
        caption_set = SRTReader().read(sample_srt_arabic, lang='ar')
        results = self.writer.write(caption_set)
        print(results)

    def test_styling(self, sample_dfxp_from_sami_with_positioning):
        caption_set = DFXPReader().read(sample_dfxp_from_sami_with_positioning)
        results = self.writer.write(caption_set)
        print(results)
