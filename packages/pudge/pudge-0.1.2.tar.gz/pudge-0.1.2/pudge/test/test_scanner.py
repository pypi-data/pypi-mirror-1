
from setupenv import *

def count_file_lines(filename):
    fo = open(filename, 'r')
    try:
        cnt=0
        while fo.readline():
            cnt+=1
    finally:
        fo.close()
    return cnt

# put a test_ at the beginning of this function to get a dump of the
# tuplize that you can paste here.
def dont_test_dump_tuble():
    from pprint import pprint
    tup = test_file_token().tuplize()
    print pprint(tup)
    assert 0


def test_file_token():
    from pudge.scanner import scan
    
    filename = get_test_file('short.py')
    file_token = scan(filename)
    actual_line_count = count_file_lines(filename)
    assert file_token.type == 'file'
    assert file_token.name == filename
    assert file_token.line == 0
    assert file_token.indent == -1
    assert file_token.last_line == actual_line_count

    return file_token

def test_module_attribute_token():
    file_token = test_file_token()
    attr_token = file_token.find('attribute')
    assert attr_token.name == 'attribute'
    assert attr_token.type == '='
    assert attr_token.line == 6
    assert attr_token.last_line == 9
    assert attr_token.indent == 0
    assert len(attr_token.children) == 0
    return attr_token

def test_function_token():
    file_token = test_file_token()
    token = file_token.find('function')
    assert token.name == 'function'
    assert token.type == 'def'
    assert token.line == 9
    assert token.last_line == 13
    assert token.indent == 0
    assert len(token.children) == 0
    return token

def test_old_class_token():
    file_token = test_file_token()
    token = file_token.find('OldClass')
    assert token.name == 'OldClass'
    assert token.type == 'class'
    assert token.line == 13
    assert token.last_line == 21
    assert token.indent == 0
    assert len(token.children) == 2
    return token

def test_new_class_token():
    file_token = test_file_token()
    token = file_token.find('NewClass')
    assert token.name == 'NewClass'
    assert token.type == 'class'
    assert token.line == 21
    assert token.last_line == 28
    assert token.indent == 0
    assert len(token.children) == 2
    return token

def test_depth_find():
    file_token = test_file_token()
    token = file_token.find('NewClass.method')
    assert token.name == 'method'

def test_dict_interface():
    file_token = test_file_token()
    assert file_token['NewClass.method'] == file_token.find('NewClass.method')

def test_caching():
    import pudge.scanner as scanner
    filename = get_test_file('short.py')
    file_token = scanner.scan(filename, cache=1)
    assert scanner.scan(filename) is file_token
    
def test_empty_cache():
    import pudge.scanner as scanner
    filename = get_test_file('short.py')
    file_token = scanner.scan(filename, cache=1)
    scanner.empty_cache()
    assert scanner.scan(filename) is not file_token
