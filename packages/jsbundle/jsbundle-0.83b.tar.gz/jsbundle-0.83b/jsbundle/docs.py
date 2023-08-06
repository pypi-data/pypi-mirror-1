#!/usr/bin/env python

import os
import re

re.comments = re.compile(r'\/\*\*(.*?)\*\*\/', re.M | re.S)

class Section(object):
    def __init__(self, name=None, description=None, args=None, important=False):
        self.path = name.split('.')
        self.name = self.path[-1]
        self.description = description.strip()
        self.children = {}
        self.args = args
        self.built = False
        self.important = important
    
    def add(self, who):
        self.children[who.name] = who
    
    @property
    def sorted_children(self):
        keys = self.children.keys()
        keys.sort()
        return [self.children[k] for k in keys]
    
    @property
    def name_with_args(self):
        return self.name + (self.args or '')
    
    def format(self, tabs=0):
        spaces = tabs * '  '
        children = "".join(child.format(tabs + 1) for child in self.sorted_children)
        dashes = (3 - tabs) * '=' or '-'
        return "%s%s %s %s\n%s%s\n\n%s" % (spaces, dashes, self.name_with_args, dashes, spaces, self.description.replace('\n', '\n' + spaces), children)
        
    __str__ = format
    
    def __repr__(self):
        return "<Section: %s>" % self.name
        
    def simple(self, mode='html'):
        return {
            'path': self.path,
            'name': self.name,
            'args': self.args,
            'description': self.description.replace('\n', '<br/>').replace('  ', ' &nbsp;'),
            'children': [c.simple(mode) for c in self.sorted_children],
            'important': self.important
        }
 
class Scanner(object):
    def __init__(self):
        self.parts = {}
        
    def parse_comment(self, src):
        src = src.strip()
        name, description = src.split('\n', 1)
        
        ## Get rid of spaces at the beginning of each line.
        count = 0
        while (description[count].isspace()):
            if (description[count] == '\n'):
                description = description[count+1:]
                count = 0
                continue
            count += 1
        description = description.replace('\n' + ' ' * count, '\n')
        
        important = False
        if name.endswith('!important'):
            name = name[:-len('!important')]
            important = True
        
        args = None
        ## Split up the name into name and args
        if '(' in name:
            name, args = name.split('(', 1)
            args = '(' + args
        
        name = name.strip()
        
        self.parts[name] = Section(name=name, description=description, args=args, important=important)
    
    def build(self, sig):
        section = self.parts[sig]
        if section.built: return
        
        if len(section.path) == 1:
            self.roots.append(section)
        else:
            parent_sig = ".".join(section.path[:-1])
            self.parts[parent_sig].add(section)
            
        section.built = True
    
    def compile(self):
        self.roots = []
        keys = self.parts.keys()
        keys.sort()
        for sig in keys:
            self.build(sig)
        self.roots.sort(lambda a, b: cmp(a.name, b.name))
        return self.roots
    
    def scan(self, path):
        if os.path.isdir(path):
            for l in os.listdir(path):
                if l.endswith('.js') or os.path.isdir(l): 
                    self.scan(os.path.join(path, l))
        else:
            for i in re.comments.findall(open(path).read()):
                self.parse_comment(i)
 
def scan(path):
    scanner = Scanner()
    scanner.scan(path)
    return scanner.compile()