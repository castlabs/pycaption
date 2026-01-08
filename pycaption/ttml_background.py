import base64
import tempfile
from datetime import timedelta
from io import BytesIO

from PIL import Image

from pycaption.base import CaptionSet
from pycaption.subtitler_image_based import SubtitleImageBasedWriter

HEADER_A = """<?xml version='1.0' encoding='UTF-8'?>
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
    <metadata>
"""

IMG_DEF = """<smpte:image imageType="PNG" encoding="Base64" xml:id="img_{index}">{png}</smpte:image>"""

HEADER_B = """
    </metadata>
</head>
<body>
"""

SUB = """<div region="r1" begin="{begin}" end="{end}" smpte:backgroundImage="#img_{index}"/>
"""

FOOTER = """</body>
</tt>"""


class TTMLBackgroundWriter(SubtitleImageBasedWriter):

    # Palette colors for TTML background images
    paColor = (255, 255, 255)  # letter body (white)
    e1Color = (190, 190, 190)  # antialiasing color (gray)
    e2Color = (0, 0, 0)  # border color (black)
    bgColor = (0, 255, 0)  # background color (green - index 3 = transparent)

    def __init__(self, relativize=True, video_width=720, video_height=480, fit_to_screen=True, tape_type='NON_DROP',
                 frame_rate=25, compat=False):
        super().__init__(relativize, video_width, video_height, fit_to_screen, frame_rate)
        self.tape_type = tape_type
        self.frame_rate = frame_rate

        # Create palette image for quantization (4 colors only - smaller output)
        self.palette_image = Image.new("P", (1, 1))
        self.palette_image.putpalette([*self.paColor, *self.e1Color, *self.e2Color, *self.bgColor])

    def save_image(self, tmp_dir, index, img):
        """Convert RGBA to paletted PNG with transparency."""
        # Replace transparent pixels with green background
        background = Image.new('RGB', img.size, self.bgColor)
        background.paste(img, mask=img.split()[3])  # Use alpha channel as mask

        # Quantize to 4-color palette
        img_quant = background.quantize(palette=self.palette_image, dither=0)
        img_quant.save(tmp_dir + '/subtitle%04d.png' % index, transparency=3)

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

        with tempfile.TemporaryDirectory() as tmpDir:
            caps_final, overlapping = self.write_images(caps, lang, tmpDir, position, align,
                                                        avoid_same_next_start_prev_end)

            subtitles = ""
            subtitles += HEADER_A

            for i, cap_list in enumerate(caps_final, 1):
                sub_img = open(tmpDir + "/subtitle%04d.png" % i, "rb").read()
                subtitles += IMG_DEF.format(
                    index=i,
                    png=base64.b64encode(sub_img).decode()
                )

            subtitles += HEADER_B

            for i, cap_list in enumerate(caps_final, 1):
                subtitles += SUB.format(
                    begin=cap_list[0].format_start(),
                    end=cap_list[0].format_end(),
                    index=i,
                )

            subtitles += FOOTER

        return subtitles
