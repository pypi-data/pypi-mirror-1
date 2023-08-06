"""
Module for serializing Python objects to and from XML
"""

from lxml import etree
from datetime import datetime, date
import iso8601

def split_tag(tag):
    if tag.startswith('{'):
        return tag[1:].split('}')
    else:
        return None, tag

def get_nsmap(obj):
    if not hasattr(obj, '_xml_metadata'):
        return None
    
    return {None: obj._xml_metadata['namespace']}

def toxml(obj, root=None):
    if hasattr(obj, '_xml_metadata'):
        elements = obj._xml_metadata['sequence']
        if 'attributes' in obj._xml_metadata:
            attributes = obj._xml_metadata['attributes']
        else:
            attributes = []
    else:
        elements = obj.__dict__
        attributes = []
   
    if root == None:
        root = etree.Element(obj.__class__.__name__, nsmap=get_nsmap(obj))

    for attribute in attributes:
        value = getattr(obj, attribute)
        if value is not None:
            if isinstance(value, str): 
                root.set(attribute, value)
            elif isinstance(value, bool):
                if value == True: root.set(attribute, 'true')
                else: root.set(attribute, 'false')
            elif hasattr(value, 'isoformat') and hasattr(value, 'time'):
                root.set(attribute, value.isoformat('T'))
            elif hasattr(value, 'isoformat'):
                root.set(attribute, value.isoformat())
            else:
                root.set(attribute, str(value))
                
    for element in elements:
        values = getattr(obj, element)
        if values is None:
            continue
        
        if not isinstance(values, list):
            values = [values]
        
        for value in values:
            if isinstance(value, str): 
                etree.SubElement(root, element).text = value
            elif isinstance(value, bool):
                if value == True: etree.SubElement(root, element).text = 'true'
                else: etree.SubElement(root, element).text = 'false'
            elif hasattr(value, 'isoformat') and hasattr(value, 'time'):
                etree.SubElement(root, element).text = value.isoformat('T')
            elif hasattr(value, 'isoformat'):
                etree.SubElement(root, element).text = value.isoformat()
            elif hasattr(value, '_xml_metadata') or hasattr(value, '__dict__'):
                toxml(value, etree.SubElement(root, element, nsmap=get_nsmap(value)))
            else:
                etree.SubElement(root, element).text = str(value)
                
    return root

def fromxml(root, obj):
    for attrib in root.attrib:
        if hasattr(obj, '_xml_metadata') and attrib in obj._xml_metadata['types']:
            child_type = obj._xml_metadata['types'][attrib]()
        else:
            child_type = None        
        
        if child_type is str:
            setattr(obj, attrib, root.attrib[attrib])
        elif child_type is int:
            setattr(obj, attrib, int(root.attrib[attrib]))            
        elif child_type is bool:
            if root.attrib[attrib] == 'true': setattr(obj, attrib, True)
            else: setattr(obj, attrib, False)
        elif child_type is datetime:
            if root.attrib[attrib] is None or len(root.attrib[attrib]) == 0:
                setattr(obj, attrib, None)
            else:
                setattr(obj, attrib, iso8601.parse_date(root.attrib[attrib]))
        else:
            setattr(obj, attrib, str(root.attrib[attrib]))

    values = {}
    for child in root.iterchildren(tag=etree.Element):
        ns, name = split_tag(child.tag)
        
        child_type_is_list = False
        if hasattr(obj, '_xml_metadata') and name in obj._xml_metadata['types']:
            child_type = obj._xml_metadata['types'][name]()
            if isinstance(child_type, list):
                child_type_is_list = True
                child_type = child_type[0]
        else:
            child_type = None
        
        if len(child) == 0:
            if child_type is str:
                value = child.text
            elif child_type is int:
                if child.text is None or len(child.text) == 0:
                    value = None
                else:
                    value = int(child.text)
            elif child_type is bool:
                if child.text == 'true': value = True
                else: value = False
            elif child_type is datetime:
                if child.text is None or len(child.text) == 0:
                    value = None
                else:
                    value = iso8601.parse_date(child.text)
            elif hasattr(child_type, '_xml_metadata'):
                child_obj = child_type()
                value = fromxml(child, child_obj)            
            else:
                value = child.text
        elif child_type is not None:
            child_obj = child_type()
            value = fromxml(child, child_obj)            
        
        if name in values and isinstance(values[name], list):
            values[name].append(value)
        elif child_type is None and name in values:
            values[name] = [values[name], value] # child_type undefined, and existing value found, then turn it into a list
        elif child_type_is_list == True:
            values[name] = [value] # if child_type is defined, and indicates a list, then always create a list
        else:
            values[name] = value

    for value in values:
        setattr(obj, value, values[value])
            
    return obj


