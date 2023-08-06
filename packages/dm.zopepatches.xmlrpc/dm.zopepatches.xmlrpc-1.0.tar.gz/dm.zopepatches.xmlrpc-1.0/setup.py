from os.path import abspath, dirname, join
try:
  # try to use setuptools
  from setuptools import setup
  setupArgs = dict(
      include_package_data=True,
      namespace_packages=['dm', 'dm.zopepatches'],
      zip_safe=False,
      install_requires=[
         'dm.reuse',
         # 'Zope2',
         ],
      entry_points = dict(
        ),
      )
except ImportError:
  # use distutils
  from distutils import setup
  setupArgs = dict(
    )

cd = abspath(dirname(__file__))
pd = join(cd, 'dm', 'zopepatches', 'xmlrpc')

def pread(filename, base=pd): return open(join(base, filename)).read().rstrip()

setup(name='dm.zopepatches.xmlrpc',
      version=pread('VERSION.txt').split('\n')[0],
      description="Control whether Zope interprets a request as xmlrpc.",
      long_description=pread('README.txt'),
      classifiers=[
#        'Development Status :: 3 - Alpha',
       'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Framework :: Zope2',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
        ],
      author='Dieter Maurer',
      author_email='dieter@handshake.de',
      url='http://pypi.python.org/pypi/dm.zopepatches.xmlrpc',
      packages=['dm', 'dm.zopepatches', 'dm.zopepatches.xmlrpc',
                'dm.zopepatches.xmlrpc.publisher',
                ],
      keywords='application development web xmlrpc Zope',
      license='ZPL',
      **setupArgs
      )
