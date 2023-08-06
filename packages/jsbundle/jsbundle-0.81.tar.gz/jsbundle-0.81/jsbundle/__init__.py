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
    Bundles javascript files found, recursively, at the path *src*, and
    searches *test_src* for tests.  If require is specified, it can be a list
    of require to bundle.
    
    The following keywords set the paths for specific files, if set to
    None, that means the file won't be built.
    
    *build* - the path to the full build.
    *min* - the path to the minified build.
    *docs* - the path to the documentation json build.
    *tests* - the path to the tests build.
    
    Also the keywords may contain these string-format variables:
    %(name)s - The name passed in as the first argument to build.
    %(hash)s - The last eight digits of the hash of the build.
    %(fullhash)s - The entire hash of the build.
    """
    
    bundle = Bundle(src_match=src_match, test_match=test_match)
    if isinstance(scan, basestring):
        bundle.scan( scan )
    else:
        for s in scan:
            bundle.scan( scan )
    
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