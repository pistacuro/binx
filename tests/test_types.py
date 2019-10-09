from tests.test_utils import FakeByteReader
from binx.types import BinaryLibrary, LengthPrefixedString, SystemClassWithMembersAndTypes

def test_read_binary_library():
    binary_library_bytes = b'\x0C\x02\x00\x00\x00\x0fAssembly-CSharp'

    fbr = FakeByteReader(binary_library_bytes)
    bl = BinaryLibrary()
    bl.read_data_from_stream(fbr)

    assert bl.record_type_id == 12
    assert bl.library_id == 2
    assert bl.library_name.value == "Assembly-CSharp"
    assert bl.library_name.size == len("Assembly-CSharp")


def test_read_length_prefixed_string():
    length_prefixed_string_bytes = b'\x0fAssembly-CSharp'

    fbr = FakeByteReader(length_prefixed_string_bytes)
    lps = LengthPrefixedString()
    lps.read_data_from_stream(fbr)

    assert lps.raw_bytes == length_prefixed_string_bytes
    assert lps.size == len("Assembly-CSharp")
    assert lps.value == "Assembly-CSharp"


def test_read_system_class_with_members_and_types():
    system_class_bytes = (b'\x04\x06\x00\x00\x00\xe2\x01System.Collections.Generic.Dictionary'
                          b'`2[[System.String, mscorlib, Version=2.0.0.0, Culture=neutral,'
                          b' PublicKeyToken=b77a5c561934e089],[Table_StartPackage, Assembl'
                          b'y-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=nul'
                          b'l]]\x04\x00\x00\x00\x07Version\x08Comparer\x08HashSize\rKeyVal'
                          b'uePairs\x00\x03\x00\x03\x08\x92\x01System.Collections.Generic.'
                          b'GenericEqualityComparer`1[[System.String, mscorlib, Version=2.'
                          b'0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]\x08'
                          b'\xe6\x01System.Collections.Generic.KeyValuePair`2[[System.Strin'
                          b'g, mscorlib, Version=2.0.0.0, Culture=neutral, PublicKeyToken='
                          b'b77a5c561934e089],[Table_StartPackage, Assembly-CSharp, Versio'
                          b'n=0.0.0.0, Culture=neutral, PublicKeyToken=null]][]\x01\x00\x00'
                          b'\x00\tM\x00\x00\x00\x0c\x00\x00\x00\tQ\x00\x00\x00')

    fbr = FakeByteReader(system_class_bytes)
    scwmt = SystemClassWithMembersAndTypes()
    scwmt.read_data_from_stream(fbr)

    assert scwmt.record_type_id == 4
    assert scwmt.class_info
    assert scwmt.class_info.object_id == 6
    assert scwmt.class_info.member_count == 4
    assert len(scwmt.class_info.member_names) == scwmt.class_info.member_count

    expected_names = ["Version", "Comparer", "HashSize", "KeyValuePairs"]
    for name in scwmt.class_info.member_names:
        assert name.value in expected_names

    expected_enums = [
        {'type': 'Primitive'}, {'type': 'SystemClass'}, 
        {'type': 'Primitive'}, {'type': 'SystemClass'}]
    assert scwmt.member_type_info.binary_type_enums == expected_enums

    assert not scwmt.library_id
    assert len(scwmt.member_type_info.additional_infos) == 4
    expected_primitive = {'type': 'Primitive', 'primitive': {'type': 'Int32'}}
    assert scwmt.member_type_info.additional_infos[0] == expected_primitive
    assert scwmt.member_type_info.additional_infos[1]["type"] == "SystemClass"
    expected_string = ('System.Collections.Generic.GenericEqualityComparer`1[[System.String,'
                       ' mscorlib, Version=2.0.0.0, Culture=neutral, PublicKeyToken=b77a5c56'
                       '1934e089]]')
    assert scwmt.member_type_info.additional_infos[1]["name"].value == expected_string
    assert scwmt.member_type_info.additional_infos[2] == expected_primitive
    assert scwmt.member_type_info.additional_infos[3]["type"] == "SystemClass"
    expected_string = ('System.Collections.Generic.KeyValuePair`2[[System.String, mscorlib, '
                       'Version=2.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089],['
                       'Table_StartPackage, Assembly-CSharp, Version=0.0.0.0, Culture=neutra'
                       'l, PublicKeyToken=null]][]')
    assert scwmt.member_type_info.additional_infos[3]["name"].value == expected_string


def test_read_binary_object_string():
    pass


def test_read_class_with_id():
    pass


def test_read_member_reference():
    pass


def test_read_class_with_members_and_types():
    pass
