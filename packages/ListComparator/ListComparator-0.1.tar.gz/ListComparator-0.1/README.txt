XML and CSV comparisons
=======================

Two scripts are provided xml_cmp and csv_cmp
They both compares 2 files and outputs delta as file_suppr,
file_addon and file_changes

the extension is forced to xml or csv respectively

List comparison
===============

listcomparator provides a Comparator object that allows to find the differences
between two lists **provided the elements of the lists appear in the same order**

>>> old = [1, 2, 3, 4, 5, 6]
>>> new = [1, 3, 4, 7, 6]

>>> from listcomparator.comparator import Comparator

Let's create a Comparator object

>>> comp = Comparator(old,new)

The check method gives values to additions and deletions attributes

>>> comp.check()
>>> comp.additions
[7]
>>> comp.deletions
[2, 5]

We can also use lists of  lists

>>> old_list = [['62145', 'azerty'], ['1234', 'qwerty'], ['9876', 'ipsum']]
>>> new_list = [['62145', 'azerty'], ['1234', 'qwertw'], ['4865', 'lorem']]
>>> comp = Comparator(old_list, new_list)
>>> comp.check()
>>> comp.additions
[['1234', 'qwertw'], ['4865', 'lorem']]
>>> comp.deletions
[['1234', 'qwerty'], ['9876', 'ipsum']]

We can have an issue when a modification, in our case "qwerty" became "qwertz",
appears in both outputs, comp.additions and comp.deletions.
You  might want to consider this a change.
Comparator can handle this and filter out such cases if you provide a function
that tells Comparator how to recognize such cases
In our example, we consider 2 elements to be the same if the first element of the
list is the same, a kind of id.

>>> def my_key(x):
...     return x[0]
...

The getChanges methods then provides a new attribute : changes

>>> comp.getChanges(my_key)
>>> comp.changes
[['1234', 'qwertw']]

of course, additions and deletions stay unchanged

>>> comp.additions
[['1234', 'qwertw'], ['4865', 'lorem']]
>>> comp.deletions
[['1234', 'qwerty'], ['9876', 'ipsum']]

You might want to consider only 'pure' additions and deletions
getChanges allows for a keyword argument 'purge' that does just that

>>> comp.getChanges(my_key, purge=True)
>>> comp.changes
[['1234', 'qwertw']]
>>> comp.additions
[['4865', 'lorem']]
>>> comp.deletions
[['9876', 'ipsum']]

The old and new attributes store the lists to be compared
you might want to reset those, Comparator provides a purgeOldNew method
to clear up memory

>>> comp.old
[['62145', 'azerty'], ['1234', 'qwerty'], ['9876', 'ipsum']]
>>> comp.new
[['62145', 'azerty'], ['1234', 'qwertw'], ['4865', 'lorem']]
>>> comp.purgeOldNew()
>>> comp.old
>>> comp.new


compare XML files
=================

Comparator can be used to compare xml files
let's make two xml files describing books

>>> old='''<?xml version="1.0" ?>
... <infos>
... <book><title>White pages 1995</title>
... <author>
... <surname>La Poste</surname>
... </author>
... <chapter><title>Paris</title>
... <para>ABEL Antoine 82 23 44 12</para>
... <para>ABEL Pierre 82 67 23 12</para>
... </chapter>
... </book>
... <book><title>Yellow pages 2007</title>
... <author>
... <surname>La Poste</surname>
... </author>
... <chapter><title>Bretagne</title>
... <para>Zindep 82 23 44 12</para>
... <para>ZYM 82 67 23 12</para>
... </chapter>
... </book>
... <book><title>Dark pages 2007</title>
... <author>
... <surname>La Poste</surname>
... </author>
... <chapter><title>Greves</title>
... <para>SNCF 82 23 44 12</para>
... </chapter>
... </book>
... </infos>
... '''

>>> new='''<?xml version="1.0"?>
... <infos>
... <book><title>White pages 1995</title>
... <author>
... <surname>La Poste</surname>
... </author>
... <chapter><title>Paris</title>
... <para>ABIL Antoine 82 23 44 12</para>
... <para>ABEL Pierre 82 67 23 12</para>
... </chapter>
... </book>
... <book><title>Yellow pages 2007</title>
... <author>
... <surname>La Poste</surname>
... </author>
... <chapter><title>Bretagne</title>
... <para>Zindep 82 23 44 12</para>
... <para>ZYM 82 67 23 12</para>
... </chapter>
... </book>
... <book><title>Blue pages 2007</title>
... <author>
... <surname>La Poste</surname>
... </author>
... <chapter><title>Bretagne</title>
... <para>Mer 82 23 44 12</para>
... <para>Ciel 82 67 23 12</para>
... </chapter>
... </book>
... </infos>
... '''

elementtree is required to parse xml

>>> from elementtree import ElementTree as ET

for this test we'll use cStringIO rather than a file

>>> import cStringIO
>>> ex_old = cStringIO.StringIO(old)
>>> ex_new = cStringIO.StringIO(new)

we parse contents

>>> root_old = ET.parse(ex_old).getroot()
>>> root_new = ET.parse(ex_new).getroot()

the "book" tag identifies objects we want
>>> objects_old = root_old.findall('book')
>>> objects_new = root_new.findall('book')

as we can't compare 2 objects, we stringify them

>>> objects_old = [ET.tostring(o) for o in objects_old]
>>> objects_new = [ET.tostring(o) for o in objects_new]

from there, Comparator is usefull

>>> my_comp = Comparator(objects_old, objects_new)
>>> my_comp.check()

>>> for e in my_comp.additions:
...     print e
...
<book><title>White pages 1995</title>
<author>
<surname>La Poste</surname>
</author>
<chapter><title>Paris</title>
<para>ABIL Antoine 82 23 44 12</para>
<para>ABEL Pierre 82 67 23 12</para>
</chapter>
</book>
<BLANKLINE>
<book><title>Blue pages 2007</title>
<author>
<surname>La Poste</surname>
</author>
<chapter><title>Bretagne</title>
<para>Mer 82 23 44 12</para>
<para>Ciel 82 67 23 12</para>
</chapter>
</book>
<BLANKLINE>

>>> for e in my_comp.deletions:
...     print e
...
<book><title>White pages 1995</title>
<author>
<surname>La Poste</surname>
</author>
<chapter><title>Paris</title>
<para>ABEL Antoine 82 23 44 12</para>
<para>ABEL Pierre 82 67 23 12</para>
</chapter>
</book>
<BLANKLINE>
<book><title>Dark pages 2007</title>
<author>
<surname>La Poste</surname>
</author>
<chapter><title>Greves</title>
<para>SNCF 82 23 44 12</para>
</chapter>
</book>
<BLANKLINE>

we need to know wich tag is used to uniquely define an object
here we choose to use the "title" tag

>>> def item_signature(xml_element):
...     title = xml_element.find('title')
...     return title.text
...

we build our custom function for use by the Comparator

>>> def my_key(str):
...     file_like = cStringIO.StringIO(str)
...     root = ET.parse(file_like)
...     return item_signature(root)
...

then the getChanges method of the Comparator becomes available

>>> my_comp.getChanges(my_key, purge=True)

What books have been exclusively added ?

>>> for e in my_comp.additions:
...     print e
...
<book><title>Blue pages 2007</title>
<author>
<surname>La Poste</surname>
</author>
<chapter><title>Bretagne</title>
<para>Mer 82 23 44 12</para>
<para>Ciel 82 67 23 12</para>
</chapter>
</book>
<BLANKLINE>

what books have been exclusively removed ?

>>> for e in my_comp.deletions:
...     print e
...
<book><title>Dark pages 2007</title>
<author>
<surname>La Poste</surname>
</author>
<chapter><title>Greves</title>
<para>SNCF 82 23 44 12</para>
</chapter>
</book>
<BLANKLINE>

what books have changed ? that is have same title, but different other values

>>> for e in my_comp.changes:
...     print e
...
<book><title>White pages 1995</title>
<author>
<surname>La Poste</surname>
</author>
<chapter><title>Paris</title>
<para>ABIL Antoine 82 23 44 12</para>
<para>ABEL Pierre 82 67 23 12</para>
</chapter>
</book>
<BLANKLINE>


then we can put those results back in xml file

* This code conforms to PEP8
* It is fully tested, 100% coverage
* A Buildbot runs tests at each commit