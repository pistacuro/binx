import os
import re
import csv
import time
import logging

boses = []


def get_length_prefixed_string_bytes(string):
    # get string in bytes, diff languages have different
    # sizes i. e. chinese, korean etc.
    string_byte_representation = bytes(string, "utf-8")
    # how much bytes the string will take
    byte_size = len(string_byte_representation)
    # only first 7 least significant bits of a byte will hold the info about the value
    # the most significant bit will be 1 if there is another byte after him that holds
    # another part of the size information.
    binary_representation = bin(byte_size)[2:]
    binary_size = len(binary_representation)
    # we reverse the bits so we can better manipulate them easier
    bin_repr_reversed = binary_representation[binary_size::-1]

    correct_size_bytes = []
    # if the string has less than 128 bytes it is defined only in 1 byte of size info
    # it will use only the less significant bits for the info and the most significant
    # bit will be zero.
    if byte_size < 128:
        correct_size_bytes.append(byte_size)
    else:
        for i in range(5):
            seven_bits = bin_repr_reversed[i*7:(i+1)*7]
            if len(seven_bits) < 7:
                correct_size_bytes.append(int(seven_bits[len(seven_bits)::-1], 2))
                break
            else:
                # add the 8 bit which is the most significant bit, this marks that there is another
                # byte after the current one which holds more info about the size of the string
                seven_bits += '1'
                correct_size_bytes.append(int(seven_bits[len(seven_bits)::-1], 2))

    return bytes(correct_size_bytes) + string_byte_representation


def write_strings_to_csv():
    timestamp = int(time.time())
    csv_filename = 'strings-{timestamp}.csv'.format(timestamp=timestamp)
    with open(csv_filename, 'w', newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        for string in boses:
            if re.search("[\uac00-\ud7a3]", string.value.value): 
                row = [string.value.value, ""]
                writer.writerow(row)

    print(csv_filename)


def translate_binary_file_with_csv(binary_file_path, csv_file_path):
    binary_file_content = b""
    with open(binary_file_path, "rb") as fd_bin:
        binary_file_content = fd_bin.read()

    with open(csv_file_path, newline="", encoding="utf-8") as fd_csv:
        csv_file = csv.reader(fd_csv)
        for row in csv_file:
            if len(row[1]):
                org_str = row[0]
                trn_str = row[1].strip()
                lps_trn_bytes = get_length_prefixed_string_bytes(trn_str)
                bos_to_replace = []
                for bos in boses:
                    if bos.value.value.strip() == org_str.strip():
                        bos_to_replace.append(bos)

                for bos in bos_to_replace:
                    find_bytes = bos.get_all_raw_bytes()
                    replace_bytes = bos.raw_bytes + lps_trn_bytes
                    binary_file_content = binary_file_content.replace(
                        find_bytes, replace_bytes)

    timestamp = int(time.time())
    new_bin_filename = "{timestamp}.data.bin.bytes".format(timestamp=timestamp)

    with open(new_bin_filename, "wb") as fd_out:
        fd_out.write(binary_file_content)

    print(new_bin_filename)


def diff_csv_and_bin(old_csv_file_path):
    logging.info("Diffing...")
    with open(old_csv_file_path, newline="", encoding="utf-8") as fd_csv:
        old_csv_content = csv.reader(fd_csv)

        diff = {
            "meta": {
                "new": 0,
                "removed": 0,
                "trans_changed": 0,
            },
            "new": [],
            "removed":[],
            "trans_changed": [],
        }

        # get only string value from a binary object string
        strings = [string.value.value.strip() for string in boses if re.search("[\uac00-\ud7a3]",
                                                                       string.value.value)]
        # this will gather all the strings which where already found
        for orow in old_csv_content:
            found = False
            for i, string in enumerate(strings):
                if orow[0].strip() == string:
                    found = True
                    del(strings[i])
                    break
            
            if not found:
                if orow[1]:
                    diff["trans_changed"].append(orow)
                else:
                    diff["removed"].append(orow[0])

        diff["new"] = strings
        diff["meta"]["new"] = len(diff["new"])
        diff["meta"]["removed"] = len(diff["removed"])
        diff["meta"]["trans_changed"] = len(diff["trans_changed"])
    
    timestamp = int(time.time())
    diff_dir = 'diff_{timestamp}/'.format(timestamp=timestamp)
    os.mkdir(diff_dir)

    # TODO refactor this as it is lazy coding AF. Put in a diff function
    with open(diff_dir + "new.csv", 'w', newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        for string in diff["new"]:
                row = [string, ""]
                writer.writerow(row)

    with open(diff_dir + "trans_changed.csv", 'w', newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        for string in diff["trans_changed"]:
                writer.writerow(string)

    with open(diff_dir + "removed.csv", 'w', newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        for string in diff["removed"]:
                row = [string, ""]
                writer.writerow(row)

    return diff["meta"]
