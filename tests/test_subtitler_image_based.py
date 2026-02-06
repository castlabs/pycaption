
import os

import pytest
from PIL import Image, ImageDraw, ImageFont

from pycaption.base import Caption, CaptionNode
from pycaption.exceptions import CaptionRendererError
from pycaption.geometry import Layout, Point, Size, UnitEnum
from pycaption.subtitler_image_based import SubtitleImageBasedWriter


FONT_PATH = os.path.join(
    os.path.dirname(__file__),
    '..', 'pycaption', 'NotoSansDisplay-Regular-Note-Math.ttf'
)


def make_caption(text, layout_info=None):
    nodes = [CaptionNode.create_text(text)]
    return Caption(0, 1000000, nodes, layout_info=layout_info)


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
        with pytest.raises(CaptionRendererError, match="Text runs off screen"):
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
        with pytest.raises(CaptionRendererError, match="Text runs off screen"):
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
        with pytest.raises(CaptionRendererError, match="Text runs off screen"):
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
        with pytest.raises(CaptionRendererError, match="Text runs off screen"):
            writer.printLine(draw, [caption], fnt, position='source', align='left')

    def test_left_sticks_out(self):
        # 200px wide screen, text at x=10% (x=20), text wider than screen
        # so repositioning pushes x past the left edge
        writer, draw = make_writer_and_draw(200, 200)
        fnt = ImageFont.truetype(FONT_PATH, 20)
        layout = make_source_layout(x_pct=10, y_pct=50)
        caption = make_caption("This text sticks out on the left", layout_info=layout)
        with pytest.raises(CaptionRendererError, match="Text runs off screen"):
            writer.printLine(draw, [caption], fnt, position='source', align='left')