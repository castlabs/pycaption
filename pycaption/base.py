import os
import re
from collections import defaultdict
from collections import OrderedDict
from datetime import timedelta
from numbers import Number

from .exceptions import CaptionReadError, CaptionReadTimingError

# `und` a special identifier for an undetermined language according to ISO 639-2
DEFAULT_LANGUAGE_CODE = os.getenv("PYCAPTION_DEFAULT_LANG", "und")


def force_byte_string(content):
    try:
        return content.encode("UTF-8")
    except UnicodeEncodeError:
        raise RuntimeError("Invalid content encoding")
    except UnicodeDecodeError:
        return content


class CaptionConverter:
    def __init__(self, captions=None):
        self.captions = captions if captions else []

    def read(self, content, caption_reader):
        try:
            self.captions = caption_reader.read(content)
        except AttributeError as e:
            raise Exception(e)
        return self

    def write(self, caption_writer):
        try:
            return caption_writer.write(self.captions)
        except AttributeError as e:
            raise Exception(e)


class BaseReader:
    def __init__(self, *args, **kwargs):
        pass

    def detect(self, content):
        if content:
            return True
        else:
            return False

    def read(self, content):
        return CaptionSet({DEFAULT_LANGUAGE_CODE: []})


class BaseWriter:
    def __init__(
        self, relativize=True, video_width=None, video_height=None, fit_to_screen=True
    ):
        """
        Initialize writer with the given parameters.

        :param relativize: If True (default), converts absolute positioning
            values (e.g. px) to percentage. ATTENTION: WebVTT does not support
            absolute positioning. If relativize is set to False and it finds
            an absolute positioning parameter for a given caption, it will
            ignore all positioning for that cue and show it in the default
            position.
        :param video_width: The width of the video for which the captions being
            converted were made. This is necessary for relativization.
        :param video_height: The height of the video for which the captions
            being converted were made. This is necessary for relativization.
        :param fit_to_screen: If extent is not set or
            if origin + extent > 100%, (re)calculate it based on origin.
            It is a pycaption fix for caption files that are technically valid
            but contains inconsistent settings that may cause long captions to
            be cut out of the screen.
        """
        self.relativize = relativize
        self.video_width = video_width
        self.video_height = video_height
        self.fit_to_screen = fit_to_screen

    def _relativize_and_fit_to_screen(self, layout_info):
        if layout_info:
            if self.relativize:
                # Transform absolute values (e.g. px) into percentages
                layout_info = layout_info.as_percentage_of(
                    self.video_width, self.video_height
                )
            if self.fit_to_screen:
                # Make sure origin + extent <= 100%
                layout_info = layout_info.fit_to_screen()
        return layout_info

    def write(self, content):
        return content


class Style:
    def __init__(self):
        pass


class CaptionNode:
    """
    A single node within a caption, representing either
    text, a style, or a linebreak.

    Rules:
        1. All nodes should have the property layout_info set.
        The value None means specifically that no positioning information
        should be specified. Each reader is to supply its own default
        values (if necessary) when reading their respective formats.
    """

    TEXT = 1
    # When and if this is extended, it might be better to turn it into a
    # property of the node, not a type of node itself.
    STYLE = 2
    BREAK = 3

    def __init__(
        self, type_, layout_info=None, content=None, start=None, position=None
    ):
        """
        :type type_: int
        :type layout_info: Layout
        """
        self.type_ = type_
        self.content = content
        self.position = position

        # Boolean. Marks the beginning/ end of a Style node.
        self.start = start
        self.layout_info = layout_info

    def __repr__(self):
        t = self.type_

        if t == CaptionNode.TEXT:
            return repr(self.content)
        elif t == CaptionNode.BREAK:
            return repr("BREAK")
        elif t == CaptionNode.STYLE:
            return repr(f"STYLE: {self.start} {self.content}")
        else:
            raise RuntimeError(f"Unknown node type: {t}")

    @staticmethod
    def create_text(text, layout_info=None, position=None):
        return CaptionNode(
            type_=CaptionNode.TEXT,
            layout_info=layout_info,
            position=position,
            content=text,
        )

    @staticmethod
    def create_style(start, content, layout_info=None):
        return CaptionNode(
            type_=CaptionNode.STYLE,
            layout_info=layout_info,
            content=content,
            start=start,
        )

    @staticmethod
    def create_break(layout_info=None, content=None):
        return CaptionNode(
            type_=CaptionNode.BREAK, layout_info=layout_info, content=content
        )


class Caption:
    """
    A single caption, including the time and styling information
    for its display.
    """

    def __init__(self, start, end, nodes, style={}, layout_info=None):
        """
        Initialize the Caption object
        :param start: The start time in microseconds
        :type start: Number
        :param end: The end time in microseconds
        :type end: Number
        :param nodes: A list of CaptionNodes
        :type nodes: list
        :param style: A dictionary with CSS-like styling rules
        :type style: dict
        :param layout_info: A Layout object with the necessary positioning
            information
        :type layout_info: Layout
        """
        if not isinstance(start, Number):
            raise CaptionReadTimingError(
                "Captions must be initialized with a" " valid start time"
            )
        if not isinstance(end, Number):
            raise CaptionReadTimingError(
                "Captions must be initialized with a" " valid end time"
            )
        if not nodes:
            raise CaptionReadError("Node list cannot be empty")
        self.start = start
        self.end = end
        self.nodes = nodes
        self.style = style
        self.layout_info = layout_info

    def is_empty(self):
        return len(self.nodes) == 0

    def format_start(self, msec_separator=None):
        """
        Format the start time value in milliseconds into a string
        value suitable for some of the supported output formats (ex.
        SRT, DFXP).
        """
        return self._format_timestamp(self.start, msec_separator)

    def format_end(self, msec_separator=None):
        """
        Format the end time value in milliseconds into a string value suitable
        for some of the supported output formats (ex. SRT, DFXP).
        """
        return self._format_timestamp(self.end, msec_separator)

    def __repr__(self):
        return repr(f"{self.format_start()} --> {self.format_end()}\n{self.get_text()}")

    def get_text_nodes(self):
        """
        Get the text of the caption.
        """

        def get_text_for_node(node):
            if node.type_ == CaptionNode.TEXT:
                return node.content
            if node.type_ == CaptionNode.BREAK:
                return "\n"
            return ""

        return [get_text_for_node(node) for node in self.nodes]

    def get_text(self):
        text_nodes = self.get_text_nodes()
        return "".join(text_nodes).strip()

    def _format_timestamp(self, microseconds, msec_separator=None):
        duration = timedelta(microseconds=microseconds)
        hours, rem = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(rem, 60)
        milliseconds = f"{duration.microseconds // 1000:03d}"
        timestamp = (
            f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            f"{msec_separator or '.'}{milliseconds:.3s}"
        )
        return timestamp


class CaptionList(list):
    """A list of captions with a layout object attached to it"""

    def __init__(self, iterable=None, layout_info=None):
        """
        :param iterable: An iterator used to populate the caption list
        :param Layout layout_info: A Layout object with the positioning info
        """
        self.layout_info = layout_info
        args = [iterable] if iterable else []
        super().__init__(*args)

    def __getslice__(self, i, j):
        return CaptionList(list.__getslice__(self, i, j), layout_info=self.layout_info)

    def __getitem__(self, y):
        item = list.__getitem__(self, y)
        if isinstance(item, Caption):
            return item
        return CaptionList(item, layout_info=self.layout_info)

    def __add__(self, other):
        add_is_safe = (
            not hasattr(other, "layout_info")
            or not other.layout_info
            or self.layout_info == other.layout_info
        )
        if add_is_safe:
            return CaptionList(list.__add__(self, other), layout_info=self.layout_info)
        else:
            raise ValueError(
                "Cannot add CaptionList objects with different layout_info"
            )

    def __mul__(self, other):
        return CaptionList(list.__mul__(self, other), layout_info=self.layout_info)

    __rmul__ = __mul__


class CaptionSet:
    """
    A set of captions in potentially multiple languages,
    all representing the same underlying content.

    The .layout_info attribute, keeps information that should be inherited
    by all the children.
    """

    RE_HTML_STRIP = re.compile(r"<[^>]+>")
    RE_ASS_STRIP = re.compile(r"{[^}]+}")

    def __init__(self, captions, styles={}, layout_info=None):
        """
        :param captions: A dictionary of the format {'language': CaptionList}
        :param styles: A dictionary with CSS-like styling rules
        :param Layout layout_info: A Layout object with the positioning info
        """
        self._captions = captions
        self._styles = styles
        self.layout_info = layout_info

    def set_captions(self, lang, captions):
        self._captions[lang] = captions

    def get_languages(self):
        return list(self._captions.keys())

    def get_captions(self, lang):
        return self._captions.get(lang, [])

    def add_style(self, selector, rules):
        """
        :param selector: The selector indicating the elements to which the
            rules should be applied.
        :param rules: A dictionary with CSS-like styling rules.
        """
        self._styles[selector] = rules

    def get_style(self, selector):
        """
        Returns a dictionary with CSS-like styling rules for a given selector.
        :param selector: The selector whose rules should be returned (e.g. an
            element or class name).
        """
        return self._styles.get(selector, {})

    def get_styles(self):
        return sorted(self._styles.items())

    def set_styles(self, styles):
        self._styles = styles

    def is_empty(self):
        return all([len(captions) == 0 for captions in list(self._captions.values())])

    def set_layout_info(self, lang, layout_info):
        self._captions[lang].layout_info = layout_info

    def get_layout_info(self, lang):
        caption_list = self._captions.get(lang)
        if caption_list:
            return caption_list.layout_info
        return None

    def adjust_caption_timing(self, offset=0, rate_skew=1.0):
        """
        Adjust the timing according to offset and rate_skew.
        Skew is applied first, then offset.

        e.g. if skew == 1.1, and offset is 5, a caption originally
        displayed from 10-11 seconds would instead be at 16-17.1
        """
        for lang in self.get_languages():
            captions = self.get_captions(lang)
            out_captions = CaptionList()
            for caption in captions:
                caption.start = caption.start * rate_skew + offset
                caption.end = caption.end * rate_skew + offset
                if caption.start >= 0:
                    out_captions.append(caption)
            self.set_captions(lang, out_captions)

    def strip_html_tags(self):
        """
        Iterates all captions and nodes in all languages and strips HTML tags (matching the RE_HTML_STRIP regex)
        """
        for lang in self.get_languages():
            captions = self.get_captions(lang)
            out_captions = CaptionList()
            for caption in captions:
                for node in caption.nodes:
                    if node.type_ == CaptionNode.TEXT:
                        node.content = self.RE_HTML_STRIP.sub("", node.content)
                out_captions.append(caption)
            self.set_captions(lang, out_captions)

    def strip_ass_tags(self):
        """
        Iterates all captions and nodes in all languages and strips ASS tags (matching the RE_ASS_STRIP regex)
        """
        for lang in self.get_languages():
            captions = self.get_captions(lang)
            out_captions = CaptionList()
            for caption in captions:
                for node in caption.nodes:
                    if node.type_ == CaptionNode.TEXT:
                        node.content = self.RE_ASS_STRIP.sub("", node.content)
                out_captions.append(caption)
            self.set_captions(lang, out_captions)

    def remove_empty_captions(self):
        """
        Removes captions which have only empty TEXT nodes.
        """
        for lang in self.get_languages():
            captions = self.get_captions(lang)
            out_captions = CaptionList()
            for caption in captions:
                valid_text_nodes = [
                    node for node in caption.nodes if node.type_ == CaptionNode.TEXT and node.content.strip()
                ]
                if valid_text_nodes:
                    out_captions.append(caption)
            self.set_captions(lang, out_captions)

    def remove_layout_info(self):
        """
        Removes layout info from all captions and nodes in all languages.
        """
        for lang in self.get_languages():
            captions = self.get_captions(lang)
            for caption in captions:
                # strip layout info from caption
                caption.layout_info = None

                # strip layout info from all nodes in caption
                for node in caption.nodes:
                    node.layout_info = None

    @staticmethod
    def _group_captions_by_start_time(caps: CaptionList) -> list[list[Caption]]:
        """
        Groups captions that have the same start time.

        :param caps: CaptionList of captions to group
        :return: List of lists of captions, where each inner list contains captions with the same start time.
        """

        caps_start_time = OrderedDict()
        for i, cap in enumerate(caps):
            if cap.start not in caps_start_time:
                caps_start_time[cap.start] = [cap]
            else:
                caps_start_time[cap.start].append(cap)

        # order by start timestamp
        caps_start_time = OrderedDict(sorted(caps_start_time.items(), key=lambda item: item[0]))

        # check if captions with the same start time also have the same end time
        # fail if different end times are found - this is not (yet?) supported
        caps_final = []
        for start_time, caps_list in caps_start_time.items():
            if len(caps_list) == 1:
                caps_final.append(caps_list)
            else:
                end_times = list(set([c.end for c in caps_list]))
                if len(end_times) != 1:
                    raise ValueError("Unsupported subtitles - overlapping subtitles with different end times found")
                else:
                    caps_final.append(caps_list)
        return caps_final

    def make_sure_of_sane_start_times_and_gap(self, min_sub_gap_ms=250):
        """
        Makes sure that the start of a caption is not identical to end of the previous one
        and that there is a minimum gap between captions.
        :param min_sub_gap_ms: minimum gap in milliseconds that should be between captions
        """
        for lang in self.get_languages():
            _captions = self.get_captions(lang)
            _captions_by_start = self._group_captions_by_start_time(_captions)

            for i, caps in enumerate(_captions_by_start):
                # skip the first caption, as it has no previous caption to compare to
                if i == 0:
                    continue

                prev_caption_end = _captions_by_start[i - 1][0].end
                curr_caption_start = caps[0].start
                curr_caption_end = caps[0].end

                if curr_caption_start < prev_caption_end:
                    for c in caps:
                        c.start = min(prev_caption_end + (min_sub_gap_ms * 1000), c.end)
                elif curr_caption_start == prev_caption_end:
                    for c in caps:
                        c.start = min(prev_caption_end + (min_sub_gap_ms * 1000), curr_caption_end)

    def merge_captions(self, merge_layout_info=False):
        """
        Merge captions that have the same start and end time.
        We do this by merging their nodes together, separating them with a line break.
        """
        for lang in self.get_languages():
            captions_raw = self.get_captions(lang)
            _captions_by_start = self._group_captions_by_start_time(captions_raw)

            all_captions_with_same_time = [l for l in _captions_by_start if len(l) > 1]
            for current_captions_with_same_time in all_captions_with_same_time:
                nodes_to_append = [CaptionNode(CaptionNode.BREAK)]
                for dupe_caption in current_captions_with_same_time[1:]:
                    nodes_to_append.extend(dupe_caption.nodes)
                    nodes_to_append.append(CaptionNode(CaptionNode.BREAK))
                    captions_raw.remove(dupe_caption)

                if len(nodes_to_append) > 0:
                    if nodes_to_append[-1].type_ == CaptionNode.BREAK:
                        nodes_to_append.pop()

                if nodes_to_append:
                    current_caption = current_captions_with_same_time[0]
                    current_caption.nodes.extend(nodes_to_append)
                    if merge_layout_info:
                        layout_info = current_caption.layout_info
                        if not layout_info:
                            for node in current_caption.nodes:
                                if node.type_ == CaptionNode.TEXT:
                                    layout_info = node.layout_info
                                    if layout_info:
                                        break
                        if not layout_info:
                            return

                        current_caption.layout_info = layout_info
                        for node in current_captions_with_same_time[0].nodes:
                            node.layout_info = layout_info

# Functions
def merge_concurrent_captions(caption_set):
    """Merge captions that have the same start and end times"""
    for lang in caption_set.get_languages():
        captions = caption_set.get_captions(lang)
        last_caption = None
        concurrent_captions = CaptionList()
        merged_captions = CaptionList()
        for caption in captions:
            if last_caption:
                last_timespan = last_caption.start, last_caption.end
                current_timespan = caption.start, caption.end
                if current_timespan == last_timespan:
                    concurrent_captions.append(caption)
                    last_caption = caption
                    continue
                else:
                    merged_captions.append(merge(concurrent_captions))
            concurrent_captions = [caption]
            last_caption = caption

        if concurrent_captions:
            merged_captions.append(merge(concurrent_captions))
        if merged_captions:
            caption_set.set_captions(lang, merged_captions)
    return caption_set


def merge(captions):
    """
    Merge list of captions into one caption. The start/end times from the first
    caption are kept.
    """
    new_nodes = []
    for caption in captions:
        if new_nodes:
            new_nodes.append(CaptionNode.create_break())
        for node in caption.nodes:
            new_nodes.append(node)
    caption = Caption(captions[0].start, captions[0].end, new_nodes, captions[0].style)
    return caption
