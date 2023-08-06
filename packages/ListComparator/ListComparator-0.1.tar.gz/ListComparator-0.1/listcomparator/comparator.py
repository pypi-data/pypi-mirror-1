# -*- coding: UTF8 -*-

class Comparator(object):
    """ lists comparator
    """

    def __init__(self, old, new):
        """ creates new instance
        """
        self.old = old
        self.new = new

        self.len_old = len(old)
        self.len_new = len(new)
        self.additions = []
        self.deletions = []
        self.changes = []

        self.index_old = 0
        self.index_new = 0

        self.scout_old = 1
        self.scout_new = 1

    def getChanges(self, key, purge=False):
        key_del = [key(e) for e in self.deletions]
        self.changes = [e for e in self.additions if key(e) in key_del]
        if purge:
            self.additions = [e for e in self.additions \
                              if not e in self.changes]
            key_changes = [key(e) for e in self.changes]
            self.deletions = [e for e in self.deletions \
                              if not key(e) in key_changes]

    def purgeOldNew(self):
        """ Purges lists that have been compared
        >>> from comparator import Comparator
        >>> old_list = [['62145','azerty'],['1234','qwerty'],['9876','ipsum']]
        >>> new_list = [['62145','azerty'],['1234','qwertw'],['4865','lorem']]
        >>> comp = Comparator(old_list,new_list)
        >>> comp.purgeOldNew()
        >>> comp.old
        >>> comp.new
        """
        self.old = None
        self.new = None
        self.len_old = 0
        self.len_new = 0

    def check(self):
        """ Compares old and new lists attributes

        tries trivial cases
        ===================
        >>> from comparator import Comparator
        >>> old_list = [1,2,3,4,5,6]
        >>> new_list = []

        new_list is empty
        -----------------
        >>> comp = Comparator(old_list,new_list)
        >>> comp.check()

        then additions is empty
        >>> comp.additions
        []

        and deletions is old list
        >>> comp.deletions
        [1, 2, 3, 4, 5, 6]

        old_list is empty
        -----------------
        >>> comp = Comparator(new_list,old_list)
        >>> comp.check()

        then additions id new_list
        >>> comp.additions
        [1, 2, 3, 4, 5, 6]

        and deletions is empty
        >>> comp.deletions
        []

        old and new are equals
        ----------------------
        >>> comp = Comparator(old_list,old_list)
        >>> comp.check()

        then additions and deletions are empty
        >>> comp.additions
        []
        >>> comp.deletions
        []

        """
        if self.len_new == 0:
            self.deletions = self.old
            return
        if self.len_old == 0:
            self.additions = self.new
            return
        if self.old == self.new:
            return
        self.stilt_walk()

    def _append_extras(self):
        """ adds all remaining elements if we reach end of any list
        used internally
        """
        if self.index_old == self.len_old:
            self.additions.extend(self.new[self.index_new:])
            return True
        if self.index_new == self.len_new:
            self.deletions.extend(self.old[self.index_old:])
            return True
        return False

    def stilt_walk(self):
        """ follows matching pairs
        """
        #======================================================================
        # Step 1:
        # Compare an entry on the list. The last synchronization is at A[n]
        # and B[p] entries. Increment n and p until A[n] != B[n] or end
        # of either A or B. If end, process the A or B leftovers appropriately.
        # If no match at A[n+1] and B[p+1], set ns and ps equal to 1.
        # Go to step 2.
        #======================================================================
        if self._append_extras():
            return
        while self.old[self.index_old] == self.new[self.index_new]:
            self.index_old += 1
            self.index_new += 1
            if self._append_extras():
                return
        self.scout_old = 1
        self.scout_new = 1
        self.scouting()

    def scouting(self):
        """ try to resume matching
        if found, will deduce additions or deletions
        """
        #======================================================================
        # Step 2: Compare A[n+1] against B[p+ps]. If a match, then you're good.
        # The addition/deletion entries are B[p+1] through B[p+ps-1].
        # Resync at step 1 with n=n+1 and p=p+ps. Otherwise step 3.
        #======================================================================
        try:
            new_scout_value = self.new[self.index_new + self.scout_new]
        except IndexError:
            self.deletions.append(self.old[self.index_old])
            self.index_old += 1
            self.stilt_walk()
            return

        if self.old[self.index_old] == new_scout_value:
            for i in range(self.index_new, self.index_new + self.scout_new):
                self.additions.append(self.new[i])
            self.index_new += self.scout_new
            self.stilt_walk()
            return
        #======================================================================
        # Step 3: No match, so increment the ps scouting index.
        # If ps is past end of list, you know that the A[n+1] entry is not in B
        # Process entry, increment n, and go to step 1. Otherwise, step 4.
        #======================================================================
        else:
            self.scout_new += 1
        #======================================================================
        # Step 4: Compare B[p+1] to A[n+ns].
        # If match, then A[n+1] though A[n+ns-1] are the deletion/addition
        # entries (whatever the inverse of Step 2 match).
        # Resync at step 1, with n=n+ns and p=p+1. Otherwise step 5.
        #======================================================================
        try:
            old_scout_value = self.old[self.index_old + self.scout_old]
        except IndexError:
            self.additions.append(self.new[self.index_new])
            self.index_new += 1
            self.stilt_walk()
            return

        if old_scout_value == self.new[self.index_new]:
            for i in range(self.index_old, self.index_old + self.scout_old):
                self.deletions.append(self.old[i])
            self.index_old += self.scout_old
            self.stilt_walk()
            return
        #======================================================================
        # Step 5: No match, so increment the ns scouting index.
        # If ns is past end of list, you know that the B[p+1] entry is not in A
        # Process entry, increment p, and go to step 1. Otherwise go to step 2.
        #======================================================================
        else:
            self.scout_old += 1
            self.scouting()
            return
