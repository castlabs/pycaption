SAMPLE_PL_STT_HEADER = """[HEADER]
SUBTITLING_COMPANY=Pixelogic Media
TIME_FRAME_RATE=24
TIME_FORMAT=NONDROP
TIME_CONTENT_IN=00:00:00:00
LANGUAGE=Spanish (Latin)
TITLE=Menu, The
[/HEADER]"""

SAMPLE_PL_STT_HEADER_NO_FRAMERATE = """[HEADER]
SUBTITLING_COMPANY=Pixelogic Media
TIME_FORMAT=NONDROP
TIME_CONTENT_IN=00:00:00:00
LANGUAGE=Spanish (Latin)
TITLE=Menu, The
[/HEADER]"""

SAMPLE_PL_STT_HEADER_WRONG_FORMAT = """[HEADER]
FOOBAR
[/HEADER]"""

SAMPLE_PL_STT_BODY = """[BODY]
[1]
00:00:50:00
00:00:54:00
[CENTER]First caption
With a line break
[2]
00:00:55:00
00:00:58:12
[TOP]Second [I]caption[/I], no line break
[3]
00:01:05:00
00:01:06:12
[BOTTOM]Third caption
[4]
00:01:06:20
00:01:09:08
Three
Line
Caption
[5]
00:01:09:10
00:01:11:13
Last caption,
also has a line break
[/BODY]"""

SAMPLE_PL_STT = f"""{SAMPLE_PL_STT_HEADER}
{SAMPLE_PL_STT_BODY}
"""

SAMPLE_PL_STT_NO_HEADER = f"""{SAMPLE_PL_STT_BODY}
"""

SAMPLE_PL_STT_BAD_HEADER_1 = f"""{SAMPLE_PL_STT_HEADER_WRONG_FORMAT}
{SAMPLE_PL_STT_BODY}
"""
