from striprtf import striprtf
from .base import BaseReader, CaptionSet, CaptionList, Caption, CaptionNode
from .exceptions import CaptionReadNoCaptions, InvalidInputError

import re


class PLSTTReader(BaseReader):
    RE_HEADER = re.compile(r"\[header](.*?)\[/header]", re.DOTALL | re.IGNORECASE)
    RE_BODY = re.compile(r"\[body](.*?)\[/body]", re.DOTALL | re.IGNORECASE)

    RE_SUBS_SPLIT = r"^\[\d+]$\n"
    RE_HTML = re.compile(r"\[[^>]+]")

    def _get_header(self, content) -> dict:
        header_match = self.RE_HEADER.search(content)
        if header_match is None:
            return {}

        header_lines = header_match.group(1).strip().splitlines()
        if not header_lines:
            return {}

        ret_headers = {k: v for k, v in [l.split("=") for l in header_lines]}
        return ret_headers

    def _get_body(self, content) -> str:
        body_match = self.RE_BODY.search(content)
        if body_match is None:
            return ""
        return body_match.group(1).strip()

    def _parse_sub(self, sub):
        sub_split = sub.split("\n")

        sub_start = sub_split[0].strip()
        sub_end = sub_split[1].strip()
        sub_text = [l.strip() for l in sub_split[2:]]

        return sub_start, sub_end, sub_text

    def detect(self, content):
        if content.startswith(u'{\\rtf1'):
            content = striprtf.rtf_to_text(content)
        if self._get_header(content) and self._get_body(content):
            return True
        else:
            return False

    def _guess_framerate(self, nonempty_splits):
        # Try to guess the framerate by taking the highest frame number encountered across all start and end times.
        # Once found, add 1 to it to get the best guess framerate, clamp it to 24fps as the minimum framerate and return it.
        frame_nums = []
        for sub in nonempty_splits:
            sub_start, sub_end, sub_text = self._parse_sub(sub)
            frame_nums.append(int(sub_start.split(":")[-1]))
            frame_nums.append(int(sub_end.split(":")[-1]))

        frame_nums = sorted(list(set(frame_nums)), reverse=True)
        return float(max(24, frame_nums[0] + 1))

    def read(self, content, lang="en-US"):
        if type(content) != str:
            raise InvalidInputError("The content is not a unicode string.")
        if content.startswith(u'{\\rtf1'):
            content = striprtf.rtf_to_text(content)

        try:
            header = self._get_header(content)
            if not header:
                raise InvalidInputError("Invalid or missing header.")
        except:
            raise InvalidInputError("Invalid or missing header.")

        framerate = None
        try:
            framerate = float(header.get("TIME_FRAME_RATE"))
        except:
            framerate = None

        body = self._get_body(content)

        captions = CaptionList()
        all_splits = re.split(PLSTTReader.RE_SUBS_SPLIT, body, flags=re.MULTILINE)
        nonempty_splits = [split.strip() for split in all_splits if split and split.strip()]
        if framerate is None:
            framerate = self._guess_framerate(nonempty_splits)

        for sub in nonempty_splits:
            sub_start, sub_end, sub_text = self._parse_sub(sub)
            start = self._srttomicro(sub_start, framerate)
            end = self._srttomicro(sub_end, framerate)

            nodes = []
            for line in sub_text:
                # TODO: handle formatting and positioning tags
                line = line.replace("[TOP]", "").replace("[BOTTOM]", "").replace("[CENTER]", "")
                line = line.replace("[I]", "").replace("[/I]", "")
                nodes.append(CaptionNode.create_text(line))
                nodes.append(CaptionNode.create_break())

            if nodes:
                # remove the last break
                nodes.pop()

            if nodes:
                captions.append(Caption(start, end, nodes))

        if not captions:
            raise CaptionReadNoCaptions("No captions found in file.")
        return CaptionSet({lang: captions})

    def _srttomicro(self, stamp, framerate):
        h, m, s, frame = stamp.split(":")

        frame = int(frame)
        split_second = frame / framerate
        microseconds = int(h) * 3600000000 + int(m) * 60000000 + int(s) * 1000000 + split_second * 1000000
        return microseconds

    def _find_text_line(self, start_line, lines):
        end_line = start_line

        found = False
        while end_line < len(lines):
            if lines[end_line].strip() == "":
                found = True
            elif found is True:
                end_line -= 1
                break
            end_line += 1

        return end_line + 1
