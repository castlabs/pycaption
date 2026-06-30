
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
        img.save(str(out))
        print(f"\nSaved: {out}")

