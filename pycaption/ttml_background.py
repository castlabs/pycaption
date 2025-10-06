import base64
import tempfile
from datetime import timedelta
from io import BytesIO

from pycaption.base import CaptionSet
from pycaption.subtitler_image_based import SubtitleImageBasedWriter

HEADER = """
<?xml version='1.0' encoding='UTF-8'?>
<tt xmlns:itts="http://www.w3.org/ns/ttml/profile/imsc1#styling"
    xmlns:ittp="http://www.w3.org/ns/ttml/profile/imsc1#parameter"
    xmlns:ittm="http://www.w3.org/ns/ttml/profile/imsc1#metadata"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:smpte="http://www.smpte-ra.org/schemas/2052-1/2010/smpte-tt"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tt="http://www.w3.org/ns/ttml"
    xml:lang="eng" tts:extent="852px 480px"
    ttp:profile="http://www.w3.org/ns/ttml/profile/imsc1/image"
    ittp:activeArea="100% 100% 100% 100%">
<head>
    <layout>
        <region xml:id="r1" tts:origin="0% 0%" tts:extent="100% 100%" tts:showBackground="always" tts:textAlign="left" tts:displayAlign="before" />
    </layout>
</head>
<body>
"""

SUB = """<div region="r1" begin="{begin}" end="{end}" smpte:backgroundImage="data:image/png;base64,{png}"/>
"""

FOOTER = """
</body>
</tt>"""


class TTMLBackgroundWriter(SubtitleImageBasedWriter):

    def __init__(self, relativize=True, video_width=720, video_height=480, fit_to_screen=True, tape_type='NON_DROP',
                 frame_rate=25, compat=False):
        super().__init__(relativize, video_width, video_height, fit_to_screen, frame_rate)
        self.tape_type = tape_type
        self.frame_rate = frame_rate

    def save_image(self, tmp_dir, index, img):
        # Jetzt speichern mit Transparenz
        img.save(tmp_dir + '/subtitle%04d.png' % index, transparency=3)


    def to_ttml_timestamp(self, ms: int) -> str:
        hours = ms // 3_600_000
        ms -= hours * 3_600_000
        minutes = ms // 60_000
        ms -= minutes * 60_000
        seconds = ms // 1000
        ms -= seconds * 1000
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{ms:03d}"

    def write(
            self,
            caption_set: CaptionSet,
            position='bottom',
            avoid_same_next_start_prev_end=False,
            align='center'
    ):
        lang = caption_set.get_languages().pop()
        caps = caption_set.get_captions(lang)

        buf = BytesIO()
        with tempfile.TemporaryDirectory() as tmpDir:
            caps_final, overlapping = self.write_images(caps, lang, tmpDir, position, align,
                                                        avoid_same_next_start_prev_end)

            index = 1

            subtitles = ""
            subtitles += HEADER

            for i, cap_list in enumerate(caps_final):
                sub_img = open(tmpDir + "/subtitle%04d.png" % index, "rb").read()
                subtitles += SUB.format(
                    begin=self.to_ttml_timestamp(cap_list[0].start),
                    end=self.to_ttml_timestamp(cap_list[0].end),
                    png=base64.b64encode(sub_img).decode()
                )
                index = index + 1
            subtitles += FOOTER

        return subtitles

    def format_ts(self, value):
        datetime_value = timedelta(seconds=(int(value / 1000000)))
        str_value = str(datetime_value)[:11]

        # make sure all numbers are padded with 0 to two places
        str_value = ':'.join([n.zfill(2) for n in str_value.split(':')])

        str_value = str_value + ':%02d' % (int((int(value / 1000) % 1000) / int(1000 / self.frame_rate)))
        return str_value
