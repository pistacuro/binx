import yaml

from binx.enum import (binary_type_enum, primitive_type_enum, 
                       binary_array_type_enum)
from binx.strings import boses

class GenericType():

    def __init__(self):
        self.record_type_id = None
        self.raw_bytes = b''

    def read_bytes_to_int(self, fd, size, byte_order="little"):
        byte_data = fd.read(size)
        self.raw_bytes += byte_data
        return int.from_bytes(byte_data, byteorder=byte_order)

    def peek_one_byte_to_int(self, fd, byte_order="little"):
        byte_data = fd.peek(1)[:1]
        return int.from_bytes(byte_data, byteorder=byte_order)

    def read_bytes_to_utf8(self, fd, size, byte_order="little"):
        byte_data = fd.read(size)
        self.raw_bytes += byte_data
        return byte_data.decode("utf-8") 

class SerializedStreamHeader():
    def __init__(self, header_bytes, byte_ordering="little"):
        self.header_bytes = header_bytes
        self.root_id = int.from_bytes(header_bytes[0:4], byteorder=byte_ordering)
        self.header_id = int.from_bytes(header_bytes[4:8], byteorder=byte_ordering)
        self.major_version = int.from_bytes(header_bytes[8:12], byteorder=byte_ordering)
        self.minor_version = int.from_bytes(header_bytes[12:8], byteorder=byte_ordering)

class LengthPrefixedString(GenericType):
    def __init__(self):
        GenericType.__init__(self)
        self.size = None
        self.value = None

    def read_data_from_stream(self, fd):
        self.size = self._get_correct_string_size(fd)
        self.value = self.read_bytes_to_utf8(fd, self.size)

    def _get_correct_string_size(self, fd):
        """ 
        The lenght value of a string can be defined up to 5 bytes. Only lower 7 bits
        hold the lenght value. The most significant bit defines if there is another bit
        following the previous one with rest of the lenght value. 
        """
        # store the lenght value bits
        size_bits = []
        # the value can have max 5 bytes
        for _ in range(5):
            size = self.read_bytes_to_int(fd, 1)
            # if the length value is less then 128 it means its the last
            # byte with the lenght value information and we can end.
            if size < 128:
                size_bits.append(bin(size)[2:])
                break
            else:
                # when its bigger than 128 it means that the length value
                # is using more bytes. We strip also the most significant
                # bit
                size_bits.append(bin(size)[3:])

        size_bits.reverse()
        correct_size = int("".join(size_bits), 2) 
        return correct_size

class ObjectNull(GenericType):
    def __init__(self):
        GenericType.__init__(self)

    def read_data_from_stream(self, fd):
        self.record_type_id = self.read_bytes_to_int(fd, 1)


class BinaryLibrary(GenericType):
    def __init__(self):
        GenericType.__init__(self)
        self.library_id = None
        self.library_name = None 
        self.is_fixed = False

    def read_data_from_stream(self, fd):
        self.record_type_id = self.read_bytes_to_int(fd, 1)
        self.library_id = self.read_bytes_to_int(fd, 4) 
        self.library_name = LengthPrefixedString()
        self.library_name.read_data_from_stream(fd)


class ClassInfo(GenericType):
    def __init__(self):
        GenericType.__init__(self)
        self.object_id = None
        self.name = None
        self.member_count = None
        self.member_names = []

    def read_data_from_stream(self, fd):
        self.object_id = self.read_bytes_to_int(fd, 4) 
        self.name = LengthPrefixedString()
        self.name.read_data_from_stream(fd)
        self.member_count = self.read_bytes_to_int(fd, 4)

        for _ in range(self.member_count):
            member = LengthPrefixedString()
            member.read_data_from_stream(fd) 
            self.member_names.append(member)

class MemberTypeInfo(GenericType):

    def __init__(self, class_info):
        GenericType.__init__(self)
        self.binary_type_enums = []
        self.additional_infos = []
        self.class_info = class_info

    def read_data_from_stream(self, fd):
        for _ in range(self.class_info.member_count):
            bte = self.read_bytes_to_int(fd, 1)
            self.binary_type_enums.append(
                binary_type_enum[bte]
            )

        for bte in self.binary_type_enums:
            if bte["type"] in ["String", "Object", "ObjectArray", "StringArray"]:
                self.additional_infos.append(
                    {
                        "type": bte["type"]
                    }
                )
                continue

            if bte["type"] in ["Primitive", "PrimitiveArray"]:
                pte = self.read_bytes_to_int(fd, 1)
                self.additional_infos.append(
                    {
                        "type": bte["type"],
                        "primitive": primitive_type_enum[pte],
                    }
                )
            elif bte["type"] == "SystemClass":
                class_name = LengthPrefixedString()
                class_name.read_data_from_stream(fd)
                self.additional_infos.append(
                    {
                        "type": bte["type"],
                        "name": class_name,
                    }
                )
            elif bte["type"] == "Class":
                class_name = LengthPrefixedString()
                class_name.read_data_from_stream(fd)
                library_id = self.read_bytes_to_int(fd, 4)
                self.additional_infos.append(
                    {
                        "type": bte["type"],
                        "name": class_name,
                        "library_id": library_id,
                    }
                )
            else:
                raise ValueError(
                    "Binary type enumeration {bte} is invalid, or something went wrong!".format(
                        bte=bte["type"]))


class ClassWithMembersAndTypes(GenericType):
    def __init__(self):
        GenericType.__init__(self)
        self.class_info = None
        self.member_type_info = None
        self.member_data = []
        self.library_id = None

    def read_data_from_stream(self, fd):
        self.record_type_id = self.read_bytes_to_int(fd, 1)
        self.class_info = ClassInfo()
        self.class_info.read_data_from_stream(fd)
        self.member_type_info = MemberTypeInfo(self.class_info)
        self.member_type_info.read_data_from_stream(fd)
        self.library_id = self.read_bytes_to_int(fd, 4)

    def to_yaml(self):
        # TODO: find out how we can serialize an orderectdict into yaml
        return yaml.dump({
            "type": self.__class__.__name__,
            "class_info": {
                "object_id": self.class_info.object_id,
                "class_name": self.class_info.name.value,
                "member_count": self.class_info.member_count,
                "member_names": [m.value for m in self.class_info.member_names],
            },
            "member_info": {
                "binary_type_enums": [bte["type"] for bte in
                                      self.member_type_info.binary_type_enums],
                "additional_infos": self.member_type_info.additional_infos,
            }
        })

    def read_all_member_data(self, fd, rte_objects):

            additional_infos = self.member_type_info.additional_infos

            while True:
                self.member_data.append(
                    self._read_member_data(fd, additional_infos))

                rte = self.peek_one_byte_to_int(fd)

                if rte in [4, 5, 7, 11, 15, 17]:
                    break

                if rte == 1:
                    # class with id is not a record type of a class,
                    # it only describes what systemclass an record of an array
                    # belongs to
                    # TODO info about cid cannot be lost.
                    cid = ClassWithId()
                    cid.read_data_from_stream(fd)
                    if cid.metadata_id in rte_objects:
                        additional_infos = rte_objects[cid.metadata_id].member_type_info.additional_infos
                    else:
                        additional_infos = self.member_type_info.additional_infos
        

    def _read_member_data(self, fd, additional_infos):
        data_record = []

        for member in additional_infos:
            # find out what next record is
            rte = self.peek_one_byte_to_int(fd)

            if member["type"] == "Primitive":
                if member["primitive"]["type"] == 'Int32':
                    data_record.append(
                        self.read_bytes_to_int(fd, 4))
                elif member["primitive"]["type"] == 'Double':
                    data_record.append(
                        self.read_bytes_to_int(fd, 8))
                else:
                    import ipdb; ipdb.set_trace()
                    raise ValueError("Undefined primitive value type!")
                continue

            if rte == 9:
                mr = MemberReference()
                mr.read_data_from_stream(fd)
                data_record.append(mr)

            if rte == 10:
                on = ObjectNull()
                on.read_data_from_stream(fd)
                data_record.append(on)

            if member["type"] in ["Class", "SystemClass"]:
                pass
            elif member["type"] == "Object":
                pass
            elif member["type"] == "String":
                if rte == 6:
                    bos = BinaryObjectString()
                    bos.read_data_from_stream(fd)
                    data_record.append(bos)

        return data_record

class MemberReference(GenericType):

    def __init__(self):
        GenericType.__init__(self)
        self.id_ref = None

    def read_data_from_stream(self, fd):
        self.record_type_id = self.read_bytes_to_int(fd, 1)
        self.id_ref = self.read_bytes_to_int(fd, 4)

class SystemClassWithMembersAndTypes(ClassWithMembersAndTypes):
    def __init__(self):
        ClassWithMembersAndTypes.__init__(self)

    def read_data_from_stream(self, fd):
        self.record_type_id = self.read_bytes_to_int(fd, 1)
        self.class_info = ClassInfo()
        self.class_info.read_data_from_stream(fd)
        self.member_type_info = MemberTypeInfo(self.class_info)
        self.member_type_info.read_data_from_stream(fd)

class BinaryArray(GenericType):
    def __init__(self):
        GenericType.__init__(self)
        self.object_id = None
        self.binary_array_type_enum = None
        self.rank = None
        self.lengths = []
        self.lower_bounds = []
        self.type_enum = None
        self.additional_type_info = None
        self.array_data = [] 

    def read_data_from_stream(self, fd, rte_objects):
        self.record_type_id = self.read_bytes_to_int(fd, 1)
        self.object_id = self.read_bytes_to_int(fd, 4)
        enum = self.read_bytes_to_int(fd, 1)
        self.binary_array_type_enum = binary_array_type_enum[enum]
        self.rank = self.read_bytes_to_int(fd, 4)
        for _ in range(self.rank):
            self.lengths.append(self.read_bytes_to_int(fd, 4))

        if self.binary_array_type_enum["type"] in ["SingleOffset", "JaggedOffset", 
                                                   "RectangularOffset"]:
            for _ in range(self.rank):
                self.lower_bounds.append(self.read_bytes_to_int(fd, 4))

        enum = self.read_bytes_to_int(fd, 1)
        self.type_enum = binary_type_enum[enum]
        # TODO: make this below its own function duplicity
        if self.type_enum["type"] in ["String", "Object", "ObjectArray", "StringArray"]:
            self.additional_type_info = {
                "type": self.type_enum["type"]
            }

        elif self.type_enum["type"] in ["Primitive", "PrimitiveArray"]:
            pte = self.read_bytes_to_int(fd, 1)
            self.additional_type_info = {
                "type": self.type_enum["type"],
                "primitive": primitive_type_enum[pte],
            }

        elif self.type_enum["type"] == "SystemClass":
            class_name = LengthPrefixedString()
            class_name.read_data_from_stream(fd)
            self.additional_type_info = {
                "type": self.type_enum["type"],
                "name": class_name,
            }

        elif self.type_enum["type"] == "Class":
            class_name = LengthPrefixedString()
            class_name.read_data_from_stream(fd)
            library_id = self.read_bytes_to_int(fd, 4)
            self.additional_type_info = {
                    "type": self.type_enum["type"],
                    "name": class_name,
                    "library_id": library_id,
                }

        else:
            raise ValueError(
                "Binary type enumeration {bte} is invalid, or something went wrong!".format(
                    bte=self.type_enum["type"]))
        #if self.object_id == 184649:
        #    import ipdb; ipdb.set_trace()
        if self.type_enum["type"] in ["Class", "SystemClass"]:
            rte = self.peek_one_byte_to_int(fd) 
            while rte in [1, 9, 10]:
                rte = self.peek_one_byte_to_int(fd) 
                if rte == 9:
                    mr = MemberReference()
                    mr.read_data_from_stream(fd)
                    self.array_data.append(mr)

                if rte == 10:
                    on = ObjectNull()
                    on.read_data_from_stream(fd)
                    self.array_data.append(on)

                if rte == 13:
                    onm = ObjectNullMultiple256()
                    onm.read_data_from_stream(fd)
                    for _ in range(onm.null_count):
                        self.array_data.append(None)

                if rte == 1:
                    cid = ClassWithId()
                    cid.read_data_from_stream(fd)
                    additional_infos = rte_objects[cid.metadata_id].member_type_info.additional_infos
                    clx = ClassWithMembersAndTypes()
                    clx.class_info = rte_objects[cid.metadata_id].class_info
                    record = clx._read_member_data(fd, additional_infos)
                    record.append(cid)
                    self.array_data.append(record)
            



class BinaryObjectString(GenericType):

    def __init__(self):
        GenericType.__init__(self)
        self.object_id = None
        self.value = None

    def read_data_from_stream(self, fd):
        self.record_type_id = self.read_bytes_to_int(fd, 1)
        self.object_id = self.read_bytes_to_int(fd, 4)
        self.value = LengthPrefixedString()
        self.value.read_data_from_stream(fd)
        boses.append(self)

    def get_all_raw_bytes(self):
        return self.raw_bytes + self.value.raw_bytes

class ClassWithId(GenericType):
    # defines that memebers of an array belong to the same array
    def __init__(self):
        GenericType.__init__(self)
        self.object_id = None
        self.metadata_id = None

    def read_data_from_stream(self, fd):
        self.record_type_id = self.read_bytes_to_int(fd, 1)
        self.object_id = self.read_bytes_to_int(fd, 4)
        self.metadata_id = self.read_bytes_to_int(fd, 4)

class ClassWithMembers(ClassWithMembersAndTypes):
    def __init__(self):
        ClassWithMembersAndTypes.__init__(self)

    def read_data_from_stream(self, fd):
        self.record_type_id = self.read_bytes_to_int(fd, 1)
        self.class_info = ClassInfo()
        self.class_info.read_data_from_stream(fd)
        self.library_id = self.read_bytes_to_int(fd, 4)

class SystemClassWithMembers(SystemClassWithMembersAndTypes):
    def __init__(self):
        SystemClassWithMembersAndTypes.__init__(self)

    def read_data_from_stream(self, fd):
        self.record_type_id = self.read_bytes_to_int(fd, 1)
        self.class_info = ClassInfo()
        self.class_info.read_data_from_stream(fd)

class ArrayInfo(GenericType):

    def __init__(self):
        GenericType.__init__(self)
        self.object_id = None
        self.length = None

    def read_data_from_stream(self, fd):
        self.object_id = self.read_bytes_to_int(fd, 4)
        self.length = self.read_bytes_to_int(fd, 4)

class ArraySinglePrimitive(GenericType):
    def __init__(self):
        GenericType.__init__(self)
        self.array_info = None
        self.primitive_type_enum = None
        self.array_data = []

    def read_data_from_stream(self, fd):
        self.record_type_id = self.read_bytes_to_int(fd, 1)
        self.array_info = ArrayInfo()
        self.array_info.read_data_from_stream(fd)
        self.primitive_type_enum = self.read_bytes_to_int(fd, 1)

        for _ in range(self.array_info.length):
            if self.primitive_type_enum == 8:
                self.array_data.append(self.read_bytes_to_int(fd, 4))
            elif self.primitive_type_enum == 6:
                self.array_data.append(self.read_bytes_to_int(fd, 8))
            else:
                import ipdb; ipdb.set_trace()


class ArraySingleString(GenericType):
    def __init__(self):
        GenericType.__init__(self)
        self.array_info = None
        self.array_data = []

    def read_data_from_stream(self, fd):
        self.record_type_id = self.read_bytes_to_int(fd, 1)
        self.array_info = ArrayInfo()
        self.array_info.read_data_from_stream(fd)
        for _ in range(self.array_info.length):
            rte = self.peek_one_byte_to_int(fd)
            if rte == 6:
                bos = BinaryObjectString()
                bos.read_data_from_stream(fd)
                self.array_data.append(bos)
            elif rte == 13:
                onm = ObjectNullMultiple256()
                onm.read_data_from_stream(fd)
                for _ in range(onm.null_count):
                    self.array_data.append(None)
                break
            elif rte == 10:
                on = ObjectNull()
                on.read_data_from_stream(fd)
                self.array_data.append(on)
            elif rte == 9:
                mr = MemberReference()
                mr.read_data_from_stream(fd)
                self.array_data.append(mr)
            elif rte == 11:
                self.array_data.append(None)


class ObjectNullMultiple256(GenericType):
    def __init__(self):
        GenericType.__init__(self)
        self.null_count = None

    def read_data_from_stream(self, fd):
        self.record_type_id = self.read_bytes_to_int(fd, 1)
        self.null_count = self.read_bytes_to_int(fd, 1)


class ObjectNullMultiple(GenericType):
    def __init__(self):
        GenericType.__init__(self)
        self.null_count = None

    def read_data_from_stream(self, fd):
        self.record_type_id = self.read_bytes_to_int(fd, 1)
        self.null_count = self.read_bytes_to_int(fd, 4)