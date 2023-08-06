#!/usr/bin/env python
"""Client implentation of the http://www.pypaste.com/services/json API."""

__author__ = 'Matt Kemp <matt@matticus.org>'
__version__ = 'pypaster 0.5.3 8/27/08'
__license__ = """
Copyright (c) 2008 Matt Kemp <matt@mattikus.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import httplib
import os.path
import sys
import urlparse

import simplejson

def connect(method, data=None, paste_id=None):

    site = 'www.pypaste.com'
    headers = {'Accept': 'application/json',
               'Content-type': 'application/json'}

    conn = httplib.HTTPConnection(site)
    if method == 'create' and data:
        conn.request('POST', '/', data, headers)
    elif method == 'update' and paste_id and data:
        conn.request('PUT', '/%s' % paste_id, data, headers)
    elif method == 'get' and paste_id:
        conn.request('GET', '/%s' % paste_id, headers=headers)
    else:
        return 'Error: unsupported method or missing argument'

    try:
        response = conn.getresponse()
    except httplib.HTTPException, e:
        return e.message
    else:
        if response.status != 200:
            return 'Error: %d %s, method: %s\n' % (response.status, 
                                                   response.reason,
                                                   method)
        else:
            return simplejson.load(response)

def get_paste(paste_id):

    return connect('get', paste_id=paste_id)

def get_languages():

    return connect('get', paste_id='_all_languages')

def update_string(snippet, paste_id, title=None, language=None):

    data = get_paste(paste_id)
    if isinstance(data, str):
        return data
    if title != data['title']:
        data['title'] = title
    if language != data['language']:
        data['language'] = language
    data['snippet'] = snippet
    data = simplejson.dumps(data)
    sys.stdout.write(data)
    json_data = connect('update', data=data, paste_id=paste_id)
    if json_data['ok']:
        return '%s updated to revision: %s' % (json_data['url'], 
                                               json_data['revid'])
    else:
        return 'Error: %s' % json_data['reason']

def update_file(fp, paste_id, title='', language='text'):

    return update_string(fp.read(), paste_id, title=title, language=language)

def post_string(snippet, title, language):

    data = {'snippet': snippet,
            'title': title,
            'language': language }

    json_data = connect('create', data=simplejson.dumps(data))
    if isinstance(json_data, str):
        return json_data
    if json_data['ok']:
        return 'Paste URL for %s: %s' % (title, json_data['url'])
    else:
        return 'Error: %s' % json_data['reason']

def post_file(fp, title, language):

    try:
        snippet = fp.read()
    except KeyboardInterrupt, e:
        sys.exit('\n')

    return post_string(snippet, title=title, language=language)

def main():
    from optparse import OptionParser

    parser = OptionParser(version=__version__)
    parser.add_option('-g', '--get', dest='get_url', 
                      help='download a paste identified by pypaste url')
    parser.add_option('-l', '--language', dest='language',
                      help='language snippet is written in', default='text')
    parser.add_option('-u','--update', dest='update_url',
                      help='updates a paste identified by pypaste url')
    parser.add_option('-t', '--title', dest='title', 
                      help='title of the snippet')
    parser.add_option('-O', dest='filename',
                      help='output to FILENAME instead of stdout')
    parser.add_option('--get-languages', dest='getlang', action='store_true',
                      help='gets a list of all supported languages and exit')
    parser.set_usage("%prog [options] [file1 file2 ...]")
    parser.set_description(__doc__)

    opts, args = parser.parse_args()

    if opts.get_url:
        if opts.filename:
            sys.stdout = open(opts.filename, 'w')
        paste_id = urlparse.urlsplit(opts.get_url)[2]
        print get_paste(paste_id)['snippet']
        sys.exit()

    if opts.getlang:
        langs = get_languages()
        temp = langs.items()
        temp.sort()
        print "Supported Languages:"
        for key, value in temp:
            print value + ':', "".join(key).rjust(30 - len(value)) 
        sys.exit()

    if opts.update_url:
        snippet = open(args[0], 'r')
        url = urlparse.urlsplit(opts.update_url)[2]
        print update_file(snippet, url, opts.title, opts.language)
    else:
        if len(args) < 1:
            print post_file(sys.stdin, '', opts.language)
        else:
            for filename in args:
                if not opts.title:
                    title = os.path.basename(filename)
                else:
                    title = opts.title
                snippet = open(filename, 'r')
                print post_file(snippet, title, opts.language)
                snippet.close()


if __name__ == '__main__':
    main()
