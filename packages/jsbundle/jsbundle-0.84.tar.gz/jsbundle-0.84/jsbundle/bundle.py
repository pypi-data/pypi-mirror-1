import glob, re, os, hashlib
from StringIO import StringIO
from jsmin import JavascriptMinify

class Directive(object):
    def __init__(self, name, args=None):
        self.name = name
        if (args):
            self.args = args.split(None)
        else:
            self.args = ''

def title_bar(text, *args):
    text = ' ' + text % args
    return "%s //\n" % text.rjust(75, '/')

class DocScanner(object):
    margin = re.compile('^([\s\*]+).*?')
    directive = re.compile('^\s*@([\w-]+)\s*(.*)$')
    
    def __init__(self, lines, filename):
        self.lines = lines
        self.filename = filename
        if (lines):
            m = self.margin.match(lines[0])
            if (m):
                self.indent = m.group(1)
            else:
                self.indent = ""
    
    def __iter__(self):
        return self.next()
    
    def next(self):
        for line in self.lines:
            if line.strip() == '':
                yield ''
                continue
            
            elif line.startswith(self.indent.rstrip(' ')):
                line = line[len(self.indent):]
            
            m = self.directive.match(line)
            if m:
                try:
                    yield Directive(m.group(1), m.group(2))
                    continue
                except:
                    pass
            
            yield line

class Module(object):
    def __init__(self, path, name):
        self.name = name
        self.path = path
        self.src = open(path).read().strip()
        self.entries = []
        self.default = None
    
    def get_requirements(self):
        reqs = set()
        for e in self.entries:
            reqs.update( e.requires )
        return reqs
    
    def entry(self, name=None, sig=None):
        if name is None:
            if self.default:
                return self.default
            else:
               self.default = entry = Entry(self.name)
        else:
            entry = Entry(name, sig)
        
        entry.module = self
        self.entries.append(entry)
        return entry
    
    def __repr__(self):
        import pprint
        return pprint.pformat(self.__dict__)

class Entry(object):
    def __init__(self, name, sig=None):
        self.name = name
        self.sig = sig
        self.requires = set()
        self.module = None
        self.directives = []
        self._lines = []
    
    def append(self, line):
        self._lines.append(line)
    
    @property
    def text(self):
        return "\n".join(self._lines).strip()

def ensure_write_buffer(string_or_buffer):
    """
    If given a string, it will be treated as a path to a file. All directories
    in the path will be created if they don't exist, and a file object will be
    returned.
    
    If given a buffer, it will ensure a .write() method and return it.
    """
    if isinstance(string_or_buffer, basestring):
        dirname = os.path.dirname(string_or_buffer)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        return open(string_or_buffer, 'w')
    else:
        if not hasattr(string_or_buffer, 'write'):
            raise TypeError("Buffer object has no write() function: %r" % string_or_buffer)
        return string_or_buffer

def join_prefix(prefix, name):
    if prefix is None:
        return ()
    else:
        return prefix + (name,)

class Bundle(object):
    """
    Bundle instances scan() for javascript files, and then allows an interface
    for compiling source, documentation, and tests.
    
    see: make() at the bottom for an example on how to use a Bundle.
    """
    re_section_doc = re.compile(r"/\*\*+(.*?)\*+/", re.S)
    
    def __init__(self, src_match = '^(?!test_|__)(?P<name>.*)\.js$',
                       test_match = '^test_(?P<name>.*)\.js$',
                       section_match = r"/\*\*+(.*?)\*+/",
                       scanner=DocScanner):
        self.modules = {}
        self.entries = {}
        self.tests = {}
        self.docs = {}
        self.src_match = re.compile(src_match, re.S)
        self.test_match = re.compile(test_match, re.S)
        self.section_match = re.compile(section_match, re.S)
        self.scanner = scanner
    
    def scan(self, path, prefix=None):
        """
        Recursively scans the given path, adding and processing all files
        matching src_match, and test_match.
        
        *path* should be a file system path
        *prefix* should be ignored, or a tuple that contains the documentation
                 path to start these files at, i.e. ('package',) -> package.module
        """
        
        basename = os.path.basename(path)
        
        if os.path.isdir(path):
            for file in os.listdir(path):
                name, _ = os.path.splitext( basename )
                self.scan(os.path.join(path, file), join_prefix(prefix, name))
            return
        
        m = self.src_match.match( basename )
        if (m):
            name = m.group('name')
            self.process_module(path, ".".join( join_prefix(prefix, name) ))
            return
        
        m = self.test_match.match( basename )
        if (m):
            name = m.group('name')
            self.process_test(path, ".".join( join_prefix(prefix, name) ))
            return
    
    def hash(self, modules=None):
        """
        Returns a hash of the full buffer source.  Usefull for a unique hash
        for each version of the source.
        """
        buffer = StringIO()
        self.compile(buffer, modules)
        return hashlib.new( 'md5', buffer.getvalue() ).hexdigest()
    
    def get_modules(self, require=None):
        """
        Returns a list of the modules, and if *require* is specified, it will
        return a list of modules with only those names, and the modules that
        are required.
        """
        include = []
        seen = set()
        
        if require is None:
            require = list(self.modules.keys())
        else:
            require = list(require)
        
        def visit(o):
            if isinstance(o, Module):
                if o not in seen:
                    seen.add(o)
                    for req in o.get_requirements():
                        visit(req)
                    include.append(o)
            elif isinstance(o, Entry):
                visit(o.module)
            elif o in self.modules:
                visit(self.modules[o])
            elif o in self.entries:
                visit(self.entries[o].module)
            else:
                RuntimeError("Cannot resolve dependancy: %r" % o)
        
        for name in require:
            visit(name)
        
        return include
    
    def compile(self, out, require=None):
        buffer = ensure_write_buffer(out)
        
        for module in self.get_modules(require):
            buffer.write(title_bar(module.path))
            buffer.write(module.src)
            buffer.write("\n\n")
    
    def compile_min(self, out, require=None):
        """
        Compiles and minifies the modules and outputs it to the given buffer 
        or path.
        
        The optional modules allows you to specify the modules you want to be
        built.
        
        If given a path as the first argument, the file will be created there,
        and all directories underneath it will be automatically created.
        """
        buffer = ensure_write_buffer(out)
        
        sbuff = StringIO()
        self.compile(sbuff, require=require)
        sbuff.seek(0)
        jsm = JavascriptMinify()
        jsm.minify( sbuff, buffer )
    
    def compile_tests(self, out, require=None):
        """
        Compiles the tests for the modules, and outputs it to the given buffer
        or path.
        
        The optional modules allows you to specify the modules you want to be
        built.
        
        If given a path as the first argument, the file will be created there,
        and all directories underneath it will be automatically created.
        """
        buffer = ensure_write_buffer(out)
        
        for module in self.get_modules(require):
            if module.name not in self.tests:
                continue
            
            test = self.tests[module.name]
                        
            buffer.write(title_bar('module tests: %s', module.name))
            buffer.write(test)
            buffer.write('\n\n')    
    
    def compile_docs(self, out, require=None):
        """
        Compiles the documents for the modules into a json structure, and 
        outputs it to the given buffer or path.
        
        The optional modules allows you to specify the modules you want to be
        built.
        
        If given a path as the first argument, the file will be created there,
        and all directories underneath it will be automatically created.
        """
        buffer = ensure_write_buffer(out)
        
        try:
            import simplejson
        except ImportError:
            print "Unable to import simplejson, 'easy_install simplejson' and try again to build the docs."
            return
        
        entries = []
        
        for module in self.get_modules(require):
            for entry in module.entries:
                e = {
                    'name': entry.name,
                    'sig': entry.sig,
                    'text': entry.text
                }
                for k, v in entry.directives:
                    e[k] = v
                entries.append(e)
        
        simplejson.dump(entries, buffer)
    
    def process_module(self, path, name):
        """
        Parses the module with the given name at the given path.
        """
        
        module = Module(path, name)
        for match in self.section_match.findall( module.src ):
            self.process_section( module, match )

        self.modules[module.name] = module
    
    def process_section(self, module, section):
        """
        Processes a section in the given module with the given source.
        """
        lines = section.split("\n")
        if not lines:
            return ()
        
        name = lines.pop(0).strip()
        if not name:
            entry = module.entry()
        elif name.startswith('@'):
            entry = module.entry()
            lines.insert(0, name)
        else:
            m = re.match(r'([\w\$\.]+)\s*(.*)', name)
            if m:
                name, sig = m.group(1).strip(), m.group(2).strip()
            else:
                sig = ''
            entry = module.entry(name, sig)
        
        for o in self.scanner(lines, section):
            if isinstance(o, Directive):
                if o.name in ('requires', 'extends'):
                    entry.requires.update( o.args )
                entry.directives.append((o.name, o.args))
            else:
                entry.append(o)
        
        self.entries[entry.name] = entry
        
    def process_test(self, path, name):
        """
        Processes the tests with the given name at the given path.
        """
        src = open(path).read().strip()
        self.tests[name] = src