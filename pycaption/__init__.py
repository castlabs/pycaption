import bs4

from .base import (
    CaptionConverter, CaptionNode, Caption, CaptionList, CaptionSet,
)
from .dfxp import DFXPWriter, DFXPReader
from .microdvd import MicroDVDReader, MicroDVDWriter
from .sami import SAMIReader, SAMIWriter
from .scenarist import ScenaristDVDWriter
from .srt import SRTReader, SRTWriter
from .scc import SCCReader, SCCWriter
from .scc.translator import translate_scc
from .transcript import TranscriptWriter
from .webvtt import WebVTTReader, WebVTTWriter
from .exceptions import (
    CaptionReadError, CaptionReadNoCaptions, CaptionReadSyntaxError, CaptionLineLengthError
)


__all__ = [
    'CaptionConverter', 'DFXPReader', 'DFXPWriter', 'MicroDVDReader',
    'MicroDVDWriter', 'SAMIReader', 'SAMIWriter', 'SRTReader', 'SRTWriter',
    'SCCReader', 'SCCWriter', 'translate_scc', 'WebVTTReader', 'WebVTTWriter',
    'CaptionReadError', 'CaptionReadNoCaptions', 'CaptionReadSyntaxError',
    'detect_format', 'CaptionNode', 'Caption', 'CaptionList', 'CaptionSet', 'ScenaristDVDWriter'
    'TranscriptWriter'
]

SUPPORTED_READERS = (
    DFXPReader, MicroDVDReader, WebVTTReader, SAMIReader, SRTReader, SCCReader,
)


def detect_format(caps):
    """
    Detect the format of the provided caption string.

    :returns: the reader class for the detected format.
    """
    if not len(caps):
        raise CaptionReadNoCaptions("Empty caption file")

    for reader in SUPPORTED_READERS:
        if reader().detect(caps):
            return reader

    return None
