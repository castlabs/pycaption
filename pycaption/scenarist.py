import os
import tempfile
import zipfile
from io import BytesIO
from math import sqrt

from PIL import Image, ImageFont, ImageDraw
from PIL.ImagePalette import ImagePalette

from pycaption.base import BaseWriter, CaptionSet, Caption

HEADER = """st_format 2
SubTitle\tFace_Painting
Tape_Type\tNON_DROP
Display_Start\tnon_forced
Pixel_Area\t(2 479)
Display_Area\t(0 2 719 479)
Color\t(0 1 2 3)
Contrast\t(7 7 7 7)
BG\t({bg_red} {bg_green} {bg_blue} = = =)
PA\t({pa_red} {pa_green} {pa_blue} = = =)
E1\t({e1_red} {e1_green} {e1_blue} = = =)
E2\t({e2_red} {e2_green} {e2_blue} = = =)
directory\tC:\\
Base_Time\t00:00:00:00
################################################
SP_NUMBER START END FILE_NAME
"""

a = """
0001 01:00:30:12 01:00:35:08 eng0001.tif
0002 01:00:35:13 01:00:40:07 eng0002.tif
0003 01:00:41:17 01:00:44:08 eng0003.tif
0004 01:00:44:13 01:00:48:02 eng0004.tif

"""

def zipit(path, arch, mode='w'):
    archive = zipfile.ZipFile(arch, mode, zipfile.ZIP_DEFLATED)
    if os.path.isdir(path):
        if not path.endswith('tmp'):
            _zippy(path, path, archive)
    else:
        _, name = os.path.split(path)
        archive.write(path, name)
    archive.close()


def _zippy(base_path, path, archive):
    paths = os.listdir(path)
    for p in paths:
        p = os.path.join(path, p)
        if os.path.isdir(p):
            _zippy(base_path, p, archive)
        else:
            archive.write(p, os.path.relpath(p, base_path))


class ScenaristDVDWriter(BaseWriter):
    paColor = (255, 255, 255) # letter body
    e1Color = (190, 190, 190) # antialiasing color
    e2Color = (0, 0, 0) # border color
    bgColor = (0, 255, 0) # background color

    palette = [paColor, e1Color, e2Color, bgColor]


    def __init__(self, relativize=True, video_width=720, video_height=480, fit_to_screen=True):
        super().__init__(relativize, video_width, video_height, fit_to_screen)

    def write(self, caption_set: CaptionSet):
        lang = caption_set.get_languages().pop()
        caps = caption_set.get_captions(lang)


        buf = BytesIO()
        with tempfile.TemporaryDirectory() as tmpDir:
            with open(tmpDir + '/subtitles.sst', 'w+') as sst:
                index = 1
                for cap in caps:
                    sst.write("%04d %s %s subtitle%04d.tif\n" % (index, cap.format_start(), cap.format_end(), index))
                    backgroundColor = 3#self.bgColor
                    img = Image.new('RGB', (self.video_width, self.video_height), self.bgColor)
                    #img.putpalette(self.paletteRaw)
                    draw = ImageDraw.Draw(img)
                    self.printLine(draw, cap)

                    for py in range(img.height):
                        for px in range(img.width):
                            pix = img.getpixel((px, py))
                            # Perform exhaustive search for closest Euclidean distance
                            dist = 450
                            best_fit = (0, 0, 0)
                            for c in self.palette:
                                if pix == c:  # If pixel matches exactly, break
                                    best_fit = c
                                    break
                                tmp = sqrt(pow(pix[0] - c[0], 2) + pow(pix[1] - c[1], 2) + pow(pix[2] - c[2], 2))
                                if tmp < dist:
                                    dist = tmp
                                    best_fit = c
                            img.putpixel((px, py), best_fit)
                    img.save(tmpDir + '/subtitle%04d.tif' % index)  #
                    # None, "tiff_ccitt", "group3", "group4", "tiff_jpeg", "tiff_adobe_deflate", "tiff_thunderscan", "tiff_deflate", "tiff_sgilog", "tiff_sgilog24", "tiff_raw_16"


                    index = index + 1

            zipit(tmpDir, buf)
        buf.seek(0)
        return buf.read()

    def quantizetopalette(self, silf, palette, dither=False):
        """Convert an RGB or L mode image to use a given P image's palette."""

        silf.load()

        # use palette from reference image
        palette.load()
        if palette.mode != "P":
            raise ValueError("bad mode for palette image")
        if silf.mode != "RGB" and silf.mode != "L":
            raise ValueError(
                "only RGB or L mode images can be quantized to a palette"
            )
        im = silf.im.convert("P", 1 if dither else 0, palette.im)
        # the 0 above means turn OFF dithering

        # Later versions of Pillow (4.x) rename _makeself to _new
        try:
            return silf._new(im)
        except AttributeError:
            return silf._makeself(im)

    def printLine(self, draw: ImageDraw, caption: Caption):
        text = caption.get_text()

        fnt = ImageFont.truetype(os.path.dirname(__file__) + '/NotoSansDisplay-Regular.ttf', 30)
        txtWidth, txtHeight = draw.textsize(text, font=fnt)
        x = self.video_width / 2 - txtWidth / 2
        y = self.video_height - txtHeight - 10 # padding for readability

        borderColor = self.e2Color
        fontColor = self.paColor
        for adj in range(3):
            # move right
            draw.text((x - adj, y), text, font=fnt, fill=borderColor)
            # move left
            draw.text((x + adj, y), text, font=fnt, fill=borderColor)
            # move up
            draw.text((x, y + adj), text, font=fnt, fill=borderColor)
            # move down
            draw.text((x, y - adj), text, font=fnt, fill=borderColor)
            # diagnal left up
            draw.text((x - adj, y + adj), text, font=fnt, fill=borderColor)
            # diagnal right up
            draw.text((x + adj, y + adj), text, font=fnt, fill=borderColor)
            # diagnal left down
            draw.text((x - adj, y - adj), text, font=fnt, fill=borderColor)
            # diagnal right down
            draw.text((x + adj, y - adj), text, font=fnt, fill=borderColor)

        draw.text((x, y), text, font=fnt, fill=fontColor)
        pass