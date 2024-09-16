import pytest


@pytest.fixture(scope="session")
def sample_scc_created_dfxp_with_wrongly_closing_spans():
    return """\
Scenarist_SCC V1.0

00:01:28;09 9420 94ae 9420 9452 8080 e3e3 e3e3 e3e3 9470 8080 e3a1 e3a1 942f

00:01:31;10 9420 942f 94ae

00:01:31;18 9420 9454 6262 6262 9458 8080 91ae e3e3 e3e3 9470 8080 6262 6161 942f

00:01:35;18 9420 942f 94ae

00:01:40;25 942c

00:01:51;18 9420 9452 8080 6161 94da 8080 91ae 6262 9470 8080 e3e3 942f

00:01:55;22 9420 6162 e364 94f4 8080 6162 e364 942f

00:01:59;14 9420 942f 94ae
"""


@pytest.fixture(scope="session")
def scc_that_generates_webvtt_with_proper_newlines():
    return """\
Scenarist_SCC V1.0

00:21:29;23    9420 9452 6161 94f4 97a2 6262 942c 942f
"""


@pytest.fixture(scope="session")
def sample_scc_produces_captions_with_start_and_end_time_the_same():
    return """\
Scenarist_SCC V1.0

00:01:31;18 9420 9454 6162 9758 97a1 91ae 6261 9170 97a1 e362

00:01:35;18 9420 942f 94ae

00:01:40;25 942c
"""


@pytest.fixture(scope="session")
def sample_scc_pop_on():
    return """Scenarist_SCC V1.0

00:00:09:05 94ae 94ae 9420 9420 9470 9470 a820 e3ec efe3 6b20 f4e9 e36b e96e 6720 2980 942c 942c 942f 942f

00:00:12:08 942c 942c

00:00:13:18 94ae 94ae 9420 9420 1370 1370 cdc1 ceba 94d0 94d0 5768 e56e 20f7 e520 f468 e96e 6b80 9470 9470 efe6 20a2 4520 e5f1 7561 ec73 206d 20e3 ad73 f175 61f2 e564 a22c 942c 942c 942f 942f

00:00:16:03 94ae 94ae 9420 9420 9470 9470 f7e5 2068 6176 e520 f468 e973 2076 e973 e9ef 6e20 efe6 2045 e96e 73f4 e5e9 6e80 942c 942c 942f 942f

00:00:17:20 94ae 94ae 9420 9420 94d0 94d0 6173 2061 6e20 efec 642c 20f7 f2e9 6e6b ec79 206d 616e 9470 9470 f7e9 f468 20f7 68e9 f4e5 2068 61e9 f2ae 942c 942c 942f 942f

00:00:19:13 94ae 94ae 9420 9420 1370 1370 cdc1 ce20 32ba 94d0 94d0 4520 e5f1 7561 ec73 206d 20e3 ad73 f175 61f2 e564 20e9 7380 9470 9470 6eef f420 6162 ef75 f420 616e 20ef ec64 2045 e96e 73f4 e5e9 6eae 942c 942c 942f 942f

00:00:25:16 94ae 94ae 9420 9420 1370 1370 cdc1 ce20 32ba 94d0 94d0 49f4 a773 2061 ecec 2061 62ef 75f4 2061 6e20 e5f4 e5f2 6e61 ec80 9470 9470 45e9 6e73 f4e5 e96e ae80 942c 942c 942f 942f

00:00:31:15 94ae 94ae 9420 9420 9470 9470 bc4c c1d5 c7c8 49ce c720 2620 57c8 4f4f d0d3 a13e 942c 942c 942f 942f

00:00:36:04 942c 942c

"""


# 6 captions
#   2 Pop-On captions.
#       The first has 3 random positions, and thus 3 captions
#       The second should be interpreted as 1 caption with 2 line breaks
#   2 Roll-Up captions - same comment
#   2 Paint-on captions - same comment
@pytest.fixture(scope="session")
def sample_scc_multiple_positioning():
    return """Scenarist_SCC V1.0

00:00:00:16 94ae 94ae 9420 9420 1370 1370 6162 6162 91d6 91d6 e364 e364 92fd 92fd e5e6 e5e6 942c 942c 942f 942f

00:00:02:16 94ae 94ae 9420 9420 16f2 16f2 6768 6768 9752 9752 e9ea e9ea 97f2 97f2 6bec 6bec 942c 942c 942f 942f

00:00:09:21 9425 9425 94ad 94ad 94f2 94f2 6d6e 6d6e 97d6 97d6 ef70 ef70 92dc 92dc f1f2 f1f2

00:00:11:21 9425 9425 94ad 94ad 15f2 15f2 73f4 73f4 1652 1652 7576 7576 16f2 f7f8 f7f8

00:00:20:02 9429 9429 9452 9452 97A2 97A2 797A 797A 917c 917c B031 B031 16d6 16d6 32B3 32B3

00:00:22:02 9429 9429 1352 1352 97A2 97A2 34B5 34B5 13f2 13f2 B637 B637 9452 9452 38B9 38B9

00:00:36:04 942c 942c

"""


# UNUSED SAMPLE
@pytest.fixture(scope="session")
def sample_scc_with_italics_bkup():
    return """\
Scenarist_SCC V1.0

00:00:00:01 9420 10d0 97a2 91ae 6162 6162 6162 6162 942c 8080 8080 942f
"""


@pytest.fixture(scope="session")
def sample_scc_with_italics():
    return """\

00:00:00:01 9420 10d0 97a2 91ae 6162 6162 6162 6162 942c 8080 8080 942f
"""


@pytest.fixture(scope="session")
def sample_scc_empty():
    return """Scenarist_SCC V1.0
"""


@pytest.fixture(scope="session")
def sample_scc_roll_up_ru2():
    return """\
Scenarist_SCC V1.0
00:00:00;22    9425 9425 94ad 94ad 9470 9470 3e3e 3e20 c849 ae80

00:00:02;23    9425 9425 94ad 94ad 9470 9470 49a7 cd20 cb45 d649 ce20 43d5 cece 49ce c720 c1ce c420 c154

00:00:04;17    9425 9425 94ad 94ad 9470 9470 49ce d645 d354 4f52 a7d3 20c2 c1ce cb20 5745 20c2 454c 4945 d645 2049 ce80

00:00:06;04    9425 9425 94ad 94ad 9470 9470 c845 4cd0 49ce c720 54c8 4520 4c4f 43c1 4c20 ce45 49c7 c8c2 4f52 c84f 4fc4 d380

00:00:09;21    9425 9425 94ad 94ad 9470 9470 c1ce c420 49cd d052 4fd6 49ce c720 54c8 4520 4c49 d645 d320 4f46 20c1 4c4c

00:00:11;07    9425 9425 94ad 94ad 9470 9470 5745 20d3 4552 d645 ae80

00:00:12;07    9425 9425 94ad 94ad 9470 9470 91b0 9131 9132 9132

00:00:12;30    9425 94ad 94ad 9470 9470 91b0 9131 9132 9132

00:00:13;07    9425 9425 94ad 94ad 9470 9470 c1c2 c3c4 c580 91bf

00:00:14;07    9425 9425 94ad 94ad 9470 9470 9220 9220 92a1 92a2 92a7

00:00:17;01    9426 9426 94ad 94ad 9470 9470 57c8 4552 4520 d94f d5a7 5245 20d3 54c1 cec4 49ce c720 ce4f 572c

00:00:18;19    9426 9426 94ad 94ad 9470 9470 4c4f 4fcb 49ce c720 4fd5 5420 54c8 4552 452c 2054 c8c1 54a7 d320 c14c 4c

00:00:20;06    9426 9426 94ad 94ad 9470 9470 54c8 4520 4352 4f57 c4ae

00:00:21;24    9426 9426 94ad 94ad 9470 9470 3e3e 2049 5420 57c1 d320 c74f 4fc4 2054 4f20 c245 2049 ce20 54c8 45

00:00:34;27    94a7 94ad 9470 c16e 6420 f2e5 73f4 eff2 e520 49ef f761 a773 20ec 616e 642c 20f7 61f4 e5f2

00:00:36;12    94a7 94ad 9470 c16e 6420 f7e9 ec64 ece9 e6e5 ae80

00:00:44;08    94a7 94ad 9470 3e3e 20c2 e96b e520 49ef f761 2c20 79ef 75f2 2073 ef75 f2e3 e520 e6ef f280
"""


@pytest.fixture(scope="session")
def sample_scc_roll_up_ru3():
    return """\
Scenarist_SCC V1.0
00:00:00;22    9425 9425 94ad 94ad 9470 9470 3e3e 3e20 c849 ae80

00:00:02;23    9425 9425 94ad 94ad 9470 9470 49a7 cd20 cb45 d649 ce20 43d5 cece 49ce c720 c1ce c420 c154

00:00:04;17    9425 9425 94ad 94ad 9470 9470 49ce d645 d354 4f52 a7d3 20c2 c1ce cb20 5745 20c2 454c 4945 d645 2049 ce80

00:00:06;04    9425 9425 94ad 94ad 9470 9470 c845 4cd0 49ce c720 54c8 4520 4c4f 43c1 4c20 ce45 49c7 c8c2 4f52 c84f 4fc4 d380

00:00:09;21    9425 9425 94ad 94ad 9470 9470 c1ce c420 49cd d052 4fd6 49ce c720 54c8 4520 4c49 d645 d320 4f46 20c1 4c4c

00:00:11;07    9425 9425 94ad 94ad 9470 9470 5745 20d3 4552 d645 ae80

00:00:12;07    9425 9425 94ad 94ad 9470 9470 91b0 9131 9132 9132

00:00:13;07    9425 9425 94ad 94ad 9470 9470 c1c2 c3c4 c580 91bf

00:00:14;07    9425 9425 94ad 94ad 9470 9470 9220 9220 92a1 92a2 92a7

00:00:17;01    9426 9426 94ad 94ad 9470 9470 57c8 4552 4520 d94f d5a7 5245 20d3 54c1 cec4 49ce c720 ce4f 572c

00:00:18;19    9426 9426 94ad 94ad 9470 9470 4c4f 4fcb 49ce c720 4fd5 5420 54c8 4552 452c 2054 c8c1 54a7 d320 c14c 4c

00:00:20;06    9426 9426 94ad 94ad 9470 9470 54c8 4520 4352 4f57 c4ae

00:00:21;24    9426 9426 94ad 94ad 9470 9470 3e3e 2049 5420 57c1 d320 c74f 4fc4 2054 4f20 c245 2049 ce20 54c8 45

00:00:34;27    94a7 94ad 9470 c16e 6420 f2e5 73f4 eff2 e520 49ef f761 a773 20ec 616e 642c 20f7 61f4 e5f2

00:00:36;12    94a7 94ad 9470 c16e 6420 f7e9 ec64 ece9 e6e5 ae80

00:00:44;08    94a7 94ad 9470 3e3e 20c2 e96b e520 49ef f761 2c20 79ef 75f2 2073 ef75 f2e3 e520 e6ef f280
"""


@pytest.fixture(scope="session")
def sample_no_positioning_at_all_scc():
    return """\
Scenarist_SCC V1.0

00:23:28;01    9420 94ae 5245 c1c2 942f

00:24:29;21    942c

00:53:28;01    9420 94ae 4552 aeae 942f

00:54:29;21    942c
"""


# UNUSED SAMPLE
@pytest.fixture(scope="session")
def sample_scc_not_explicitly_switching_italics_off():
    return """\
Scenarist_SCC V1.0

00:01:28;09    9420 942f 94ae 9420 9452 97a2 b031 6161 9470 9723 b031 6262

00:01:31;10    9420 942f 94ae

00:01:31;18    9420 9454 b032 e3e3 9458 97a1 91ae b032 6464 9470 97a1 b032 e5e5

00:01:35;18    9420 942f 94ae

00:01:40;25    942c

00:01:51;18    9420 9452 97a1 b0b3 6161 94da 97a2 91ae b0b3 6262 9470 97a1 b0b3 e3e3

00:01:55;22    9420 942f b034 6161 94f4 9723 b034 6262

00:01:59;14    9420 942f 94ae 9420 94f4 b034 3180 e3e3

00:02:02;01    9420 942f 94ae 9420 94d0 b0b5 6161 94f2 97a2 b0b5 6262

00:02:04;05    9420 942f 94ae

00:09:53;06    942c 9420 13f4 9723 b0b6 e3e3 9454 97a2 b0b6 6464 9470 97a2 b0b6 e5e5

00:09:56;09    9420 942f 94ae 9420 94f2 b037 6161

00:09:58;18    9420 942f 94ae 9420 9454 b038 6262 9454 97a2 91ae b038 e3e3 94f2 97a1 94f2 97a1 91ae b038 6162 6464

00:09:59;28    9420 942f 94ae 9420 9452 97a2 e5e5 94f4 b0b9 6161

00:10:02;22    9420 942f 94ae 9420 9452 97a1 31b0 e5e5 9470 97a2 31b0 6262

00:10:04;10    9420 942f 94ae

00:52:03;02    9420 9470 97a2 3131 e3e3

00:52:18;20    9420 91d0 9723 3132 6464 9158 97a1 91ae 3132 e5e5 91da 97a2 9120 3132 6161 91f2 9723 3132 6262

00:52:22;22    9420 942c 942f 9420 9152 97a2 31b3 e3e3

00:52:25;04    9420 942c 942f 9420 91d0 97a2 3134 6464 91f2 e5e5

00:52:26;28    9420 942c 942f

00:52:27;18    9420 9152 9152 9152 91ae 31b5 6161 9154 97a1 9120 31b5 6262 9170 9723 31b5 e3e3

00:52:31;22    9420 942c 942f

00:52:34;14    942c

00:53:03;15    9420 94f4 97a1 94f4 97a1 91ae 31b6 6464
"""


@pytest.fixture(scope="session")
def sample_scc_no_explicit_end_to_last_caption():
    return """\
Scenarist_SCC V1.0

00:00:00;00    73e9 e329 942f

00:00:06;01    942c

00:24:55;14    9420 94ae 9470 97a2 a875 7062 e561 f420 f2ef e36b 206d 7573 e9e3 2980 942f
"""


@pytest.fixture(scope="session")
def sample_scc_flashing_cue():
    return """\
Scenarist_SCC V1.0

00:00:00;20 9420 9420 942c 942c 942f 942f 9420 9420 9152 9152 4fd5 5220 cec1 5449 4fce c14c 20d0 c152 cbd3 91f2 91f2 c245 4c4f cec7 2054 4f20 c14c 4c20 4f46 20d5 d3ae

00:00:02;02 9420 9420 942c 942c 942f 942f 9420 9420 91d0 91d0 54c8 45d9 20c1 5245 20d0 4cc1 4345 d320 4f46 20c4 49d3 434f d645 52d9 2c80 9170 9170 54c8 45d9 20c1 5245 20d0 4cc1 4345 d320 4f46 2049 ced3 d049 52c1 5449 4fce 2c80

00:00:04;29 9420 9420 942c 942c 942f 942f

00:00:06;08 9420 9420 9154 9154 54c8 45d9 20c1 5245 91f2 91f2 c1cd 4552 4943 c1a7 d320 c245 d354 2049 c445 c1ae

00:00:09;24 9420 9420 942c 942c 942f 942f

00:00:10;06 9420 9420 9152 9152 cdc1 4a4f 5220 46d5 cec4 49ce c720 d052 4fd6 49c4 45c4 20c2 d980

00:00:13;19 9420 9420 942c 942c 942f 942f 9420 9420 9154 9154 54c8 4520 45d6 454c d9ce 9170 9170 c1ce c420 57c1 4c54 4552 20c8 c1c1 d32c 204a 52ae 2046 d5ce c4ae

00:00:15;11 9420 9420 942c 942c 942f 942f

00:00:16;08 9420 9420 9152 9152 c1c4 c449 5449 4fce c14c 2046 d5ce c449 cec7 91f2 91f2 57c1 d320 d052 4fd6 49c4 45c4 20c2 d9ba

00:00:19;19 9420 94ae 9152 9723 c1c4 c449 5449 4fce c14c 2046 d5ce c449 cec7 91f4 57c1 d320 d052 4fd6 49c4 45c4 20c2 d9ba 942c

00:00:20;13 942f 942c

00:00:21;19 9420 94ae 9152 9723 54c8 4520 d0c1 52cb 2046 4fd5 cec4 c154 494f ce80 942c

00:00:22;07 942f 942c

00:00:22;14 9420 94ae 9152 97a2 49ce 20d3 d5d0 d04f 5254 204f 4620 c120 434c 45c1 ce80 91f2 c1ce c420 c845 c14c 54c8 d920 45ce d649 524f cecd 45ce 543b 942c

00:00:23;15 942f 942c

00:00:25;09 9420 94ae 9152 97a1 54c8 4520 c152 54c8 d552 20d6 49ce 49ce c720 c4c1 d649 d380 91f4 97a2 464f d5ce c4c1 5449 4fce d32c 942c

00:00:26;06 942f 942c

00:00:27;15 9420 94ae 91d0 9723 c445 c449 43c1 5445 c420 544f 20d3 5452 45ce c754 c845 ce49 cec7 91f4 c1cd 4552 4943 c1a7 d320 46d5 54d5 5245 942c

00:00:28;14 942f 942c
"""


@pytest.fixture(scope="session")
def sample_scc_eoc_first_command():
    return """\
Scenarist_SCC V1.0

00:00:00;84    942f

00:00:02;00    73e9 e329 942f

00:00:06;01    942c

00:24:55;14    9420 94ae 9470 97a2 a875 7062 e561 f420 f2ef e36b 206d 7573 e9e3 2980 942f

00:25:00;00    942c
"""


@pytest.fixture(scope="session")
def sample_scc_with_extended_characters():
    return """\
Scenarist_SCC V1.0

00:04:36;06	9420 942c 942f 9420 91d6 cdc1 13b0 5254 c8c1 ba80 942f
00:22:32:18	9420 942c 942f 9420 9454 97a1 4ad5 ce49 4f52 ba20 a180 92a7 d975 6da1 9470 9723 d961 206d e520 73e9

00:22:34:28	942c e56e f4ef 206d 75e3 68ef 206d e5ea eff2 ae80 9420 942c 942f 9420 94f2 9723 4ad5 ce49 4f52 ba20 4f79 e52c 20c1 ec6d 612c
"""


@pytest.fixture(scope="session")
def sample_scc_with_ampersand_character():
    return """\
Scenarist_SCC V1.0

00:04:36;06	 9420 9420 9152 9152 cdc1 4a4f 5220 46d5 cec4 49ce c720 d052 4fd6 49c4 45c4 20c2 d980 2026 942f
"""


@pytest.fixture(scope="session")
def sample_scc_multiple_formats():
    return """\
Scenarist_SCC V1.0

00:00:00;00	942c 1c2c

00:00:00;08	9429 9152 97a2 a843 ece9 e56e f4a7 7320 d6ef e9e3 e529 91f2 97a2 52e5 6de5 6d62 e5f2 20f4 6861 f420 64e5 67f2 e5e5 9252 97a2 79ef 7520 67ef f420 e96e 20f4 61f8 61f4 e9ef 6ebf 9420 9152 97a2 a8c4 616e 6e79 2980 91f2 97a2 4fe6 20e3 ef75 f273 e520 79ef 7520 64ef 6ea7 f480 9252 97a2 62e5 e361 7573 e520 79ef 7520 64e9 646e a7f4 a180

00:00:02;15	9420 942c 942f 9420 91d0 9723 d9ef 75f2 20ea ef62 20e9 736e a7f4 2064 efe9 6e67 2068 61f2 6480 9170 9723 f7ef f26b aeae ae80

00:00:04;15	9420 942c 942f 9420 91d0 97a2 aeae aee9 f4a7 7320 6d61 6be9 6e67 20f4 68e5 6d20 64ef 2068 61f2 6480 9170 97a2 f7ef f26b aeae ae80

00:00:06;03	9420 942c 942f 9420 91d0 97a2 aeae ae61 6e64 2067 e5f4 f4e9 6e67 2070 61e9 6420 e6ef f220 e9f4 ae80

00:00:08;04	9420 942c 942f 9420 91d0 97a1 a8d6 4f29 9170 97a1 d36e 6170 2061 6e64 2073 eff2 f420 79ef 75f2 20e5 f870 e56e 73e5 7320 f4ef 92d0 97a1 7361 76e5 20ef 76e5 f220 a434 2cb6 b0b0 2061 f420 f461 f820 f4e9 6de5 ae80

00:00:09;18	9420 942c 942f 9420 9152 51d5 4943 cbc2 4f4f cbd3 ae20 c2c1 43cb 49ce c720 d94f d5ae

00:00:13;04	9420 942c 942f

"""


@pytest.fixture(scope="session")
def sample_scc_duplicate_tab_offset():
    return """\
Scenarist_SCC V1.0

00:00:29:04 9420 1370 97a1 1370 97a1 91ae 5b52 6164 e9ef 20f2 e570 eff2 f4e5 f25d 94d0 97a1 94d0 97a1 91ae 5468 e520 49ad 31b0 20d3 616e f461 20cd ef6e e9e3 6120 46f2 e5e5 f761 7980 9470 97a1 9470 97a1 91ae f7e5 73f4 62ef 756e 6420 e973 20ea 616d 6de5 642c 9420 942c 942f 9420 94d0 97a2 94d0 97a2 91ae 6475 e520 f4ef 2061 20f4 68f2 e5e5 ade3 61f2 2061 e3e3 e964 e56e f480 9470 97a2 9470 97a2 91ae 62ec efe3 6be9 6e67 20ec 616e e573 2031 2061 6e64 2032 942f
"""


@pytest.fixture(scope="session")
def sample_scc_duplicate_special_characters():
    return """\
Scenarist_SCC V1.0

00:23:28;01 9420 9420 91b0 91b0 9131 9131 9132 9132 91b3 91b3 9134 9134 91b5 91b5 91b6 91b6 9137 9137 9138 9138 91b9 91b9 91ba 91ba 913b 913b 91bc 91bc 913d 913d 913e 913e 91bf 91bf 942f

00:33:28;01 9420 91b0 9131 9132 91b3 9134 91b5 91b6 9137 9138 91b9 91ba 913b 91bc 913d 913e 91bf 942f

00:53:28;01 9420 91b0 9131 c1c1 9132 91b3 9134 91b5 91b6 9137 9138 91b9 91ba 913b 91bc c1c1 913d 913e 91bf 942f

"""


@pytest.fixture(scope="session")
def sample_scc_tab_offset():
    return """\
Scenarist_SCC V1.0

00:00:00;00	9420 9420

00:00:00;03	942f 9420 9454 9723 cec1 5252 c154 4f52 ba80 9470 97a1 5468 e520 f7ef f2ec 6420 efe6 20f7 eff2 6b20 e973 20e3 6861 6e67 e96e 67ae

00:00:02;01	9420 942c 942f

00:00:02;08	9420 9470 9723 c2d9 524f ce20 c1d5 c7d5 d354 45ba 2054 68e5 20e6 75f4 75f2 e580

00:00:05;24	9420 942c 942f 9420 94d0 97a1 e973 2067 efe9 6e67 20f4 ef20 62e5 2076 e5f2 7920 64e9 e6e6 e5f2 e56e f480 94f4 97a1 f468 616e 20f4 68e5 2070 6173 f4ae 9420 942c 942f 9420 9452 9723 cec1 5252 c154 4f52 ba20 52ef 62ef f4e9 e373 9470 97a2 616e 6420 61f2 f4e9 e6e9 e3e9 61ec 20e9 6ef4 e5ec ece9 67e5 6ee3 e580

00:00:09;10	9420 942c 942f 9420 94f4 61f2 e520 ef6e 20f4 68e5 20f2 e973 e5ae

00:00:12;00	9420 942c 942f 9420 9454 97a2 cbc1 49ad 46d5 204c 4545 ba80 94f2 97a1 57e5 a7f2 e520 6275 e9ec 64e9 6e67 2073 7973 f4e5 6d73

00:00:13;06	9420 942c 942f 9420 94d0 9723 f468 61f4 20e3 616e 2064 e9f2 e5e3 f4ec 7920 f2e5 70ec 61e3 e580 94f2 97a1 6875 6d61 6e20 eaef 6273 2061 6e64 20f4 6173 6b73 ae80

00:00:15;26	9420 942c 942f """


@pytest.fixture(scope="session")
def sample_scc_with_unknown_commands():
    return """\
Scenarist_SCC V1.0

00:04:36;06 942x 942x 942x 942x 91d6 cdc1 13b0 525x c8cx ba8x
"""


@pytest.fixture(scope="session")
def sample_scc_special_and_extended_characters():
    return """\
Scenarist_SCC V1.0

00:00:16;29 2080 91b0 9131 9132 91b3 9134 91b5 91b6 

00:04:36;06 9137 9138 91b9 91ba 913b 91bc 913d 913e 91bf

00:08:00;00 92a1 92a2 9223 92a4 9225 9226 92a7 92a8 9229 922a 92ab

00:12:00;23 922c 92ad 92ae 922f 92b0 9231 9232 92b3 9234 92b5 92b6 9237 9238 

00:16:24;11 92b9 92ba 923b 92bc 923d 923e 92bf 1320 13a1 13a2 1323 13a4 1325

00:20:19;12 1326 13a7 13a8 1329 132a 13ab 132c 13ad 13ae 132f 13b0 1331 1332

00:24:39;28 13b3 1334 13b5 13b6 1337 1338 13b9 13ba 133b 13bc 133d 133e 13bf
"""


@pytest.fixture(scope="session")
def sample_scc_with_line_too_long():
    return """\
Scenarist_SCC V1.0

00:00:00;03	942c

00:00:01;45	9420 91f4 cb45 4c4c d920 4ac1 cd45 d3ba 20c8 eff7 9254 f468 e520 7368 eff7 2073 f461 f2f4 e564 942c 8080 8080 942f

00:00:02;55	9420 91e0 9723 f761 7320 4361 ec20 ec20 ec20 ec20 ec20 ec20 ec20 ec20 ec20 ec20 ec20 ec20 ec20 ec20 ec20 ec20 ec20 ec20 ec20 ec20 ec20 ec20 ec20 ec20 ec20 ec20 ec20 ec20 ec20 c4e5 6ee9 73ef 6e2c 2061 20e6 f2e9 e56e 6480 9240 9723 efe6 20ef 75f2 732c 20f7 6173 2064 efe9 6e67 206d 7920 43c4 73ae 942c 8080 8080 942f

00:00:06;57	9420 94e0 c16e 6420 68e5 2073 61e9 642c 2049 20e3 616e 2064 ef20 6120 54d6 2073 68ef f7ae 942c 8080 8080 942f

00:00:08;58	9420 9452 4920 ea75 73f4 20f7 616e f4e5 6420 ef6e e520 7368 eff7 2c80 94f2 ea75 73f4 20f4 ef20 6861 76e5 2061 7320 6120 ece9 f4f4 ece5 942c 8080 8080 942f
"""


@pytest.fixture(scope="function")
def sample_scc_mid_row_before_text_pop():
    return """\
Scenarist_SCC V1.0

00:00:01:24	9420 91d0 9120 c1c2 20c1 c280 942f
    
"""


@pytest.fixture(scope="function")
def sample_scc_mid_row_before_text_roll():
    return """\
Scenarist_SCC V1.0

00:00:01:24	9425 91d0 9120 c1c2 20c1 c280

"""


@pytest.fixture(scope="session")
def sample_scc_mid_row_before_text_paint():
    return """\
Scenarist_SCC V1.0

00:00:01:24	9429 91d0 9120 c1c2 20c1 c280

"""


@pytest.fixture(scope="session")
def sample_scc_mid_row_following_text_no_text_before_italics_off_pop():
    return """\
Scenarist_SCC V1.0

00:00:01:24	9420 91ce 91ab 91ae c1c2 9120 c1c2 942f

"""


@pytest.fixture(scope="session")
def sample_scc_mid_row_following_text_no_text_before_italics_off_roll():
    return """\
Scenarist_SCC V1.0

00:00:01:24	9425 91ce 91ab 91ae c1c2 9120 c1c2 

"""


@pytest.fixture(scope="session")
def sample_scc_mid_row_following_text_no_text_before_italics_off_paint():
    return """\
Scenarist_SCC V1.0

00:00:01:24	9429 91ce 91ab 91ae c1c2 9120 c1c2 

"""


@pytest.fixture(scope="session")
def sample_scc_mid_row_following_text_no_text_before_italics_on_pop():
    return """\
Scenarist_SCC V1.0

00:00:01:24	9420 91d0 c1c2 91ae c1c2 942f

"""


@pytest.fixture(scope="session")
def sample_scc_mid_row_following_text_no_text_before_italics_on_roll():
    return """\
Scenarist_SCC V1.0

00:00:01:24	9425 91d0 c1c2 91ae c1c2 

"""


@pytest.fixture(scope="session")
def sample_scc_mid_row_following_text_no_text_before_italics_on_paint():
    return """\
Scenarist_SCC V1.0

00:00:01:24	9429 91d0 c1c2 91ae c1c2 

"""


@pytest.fixture(scope="session")
def sample_scc_mid_row_with_space_before_pop():
    return """\
Scenarist_SCC V1.0

00:00:01:24	9420 91d0 c180 c220 91ae c1c2 942f

"""


@pytest.fixture(scope="session")
def sample_scc_mid_row_with_space_before_roll():
    return """\
Scenarist_SCC V1.0

00:00:01:24	9425 91d0 c180 c220 91ae c1c2

"""


@pytest.fixture(scope="session")
def sample_scc_mid_row_with_space_before_paint():
    return """\
Scenarist_SCC V1.0

00:00:01:24	9429 91d0 c180 c220 91ae c1c2

"""


@pytest.fixture(scope="session")
def sample_scc_with_spaces_at_eol_pop():
    return """\
Scenarist_SCC V1.0

00:00:01:24	9420 91d0 c180 c220 91e0 c1c2 2020 2080 92c2 c1c2 2080 942f

"""


@pytest.fixture(scope="session")
def sample_scc_with_spaces_at_eol_roll():
    return """\
Scenarist_SCC V1.0

00:00:01:24	9425 91d0 c180 c220 91e0 c1c2 2020 2080 92c2 c1c2 2080

"""


@pytest.fixture(scope="session")
def sample_scc_with_spaces_at_eol_paint():
    return """\
Scenarist_SCC V1.0

00:00:01:24	9429 91d0 c180 c220 91e0 c1c2 2020 2080 92c2 c1c2 2080

"""
