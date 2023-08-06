import os, urllib2, zipfile
from setuptools import setup, find_packages

name = 'zw.jsmath'
version = '3.4f-0.9'
patch = 'jsmath-3.4f-xhtml.patch'
jsmath_src_name = 'jsMath-3.4f.zip'
jsmath_fonts_src_name = 'jsMath-fonts-1.3.zip'
url_base = 'http://downloads.sourceforge.net/jsmath'
dest = os.path.join(os.path.dirname(__file__),
                    'src', 'zw', 'jsmath', 'jsMath')
dest_fonts = os.path.join(dest, 'fonts')
extpaths = []

if not os.path.exists(dest):
    if not os.path.exists(jsmath_src_name):
        x = urllib2.urlopen( url_base+'/'+jsmath_src_name).read()
        open(jsmath_src_name, 'w').write(x)
    zfile = zipfile.ZipFile(jsmath_src_name, 'r')
    prefix = 'jsMath/'
    lprefix = len('jsMath')
    for zname in sorted(zfile.namelist()):
        assert zname.startswith(prefix)
        dname = dest + zname[lprefix:]
        if dname[-1:] == '/':
            os.makedirs(dname)
        else:
            open(dname, 'w').write(zfile.read(zname))
            #extpaths.append(zname)

    #apply xhtml patch
    os.system( 'patch -d '+dest+' < '+\
                   os.path.join( os.path.dirname(__file__), patch ) )

if not os.path.exists(dest_fonts):
    # unpack fonts
    if not os.path.exists(jsmath_fonts_src_name):
        x = urllib2.urlopen( url_base+'/'+jsmath_fonts_src_name).read()
        open(jsmath_fonts_src_name, 'w').write(x)
    zfile = zipfile.ZipFile(jsmath_fonts_src_name, 'r')
    prefix = 'jsMath/fonts/'
    lprefix = len('jsMath/fonts')
    for zname in sorted(zfile.namelist()):
        try:
            assert zname.startswith(prefix)
        except AssertionError:
            continue
        dname = dest_fonts + zname[lprefix:]
        if dname[-1:] == '/':
            os.makedirs(dname)
        else:
            open(dname, 'w').write(zfile.read(zname))
            #extpaths.append(zname)

# Add files for packaging    
lbase = len(os.path.dirname(dest))+1
for path, dirs, files in os.walk(dest):
    prefix = path[lbase:]
    for file in files:
        extpaths.append(os.path.join(prefix, file))

               
def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name=name,

      # Fill in project info below
      version=version,
      description="jsMath integration into zope3",
      long_description=(
        read('README.txt')),
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
      include_package_data=True,
      package_data = {'zw.jsmath': extpaths},
      namespace_packages = ['zw'],
      zip_safe=False,
      extras_require = dict(
        test = [ 'zope.testing',
                 'zope.app.testing',
                 'zope.app.zcmlfiles',
                 'zope.testbrowser',
                ], ),
      install_requires = ['setuptools',
                          'zc.resourcelibrary',
                          ],
      )
