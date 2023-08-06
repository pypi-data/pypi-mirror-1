#!/usr/bin/python
# -*- coding: UTF8 -*-

import csv
import sys
from os import path
from comparator import Comparator

help = """
compares 2 csv files and outputs delta as file_suppr.csv, file_addon.csv and file_changes.csv
usage : %s old_filename new_filenane
""" % sys.argv[0]


class SKV(csv.excel):
    # like excel, but uses semicolons
    delimiter = ";"
#    quoting = csv.QUOTE_NONE

csv.register_dialect("SKV", SKV)


def output_difference(old_file, new_file):
    dirname, filename = path.split(new_file)
    filename, ext = path.splitext(filename)

    old_file = open(old_file)
    new_file = open(new_file)
    old_file = list(csv.reader(old_file, "SKV"))
    new_file = list(csv.reader(new_file, "SKV"))

    comp = Comparator(old_file, new_file)
    comp.check()
    comp.getChanges(lambda x: x[0], purge=True)
    comp.purgeOldNew()

    suppr_file = open(filename + '_suppr.csv', 'wb')
    suppr_writer = csv.writer(suppr_file)
    suppr_writer.writerows(comp.deletions)
    suppr_file.close()

    addon_file = open(filename + '_addon.csv', 'wb')
    addon_writer = csv.writer(addon_file)
    addon_writer.writerows(comp.additions)
    addon_file.close()

    change_file = open(filename + '_changes.csv', 'wb')
    change_writer = csv.writer(change_file)
    change_writer.writerows(comp.changes)
    change_file.close()


def main():
    args = sys.argv
    if len(args) != 3:
        print help
        sys.exit(1)
    else:
        output_difference(args[1], args[2])
        sys.exit(0)

if __name__ == '__main__':
    main()
