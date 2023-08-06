============
dict_compare
============

dict_compare compares two python dictionaries and reports on any
differences between them. 

This can be very handy when comparing dictionary structures. Typical
case is comparing expected and received values in a unittest. 

The typical use case is::

  import unittest
  from dict_compare import dict_compare

  class TestSample(unittest.TestCase):
      def test_someExample(self):
          expected_dict = {
              'foo': 'bar',
              'quux': ['some', 'more']
          }
          received_dict = {
              'foo': 'bar',
              'quux': ['some', 'other']
          }
          self.assertTrue( dict_compare(expected_dict, received_dict, reporter=self.fail) )

  if __name__ == '__main__':
      unittest.main()

Have fun!

