
from pycaption.srt import SRTReader
from pycaption.scenarist import ScenaristDVDWriter


srtReader = SRTReader()
c = srtReader.read(content=open("cookoff-1080p-h264-tidpix.srt", "rb").read().decode('UTF-8-SIG'), lang='zh-Hans')
w = ScenaristDVDWriter()
open("cookoff-1080p-h264-tidpix.zip", "wb").write(w.write(c))

