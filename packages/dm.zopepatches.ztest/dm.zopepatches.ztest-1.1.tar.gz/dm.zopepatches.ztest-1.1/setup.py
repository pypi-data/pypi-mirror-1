from os.path import abspath, dirname, join
try:
  # try to use setuptools
  from setuptools import setup
  setupArgs = dict(
      include_package_data=True,
      namespace_packages=['dm', 'dm.zopepatches'],
      zip_safe=False,
      entry_points = dict(
         console_scripts = [
           'ztest = dm.zopepatches.ztest:main',
           ]
        ),
      )
except ImportError:
  # use distutils
  from distutils import setup
  setupArgs = dict(
    )

cd = abspath(dirname(__file__))
pd = join(cd, 'dm', 'zopepatches', 'ztest')

def pread(filename, base=pd): return open(join(base, filename)).read().rstrip()

setup(name='dm.zopepatches.ztest',
      version=pread('VERSION.txt').split('\n')[0],
      description='Script to run tests for Zope application components (without buildout).',
      long_description=pread('README.txt'),
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Framework :: Zope2',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
        ],
      author='Dieter Maurer',
      author_email='dieter@handshake.de',
      url='http://pypi.python.org/dm.zopepatches.ztest',
      packages=['dm', 'dm.zopepatches', 'dm.zopepatches.ztest'],
      keywords='script test component',
      license='BSD',
      **setupArgs
      )



