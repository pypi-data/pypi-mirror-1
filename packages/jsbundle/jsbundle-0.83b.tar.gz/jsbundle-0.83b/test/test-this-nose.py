import os
from make import make
from nose import with_setup

if not os.path.exists('make.py'):
    raise RuntimeError("Nosetests should be run in the directory with make.py")

### Tests ###
@with_setup(make)
def build_test():
    src = open('build/test.js').read()
    assert(src.find('one = true') > -1)
    assert(src.find('d_one = true') > -1)
    assert(src.find('two = true') > -1)
    assert(src.find('d_two = true') > -1)
    assert(src.find('three = true') == -1)

@with_setup(make)
def min_test():
    src = open('build/test.min.js').read()
    assert(src.find('one=true') > -1)
    assert(src.find('two=true') > -1)
    assert(src.find('three=true') == -1)

@with_setup(make)
def tests_test():
    src = open('build/test.tests.js').read()
    assert(src.find('test_one = true;') > -1)
    assert(src.find('test_d_one = true;') > -1)
    assert(src.find('test_two = true') == -1)    # Cause it doesn't have tests
    assert(src.find('test_three = true;') == -1) # Cause it's not in our *modules* sent in to build()

@with_setup(make)
def test_docs():
    import simplejson
    docs = simplejson.load(open('build/test.docs.js'))
    
    one = None
    two = None
    require = None
    for entry in docs:
        print entry['name'], '-', entry['sig']
        if entry['name'] == 'Test.one':
            one = entry
        if entry['name'] == 'Test.two':
            two = entry
        if entry['name'] == 'Test.one.require':
            require = entry
            
    assert one
    assert one['sig'] == '!module'
    assert one['text'] == "The test module."
    
    assert two
    assert two['sig'] == ''
    assert two['text'] == 'The second test module.'
    
    assert require
    assert require['sig'] == '( [.js or .css files] )'
    
def test_dependancies():
    def test_order(modules, expected):
        make(modules)
        src = open('build/test.js').read()
        
        results = [(src.find(string), string) for string in expected]
        results.sort()
        results = [r[1] for r in results]
        print "Expected:", expected
        print "Got:", results
        assert results == expected

    test_order(
        ['dependancies.one', 'dependancies.two', 'one', 'two'],
        ['js/dependancies/one.js', 'js/dependancies/two.js', 'js/one.js', 'js/two.js']
    )
    
    test_order(
        ['one', 'two'],
        ['js/dependancies/one.js', 'js/one.js', 'js/dependancies/two.js', 'js/two.js']
    )