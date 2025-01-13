import glob
import tempfile
import unittest
import zipfile
from io import BytesIO

from pycaption import (ScenaristDVDWriter, DFXPReader, SRTReader)


class TestScenaristDVDWriterTestCase:

    def setup_class(self):
        self.writer = ScenaristDVDWriter()

    def test_arabic(self, sample_srt_arabic):
        caption_set = SRTReader().read(sample_srt_arabic, lang='ar')
        results = self.writer.write(caption_set)
        with tempfile.TemporaryDirectory() as tmpDir:
            with zipfile.ZipFile(BytesIO(results), 'r') as zip_ref:
                zip_ref.extractall(tmpDir)
                print(tmpDir)
                assert len(glob.glob(tmpDir + '/*.sst')) == 1
                assert len(glob.glob(tmpDir + '/*.tif')) == 4

    def test_styling(self, sample_dfxp_from_sami_with_positioning):
        caption_set = DFXPReader().read(sample_dfxp_from_sami_with_positioning)
        results = self.writer.write(caption_set)
        with tempfile.TemporaryDirectory() as tmpDir:
            with zipfile.ZipFile(BytesIO(results), 'r') as zip_ref:
                zip_ref.extractall(tmpDir)
                assert len(glob.glob(tmpDir + '/*.sst')) == 1
                assert len(glob.glob(tmpDir + '/*.tif')) == 7
