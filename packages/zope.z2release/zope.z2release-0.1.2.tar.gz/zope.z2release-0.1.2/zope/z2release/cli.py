"""
Generate an index file based on the version.cfg file of Zope 2
in order to provide a version specific index page generated to be used
in combination with easy_install -i <some_url>

Usage:

cli.py tags/2.12.0a3 /tmp/index/2.12.0a3
cli.py branches/2.12 tmp/index/2.12

"""

import os
import sys
import urlparse
import urllib
import tempfile
from xmlrpclib import Server
from ConfigParser import RawConfigParser as ConfigParser

# packages containing upper-case letters
upper_names = ('ClientForm', 'RestrictedPython', 'ZConfig', 'ZODB3', 'zLOG', 
               'Acquisition', 'DateTime', 'ExtensionClass', 'Persistence')

def write_index(package, version, dirname):
    print >>sys.stderr, 'Package %s==%s' % (package, version)
    dest_dir = os.path.join(dirname, package)
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    index_html = os.path.join(dest_dir, 'index.html')

    fp = file(index_html, 'w')
    print >>fp, '<html><body>'
    lst = server.package_urls(package, version)
    if lst:
        # package hosted on PyPI
        for d in lst:
            link = '<a href="%s">%s</a>' % (d['url'], d['filename'])
            print >>fp, link
            print >>fp, '<br/>'
    else:
        # for externally hosted packages we need to rely on the 
        # download_url metadata
        rel_data = server.release_data(package, version)
        download_url = rel_data['download_url']
        filename = os.path.basename(urlparse.urlparse(download_url)[2])
        link = '<a href="%s">%s</a>' % (download_url, filename)
        print >>fp, link

    print >>fp, '</body></html>'
    fp.close()

def main():

    global server

    tag = sys.argv[1]
    dirname = sys.argv[2]

    version = tag.split('/')[-1]

    versions_url = 'http://svn.zope.org/*checkout*/Zope/%s/versions.cfg' % tag
    print >>sys.stderr, 'Fetching %s' % versions_url
    data = urllib.urlopen(versions_url).read()
    tmp_version_file = tempfile.mktemp()
    file(tmp_version_file, 'w').write(data)

    CP = ConfigParser()
    CP.read(tmp_version_file)

    server = Server('http://pypi.python.org/pypi')
    links = list()

    write_index('Zope2', version, dirname)
    for package in CP.options('versions'):

        # options() returns all options in lowercase but
        # we must preserve the case for package names
        for name in upper_names:
            if name.lower() == package:
                package = name
                break
        version = CP.get('versions', package)
        write_index(package, version, dirname)

if __name__ == '__main__':
    main()
