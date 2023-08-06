import sys, os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version='0.2.2'

setup(
    name='ice.adverlet',
    version='0.2.2',
    author='Ilshad Habibullin',
    author_email = 'astoon.net at gmail.com',
    url='http://launchpad.net/ice.adverlet',
    description = 'Simple way to edit any HTML snippet',
    long_description = (
        read('src/ice/adverlet/README.txt')
        + '\n\n' +
        read('src/ice/adverlet/demo/README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
        'Framework :: Zope3'],
    license = 'GPL v.3',
   
    packages=find_packages('src'),
    namespace_packages=['ice',],
    package_dir={'':'src'},

    extras_require = dict(
        test = ['zope.app.testing',
                'zope.app.twisted',
                'zope.app.cache',
                'zope.app.catalog',
                'zope.app.securitypolicy',
                'zope.contentprovider',
                'zope.testbrowser',
                'z3c.autoinclude',
                'z3c.sampledata'
                ]
        ),

    install_requires=['setuptools',
                      'rwproperty',
                      'z3c.autoinclude',
                      'zope.contentprovider',
                      'zope.app.undo',
                      'zc.resourcelibrary',
                      'z3c.widget',
                      # demo app
                      'zope.app.zcmlfiles',
                      'zope.app.twisted',
                      'zope.app.securitypolicy',
                      'zope.app.catalog',
                      'zope.app.apidoc',
                      'zope.app.preference'
                      ],

    dependency_links = ['http://download.zope.org/distribution'], 
    include_package_data=True,
    zip_safe=False,
    )
