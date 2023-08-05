"""skel - Template-based filesystem manipulation.

Copyright (C) 2006 Luke Arno - http://lukearno.com/

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to 
the Free Software Foundation, Inc., 51 Franklin Street, 
Fifth Floor, Boston, MA  02110-1301  USA

Luke Arno can be found at http://lukearno.com/

"""

from os import walk, sep, makedirs, chmod, lstat
from os.path import exists, abspath
from string import Template
import re
from fnmatch import fnmatch


def fnmatch_any(name, patterns):
    """Name matchs any of the give patterns via fnmatch.
    
    In case it is useful, returns pattern that matched or ''.
    """
    for pattern in patterns:
        if fnmatch(name, pattern):
            return pattern
    return ""


def prompt_for_overwrite(path):
    """Return True/False based on user input."""
    print "File exists:", path
    overwrite = ''
    while overwrite not in ('y','n'):
        overwrite = raw_input("Overwrite? (y/n) >").lower()
    return overwrite == 'y'


class Builder(object):
    """Filesystem manipulation using templates, data and filters."""

    default_regex = r'\+(?P<key>\w+)\+'

    def __init__(self, data, 
                 ignore=None, filters=None, 
                 overwrite=False, regex=None):
        """Initialize a Builder (duh! :-)
        
        data - the variables to replace
        ignore - list of patterns not to copy at all
        filters - list of filters (see StringTemplateFilter docs)
        regex - regex to find variables in file/dir names
        overwrite - True False or 'PROMPT'
        """
        self.data = data
        if ignore is None:
            ignore = []
        self.ignore = ignore
        if filters is None:
            filters = []
        self.filters = filters
        if regex is None:
            regex = self.default_regex
        self.set_regex(regex)
        self.overwrite = overwrite
    
    def set_regex(self, regex):
        """Compile and set the regex used on directory names.
        
        Should have named group 'key' to be compatible with xlat().
        """
        self.regex = re.compile(regex)

    def xlat(self, match):
        """Return the appropriate value from data for the match."""
        return self.data.get(match.group('key'), match.group(0))

    def replace_path(self, path):
        """Replace variables in a path using regex and data."""
        return self.regex.sub(self.xlat, path)

    def to_where(self, from_base, to_base, path):
        """Get path of a (possibly) new directory."""
        to_dir = sep.join([to_base, path[len(from_base)+1:]])
        return self.replace_path(to_dir)

    def ignorable(self, name):
        """Is file ignorable?"""
        return fnmatch_any(name, self.ignore)

    def find_filter(self, to_path):
        """Find a filter that applies to this file.
        
        returns (filter or None, possibly transformed path)
        """
        for filter in self.filters:
            if filter.applies(to_path):
                return filter, filter.new_path(to_path)
        else:
            return None, to_path

    def overwritable(self, to_path):
        """Is path overwritable? (may prompt)"""
        if self.overwrite == 'PROMPT':
            return prompt_for_overwrite(to_path)
        else:
            return self.overwrite

    def build(self, from_base, to_base):
        """Build new directory structure and files based on template."""
        from_base, to_base = map(abspath, (from_base, to_base))
        file_count = 0
        dir_count = 0
        for from_dir, dirs, files in walk(from_base):
            if [i for i in from_dir.split(sep) if self.ignorable(i)]:
                continue
            to_dir = self.to_where(from_base, to_base, from_dir)
            try:
                makedirs(to_dir)
                dir_count += 1
            except OSError:
                pass
            for name in [n for n in files if not self.ignorable(n)]:
                from_path = sep.join([from_dir, name])
                to_path = sep.join([to_dir, name])
                to_path = self.replace_path(to_path)
                filter, to_path = self.find_filter(to_path)
                if exists(to_path) and not self.overwritable(to_path):
                    continue
                from_file = open(from_path, 'rb')
                to_file = open(to_path, 'w')
                if filter is None:
                    to_file.write(from_file.read())
                else:
                    to_file.write(filter(from_file.read(), self.data))
                to_file.close()
                from_file.close()
                print to_path
                chmod(to_path, lstat(from_path)[0])
                file_count += 1
        return dir_count, file_count


class StringTemplateFilter(object):
    """String template based filter builder."""

    extension = '.tpl'

    def applies(self, to_path):
        """Does this filter apply to this path?
        
        (Does it have the right extension in this case?)
        """
        return to_path.endswith(self.extension)

    def new_path(self, to_path):
        """Convert the path.
        
        (In this case, knock the extension off.)
        """
        return to_path[:-len(self.extension)]

    def __call__(self, text, data):
        """Replace variables in file contents."""
        return Template(text).safe_substitute(data)


def prompt_for_dct(dct):
    """Prompt for new value for each key/val in dct.
    
    Empty input means keep default value.
    """
    for key, val in dct.iteritems():
        print "Just press enter for default: " + val
        newval = raw_input("%s > " % key)
        if newval:
            dct[key] = newval
    return dct


def command():
    """Command line interface."""
    import sys
    from optparse import OptionParser
    usage="%prog template_dir destination_dir [options]"
    parser = OptionParser(usage=usage, version="skel 0.01") 
    parser.add_option('-i', '--ignore', dest='ignore', default='',
                      help='comma separated list of patterns to ignore')
    parser.add_option('-o', '--overwrite', dest='overwrite', 
                      action='store_true', default='PROMPT',
                      help='overwrite existing files')
    parser.add_option('-k', '--keep', dest='overwrite', 
                      action='store_false', default='PROMPT',
                      help='keep existing files')
    parser.add_option('-d', '--data', dest='data',
                      help='vars for replacement '
                           'like foo=bar,spam=eggs')
    parser.add_option('-f', '--file', dest='file', 
                      help='file containing vars whitespace separated '
                           'like foo=bar spam=eggs')
    parser.add_option('-p', '--prompt', dest='prompt', 
                      action='store_true', 
                      help='prompt for all variables')
    parser.add_option('-r', '--regex', dest='regex', 
                      default=Builder.default_regex, 
                      help='regex for identifying variables in paths '
                           '(must have named group "key")')
    opts, args = parser.parse_args()
    if len(args) <> 2:
        print "Not enough arguments."
        print
        parser.print_help()
        sys.exit(1)
    data = {}
    try:
        if opts.file:
            data.update((d.split('=') 
                        for d in open(opts.file, 'rb').read().split()))
    except:
        print "Problem with file on -f or --file option."
        print
        parser.print_help()
        sys.exit(1)
    try:
        if opts.data:
            data.update((d.split('=') for d in opts.data.split(',')))
    except:
        print "Problem with syntax of -d or --dict option."
        print
        parser.print_help()
        sys.exit(1)
    if opts.prompt:
        data = prompt_for_dct(data)
    ignore = opts.ignore.split(',')
    builder = Builder(data, ignore, [StringTemplateFilter()], 
                      opts.overwrite, opts.regex)
    dirs, files = builder.build(*args)
    print dirs, "directories creatd"
    print files, "files written"

def test():
    dct = prompt_for_dct(dict(foo='newfoo', bar='newbar', baz='newbaz'))
    builder = Builder(dct, ignore=['dontcopy'], 
                      filters=[StringTemplateFilter()])
    print builder.build('template1', 'myproj')
    print builder.build('template2', 'myproj')

if __name__ == '__main__':
    #import sys; test(); sys.exit()
    command()


