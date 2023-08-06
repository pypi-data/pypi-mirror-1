from fnmatch import fnmatch

class FormatterBase(object):
    """
    abstract base class if you want to use __init__ methods 
    in the form of 
    'arg1, arg2, arg3, kw1=foo, kw2=bar, kw3=baz
    """

    defaults = {}

    def __init__(self, string):
        args = [ i.strip() for i in string.split(',') ]
        for index, arg in enumerate(args):
            if '=' in arg:
                break
        else:
            self.args = args
            return
        self.args = args[:index]
        self.kw = dict([i.split('=', 1) for i in args[index:]])
        for key, default in defaults.items():
            if key not in self.kw:
                self.kw[key] = default

class Ignore(object):
    """ignore files of a certain pattern"""
    

    def __init__(self, ignore):
        self.match = [ i.strip() for i in ignore.split(',')
                       if i.strip() ]

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
    """
    
    def __init__(self, pattern):
        self.match = [ i.strip() for i in pattern.split(',')
                       if i.strip() ]
        

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
        

class FilenameDescription(FormatterBase):

    def __call__(self, request, data):
        for f in data['files']:
            if f['description'] is None:
                description = f['name']
                if 'strip' in self.args:
                    description = description.rsplit('.', 1)[0]
                f['description'] = description


class TitleDescription(FormatterBase):
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
                
        
