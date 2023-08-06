from bundle import *

def make( name,
          require = None,
          build = 'build/%(name)s-%(hash)s.js',
          min = 'build/%(name)s-%(hash)s.min.js',
          docs = 'build/%(name)s.docs.js',
          tests = 'build/%(name)s.tests.js',
          src_match = '^(?!test_|__)(?P<name>.*)\.js$',
          test_match = '^test_(?P<name>.*)\.js$',
          scan = 'js' ):
    """
    Bundles up your javascript.
    
    *require*
        A list of requirements to build.  This allows you to build only the 
        modules you want, and any modules that are required by them.  This 
        defaults to None, meaning build all the modules found.

    *scan*
        A path string or iterable of path strings to scan for files.  This
        defaults to 'js'.

    *src_match*
        A regular expression that must be matched for the source to be
        included as a module.  It must contain a named group "name", that will
        define the name of the module.  
        It defaults to ^(?!test_|__)(?P<name>.*)\.js$

    *test_match*
        Like *src_match* above, but to gather test files.  It must also define
        a named group "name". It defaults to ^test_(?P<name>.*)\.js$

    In the following string arguments, one can include these variables to be
    expanded:
    %(name)s - The name passed in as the first argument to make.
    %(hash)s - The last eight digits of the hash of the bundle.
    %(fullhash)s - The entire hash of the bundle.

    Also, they define paths to create files at, all directories needed to get
    to that end point will be created if need be.
    
    *build*
        A path string to the main build file. This is the combined full source
        of all the modules to be bundled.
    	defaults to: build/%(name)s-%(hash)s.js

    *min*
        A path string to the minified build file.  This is the combined source
        of all modules after being minified, meaning all comments are
        stripped, and useless whitespace removed.
        defaults to: build/%(name)s-%(hash)s.min.js

    *tests*
        A path string to the test file. All test files found that can be
        matched up to modules will be combined into this one file.
        defaults to: build/%(name)s-%(hash)s.tests.js

    *docs*
        A path string to a json document of documentation entries.  Read the
        documentation section for more information on entries.
        defaults to: build/%(name)s-%(hash)s.docs.js
    """
    
    bundle = Bundle(src_match=src_match, test_match=test_match)
    if isinstance(scan, basestring):
        bundle.scan( scan )
    else:
        for s in scan:
            bundle.scan( s )
    
    hash = bundle.hash(require)
    context = {'name': name, 'hash': hash[-8:], 'fullhash': hash}
    
    if build:
        bundle.compile(build % context, require=require)
    if min:
        bundle.compile_min(min % context, require=require)
    if docs:
        bundle.compile_docs(docs % context, require=require)
    if tests:
        bundle.compile_tests(tests % context, require=require)
    
    return hash