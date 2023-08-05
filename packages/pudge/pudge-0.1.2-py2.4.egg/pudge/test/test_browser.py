
import pudge.browser as browser

module_names = ['pudge.test.package']
root = browser.Browser(module_names, [])

def test_browser_modules():
    modules = root.modules()
    import pudge.test.package
    assert len(modules) == 1
    assert modules[0] is not None
    actual, expected = modules[0].obj, pudge.test.package
    assert modules[0].obj == pudge.test.package
    
def test_package():
    package = root.modules()[0]
    assert package.ispackage()
    assert package.ismodule()
    assert not package.isclass()
    assert not package.isroutine()
    return package

package = test_package()

def test_module_members():
    expected_members = sorted(['string', 'func', 'name', 'pi', 'subpackage', 'Class'])
    actual_members = sorted(package.members.keys())
    assert actual_members == expected_members

def test_module_all():
    expected_members = sorted(['func', 'name', 'pi', 'subpackage', 'Class'])
    actual_members = sorted([m.name for m in package.all()])
    assert actual_members == expected_members

def test_module_all_classes():
    expected_members = ['Class']
    actual_members = [m.name for m in package.classes()]
    assert actual_members == expected_members

def test_module_all_routines():
    expected_members = ['func']
    actual_members = [m.name for m in package.routines()]
    assert actual_members == expected_members

def test_module_all_attributes():
    expected_members = ['pi', 'name']
    actual_members = [m.name for m in package.attributes()]
    assert actual_members == expected_members

def test_module_all_modules():
    expected_members = ['subpackage']
    actual_members = [m.name for m in package.modules()]
    assert actual_members == expected_members

cls = package.members['Class']

def test_class_doc():
    assert cls.hasdoc()
    assert cls.doc().startswith("A cool blurb about this class.\n\n")
    
def test_class_all():
    expected_members = sorted(['__init__', 'before', 'method', 'name'])
    actual_members = sorted([m.name for m in cls.all()])
    assert actual_members == expected_members
    
def test_class_all_routines():
    expected_members = sorted(['__init__', 'before', 'method'])
    actual_members = sorted([m.name for m in cls.routines()])
    assert actual_members == expected_members
