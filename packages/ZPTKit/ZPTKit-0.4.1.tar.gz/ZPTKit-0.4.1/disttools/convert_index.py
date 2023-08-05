import re

base_template = '''\
<!--#include virtual="/ssi/doctype.ssi" -->
<head>
<title>%(title)s</title>
<!--#include virtual="/ssi/genmeta.ssi" -->
<!--#set var="section" value="software" -->
<!--#include virtual="/ssi/dhtml.ssi" -->
<link rel="stylesheet" href="default.css" type="text/css">
</head>

<!--#include virtual="/ssi/bodytag.ssi" -->
<!--#include virtual="/ssi/header.ssi" -->
<!--#include virtual="/ssi/sidenav.ssi" -->
<!--#include virtual="/ssi/gutter.ssi" -->
<!--  =========  BEGIN PAGE CONTENT ======== -->

%(body)s

<!-- ========  END PAGE CONTENT =========  --> 
<!--#include virtual="/ssi/footer.ssi" -->
</body></html>
'''

re_start = re.compile(r'^.*<body>', re.I+re.S)
re_end = re.compile(r'</body>.*$', re.I+re.S)
re_title = re.compile(r'<title>(.*?)</title>', re.I+re.S)

def convert_index(content):
    title = re_title.search(content).group(1)
    content = re_start.sub('', content)
    content = re_end.sub('', content)
    return base_template % {
        'title': title,
        'body': content}

if __name__ == '__main__':
    import sys
    if sys.argv[1:]:
        print 'Usage: convert_index.py < rest_file.html > imagescape_version.html'
        sys.exit()
    sys.stdout.write(convert_index(sys.stdin.read()))
    
