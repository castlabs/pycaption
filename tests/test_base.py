import pytest

from pycaption.base import CaptionList, Caption, CaptionNode, CaptionSet


class TestCaption:
    def setup_method(self):
        self.caption = Caption(0, 999999999999, ['test'])

    def test_format_start(self):
        assert self.caption.format_start() == '00:00:00.000'

    def test_format_end(self):
        assert self.caption.format_end() == '13:46:39.999'


class TestCaptionList:
    def setup_method(self):
        self.layout_info = "My Layout"
        self.caps = CaptionList([1, 2, 3], layout_info=self.layout_info)

    def test_splice(self):
        newcaps = self.caps[1:]

        assert isinstance(newcaps, CaptionList)
        assert newcaps.layout_info == self.layout_info

    def test_mul(self):
        newcaps = self.caps * 2

        assert isinstance(newcaps, CaptionList)
        assert newcaps.layout_info == self.layout_info

    def test_rmul(self):
        newcaps = 2 * self.caps

        assert isinstance(newcaps, CaptionList)
        assert newcaps.layout_info == self.layout_info

    def test_add_list_to_caption_list(self):
        newcaps = self.caps + [9, 8, 7]

        assert isinstance(newcaps, CaptionList)
        assert newcaps.layout_info == self.layout_info

    def test_add_two_caption_lists(self):
        newcaps = self.caps + CaptionList([4], layout_info=None)

        assert isinstance(newcaps, CaptionList)
        assert newcaps.layout_info == self.layout_info

        newcaps = self.caps + CaptionList([4], layout_info=self.layout_info)

        assert isinstance(newcaps, CaptionList)
        assert newcaps.layout_info == self.layout_info

        with pytest.raises(ValueError):
            newcaps = self.caps + CaptionList([4], layout_info="Other Layout")


class TestCaptionSetRemoveStyling:
    def setup_method(self):
        nodes = [
            CaptionNode.create_style(True, {"italics": True}),
            CaptionNode.create_text("hello"),
            CaptionNode.create_style(False, {"italics": True}),
            CaptionNode.create_break(),
            CaptionNode.create_text("world"),
        ]
        self.caption = Caption(0, 1000, nodes, style={"italics": True})
        self.caption_set = CaptionSet({"en": CaptionList([self.caption])})

    def test_removes_style_nodes(self):
        self.caption_set.remove_styling()

        node_types = [node.type_ for node in self.caption.nodes]
        assert CaptionNode.STYLE not in node_types

    def test_clears_caption_style_attribute(self):
        self.caption_set.remove_styling()

        assert self.caption.style == {}

    def test_preserves_text_and_break_nodes(self):
        self.caption_set.remove_styling()

        remaining = [
            (node.type_, node.content) for node in self.caption.nodes
        ]
        assert remaining == [
            (CaptionNode.TEXT, "hello"),
            (CaptionNode.BREAK, None),
            (CaptionNode.TEXT, "world"),
        ]
