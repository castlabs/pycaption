
import os
from unittest import skip

import pytest
from PIL import Image, ImageDraw, ImageFont

from pycaption import SRTReader
from pycaption.base import Caption, CaptionList, CaptionNode
from pycaption.exceptions import CaptionRendererError, CaptionRendererErrorGroup
from pycaption.filtergraph import FiltergraphWriter
from pycaption.geometry import Layout, Point, Size, UnitEnum
from pycaption.subtitler_image_based import SubtitleImageBasedWriter


FONT_PATH = os.path.join(
    os.path.dirname(__file__),
    '..', 'pycaption', 'NotoSansDisplay-Regular-Note-Math.ttf'
)


def make_caption(text, layout_info=None, start=0):
    nodes = [CaptionNode.create_text(text)]
    return Caption(start, start+1000000, nodes, layout_info=layout_info)


def make_source_layout(x_pct, y_pct):
    origin = Point(Size(x_pct, UnitEnum.PERCENT), Size(y_pct, UnitEnum.PERCENT))
    return Layout(origin=origin)


def make_writer_and_draw(width, height):
    writer = SubtitleImageBasedWriter(video_width=width, video_height=height)
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    return writer, draw


class TestTextOffScreenCentered:
    def test_short_text_fits(self):
        writer, draw = make_writer_and_draw(720, 480)
        fnt = ImageFont.truetype(FONT_PATH, 20)
        caption = make_caption("Hello")
        writer.printLine(draw, [caption], fnt, position='bottom', align='center')

    def test_long_text_runs_off(self):
        writer, draw = make_writer_and_draw(200, 100)
        fnt = ImageFont.truetype(FONT_PATH, 20)
        caption = make_caption("This text is way too long to fit on a tiny screen")
        with pytest.raises(CaptionRendererError, match="Text at 00:00:00.000 runs off screen"):
            writer.printLine(draw, [caption], fnt, position='bottom', align='center')


class TestTextOffScreenLeft:
    def test_short_text_fits(self):
        writer, draw = make_writer_and_draw(720, 480)
        fnt = ImageFont.truetype(FONT_PATH, 20)
        caption = make_caption("Hello")
        writer.printLine(draw, [caption], fnt, position='bottom', align='left')

    def test_long_text_runs_off(self):
        writer, draw = make_writer_and_draw(200, 100)
        fnt = ImageFont.truetype(FONT_PATH, 20)
        caption = make_caption("This text is way too long to fit on a tiny screen")
        with pytest.raises(CaptionRendererError, match="Text at 00:00:00.000 runs off screen"):
            writer.printLine(draw, [caption], fnt, position='bottom', align='left')


class TestTextOffScreenRight:
    def test_short_text_fits(self):
        writer, draw = make_writer_and_draw(720, 480)
        fnt = ImageFont.truetype(FONT_PATH, 20)
        caption = make_caption("Hello")
        writer.printLine(draw, [caption], fnt, position='bottom', align='right')

    def test_long_text_runs_off(self):
        writer, draw = make_writer_and_draw(200, 100)
        fnt = ImageFont.truetype(FONT_PATH, 20)
        caption = make_caption("This text is way too long to fit on a tiny screen")
        with pytest.raises(CaptionRendererError, match="Text at 00:00:00.000 runs off screen"):
            writer.printLine(draw, [caption], fnt, position='bottom', align='right')


class TestTextOffScreenSourcePosition:
    def test_centered_fits(self):
        writer, draw = make_writer_and_draw(720, 480)
        fnt = ImageFont.truetype(FONT_PATH, 20)
        layout = make_source_layout(x_pct=30, y_pct=50)
        caption = make_caption("Hello", layout_info=layout)
        writer.printLine(draw, [caption], fnt, position='source', align='left')

    def test_right_sticks_out(self):
        # 200px wide screen, text at x=80% (x=160), text wider than remaining space
        writer, draw = make_writer_and_draw(200, 200)
        fnt = ImageFont.truetype(FONT_PATH, 20)
        layout = make_source_layout(x_pct=80, y_pct=50)
        caption = make_caption("This text sticks out on the right", layout_info=layout)
        with pytest.raises(CaptionRendererError, match="Text at 00:00:00.000 runs off screen"):
            writer.printLine(draw, [caption], fnt, position='source', align='left')

    def test_left_sticks_out(self):
        # 200px wide screen, text at x=10% (x=20), text wider than screen
        # so repositioning pushes x past the left edge
        writer, draw = make_writer_and_draw(200, 200)
        fnt = ImageFont.truetype(FONT_PATH, 20)
        layout = make_source_layout(x_pct=10, y_pct=50)
        caption = make_caption("This text sticks out on the left", layout_info=layout)
        with pytest.raises(CaptionRendererError, match="Text at 00:00:00.000 runs off screen"):
            writer.printLine(draw, [caption], fnt, position='source', align='left')

    def test_exception_group(self, tmp_path):
        """
        The main ``write_images`` interface collects all exceptions and reports them in a ``CaptionRendererErrorGroup``.
        """
        # 200px wide screen, text at x=80% (x=160), text wider than remaining space
        writer, draw = make_writer_and_draw(200, 200)
        layout = make_source_layout(x_pct=80, y_pct=50)
        cap_list = CaptionList(
            [
                make_caption("This text sticks out on the right 1", layout_info=layout),
                make_caption("This text sticks out on the right 2", layout_info=layout, start=2000000)
            ],
            layout
        )
        with pytest.RaisesGroup(
            pytest.RaisesExc(CaptionRendererError, match="Text at 00:00:00.000 runs off screen"),
            pytest.RaisesExc(CaptionRendererError, match="Text at 00:00:02.000 runs off screen"),
        ) as rg:
            writer.write_images(cap_list, "en", str(tmp_path), position='source', align='left')
        assert isinstance(rg.value, CaptionRendererErrorGroup), "Should be wrapped in a CaptionRendererErrorGroup"


class TestMultilineOrder:
    """The first line of a multiline caption must be rendered above the
    second line, regardless of whether the block is anchored top or bottom."""

    NARROW = "II"
    WIDE = "WWWWWWWWWW"

    @staticmethod
    def _text_bands(img):
        """Return the width of each vertical band of rendered pixels,
        top to bottom. Bands are separated by fully transparent rows."""
        alpha = img.getchannel('A')
        width, height = img.size
        bands = []
        current = None
        for y in range(height):
            row = [x for x in range(width) if alpha.getpixel((x, y)) > 0]
            if row:
                if current is None:
                    current = [min(row), max(row)]
                else:
                    current[0] = min(current[0], min(row))
                    current[1] = max(current[1], max(row))
            elif current is not None:
                bands.append(current[1] - current[0])
                current = None
        if current is not None:
            bands.append(current[1] - current[0])
        return bands

    @pytest.mark.parametrize('position', ['top', 'bottom'])
    def test_first_line_is_above_second(self, position):
        writer, draw = make_writer_and_draw(720, 480)
        fnt = ImageFont.truetype(FONT_PATH, 28)
        caption = make_caption(f"{self.NARROW}\n{self.WIDE}")
        writer.printLine(draw, [caption], fnt, position=position, align='center')

        bands = self._text_bands(draw._image)
        assert len(bands) == 2, "Expected two separate lines of text"
        assert bands[0] < bands[1], (
            f"position={position}: narrow first line must be rendered "
            f"above the wide second line"
        )


class TestBaselineAlignment:
    """Render subtitle images with/without descenders to visually verify
    that the baseline sits at a consistent 5% from the bottom."""

    NO_DESCENDER = "AHLEN"       # no descenders
    WITH_DESCENDER = "gypsy"     # descenders: g, y, p
    WITH_DESCENDER_TOP = "gypsy\nAHLEN"     # descenders: g, y, p
    WITH_DESCENDER_BOTTOM = "AHLEN\ngypsy"     # descenders: g, y, p


    COMBOS = [
        ("no_desc_x2", [NO_DESCENDER, NO_DESCENDER]),
        ("desc_x2", [WITH_DESCENDER, WITH_DESCENDER]),
        ("top_no_bottom_yes", [NO_DESCENDER, WITH_DESCENDER]),
        ("top_yes_bottom_no", [WITH_DESCENDER, NO_DESCENDER]),
        ("one_line-no", [NO_DESCENDER]),
        ("one_line-yes", [WITH_DESCENDER]),
        ("one_line-yes", [WITH_DESCENDER]),
        ("two-in-one-a", [WITH_DESCENDER_TOP]),
        ("tow-in-one-b", [WITH_DESCENDER_BOTTOM]),
    ]

    @pytest.fixture(params=COMBOS, ids=[c[0] for c in COMBOS])
    def combo(self, request):
        return request.param

    def test_baseline_visual(self, combo, tmp_path):
        name, lines = combo
        width, height = 720, 480
        writer, draw = make_writer_and_draw(width, height)
        fnt = ImageFont.truetype(FONT_PATH, 28)

        captions = [make_caption(text) for text in lines]
        writer.printLine(draw, captions, fnt, position='bottom', align='center')

        # Draw a red guide line at the 5% baseline position
        baseline_y = int(height * 0.95)
        img = draw._image
        guide = ImageDraw.Draw(img)
        guide.line([(0, baseline_y), (width, baseline_y)], fill=(255, 0, 0, 200), width=1)

        out = tmp_path / f"baseline_{name}.png"
        out = f"tests/baseline_samples/baseline_{name}.png"
        os.makedirs("tests/baseline_samples", exist_ok=True)
        img.save(str(out))
        print(f"\nSaved: {out}")



def cap(start_s, end_s):
    return Caption(int(start_s * 1000000), int(end_s * 1000000),
                   [CaptionNode.create_text('x')])


class TestSeparateAdjacentCaptions:
    """``avoid_same_next_start_prev_end`` must guarantee that, on the output
    frame grid, no caption starts before the previous one has ended."""

    def separate(self, timings, frame_rate=25):
        writer = SubtitleImageBasedWriter(frame_rate=frame_rate)
        caps_final = [[cap(s, e)] for s, e in timings]
        writer.separate_adjacent_captions(caps_final)
        return writer, caps_final

    def assert_no_overlap(self, writer, caps_final):
        for prev, cur in zip(caps_final, caps_final[1:]):
            assert writer.timestamp_to_frame(cur[0].start) > writer.timestamp_to_frame(prev[0].end)
        for caps_list in caps_final:
            assert writer.timestamp_to_frame(caps_list[0].end) > writer.timestamp_to_frame(caps_list[0].start)

    def test_overlapping_source_shortens_previous_caption(self):
        # taken from a real source: the first cue ends after the second starts
        writer, caps_final = self.separate([(4.510, 6.300), (6.000, 8.090)])

        self.assert_no_overlap(writer, caps_final)
        # the second caption keeps its start time
        assert caps_final[1][0].start == 6000000
        assert writer.timestamp_to_frame(caps_final[0][0].end) == writer.timestamp_to_frame(6000000) - 1

    def test_sub_frame_gap_is_widened(self):
        # 8ms apart: both timestamps would truncate to the same frame
        writer, caps_final = self.separate([(1.000, 2.000), (2.008, 3.000)])

        self.assert_no_overlap(writer, caps_final)

    def test_identical_timestamps_are_separated(self):
        writer, caps_final = self.separate([(1.000, 2.000), (2.000, 3.000)])

        self.assert_no_overlap(writer, caps_final)

    def test_current_caption_is_delayed_when_previous_cannot_shrink(self):
        # the previous caption is a single frame long, so it cannot be trimmed
        writer, caps_final = self.separate([(1.000, 1.040), (1.000, 3.000)])

        self.assert_no_overlap(writer, caps_final)
        assert caps_final[0][0].end == 1040000
        assert caps_final[1][0].start > 1040000

    def test_non_overlapping_captions_are_untouched(self):
        writer, caps_final = self.separate([(1.0, 2.0), (2.5, 3.0), (3.5, 4.0)])

        assert [(c[0].start, c[0].end) for c in caps_final] == [
            (1000000, 2000000), (2500000, 3000000), (3500000, 4000000)]

    def test_cascading_overlaps(self):
        writer, caps_final = self.separate([(1.0, 5.0), (2.0, 6.0), (3.0, 7.0)])

        self.assert_no_overlap(writer, caps_final)
