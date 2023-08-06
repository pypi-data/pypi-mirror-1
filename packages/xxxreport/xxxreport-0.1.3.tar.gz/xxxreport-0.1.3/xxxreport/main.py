import time
from optparse import OptionParser

from xxxreport import __version__ as VERSION

import os
import cgi

def _parse_options():
    """parses `xxxreport` args options"""

    parser = OptionParser(usage="""usage: %prog [options] sourcepath
    
""",
                          version='%%prog %s' % VERSION)

    parser.add_option('--html', dest='html_render',
                      action='store_true', default=False,
                      help='export to html format'
                      )

    parser.add_option('--txt', dest='txt_render',
                      action='store_true', default=False,
                      help='export to plain text format')

    parser.add_option('--title', dest='title',
                      action='store', default='',
                      help='define the title of document report')

    parser.add_option('--marker', dest='marker',
                      action='store', default='TODO,XXX',
                      help='define the comments marker to extract. Each item are separated by a comma. By default "%default" is used.')

    parser.add_option('--file-extension', dest='file_extension',
                      action='store', default='.py,.js',
                      help='define the file extension to parse. Each item are separated by a comma. By default "%default" is used.')

    parser.add_option('--marker-prefix', dest='marker_prefix',
                      action='store', default='#,//',
                      help='define the marker prefix. Each item are separated by a comma. By default "%default" is used.')

    (options, args) = parser.parse_args()

    if len(args) == 0:
        parser.error("`sourcepath` argument missing")


    if (options.html_render):
        options.render = 'html'
    else:
        options.render = 'txt'

    options.marker = [m.strip() for m in options.marker.split(',') ]
    options.file_extension = [m.strip() for m in options.file_extension.split(',') ]
    options.marker_prefix = [m.strip() for m in options.marker_prefix.split(',') ]

    del options.html_render
    del options.txt_render

    return options, args

def extract_files(path, filters = ('.py', )):
    for root, dirs, files in os.walk(path):
        for f in files:
            if f[0] == '.':
                continue

            for one_filter in filters:
                if f.endswith(one_filter):
                    yield os.path.join(root, f)
                    break

        for i in range(len(dirs) - 1, -1, -1):
            if dirs[i][0] == '.':
                del dirs[i]

def extract_comments(filename, marker = ('TODO', 'XXX', ), marker_prefix = ('.py', '.js',)):
    f = open(filename, 'r')
    capture = 0
    line_number = 0
    for line in f:
        line_number += 1
        if capture == 0:
            for m in marker:
                for p in marker_prefix:
                    if line.find(p + ' ' + m) > 0:
                        capture = 3
                        item = {
                            'line_number': line_number,
                            'data': line
                        }
                        break
        else:
            item['data'] += line
            capture -= 1
            if capture == 0:
                yield item

    if capture > 0:
          yield item  

    f.close()

def item_txt_render(item):
    return """File : %(filename)s:%(line)s

%(text)s
""" % {
    'filename': item['filename'],
    'line': item['line_number'],
    'text': item['data']
}

def item_html_render(item):
    return """<li><strong>File : %(filename)s:%(line)s</strong><br />
<pre>%(text)s</pre></li>
""" % {
    'filename': item['filename'],
    'line': item['line_number'],
    'text': cgi.escape(item['data'])
}

def page_txt_render(number_item, content, title= '', marker='XXX/TODO'):
    page_title = marker + ' Comment report' + (' for ' + title if title !='' else '')
    buffer = ('=' * len(page_title)) + "\n"
    buffer += page_title + "\n"
    buffer += ('=' * len(page_title)) + "\n"
    buffer += """

Generated on %(reporttime)s

Summary
=======

There are currently %(commentcount)s %(marker)s comments.

Listing
=======

""" % {
        'commentcount': number_item,
        'reporttime': time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime()),
        'marker': marker
    }

    buffer += content
    return buffer

def page_html_render(number_item, content, title, marker='XXX/TODO'):
    buffer = """<html>
    <head>
        <title>%(marker)s Comment report%(pagetitle)s</title>
    </head>
    <body>
        <h1>%(marker)s Comment report%(pagetitle)s</h1>

<p>Generated on %(reporttime)s</p>

<h3>Summary</h3>

<p>There are currently %(commentcount)s %(marker)s comments.</p>

<h3>Listing</h3>

""" % {
        'pagetitle': (' for ' + title) if title !='' else '',
        'commentcount': number_item,
        'reporttime': time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime()),
        'marker': marker
    }

    buffer += content
    buffer += '</body></html>'
    return buffer

def main():
    options, path = _parse_options()

    buffer = ''
    number_item = 0
    root_path_str_len = len(path[0])
    for f in extract_files(path[0], options.file_extension):
        for item in extract_comments(f, options.marker, options.marker_prefix):
            number_item += 1
            item['filename'] = f[root_path_str_len:]
            if options.render == 'txt':
                buffer += item_txt_render(item)
            elif options.render == 'html':
                buffer += item_html_render(item)
    
    if options.render == 'txt':
        print(page_txt_render(number_item, buffer, options.title, '/'.join(options.marker)))
    elif options.render == 'html':
        print(page_html_render(number_item, buffer, options.title, '/'.join(options.marker)))
        

if __name__ == "__main__":
    main()
