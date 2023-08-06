from fnmatch import fnmatch

class Ignore(object):

    def __init__(self, ignore):
        self.ignore = [ i.strip() for i in ignore.split(',')
                        if i.strip() ]

    def __call__(self, request, data):
        _files = []
        for f in data['files']:
            for pattern in self.ignore:
                if fnmatch(f['name'], pattern):
                    break
            else:
                _files.append(f)
        data['files'] = _files
