import pytest


class FakeByteReader():
    def __init__(self, byte_string):
        self._byte_string = byte_string
        self._position = 0

    def read(self, size):
        if size > len(self._byte_string):
            raise IOError("Requested size (%s) is bigger then byte buffer (%s)!" % (
                size, len(self._byte_string)))
        bytes_read = self._byte_string[self._position:self._position+size]
        self._position += size
        return bytes_read

    def seek(self, new_pos):
        self._position = new_pos

    def tell(self):
        return self._position


def test_fake_reader_read():
    byte_string = b'\x01\x00\x00\x00\xff\xff\xff\xff\x01\x00\x00\x00\x00\x00\x00\x00'
    fbr = FakeByteReader(byte_string)

    root_id = fbr.read(4)
    header_id = fbr.read(4)
    major_version = fbr.read(4)
    minor_version = fbr.read(4)
    assert fbr.tell() == 16
    assert len(root_id) == 4
    assert len(header_id) == 4
    assert len(major_version) == 4
    assert len(minor_version) == 4
    assert int.from_bytes(root_id, byteorder="little") == 1
    assert int.from_bytes(header_id, byteorder="little") == 4294967295
    assert int.from_bytes(major_version, byteorder="little") == 1
    assert int.from_bytes(minor_version, byteorder="little") == 0


def test_fake_reader_seek():
    byte_string = b'\x01\x00\x00\x00\xff\xff\xff\xff\x01\x00\x00\x00\x00\x00\x00\x00'
    fbr = FakeByteReader(byte_string)

    fbr.read(5)

    assert fbr.tell() == 5
    
    fbr.seek(2)

    assert fbr.tell() == 2

    fbr.read(5)

    assert fbr.tell() == 7


def test_fake_reader_buffer_exception():

    byte_string = b'\x01\x00\x00\x00\xff\xff\xff\xff\x01\x00\x00\x00\x00\x00\x00\x00'
    fbr = FakeByteReader(byte_string)

    with pytest.raises(Exception) as e:
        fbr.read(17)
        
    assert type(e.value) == OSError
    assert e.value.args[0] == 'Requested size (17) is bigger then byte buffer (16)!'


def test_fake_reader_tell():
    byte_string = b'\x01\x00\x00\x00\xff\xff\xff\xff\x01\x00\x00\x00\x00\x00\x00\x00'
    fbr = FakeByteReader(byte_string)

    assert fbr.tell() == 0

    fbr.read(9)

    assert fbr.tell() == 9