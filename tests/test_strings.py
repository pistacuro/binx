from binx.strings import get_length_prefixed_string_bytes
from binx.types import LengthPrefixedString
from tests.test_utils import FakeByteReader



def test_get_string_bytes():

    ko_string = "아니, 익숙한 기분이 들어."
    eng_string = "test string"
    long_string = ("System.Collections.Generic.Dictionary`2[[System.Int32, mscorlib,"
                   " Version=2.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e0"
                   "89],[System.Collections.Generic.List`1[[Table_PCStory, Assembly-"
                   "CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]],"
                   " mscorlib, Version=2.0.0.0, Culture=neutral, PublicKeyToken=b77a"
                   "5c561934e089]]")

    ko_bytes = get_length_prefixed_string_bytes(ko_string)

    ko_fbr = FakeByteReader(ko_bytes)

    ko_lps = LengthPrefixedString()
    ko_lps.read_data_from_stream(ko_fbr)

    assert ko_lps.value == ko_string
    assert ko_lps.size == 35

    eng_bytes = get_length_prefixed_string_bytes(eng_string)

    eng_fbr = FakeByteReader(eng_bytes)

    eng_lps = LengthPrefixedString()
    eng_lps.read_data_from_stream(eng_fbr)

    assert eng_lps.value == eng_string
    assert eng_lps.size == 11

    long_bytes = get_length_prefixed_string_bytes(long_string)

    long_fbr = FakeByteReader(long_bytes)

    long_lps = LengthPrefixedString()
    long_lps.read_data_from_stream(long_fbr)

    assert long_lps.value == long_string
    assert long_lps.size == 334