import pytest

from pycaption.exceptions import InvalidInputError
from pycaption.pl_stt import PLSTTReader

from tests.fixtures.pl_stt import (
    SAMPLE_PL_STT,
    SAMPLE_PL_STT_NO_HEADER,
    SAMPLE_PL_STT_BAD_HEADER_1,
)
from tests.mixins import ReaderTestingMixIn


class TestPLSTTReader(ReaderTestingMixIn):

    def setup_class(self):
        self.reader = PLSTTReader()

    def test_positive_answer_for_detection(self):
        assert self.reader.detect(SAMPLE_PL_STT)

    def test_negative_answer_for_detection(self, sample_srt):
        assert not self.reader.detect(sample_srt)

    def test_caption_length(self):
        captions = self.reader.read(SAMPLE_PL_STT)
        assert len(captions.get_captions("en-US")) == 5

    def test_proper_timestamps(self):
        captions = self.reader.read(SAMPLE_PL_STT)
        cue = captions.get_captions("en-US")[2]
        assert cue.start == 65000000
        assert cue.end == 66500000

    def test_tags_removed_from_text(self):
        captions = self.reader.read(SAMPLE_PL_STT)

        cue = captions.get_captions("en-US")[0]
        assert cue.nodes[0].content == "First caption"

        cue = captions.get_captions("en-US")[1]
        assert cue.nodes[0].content == "Second caption, no line break"

        cue = captions.get_captions("en-US")[2]
        assert cue.nodes[0].content == "Third caption"

    def test_no_header_file(self):
        with pytest.raises(InvalidInputError):
            self.reader.read(SAMPLE_PL_STT_NO_HEADER)

    def test_bad_header_1(self):
        with pytest.raises(InvalidInputError):
            self.reader.read(SAMPLE_PL_STT_BAD_HEADER_1)
