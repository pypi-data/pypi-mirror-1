#!/usr/bin/python
# -*- coding: UTF8 -*-

from os import path
import sys
from elementtree import ElementTree as ET
from comparator import Comparator
import cStringIO

help = """
compares 2 xml files and outputs delta as file_suppr.xml, file_addon.xml and file_changes.xml
usage : %s old_filename new_filenane object_tag id_tag
or
%s test
""" % (sys.argv[0], sys.argv[0])


def output_difference(old_file, new_file, object_tag, id_tag):
    """ checks two xml files
    """
    dirname, filename = path.split(new_file)
    filename, ext = path.splitext(filename)

    root_old = ET.ElementTree(file=old_file)
    root_new = ET.ElementTree(file=new_file)

    objects_old = root_old.findall(object_tag)
    objects_new = root_new.findall(object_tag)

    objects_old = [ET.tostring(o) for o in objects_old]
    objects_new = [ET.tostring(o) for o in objects_new]

    def item_signature(xml_element):
        title = xml_element.find(id_tag)
        return title.text

    def my_key(str):
        file_like = cStringIO.StringIO(str)
        root = ET.parse(file_like)
        return item_signature(root)

    my_comp = Comparator(objects_old, objects_new)
    my_comp.check()
    my_comp.getChanges(my_key, purge=True)

    suppr_tree = ET.XML(''.join(my_comp.deletions))
    ET.ElementTree(suppr_tree).write(filename + '_suppr.xml', 'utf8')

    add_tree = ET.XML(''.join(my_comp.additions))
    ET.ElementTree(add_tree).write(filename + '_add.xml', 'utf8')

    change_tree = ET.XML(''.join(my_comp.changes))
    ET.ElementTree(change_tree).write(filename + '_changes.xml', 'utf8')


def main():
    args = sys.argv
    if len(args) != 5:
        print help
        sys.exit(1)
    else:
        output_difference(args[1], args[2], args[3], args[4])
        sys.exit(0)

if __name__ == '__main__':
    main()
