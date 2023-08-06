import unittest
from listcomparator.comparator import Comparator


class testComparator(unittest.TestCase):

    def testOldEmpty(self):
        old_list = []
        new_list = [1, 2, 3]
        comp = Comparator(old_list, new_list)
        comp.check()
        self.assertEqual(comp.additions, new_list)

    def testNewEmpty(self):
        old_list = [1, 2, 3]
        new_list = []
        comp = Comparator(old_list, new_list)
        comp.check()
        self.assertEqual(comp.deletions, old_list)

    def testBothEmpty(self):
        old_list = []
        new_list = []
        comp = Comparator(old_list, new_list)
        comp.check()
        self.assertEqual(comp.additions, [])
        self.assertEqual(comp.deletions, [])

    def testEquals(self):
        old_list = [1, 2, 3]
        new_list = [1, 2, 3]
        comp = Comparator(old_list, new_list)
        comp.check()
        self.assertEqual(comp.additions, [])
        self.assertEqual(comp.deletions, [])

    def testNewLonger(self):
        old_list = [1, 2, 3]
        new_list = [1, 2, 3, 4, 5, 6]
        comp = Comparator(old_list, new_list)
        comp.check()
        self.assertEqual(comp.additions, [4, 5, 6])
        self.assertEqual(comp.deletions, [])

    def testOldLonger(self):
        old_list = [1, 2, 3, 4, 5, 6]
        new_list = [1, 2, 3]
        comp = Comparator(old_list, new_list)
        comp.check()
        self.assertEqual(comp.additions, [])
        self.assertEqual(comp.deletions, [4, 5, 6])

    def testDel(self):
        old_list = [1, 2, 3, 4, 5, 6, 7, 8]
        new_list = [2, 5, 7]
        comp = Comparator(old_list, new_list)
        comp.check()
        self.assertEqual(comp.additions, [])
        self.assertEqual(comp.deletions, [1, 3, 4, 6, 8])

    def testAdd(self):
        old_list = [1, 2, 3, 4, 5, 6]
        new_list = [0, 1, 2, 9, 3, 4, 5, 6, 7]
        comp = Comparator(old_list, new_list)
        comp.check()
        self.assertEqual(comp.additions, [0, 9, 7])
        self.assertEqual(comp.deletions, [])

    def testMix1(self):
        old_list = [1, 2, 8]
        new_list = [0, 1, 9]
        comp = Comparator(old_list, new_list)
        comp.check()
        self.assertEqual(comp.additions, [0, 9])
        self.assertEqual(comp.deletions, [2, 8])

    def testMix2(self):
        old_list = [1, 2, 3, 4]
        new_list = [0, 1, 9, 3, 11, 7]
        comp = Comparator(old_list, new_list)
        comp.check()
        self.assertEqual(comp.additions, [0, 9, 11, 7])
        self.assertEqual(comp.deletions, [2, 4])


class testChanges(unittest.TestCase):

    def setUp(self):
        old_list = [['62145', 'azerty'], ['1234', 'qwerty'], ['9876', 'ipsum']]
        new_list = [['62145', 'azerty'], ['1234', 'qwertw'], ['4865', 'lorem']]
        self.comp = Comparator(old_list, new_list)
        self.comp.check()

    def testResults(self):
        self.assertEqual(self.comp.additions, [['1234', 'qwertw'], ['4865', 'lorem']])
        self.assertEqual(self.comp.deletions, [['1234', 'qwerty'], ['9876', 'ipsum']])

    def testFunction(self):

        def my_key(x):
            return x[0]
        self.comp.getChanges(my_key)
        self.assertEqual(self.comp.changes, [['1234', 'qwertw']])

    def testLambda(self):
        self.comp.getChanges(lambda x: x[0])
        self.assertEqual(self.comp.changes, [['1234', 'qwertw']])

    def testpurgeAddDel(self):
        self.comp.getChanges(lambda x: x[0], purge=True)
        self.assertEqual(self.comp.additions, [['4865', 'lorem']])
        self.assertEqual(self.comp.deletions, [['9876', 'ipsum']])

    def testpurgeOldNew(self):
        self.comp.purgeOldNew()
        self.assertEqual(self.comp.old, None)
        self.assertEqual(self.comp.new, None)

#def test_suite():
#    ma_suite = unittest.TestSuite()
#    todo = [unittest.makeSuite(testComparator),
#            unittest.makeSuite(testChanges), ]
#    ma_suite.addTests(todo)
#    return ma_suite

if __name__ == '__main__':
    ma_suite = unittest.TestSuite()
    ma_suite.addTest(testComparator('testMix2'))
    unittest.TextTestRunner(verbosity=2).run(ma_suite)
