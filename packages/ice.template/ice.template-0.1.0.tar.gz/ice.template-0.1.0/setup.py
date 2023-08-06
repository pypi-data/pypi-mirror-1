import sys, os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version='0.1.0'

setup(name='ice.template',
      version='0.1.0',
      author='Ilshad Habibullin',
      author_email = 'astoon.net at gmail.com',
      url='http://launchpad.net/ice.template',
      description = 'Persistent cheetah templates',
      long_description = (read('src/ice/template/README.txt')
                          + '\n\n' + read('CHANGES.txt')),
      license = 'GPL v.3',
      classifiers = [
              'Development Status :: 4 - Beta',
              'Environment :: Web Environment',
              'Intended Audience :: Developers',
              'License :: OSI Approved :: GNU General Public License (GPL)',
              'Programming Language :: Python',
              'Natural Language :: English',
              'Operating System :: OS Independent',
              'Topic :: Internet :: WWW/HTTP :: Site Management',
              'Framework :: Zope3'],
      packages=find_packages('src'),
      namespace_packages=['ice',],
      package_dir={'':'src'},

      extras_require = dict(
              test=['zope.app.zcmlfiles',
                    'zope.app.testing',
                    'zope.testing',
                    'zope.testbrowser',
                    'zope.securitypolicy',
                    'z3c.sampledata']),
      
      install_requires=['setuptools',
                        'Cheetah',
                        'ZODB3',
                        'zope.dublincore',
                        'z3c.formui',
                        'z3c.layer',
                        'z3c.pagelet',
                        'z3c.table'],
      
      dependency_links = ['http://download.zope.org/distribution'], 
      include_package_data=True,
      zip_safe=False)
