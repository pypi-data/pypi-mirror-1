from os.path import abspath, dirname, join
try:
  # try to use setuptools
  from setuptools import setup
  setupArgs = dict(
      include_package_data=True,
      namespace_packages=['dm'],
      zip_safe=True,
      test_suite='dm.iter.tests.testsuite',
      )
except ImportError:
  # use distutils
  from distutils import setup
  setupArgs = dict(
    )

cd = abspath(dirname(__file__))
pd = join(cd, 'dm', 'iter')

def pread(filename, base=pd): return open(join(base, filename)).read().rstrip()

setup(name='dm.iter',
      version=pread('VERSION.txt'),
      description='Some iterator utilities',
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
      url='http://pypi.python.org/pypi/dm.iter',
      author='Dieter Maurer',
      author_email='dieter@handshake.de',
      packages=['dm', 'dm.iter',],
      keywords='iter closure',
      license='BSD (see "dm/iter/LICENSE.txt", for details)',
      **setupArgs
      )



