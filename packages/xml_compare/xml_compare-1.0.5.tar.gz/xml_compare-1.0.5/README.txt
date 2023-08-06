===========
xml_compare 
===========

xml_compare is a XML tree comparer.

The xml_compare library allows to easily test two xml trees if they
have the same content. This is especially valuable when unit testing
XML based sistems. 

If the trees differ, xml_compare tries to give a good indication on
the nature and location of difference.

It should work with any etree implementation, but it has been developed
with lxml. 

Typical usage is::

  import unittest
  from lxml import etree  
  from xml_compare import xml_compare
  class SomeExampleTest(unittest.TestCase):
     
      def test_somefunction(self):
          expected_tree = etree.fromstring('<a><b attr="some value"/></a>')
          received_tree = etree.fromstring('<a><b attr="other value"/></a>')
          self.assertTrue( xml_compare(expected_tree, received_tree,
                                       reporter=self.fail, strip_whitespaces = True ) )
  
  if __name__ == '__main__':
      unittest.main()
 
Have fun!
