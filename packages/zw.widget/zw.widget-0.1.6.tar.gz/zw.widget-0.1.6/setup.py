import os, sys, urllib, urllib2
from zipfile import ZipFile
from HTMLParser import HTMLParser
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

name = 'zw.widget'
version = '0.1.6'
extpaths = []

tinymce_version = '3.2.1.1'
tinymce_src_name = 'tinymce_%s.zip' % tinymce_version.replace('.', '_')
tinymce_base_url = 'http://downloads.sourceforge.net/tinymce'
tinymce_dest = os.path.join(os.path.dirname(__file__),
                    'src', 'zw', 'widget', 'tiny', 'tiny_mce')
tinymce_lang_src_name = 'tinymce_lang_pack.zip'
tinymce_lang_base_url = 'http://services.moxiecode.com/i18n/'
tinymce_lang_post_url = tinymce_lang_base_url+'download.aspx'
params = dict(format='zip', product='tinymce')

class TinyMCELangParser(HTMLParser):
    
    params = {}

    def handle_startendtag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'input' and attrs.get('type',None) == 'checkbox' and \
                'name' in attrs and 'value' in attrs:
            self.params[attrs['name']] = attrs['value']

# Download the TinyMCE code
if not os.path.exists(tinymce_src_name):
    if not os.path.exists(tinymce_src_name):
        f = open(tinymce_src_name, 'w')
        f.write(urllib2.urlopen( tinymce_base_url+'/'+tinymce_src_name).read())
        f.close()
    zfile = ZipFile(tinymce_src_name, 'r')
    prefix = 'tinymce/jscripts/tiny_mce/'
    lprefix = len(prefix)-1
    for zname in sorted(zfile.namelist()):
        assert zname.startswith('tinymce/')
        if zname.startswith(prefix):
            dname = tinymce_dest + zname[lprefix:]
            if dname[-1:] == '/':
                os.makedirs(dname)
            else:
                f = open(dname, 'w')
                f.write(zfile.read(zname))
                f.close()
    zfile.close()

# Download new language packs
if not os.path.exists(tinymce_lang_src_name):
    parser = TinyMCELangParser()
    parser.feed(urllib2.urlopen( tinymce_lang_base_url ).read())
    params.update(parser.params)
    fi = urllib2.urlopen( tinymce_lang_post_url, urllib.urlencode(params) )
    fo = open(tinymce_lang_src_name, 'w')
    fo.write( fi.read() )
    fo.close()
    fi.close()
    zfile = ZipFile(tinymce_lang_src_name, 'r')
    for zname in sorted(zfile.namelist()):
        dname = os.path.join(tinymce_dest, zname)
        if dname[-1:] == '/':
            os.makedirs(dname)
        else:
            f = open(dname, 'w')
            f.write(zfile.read(zname))
            f.close()
    zfile.close()

# Add files for packaging
lbase = len(os.path.dirname(tinymce_dest))+1
for path, dirs, files in os.walk(tinymce_dest):
    prefix = path[lbase:]
    for file in files:
        extpaths.append(os.path.join(prefix, file))

setup(name=name,

      # Fill in project info below
      version=version,
      description="Additional widgets for z3c.form",
      long_description=(
        read('README.txt') + \
            '\n\n' +
        read('src', 'zw', 'widget', 'color', 'README.txt') + \
            '\n\n' +
        read('src', 'zw', 'widget', 'email', 'README.txt') + \
            '\n\n' +
        read('src', 'zw', 'widget', 'lines', 'README.txt') + \
            '\n\n' +
        read('src', 'zw', 'widget', 'tiny', 'README.txt') + \
            '\n\n' +
        read('CHANGES.txt')),
      keywords='zope3',
      author='Gregor Giesen',
      author_email='giesen@zaehlwerk.net',
      url='https://launchpad.net/'+name,
      license='GPLv3',
      # Get more from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=['Development Status :: 4 - Beta',
                   'Programming Language :: Python',
                   'Environment :: Web Environment',
                   'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
                   'Framework :: Zope3',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: GNU General Public License (GPL)',
                   ],

      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zw'],
      include_package_data=True,
      package_data = {'zw.widget': extpaths},
      zip_safe=False,
      extras_require = dict(
        test = [ 'zope.testing',
                 'zope.app.testing',
                 'zope.app.zcmlfiles',
                 'zope.testbrowser',
                 'z3c.testsetup',
                ], ),
      install_requires = ['setuptools',
                          'zope.i18nmessageid',
                          'zope.interface',
                          'zope.schema',
                          'z3c.form',
                          'z3c.schema',
                          'zw.schema',
                          'zc.resourcelibrary',
                          ],
      )
