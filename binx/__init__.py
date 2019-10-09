import os
import sys
import math
import logging

from binx.enum import record_type_enum
from binx.types import SerializedStreamHeader
from binx.utils import peek_one_byte_to_int
from binx.strings import write_strings_to_csv, translate_binary_file_with_csv, diff_csv_and_bin

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def get_serialization_header(fd, byte_ordering):
        byte = fd.read(1)
        dec_val = int.from_bytes(byte, byteorder=byte_ordering)
        
        # TODO: this only searches for the serialization at the start of the
        # file for now.
        if dec_val != 0:
                raise ValueError("Invalid file! No C# serialization found!")

        header_bytes = fd.read(16)
        return SerializedStreamHeader(header_bytes)


def read_binary_file(bin_file_path, byte_ordering="little"):
    with open(bin_file_path, "rb") as fd:
        file_size = os.stat(bin_file_path).st_size 
        get_serialization_header(fd, byte_ordering)
        logging.info("Reading binary file...")
        rte_objects = {}
        while True:
                sys.stdout.write("\r")
                sys.stdout.write("{percent}%".format(percent=math.floor(
                    (fd.tell()/file_size)*100)))
                sys.stdout.flush()

                dec_val = peek_one_byte_to_int(fd) 

                #import ipdb; ipdb.set_trace()
                if dec_val == 11:
                        break

                if dec_val > len(record_type_enum):
                        import ipdb; ipdb.set_trace()

                rte = record_type_enum[dec_val]

                if "class" not in rte:
                        import ipdb; ipdb.set_trace()
                        raise ValueError(
                                ("A class for the {rte} record type enum "
                                 "was not implemented!").format(rte=rte["type"]))

                rte_class = rte["class"]
                try:
                        rte_object = rte_class()
                except Exception:
                        import ipdb; ipdb.set_trace()

                if dec_val == 7:
                        rte_object.read_data_from_stream(fd, rte_objects)
                else:
                        rte_object.read_data_from_stream(fd)

                if rte_object.__class__.__name__ in ["SystemClassWithMembersAndTypes", 
                                                     "ClassWithMembersAndTypes", 
                                                     "SystemClassWithMembers"]:

                        rte_object.read_all_member_data(fd, rte_objects)

                if dec_val == 1:
                        import ipdb; ipdb.set_trace()
                if dec_val == 9:
                        import ipdb; ipdb.set_trace()
                if dec_val == 10:
                        import ipdb; ipdb.set_trace()

                # binary library
                if dec_val == 12:
                        rte_objects[0] = rte_object
                elif dec_val == 7:
                        if rte_object.object_id not in rte_objects:
                                rte_objects[rte_object.object_id] = rte_object
                        else:
                                raise ValueError("Duplicit object id found: %s" % rte_object.object_id)

                elif dec_val in [15, 17]:
                        if rte_object.array_info.object_id not in rte_objects:
                                rte_objects[rte_object.array_info.object_id] = rte_object
                        else:
                                raise ValueError("Duplicit object id found: %s" % rte_object.object_id)

                else: 
                        if rte_object.class_info.object_id not in rte_objects:
                                rte_objects[rte_object.class_info.object_id] = rte_object
                        else:
                                raise ValueError("Duplicit object id found: %s" %
                                                 rte_object.class_info.object_id)
        sys.stdout.write("\r")
        sys.stdout.write("100%\n")
        sys.stdout.flush()


def main(args):

    read_binary_file(args.bin_file_path)

    if args.diff_csv_file_path:
        diff = diff_csv_and_bin(args.diff_csv_file_path)
        print(diff)
        return

    if args.dump:
        write_strings_to_csv()
        return

    if args.trans_csv_file_path:
        translate_binary_file_with_csv(args.bin_file_path,
                                       args.trans_csv_file_path)
        return
