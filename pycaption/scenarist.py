import os
import tempfile
import zipfile
from datetime import timedelta
from io import BytesIO

from PIL import Image

from pycaption.base import CaptionSet
from pycaption.subtitler_image_based import SubtitleImageBasedWriter


def get_sst_pixel_display_params(video_width, video_height):
    py0 = 2
    py1 = video_height - 1

    dx0 = 0
    dy0 = 2

    dx1 = video_width - 1
    dy1 = video_height - 1

    return py0, py1, dy0, dy1, dx0, dx1


HEADER = """st_format 2
SubTitle\tFace_Painting
Tape_Type\t{tape_type}
Display_Start\tnon_forced
Pixel_Area\t({py0} {py1})
Display_Area\t({dx0} {dy0} {dx1} {dy1})
Color\t{color}
Contrast\t{contrast}
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


class ScenaristDVDWriter(SubtitleImageBasedWriter):

    tiff_compression = None

    def __init__(self, relativize=True, video_width=720, video_height=480, fit_to_screen=True, tape_type='NON_DROP',
                 frame_rate=25, compat=False):
        super().__init__(relativize, video_width, video_height, fit_to_screen, frame_rate)
        self.tape_type = tape_type
        self.frame_rate = frame_rate

        if compat:
            self.color = '(1 2 3 4)'
            self.contrast = '(15 15 15 0)'
        else:
            self.color = '(0 1 2 3)'
            self.contrast = '(7 7 7 7)'

    def save_image(self, tmp_dir, index, img):
        """Convert RGBA to paletted image for DVD subtitles."""
        # Replace transparent pixels with green background
        background = Image.new('RGB', img.size, self.bgColor)
        background.paste(img, mask=img.split()[3])  # Use alpha channel as mask

        # Quantize to 4-color palette
        img_quant = background.quantize(palette=self.palette_image, dither=0)
        img_quant.save(tmp_dir + '/subtitle%04d.tif' % index, compression=self.tiff_compression)

    def write(
            self,
            caption_set: CaptionSet,
            position='bottom',
            avoid_same_next_start_prev_end=False,
            tiff_compression='tiff_deflate',
            align='center'
    ):
        self.tiff_compression = tiff_compression
        lang = caption_set.get_languages().pop()
        caps = caption_set.get_captions(lang)


        buf = BytesIO()
        with tempfile.TemporaryDirectory() as tmpDir:
            caps_final, overlapping = self.write_images(caps, lang, tmpDir, position, align, avoid_same_next_start_prev_end)
            with open(tmpDir + '/subtitles.sst', 'w+') as sst:
                index = 1
                py0, py1, dy0, dy1, dx0, dx1 = get_sst_pixel_display_params(self.video_width, self.video_height)
                sst.write(HEADER.format(
                    py0=py0, py1=py1,
                    dx0=dx0, dy0=dy0, dx1=dx1, dy1=dy1,
                    bg_red=self.bgColor[0], bg_green=self.bgColor[1], bg_blue=self.bgColor[2],
                    pa_red=self.paColor[0], pa_green=self.paColor[1], pa_blue=self.paColor[2],
                    e1_red=self.e1Color[0], e1_green=self.e1Color[1], e1_blue=self.e1Color[2],
                    e2_red=self.e2Color[0], e2_green=self.e2Color[1], e2_blue=self.e2Color[2],
                    tape_type=self.tape_type, color=self.color, contrast=self.contrast
                ))

                for i, cap_list in enumerate(caps_final):
                    sst.write("%04d %s %s subtitle%04d.tif\n" % (
                        index,
                        self.format_ts(cap_list[0].start),
                        self.format_ts(cap_list[0].end),
                        index
                    ))
                    index = index + 1
            zipit(tmpDir, buf)
        buf.seek(0)
        return buf.read()

    def format_ts(self, value):
        datetime_value = timedelta(seconds=(int(value / 1000000)))
        str_value = str(datetime_value)[:11]

        # make sure all numbers are padded with 0 to two places
        str_value = ':'.join([n.zfill(2) for n in str_value.split(':')])

        str_value = str_value + ':%02d' % (int((int(value / 1000) % 1000) / int(1000 / self.frame_rate)))
        return str_value
