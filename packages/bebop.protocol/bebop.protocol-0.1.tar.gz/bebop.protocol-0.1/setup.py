from setuptools import setup, find_packages
import xml.sax.saxutils

from os.path import dirname, join

def read(*rnames): 
    text = open(join(dirname(__file__), *rnames)).read()
    return xml.sax.saxutils.escape(text)

long_description=( 
        read('README.txt') 
        + '\n' + 
        'Detailed Documentation\n' 
        '**********************\n' 
        + '\n' + 
        read('src', 'bebop', 'protocol', 'README.txt') 
        + '\n' + 
        'Download\n' 
        '**********************\n' 
        ) 
open('documentation.txt', 'w').write(long_description) 

description = "This package allows to register components from Python."\
              " It also provides a basic implementation"\
              " of generic functions in Zope3"
setup(
    name='bebop.protocol',
    version='0.1',
    author='Bebop Team',
    author_email='uwe_oestermeier@iwm-kmrc.de',
    summary='Registers components and generic functions in Python',
    url='http://svn.kmrc.de/projects/devel/bebop.protocol',
    description=description,
    long_description=long_description,
    
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
    keywords = "zope3 ZCML generation configuration",    
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    zip_safe=False,
    license='GPL',
    platforms = ["any"],
    install_requires=['setuptools',
                      'zope.interface',
                      'zope.component',
                      'zope.configuration',
                      'zope.publisher',
                      'zope.schema',
                      'zope.dottedname',
                      'zope.app.component',
                      'zope.app.publisher'
                      ],
)
