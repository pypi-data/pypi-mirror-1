from os.path import abspath, dirname, join
try:
  # try to use setuptools
  from setuptools import setup
  setupArgs = dict(
      include_package_data=True,
      namespace_packages=['dm'],
      zip_safe=True,
      test_suite='dm.sharedresource.tests.testsuite',
      )
except ImportError:
  # use distutils
  from distutils import setup
  setupArgs = dict(
    )

cd = abspath(dirname(__file__))
pd = join(cd, 'dm', 'sharedresource')

def pread(filename, base=pd): return open(join(base, filename)).read().rstrip()

setup(name='dm.sharedresource',
      version=pread('VERSION.txt'),
      description='Resources which can safely be used by concurrent threads',
      long_description=pread('README.txt'),
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development',
        'Topic :: Utilities',
        ],
      author='Dieter Maurer',
      author_email='dieter@handshake.de',
      url='http://www.dieter.handshake.de/pyprojects/Zope',
      packages=['dm', 'dm.sharedresource',],
      keywords='sharedresource ',
      license='BSD (see "dm/sharedresource/LICENSE.txt", for details)',
      **setupArgs
      )
