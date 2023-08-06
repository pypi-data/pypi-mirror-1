from jinja2 import PackageLoader, Environment
from lxml import etree
import sys, os
import string
import getopt

def get_type_info(type_name, nsmap):
    ns = nsmap[None]

    if ':' in type_name:
        prefix, type_name = type_name.split(':')
        ns = nsmap[prefix]    
    
    return ns, type_name

def resolve_type(element):
    target_namespace = element.xpath('/x:schema', namespaces={'x': 'http://www.w3.org/2001/XMLSchema'})[0].get('targetNamespace')
    test_assignment = None
    
    ns, type_name = get_type_info(element.get('type'), element.nsmap)

    if ns == target_namespace:
        e = element.xpath('/x:schema/x:simpleType[@name="%s"]' % type_name, namespaces={'x': 'http://www.w3.org/2001/XMLSchema'})
        if e:
            if e[0].xpath('x:restriction/x:enumeration', namespaces={'x': 'http://www.w3.org/2001/XMLSchema'}):
                test_assignment = '%s.' % type_name
            ns, type_name = get_type_info(e[0].xpath('.//x:restriction', namespaces={'x': 'http://www.w3.org/2001/XMLSchema'})[0].get('base'), element.nsmap)
        else:    
            return type_name, '%s()' % type_name
    
    if ns == 'http://www.w3.org/2001/XMLSchema':
        if type_name == 'string': return 'str', test_assignment or '\'string value\''
        if type_name == 'dateTime': return 'datetime', 'datetime(1999, 12, 31, 23, 59, tzinfo=pytz.utc)'
        if type_name == 'integer': return 'int', '7'
        if type_name == 'boolean': return 'bool', 'True'
        raise Exception
    
    if ns in dependencies:
        ref = dependencies[ns]
        return '%s.%s' % (ref, type_name), '%s.%s()' % (ref, type_name)
    
    raise Exception('Unresolved namespace %s' % ns)

def pick_enum_for_doctest(test_assignment, constant_classes):
    if test_assignment.endswith('.'):
        for c in constant_classes:
            if c['name'] == test_assignment[:-1]:
                test_assignment = '%s.%s' % (c['name'], c['members'][0])
                break
    return test_assignment    

def go(schema_path, dependencies):
    classes = []
    constant_classes = []
    
    env = Environment(loader=PackageLoader('xmltopy', 'templates'), trim_blocks=True)
    template = env.get_template('xsdtopy.txt')
        
    x = etree.fromstring(open(schema_path).read())
    target_namespace = x.xpath('/x:schema', namespaces={'x': 'http://www.w3.org/2001/XMLSchema'})[0].get('targetNamespace')
    
    for y in x.xpath('/x:schema/x:simpleType[x:restriction/x:enumeration]', namespaces={'x': 'http://www.w3.org/2001/XMLSchema'}):
        class_data = {}
        constant_classes.append(class_data)
        class_data['name'] = y.get('name')
        class_data['members'] = []
        
        for e in y.xpath('x:restriction/x:enumeration', namespaces={'x': 'http://www.w3.org/2001/XMLSchema'}):
            class_data['members'].append(e.get('value'))
    
    for y in x.xpath('/x:schema/x:complexType', namespaces={'x': 'http://www.w3.org/2001/XMLSchema'}):
        class_data = {}
        classes.append(class_data)
        class_data['name'] = y.get('name')
        class_data['xml_namespace'] = target_namespace
        class_data['base'] = 'object'
    
        if y.xpath('.//x:extension', namespaces={'x': 'http://www.w3.org/2001/XMLSchema'}):
            class_data['base'] = y.xpath('.//x:extension', namespaces={'x': 'http://www.w3.org/2001/XMLSchema'})[0].get('base').split(':')[1]
    
        class_data['members'] = []
        class_data['types'] = []
        class_data['elements'] = []
        for e in y.xpath('.//x:sequence/x:element', namespaces={'x': 'http://www.w3.org/2001/XMLSchema'}):
            type_name, test_assignment = resolve_type(e)
            test_assignment = pick_enum_for_doctest(test_assignment, constant_classes)
            if 'maxOccurs' in e.attrib:
                maxOccurs = e.attrib['maxOccurs']
                if maxOccurs == 'unbounded' or int(maxOccurs) > 1:
                    test_assignment = '[%s, %s]' % (test_assignment, test_assignment)
                    type_name = '[%s]' % type_name
            class_data['types'].append({'name': e.get('name'), 'type': type_name, 'test_assignment': test_assignment})
            class_data['members'].append(e.get('name'))
            class_data['elements'].append(e.get('name'))
            
        class_data['attributes'] = []
        for e in y.xpath('.//x:attribute', namespaces={'x': 'http://www.w3.org/2001/XMLSchema'}):
            type_name, test_assignment = resolve_type(e)
            test_assignment = pick_enum_for_doctest(test_assignment, constant_classes)
            class_data['types'].append({'name': e.get('name'), 'type': type_name, 'test_assignment': test_assignment})
            class_data['members'].append(e.get('name'))
            class_data['attributes'].append(e.get('name'))            
            
    for y in x.xpath('/x:schema/x:element[x:complexType]', namespaces={'x': 'http://www.w3.org/2001/XMLSchema'}):
        class_data = {}
        classes.append(class_data)
        class_data['name'] = y.get('name')
        class_data['xml_namespace'] = target_namespace
        class_data['base'] = 'object'
    
        if y.xpath('.//x:extension', namespaces={'x': 'http://www.w3.org/2001/XMLSchema'}):
            class_data['base'] = y.xpath('.//x:extension', namespaces={'x': 'http://www.w3.org/2001/XMLSchema'})[0].get('base').split(':')[1]
    
        class_data['members'] = []
        class_data['types'] = []
        class_data['elements'] = []
        for e in y.xpath('.//x:sequence/x:element', namespaces={'x': 'http://www.w3.org/2001/XMLSchema'}):
            type_name, test_assignment = resolve_type(e)
            test_assignment = pick_enum_for_doctest(test_assignment, constant_classes)      
            if 'maxOccurs' in e.attrib:
                maxOccurs = e.attrib['maxOccurs']
                if maxOccurs == 'unbounded' or int(maxOccurs) > 1:
                    test_assignment = '[%s, %s]' % (test_assignment, test_assignment)
                    type_name = '[%s]' % type_name  
            class_data['types'].append({'name': e.get('name'), 'type': type_name, 'test_assignment': test_assignment})
            class_data['members'].append(e.get('name'))
            class_data['elements'].append(e.get('name'))
            
        class_data['attributes'] = []
        for e in y.xpath('.//x:attribute', namespaces={'x': 'http://www.w3.org/2001/XMLSchema'}):
            type_name, test_assignment = resolve_type(e)
            test_assignment = pick_enum_for_doctest(test_assignment, constant_classes)          
            class_data['types'].append({'name': e.get('name'), 'type': type_name, 'test_assignment': test_assignment})
            class_data['members'].append(e.get('name'))
            class_data['attributes'].append(e.get('name'))
    
    for c in classes:
        if c['base'] != 'object':
            for b in classes:
                if b['name'] == c['base']:
                    c['elements'] = b['elements'] + c['elements']
                    c['types'] = b['types'] + c['types']
                    if 'attributes' in b and 'attributes' in c:
                        c['attributes'] = b['attributes'] + c['attributes']
                    elif 'attributes' in b:
                        c['attributes'] = b['attributes']
    
    from datetime import datetime
    
    print template.render(constant_classes=constant_classes,
                          classes=classes,
                          dependencies=dependencies.values(),
                          timestamp = str(datetime.now()),
                          target_namespace = target_namespace,
                          schema_file = os.path.basename(schema_path))

if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], 'f:d:')
    dependencies = {}
    
    for o, a in opts:
        if o == '-f':
            schema_path = a
        elif o == '-d':
            for item in a.split(','):
                module, ns = item.split(':', 1)
                dependencies[ns] = module
        
    go(schema_path, dependencies)
