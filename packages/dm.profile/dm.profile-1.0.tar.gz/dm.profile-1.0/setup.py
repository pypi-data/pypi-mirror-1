from os.path import abspath, dirname, join
try:
  # try to use setuptools
  from setuptools import setup
  setupArgs = dict(
      include_package_data=True,
      namespace_packages=['dm'],
      zip_safe=True,
      )
except ImportError:
  # use distutils
  from distutils import setup
  setupArgs = dict(
    )

cd = abspath(dirname(__file__))
pd = join(cd, 'dm', 'profile')

def pread(filename, base=pd): return open(join(base, filename)).read().rstrip()

setup(name='dm.profile',
      version=pread('VERSION.txt'),
      description='Easier readable profile statistics -- especially for caller and callee analysis',
      long_description=pread('README.txt'),
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development',
        ],
      url="http://pypi.python.org/pypi/dm.profile",
      author='Dieter Maurer',
      author_email='dieter@handshake.de',
      packages=['dm', 'dm.profile',],
      keywords='profiling statistics caller callee analysis',
      license='BSD (see "dm/profile/LICENSE.txt", for details)',
      **setupArgs
      )
