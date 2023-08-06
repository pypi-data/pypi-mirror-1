#!/usr/bin/env python

import sys
from fnmatch import fnmatch
from pkg_resources import iter_entry_points

### abstract base classes for formatters

class FormatterBase(object):
    """
    abstract base class if you want to use __init__ methods 
    in the form of 
    'arg1, arg2, arg3, kw1=foo, kw2=bar, kw3=baz
    """

    defaults = {} # default values for attrs to be set on the instance
    

    def __init__(self, string):
        args = [ i.strip() for i in string.split(',')]
        for index, arg in enumerate(args):
            if '=' in arg:
                break
        else:
            self.args = args
            for key, default in self.defaults.items():
                setattr(self, key, default)
            return
        self.args = args[:index]
        self.kw = dict([i.split('=', 1) for i in args[index:]])
        for key, default in self.defaults.items():
            value = self.kw.pop(key, default)
            setattr(self, key, value)


### formatters

class Ignore(object):
    """ignore files of a certain pattern"""
    

    def __init__(self, ignore):
        self.match = ignore.split()

    def __call__(self, request, data):
        _files = []
        for f in data['files']:
            for pattern in self.match:
                if fnmatch(f['name'], pattern):
                    break
            else:
                _files.append(f)
        data['files'] = _files


class All(object):
    """
    only pass files of a certain pattern; 
    the inverse of ignore
    calling all with no arguments means only files with descriptions are used
    """
    
    def __init__(self, pattern):
        self.match = pattern.split()
        

    def __call__(self, request, data):
        _files = []
        for f in data['files']:
            if self.match:
                for pattern in self.match:
                    if fnmatch(f['name'], pattern):
                        _files.append(f)
                        break
            else:
                # use only files where the description is not None
                if f['description'] is not None:
                    _files.append(f)
        data['files'] = _files
        
class Sort(object):
    """ determines how to sort the files in a directory """
    def __init__(self, pattern):
        self.args = [i.strip() for i in pattern.split(',')]
    
    def __call__(self, request, data):

        data['files'] = sorted(data['files'], key=lambda x: x['name'].lower())

        if 'reverse' in self.args:
            data['files'] = list(reversed(data['files']))
    

class FilenameDescription(FormatterBase):
    """substitute the description for the filename"""

    def __call__(self, request, data):
        for f in data['files']:
            if f['description'] is None:
                description = f['name']
                description = description.rsplit('.', 1)[0]
                decription = description.strip('_')
                if '_' in description:
                    description = ' '.join([i.title() for i in description.split('_')])
                f['description'] = description


class TitleDescription(FormatterBase):
    """splits a description into a title and a description with a separator"""
    

    defaults = { 'separator': ':' }
        
    def __call__(self, request, data):
        for f in data['files']:
            if f['description'] and self.separator in f['description']:
                title, description = f['description'].split(self.separator, 1)
                f['title'] = title
                f['description'] = description
            else:
                f['title'] = f['description']
                f['description'] = None

class CSS(object):
    """specify CSS"""

    def __init__(self, arg):
        self.css = arg.split()
    def __call__(self, request, data):
        data['css'] = self.css

class Include(object):
    """include a file at the top of the body"""

    def __init__(self, arg):
        self.include = arg
    def __call__(self, request, data):
        data['include'] = self.include

        
def formatters():
    formatters = {}
    for entry_point in iter_entry_points('decoupage.formatters'):
        try:
            formatter = entry_point.load()
        except:
            continue
        formatters[entry_point.name] = formatter
    return formatters

def main(args=sys.argv[1:]):
    for name, formatter in formatters().items():
        print '%s%s' % (name, formatter.__doc__ and ': ' + formatter.__doc__ or '')

if __name__ == '__main__':
    main()
