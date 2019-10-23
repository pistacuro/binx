#!/bin/env python
import argparse
from binx import main

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='c# serialization introspection tool')
    parser.add_argument('bin_file_path', help='binary C# serialization file path')
    parser.add_argument('-d', '--dump', action="store_true", dest="dump",
                        help='dump the strings from provided c# file into a *.csv')
    parser.add_argument('-t', '--translate', dest="trans_csv_file_path",
                        help='translated *.csv file path')
    parser.add_argument('-gt', '--gtranslate', dest="trans_csv_url",
                        help='URL to Google Sheets csv IN QUOTES')
    parser.add_argument('-x', '--diff', dest="diff_csv_file_path",
                        help=('*.csv file path, againts whom we are diffing the '
                              'strings from the binary file'))
    args = parser.parse_args()

    main(args)



