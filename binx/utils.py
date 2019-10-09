

def read_bytes_to_int(fd, size, byte_order="little"):
    byte_data = fd.read(size)
    return int.from_bytes(byte_data, byteorder=byte_order)

def peek_one_byte_to_int(fd, byte_order="little"):
    byte_data = fd.peek(1)[:1]
    return int.from_bytes(byte_data, byteorder=byte_order)

def read_bytes_to_utf8(fd, size, byte_order="little"):
    byte_data = fd.read(size)
    return byte_data.decode("utf-8") 