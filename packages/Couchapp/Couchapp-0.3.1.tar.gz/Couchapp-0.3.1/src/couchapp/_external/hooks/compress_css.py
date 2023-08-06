#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2008, 2009 Benoit Chesneau <benoitc@e-engura.org>
#
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution.

from optparse import OptionParser
import os
import sys
sys.path.append(os.path.dirname(__file__))

# backport os.path.relpath if python < 2.6
try:
    import os.path.relpath as _relpath
except ImportError:
    def _relpath(path, start=os.curdir):
        if not path:
            raise ValueError("no path specified")
        
        start_list = os.path.abspath(start).split("/")
        path_list = os.path.abspath(path).split("/")

        # Work out how much of the filepath is shared by start and path.
        i = len(os.path.commonprefix([start_list, path_list]))

        rel_list = ['..'] * (len(start_list)-i) + path_list[i:]
        if not rel_list:
            return os.curdir
        return os.path.join(*rel_list)

from couchapp.utils import write_content

__all__ = ['CSSParser', 'merge_css']

re_selector = re.compile("/\./")
re_comments = re.compile("(\/\*).*?(\*\/)")
re_sep = re.compile(':\s*')
re_line1 = re.compile('\n')
re_line = re.compile('(\n)')
re_comma = re.compile(',')
re_comma2 = re.compile(',  ')


def strip_space(string):
    """  strip space after :, remove newlines, replace 
    multiple spaces with only one space, remove comments """
    if isinstance(string, basestring):
        string = re_line1.sub('', re_sep.sub(':', string))
        string = re_comments.sub('', string.strip())
    return string
    
def strip_selector_space(string):
    """ remove newlines, insert space after comma, replace 
    two spaces with one space after comma """
    if isinstance(string, basestring):
        string = re_comma2.sub(', ', re_comma.sub(', ', re_line.sub('', string)))
    return string
    
class CSSParser(object):
    
    def __init__(self, css_string, options=None):
        options = options or {}
        self.namespace = options.get('namespace', '')
        self.raw_data = css_string
        self.css_output = ''
        
        self._compress(self.raw_data)
        
    def __str__(self):
        return self.css_output
        
    def parse(self, data):
        data = data or self.raw_data
        css_out = []
        data = strip_space(data.strip())
        for index, assignements in enumerate(data.split('}')):
            try:
                tags, styles = [a.strip() for a in assignements.strip().split('{')]
                rules = []
                if styles:
                    if self.namespace:
                        tags = strip_selector_space(tags)
                        tags = re_selector.sub(self.namespace, tags)
                        rules = []
                    for key_val_pair in styles.split(';'):
                        try:
                            key, value =  [a.strip() for a in key_val_pair.split(':')]
                            rules.append("%s:%s;" % (key, value))
                        except ValueError:
                            continue
                    css_out.append({
                        'tags': tags,
                        'rules': ''.join(rules),
                        'idx': index 
                    })
            except ValueError:
                continue
        css_out.sort(lambda a,b: cmp(a['idx'], b['idx']))
        return css_out
        
    def _compress(self, data):
        self.css_output = '';

        for line in self.parse(data):
            self.css_output += "%s {%s}\n" % (line['tags'], line['rules'])    


def merge_css(app_dir, app_name, verbose=False):
    docid = '_design/%s' % app_name
    attach_dir = os.path.join(app_dir, '_attachments')
    
    re_url = re.compile('url\s*\(([^\s"].*)\)')

    src_fpath = ''
    fname_dir = ''

    def replace_url(mo):
        """ make sure urls are relative to css path """
        css_url = mo.group(0)[4:].strip(")").replace("'", "").replace('"','')
        css_path = os.path.join(os.path.dirname(src_fpath),
                css_url)

        rel_path = _relpath(css_path, fname_dir)
        return "url(%s)" % rel_path
    
    for fname, src_files in conf['css'].iteritems():
        output_css = ''

        dest_path = os.path.join(attach_dir, fname)
        fname_dir = os.path.dirname(dest_path)

        for src_fname in src_files:
            src_fpath = os.path.join(attach_dir, src_fname)
            
            if os.path.exists(src_fpath):
                content_css = str(CSSParser(read_file(src_fpath)))
                content_css = re_url.sub(replace_url, content_css) 
                output_css += content_css
                if verbose >= 2:
                    print "Merging %s in %s" % (src_fname, fname)

        if not os.path.isdir(fname_dir):
            os.makedirs(fname_dir)

        write_content(dest_path, output_css)
        
def main():
    parser = OptionParser(usage='%prog appdir appname') 
    options, args = parser.parse_args()

    if len(args) < 2:
        return parser.error('incorrect number of arguments')
        
    merge_css(args[0], args[1])
    
if __name__ == '__main__':
    main()