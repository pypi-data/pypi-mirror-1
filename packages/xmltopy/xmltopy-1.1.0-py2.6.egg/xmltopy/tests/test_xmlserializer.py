import unittest
from xmltopy.xmlserializer import *
from test_classes import *
from lxml import etree
from datetime import datetime

try: import pytz
except ImportError: print 'WARNING! pytz not installed. datetime related tests will fail.'

class TestReflexivity(unittest.TestCase):
    def test_empty_children(self):
        widget = Widget()
        widget.Customer = Person()
        
        tree = toxml(widget)        
        expected = '<Widget xmlns="http://www.example.com/schemas/widget"><Customer/></Widget>'
        self.assertEqual(expected, etree.tostring(tree))
        
        widget_after = fromxml(tree, Widget())
        self.assertFalse(widget_after.Customer is None)
        
        tree_after = toxml(widget_after)        
        self.assertEqual(expected, etree.tostring(tree_after))
    
    def test_empty_class(self):
        widget = Widget()
        self.assertEqual(None, widget.Name)
        self.assertEqual(None, widget.Description)
        self.assertEqual(None, widget.Created)
        self.assertEqual(None, widget.IsActive)
        self.assertEqual(None, widget.Default)
        self.assertEqual(None, widget.Color)
        self.assertEqual(None, widget.Customer)          
        
        tree = toxml(widget)        
        expected = '<Widget xmlns="http://www.example.com/schemas/widget"/>'
        self.assertEqual(expected, etree.tostring(tree))
        
        widget_after = fromxml(tree, Widget())
        self.assertEqual(None, widget_after.Name)
        self.assertEqual(None, widget_after.Description)
        self.assertEqual(None, widget_after.Created)
        self.assertEqual(None, widget_after.IsActive)
        self.assertEqual(None, widget_after.Default)
        self.assertEqual(None, widget_after.Color)
        self.assertEqual(None, widget_after.Customer)
        
        tree_after = toxml(widget_after)        
        self.assertEqual(expected, etree.tostring(tree_after))

    def test_single_class(self):
        widget = Widget()
        widget.Name = 'Woozle'
        widget.Description = 'The Woozle is Widget'
        widget.Created = datetime(1999, 12, 31, 23, 59, 59, tzinfo=pytz.utc)
        widget.IsActive = True
        widget.Default = False
        widget.Color = 'red'
        widget.LastPurchase = datetime(2009, 1, 2, 3, 4, 5, tzinfo=pytz.utc)
        
        tree = toxml(widget)
        expected = '<Widget xmlns="http://www.example.com/schemas/widget" Default="false" Color="red" LastPurchase="2009-01-02T03:04:05+00:00"><Name>Woozle</Name><Description>The Woozle is Widget</Description><Created>1999-12-31T23:59:59+00:00</Created><IsActive>true</IsActive></Widget>'
        self.assertEqual(expected, etree.tostring(tree))        

        widget_after = fromxml(tree, Widget())
        self.assertEqual('Woozle', widget_after.Name)
        self.assertEqual('The Woozle is Widget', widget_after.Description)
        self.assertEqual(datetime(1999, 12, 31, 23, 59, 59, tzinfo=pytz.utc), widget_after.Created)
        self.assertEqual(True, widget_after.IsActive)
        self.assertEqual(False, widget_after.Default)
        self.assertEqual('red', widget_after.Color)
        self.assertEqual(datetime(2009, 1, 2, 3, 4, 5, tzinfo=pytz.utc), widget_after.LastPurchase)
        self.assertEqual(None, widget_after.Customer)
        
        tree_after = toxml(widget_after)        
        self.assertEqual(expected, etree.tostring(tree_after))
        
    def test_list_values(self):        
        widget = Widget()
        widget.Sku = ['part1', 'part2', 'part3',]
        
        tree = toxml(widget)
        expected = '<Widget xmlns="http://www.example.com/schemas/widget"><Sku>part1</Sku><Sku>part2</Sku><Sku>part3</Sku></Widget>'
        self.assertEqual(expected, etree.tostring(tree))
        
        widget_after = fromxml(tree, Widget())
        self.assertTrue(isinstance(widget_after.Sku, list))
        self.assertEqual(3, len(widget.Sku))
        self.assertTrue('part1' in widget_after.Sku)
        self.assertTrue('part2' in widget_after.Sku)
        self.assertTrue('part3' in widget_after.Sku)
        
        tree_after = toxml(widget_after)        
        self.assertEqual(expected, etree.tostring(tree_after))        

    def test_lists_with_one_value(self):
        # ensure lists with a single value remain a list after py -> xml -> py
        widget = Widget()
        widget.Sku = ['part1',]
        
        tree = toxml(widget)
        expected = '<Widget xmlns="http://www.example.com/schemas/widget"><Sku>part1</Sku></Widget>'
        self.assertEqual(expected, etree.tostring(tree))
        
        widget_after = fromxml(tree, Widget())
        self.assertTrue(isinstance(widget_after.Sku, list))
        self.assertEqual(1, len(widget.Sku))
        self.assertTrue('part1' in widget_after.Sku)
        
        tree_after = toxml(widget_after)        
        self.assertEqual(expected, etree.tostring(tree_after))           

class TestToXml(unittest.TestCase):
    def test_empty_children(self):
        widget = Widget()
        widget.Customer = Person()
        
        tree = toxml(widget)        
        expected = '<Widget xmlns="http://www.example.com/schemas/widget"><Customer/></Widget>'
        self.assertEqual(expected, etree.tostring(tree))
        
    def test_child_with_just_attributes(self):
        widget = Widget()
        widget.Customer = Person()
        widget.Customer.IsDefault = 'yes'
        
        tree = toxml(widget)        
        expected = '<Widget xmlns="http://www.example.com/schemas/widget"><Customer IsDefault="yes"/></Widget>'
        self.assertEqual(expected, etree.tostring(tree))        
        
    def test_empty_class(self):
        widget = Widget()
        tree = toxml(widget)
        expected = '<Widget xmlns="http://www.example.com/schemas/widget"/>'
        self.assertEqual(expected, etree.tostring(tree))
    
    def test_single_class(self):
        widget = Widget()
        widget.Name = 'Woozle'
        widget.Description = 'The Woozle is Widget'
        widget.Created = datetime(1999, 12, 31, 23, 59, 59, tzinfo=pytz.utc)
        widget.IsActive = True
        widget.Default = False
        widget.Color = 'red'
        widget.Id = 42
        widget.LastPurchase = datetime(2009, 1, 2, 3, 4, 5, tzinfo=pytz.utc)
        
        tree = toxml(widget)
        expected = '<Widget xmlns="http://www.example.com/schemas/widget" Default="false" Color="red" LastPurchase="2009-01-02T03:04:05+00:00"><Id>42</Id><Name>Woozle</Name><Description>The Woozle is Widget</Description><Created>1999-12-31T23:59:59+00:00</Created><IsActive>true</IsActive></Widget>'
        self.assertEqual(expected, etree.tostring(tree))
    
    def test_class_hierarchy(self):
        widget = Widget()
        widget.Name = 'Woozle'
        widget.Customer = Person()
        widget.Customer.FullName = 'Kilroy'
        
        tree = toxml(widget)
        expected = '<Widget xmlns="http://www.example.com/schemas/widget"><Name>Woozle</Name><Customer><FullName>Kilroy</FullName></Customer></Widget>'
        self.assertEqual(expected, etree.tostring(tree))
        
    def test_list_values(self):
        widget = Widget()
        widget.Name = ['part1', 'part2', 'part3',]
        
        tree = toxml(widget)
        expected = '<Widget xmlns="http://www.example.com/schemas/widget"><Name>part1</Name><Name>part2</Name><Name>part3</Name></Widget>'
        self.assertEqual(expected, etree.tostring(tree))

        widget = Widget()
        widget.Customer = [Person(), Person()]
        widget.Customer[0].FullName = 'Kilroy'
        widget.Customer[1].FullName = 'Anakin'
        
        tree = toxml(widget)
        expected = '<Widget xmlns="http://www.example.com/schemas/widget"><Customer><FullName>Kilroy</FullName></Customer><Customer><FullName>Anakin</FullName></Customer></Widget>'
        self.assertEqual(expected, etree.tostring(tree))        

class TestFromXml(unittest.TestCase):
    def test_empty_children(self):
        xml = '<Widget xmlns="http://www.example.com/schemas/widget"><Customer/></Widget>'
        tree = etree.fromstring(xml)
        widget = fromxml(tree, Widget())
        self.assertFalse(widget.Customer is None)

    def test_child_with_just_attributes(self):
        xml = '<Widget xmlns="http://www.example.com/schemas/widget"><Customer IsDefault="yes"/></Widget>'
        tree = etree.fromstring(xml)
        widget = fromxml(tree, Widget())
        self.assertFalse(widget.Customer is None)
        self.assertEqual('yes', widget.Customer.IsDefault)
    
    def test_empty_tree(self):
        xml = '<Widget xmlns="http://www.example.com/schemas/widget"/>'
        tree = etree.fromstring(xml)
        widget = fromxml(tree, Widget())
        self.assertEqual(None, widget.Name)
        self.assertEqual(None, widget.Description)
        self.assertEqual(None, widget.Created)
        self.assertEqual(None, widget.IsActive)
        self.assertEqual(None, widget.Default)
        self.assertEqual(None, widget.Color)
        self.assertEqual(None, widget.Customer)
    
    def test_single_class(self):
        xml = '<Widget xmlns="http://www.example.com/schemas/widget" Default="false" Color="red" LastPurchase="2009-01-02T03:04:05+00:00"><Id>42</Id><Name>Woozle</Name><Description>The Woozle is Widget</Description><Created>1999-12-31T23:59:59+00:00</Created><IsActive>true</IsActive></Widget>'
        tree = etree.fromstring(xml)
        widget = fromxml(tree, Widget())
        self.assertEqual('Woozle', widget.Name)
        self.assertEqual('The Woozle is Widget', widget.Description)       
        self.assertEqual(datetime(2009, 1, 2, 3, 4, 5, tzinfo=pytz.utc), widget.LastPurchase)        
        self.assertEqual(datetime(1999, 12, 31, 23, 59, 59, tzinfo=pytz.utc), widget.Created)
        self.assertEqual(True, widget.IsActive)
        self.assertEqual(False, widget.Default)
        self.assertEqual('red', widget.Color)
        self.assertEqual(None, widget.Customer)
        self.assertEqual(42, widget.Id)
    
    def test_class_hierarchy(self):     
        xml = '<Widget xmlns="http://www.example.com/schemas/widget"><Name>Woozle</Name><Customer><FullName>Kilroy</FullName></Customer></Widget>'
        tree = etree.fromstring(xml)
        widget = fromxml(tree, Widget())
        self.assertEqual('Woozle', widget.Name)        
        self.assertEqual('Kilroy', widget.Customer.FullName)
        